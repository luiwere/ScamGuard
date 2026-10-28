import io
import wave
import logging
from typing import Optional
import httpx
from app.config import settings

logger = logging.getLogger("scamguard.stt")

FIREWORKS_AUDIO_URL = "https://api.fireworks.ai/inference/v1/audio/transcriptions"


def pcm16_to_wav(pcm_data: bytes, sample_rate: int = 16000) -> bytes:
    """Pack raw PCM16 mono bytes into a valid in-memory WAV container."""
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(1)      # Mono
        wf.setsampwidth(2)      # 16-bit PCM = 2 bytes/sample
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    return wav_io.getvalue()


class SpeechToTextService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.FIREWORKS_API_KEY
        self.model = model or settings.FIREWORKS_STT_MODEL
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def transcribe_pcm(self, pcm_data: bytes, sample_rate: int = 16000) -> Optional[str]:
        """Convert PCM16 bytes to WAV and transcribe via Fireworks Whisper API."""
        if not pcm_data:
            return None

        # Minimum audio length to avoid Whisper transcribing pure silence/noise: ~0.5s = 16,000 bytes
        if len(pcm_data) < 8000:
            return None

        if not self.api_key or self.api_key.startswith("your_"):
            logger.debug("No Fireworks API key configured; skipping external STT.")
            return None

        wav_bytes = pcm16_to_wav(pcm_data, sample_rate=sample_rate)
        client = await self.get_client()

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        files = {
            "file": ("audio.wav", wav_bytes, "audio/wav")
        }
        data = {
            "model": self.model,
            "response_format": "json"
        }

        try:
            response = await client.post(
                FIREWORKS_AUDIO_URL,
                headers=headers,
                files=files,
                data=data
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "").strip()
                if text:
                    logger.info(f"Transcribed audio: \"{text}\"")
                    return text
                return None
            else:
                logger.warning(
                    f"Fireworks STT returned status {response.status_code}: {response.text}"
                )
                return None
        except Exception as e:
            logger.error(f"Fireworks STT request failed: {e}")
            return None


# Singleton instance
stt_service = SpeechToTextService()
