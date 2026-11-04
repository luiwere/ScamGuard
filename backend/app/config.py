from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Any, Union
import json


class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                try:
                    return json.loads(v_trimmed)
                except Exception:
                    pass
            if "," in v_trimmed:
                return [i.strip() for i in v_trimmed.split(",") if i.strip()]
            if v_trimmed == "*":
                return ["*"]
            return [v_trimmed]
        elif isinstance(v, list):
            return v
        return ["*"]

    # AI Inference (Auto-detects Groq or Fireworks)
    FIREWORKS_API_KEY: str = ""
    FIREWORKS_STT_MODEL: str = "whisper-v3-turbo"
    FIREWORKS_LLM_MODEL: str = "accounts/fireworks/models/llama-v3p3-70b-instruct"

    GROQ_API_KEY: str = ""
    GROQ_STT_MODEL: str = "whisper-large-v3-turbo"
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"

    AI_API_KEY: str = ""

    # Telegram Alerting
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_DEFAULT_CHAT_ID: str = ""

    # Risk Scoring Thresholds
    RISK_THRESHOLD_ALERT: int = 70
    RISK_THRESHOLD_WARNING: int = 40

    @property
    def active_api_key(self) -> str:
        return self.GROQ_API_KEY or self.FIREWORKS_API_KEY or self.AI_API_KEY

    @property
    def is_groq(self) -> bool:
        if self.GROQ_API_KEY:
            return True
        key = self.active_api_key
        return bool(key and key.startswith("gsk_"))

    @property
    def chat_url(self) -> str:
        if self.is_groq:
            return "https://api.groq.com/openai/v1/chat/completions"
        return "https://api.fireworks.ai/inference/v1/chat/completions"

    @property
    def audio_url(self) -> str:
        if self.is_groq:
            return "https://api.groq.com/openai/v1/audio/transcriptions"
        return "https://api.fireworks.ai/inference/v1/audio/transcriptions"

    @property
    def active_llm_model(self) -> str:
        if self.is_groq:
            if "fireworks" in self.FIREWORKS_LLM_MODEL.lower() or not self.GROQ_LLM_MODEL:
                return "llama-3.3-70b-versatile"
            return self.GROQ_LLM_MODEL
        return self.FIREWORKS_LLM_MODEL

    @property
    def active_stt_model(self) -> str:
        if self.is_groq:
            if "fireworks" in self.FIREWORKS_STT_MODEL.lower() or not self.GROQ_STT_MODEL:
                return "whisper-large-v3-turbo"
            return self.GROQ_STT_MODEL
        return self.FIREWORKS_STT_MODEL

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")



settings = Settings()
