from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

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
