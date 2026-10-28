import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional, List
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
    TacticItem,
    Scenario,
)
from app.services.rules import rules_engine
from app.services.stt import stt_service
from app.services.llm import llm_judge
from app.services.scoring import RiskScoringEngine

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
        self.audio_buffer = bytearray()
        self.transcript_window: List[str] = []
        self.all_detected_tactics: List[TacticItem] = []
        self.scoring_engine = RiskScoringEngine()
        self.start_time: float = 0.0
        self._replay_task: Optional[asyncio.Task] = None

    async def send_event(self, event_model):
        """Send a Pydantic event as a JSON text frame to the client."""
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
            self.audio_buffer.clear()
            self.transcript_window.clear()
            self.all_detected_tactics.clear()
            self.scoring_engine.reset()
            self.start_time = time.time()
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

            # If scenario is selected, launch background replay runner
            if self.scenario_id:
                self._replay_task = asyncio.create_task(self.run_scenario_replay(self.scenario_id))

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

    async def process_transcript_text(self, text: str, is_final: bool = True):
        """Evaluate a snippet of transcript text through rules, LLM, and scoring."""
        if not text or not text.strip():
            return

        # 1. Emit live transcript event
        await self.send_event(
            TranscriptEvent(text=text, is_final=is_final, speaker="caller")
        )

        # 2. Track transcript sliding window (last 5 sentences)
        self.transcript_window.append(text)
        if len(self.transcript_window) > 5:
            self.transcript_window.pop(0)

        # 3. Fast Rules Engine (0ms instantaneous hard flags)
        rules_result = rules_engine.evaluate(text)
        new_tactics = []
        for t in rules_result.all_tactics:
            if not any(x.name == t.name and x.evidence == t.evidence for x in self.all_detected_tactics):
                self.all_detected_tactics.append(t)
                new_tactics.append(t)

        if new_tactics:
            await self.send_event(TacticsEvent(items=list(self.all_detected_tactics)))

        # 4. LLM Judge on context window
        llm_result = await llm_judge.evaluate_context(self.transcript_window)
        for t in llm_result.tactics:
            if not any(x.name == t.name and x.evidence == t.evidence for x in self.all_detected_tactics):
                self.all_detected_tactics.append(t)
                new_tactics.append(t)

        if new_tactics:
            await self.send_event(TacticsEvent(items=list(self.all_detected_tactics)))

        # 5. Risk Scoring Engine Update
        elapsed = time.time() - self.start_time if self.start_time else 0.0
        risk_event = self.scoring_engine.update(
            rules_result=rules_result,
            llm_result=llm_result,
            duration_seconds=elapsed
        )
        await self.send_event(risk_event)

        # 6. Check for Critical Alert Trigger
        if self.scoring_engine.should_trigger_alert():
            alert_event = self.scoring_engine.create_alert_event(contact_notified=False)
            logger.warning(f"🚨 CRITICAL ALERT TRIGGERED: {alert_event.advice}")
            await self.send_event(alert_event)

    async def handle_audio_chunk(self, data: bytes):
        if not self.is_active:
            return
        self.total_audio_bytes += len(data)
        self.chunk_count += 1
        self.audio_buffer.extend(data)

        # Transcribe every ~1.5s of audio (16,000Hz mono 16-bit = 32,000 bytes/sec -> 24,000 bytes = 0.75s)
        # 24,000 bytes gives fast turnaround for speakerphone speech
        if len(self.audio_buffer) >= 32000:
            audio_to_transcribe = bytes(self.audio_buffer)
            self.audio_buffer.clear()
            transcript = await stt_service.transcribe_pcm(audio_to_transcribe)
            if transcript:
                await self.process_transcript_text(transcript)

    async def run_scenario_replay(self, scenario_id: str):
        """Simulate a call using a scripted scenario for demo mode."""
        scenarios_dir = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios"
        scenario_file = scenarios_dir / f"{scenario_id}.json"
        if not scenario_file.exists():
            await self.send_event(ErrorEvent(message=f"Scenario {scenario_id} not found"))
            return

        try:
            with open(scenario_file, "r") as f:
                data = json.load(f)
            scenario = Scenario(**data)
            logger.info(f"Replaying scenario '{scenario.title}' ({len(scenario.steps)} steps)")

            for step in scenario.steps:
                if not self.is_active:
                    break
                await asyncio.sleep(step.delay_ms / 1000.0)
                if not self.is_active:
                    break
                await self.process_transcript_text(step.text, is_final=step.is_final)

        except asyncio.CancelledError:
            logger.info("Scenario replay task cancelled.")
        except Exception as e:
            logger.error(f"Error during scenario replay: {e}")
            await self.send_event(ErrorEvent(message=f"Replay error: {e}"))


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
