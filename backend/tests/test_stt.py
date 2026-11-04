import io
import wave
import pytest
from app.services.stt import pcm16_to_wav, SpeechToTextService


def test_pcm16_to_wav_header_format():
    # 1000 samples of 16-bit mono PCM (zeros)
    pcm_data = b"\x00\x00" * 1000
    wav_bytes = pcm16_to_wav(pcm_data, sample_rate=16000)

    assert wav_bytes.startswith(b"RIFF")
    assert b"WAVE" in wav_bytes

    # Parse with Python wave module to verify standard compliance
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 16000
        assert wf.getnframes() == 1000


@pytest.mark.asyncio
async def test_stt_graceful_fallback_without_key():
    service = SpeechToTextService(api_key="")
    pcm_data = b"\x00\x00" * 8000
    result = await service.transcribe_pcm(pcm_data)
    assert result is None  # Should cleanly return None without crashing


def test_stt_groq_auto_detection():
    service = SpeechToTextService(api_key="gsk_test123456789")
    assert service.audio_url == "https://api.groq.com/openai/v1/audio/transcriptions"
    assert service.model == "whisper-large-v3-turbo"


def test_stt_fireworks_auto_detection():
    service = SpeechToTextService(api_key="fw_test123456789")
    assert service.audio_url == "https://api.fireworks.ai/inference/v1/audio/transcriptions"
    assert "whisper-v3-turbo" in service.model
