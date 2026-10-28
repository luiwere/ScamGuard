import asyncio
import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.models.schemas import (
    StartCallMessage,
    StopCallMessage,
    TranscriptEvent,
    TacticsEvent,
    RiskEvent,
    AlertEvent,
    ErrorEvent,
)

logger = logging.getLogger("scamguard.ws")
router = APIRouter()


class CallSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.is_active = False
        self.scenario_id: Optional[str] = None
        self.contact = None
        self.total_audio_bytes = 0
        self.chunk_count = 0
        self._replay_task: Optional[asyncio.Task] = None

    async def send_event(self, event_model):
        """Send a Pydantic event as JSON text frame to the client."""
        try:
            payload = event_model.model_dump_json()
            await self.websocket.send_text(payload)
        except Exception as e:
            logger.error(f"Failed to send event: {e}")

    async def handle_start(self, data: dict):
        try:
            msg = StartCallMessage(**data)
            self.is_active = True
            self.scenario_id = msg.scenario
            self.contact = msg.contact
            self.total_audio_bytes = 0
            self.chunk_count = 0
            logger.info(f"Call session started. Scenario: {self.scenario_id}, Contact: {self.contact}")

            # Send initial safe risk state
            await self.send_event(RiskEvent(score=0, level="safe"))

            # Inform client call session is established
            await self.send_event(
                TranscriptEvent(
                    text="[Call connected - ScamGuard active]",
                    is_final=True,
                    speaker="system"
                )
            )
        except ValidationError as e:
            await self.send_event(ErrorEvent(message=f"Invalid start payload: {e}"))

    async def handle_stop(self):
        logger.info(f"Call session stopped. Processed {self.chunk_count} chunks ({self.total_audio_bytes} bytes).")
        self.is_active = False
        if self._replay_task and not self._replay_task.done():
            self._replay_task.cancel()
        await self.send_event(
            TranscriptEvent(
                text="[Call disconnected]",
                is_final=True,
                speaker="system"
            )
        )

    async def handle_audio_chunk(self, data: bytes):
        if not self.is_active:
            return
        self.total_audio_bytes += len(data)
        self.chunk_count += 1

        # PCM16 16kHz mono = 2 bytes per sample -> len(data) / 2 samples
        # Every ~40 chunks (~10s of audio or on speech pause), STT and pipeline kick in.
        # In Phase 1 foundation: verify audio intake and log periodic throughput.
        if self.chunk_count % 20 == 0:
            logger.debug(f"Received {self.chunk_count} audio chunks ({self.total_audio_bytes} bytes).")


@router.websocket("/ws/call")
async def call_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = CallSession(websocket)
    logger.info("Client connected to /ws/call")

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                await session.handle_audio_chunk(message["bytes"])
            elif "text" in message and message["text"]:
                try:
                    payload = json.loads(message["text"])
                    msg_type = payload.get("type")
                    if msg_type == "start":
                        await session.handle_start(payload)
                    elif msg_type == "stop":
                        await session.handle_stop()
                    else:
                        await session.send_event(ErrorEvent(message=f"Unknown message type: {msg_type}"))
                except json.JSONDecodeError:
                    await session.send_event(ErrorEvent(message="Malformed JSON message"))
            elif message.get("type") == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        logger.info("Client disconnected from /ws/call")
    except Exception as e:
        logger.error(f"Unexpected error in /ws/call: {e}", exc_info=True)
    finally:
        await session.handle_stop()
