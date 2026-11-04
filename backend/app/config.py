from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Any
import json


class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
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

    # Fireworks AI
    FIREWORKS_API_KEY: str = ""
    FIREWORKS_STT_MODEL: str = "whisper-v3-turbo"
    FIREWORKS_LLM_MODEL: str = "accounts/fireworks/models/llama-v3p3-70b-instruct"

    # Telegram Alerting
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_DEFAULT_CHAT_ID: str = ""

    # Risk Scoring Thresholds
    RISK_THRESHOLD_ALERT: int = 70
    RISK_THRESHOLD_WARNING: int = 40

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")



settings = Settings()
