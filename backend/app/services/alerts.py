import logging
from typing import List, Optional
import httpx
from app.config import settings

logger = logging.getLogger("scamguard.alerts")


class TelegramAlertService:
    def __init__(
        self,
        bot_token: Optional[str] = None,
        default_chat_id: Optional[str] = None
    ):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.default_chat_id = default_chat_id or settings.TELEGRAM_DEFAULT_CHAT_ID
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=4.0)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def format_alert_message(
        self,
        contact_name: str,
        score: int,
        tactics: List[str],
        advice: str
    ) -> str:
        tactics_list = "\n".join([f"• {t}" for t in tactics]) if tactics else "• High Risk Psychological Coercion"
        return (
            f"🚨 <b>ScamGuard Emergency Alert!</b>\n\n"
            f"A high-probability phone scam has been detected on <b>{contact_name}</b>'s device.\n\n"
            f"⚠️ <b>Threat Score:</b> {score}/100 (CRITICAL)\n"
            f"🎯 <b>Detected Tactics:</b>\n{tactics_list}\n\n"
            f"💡 <b>Advice Given:</b> {advice}\n\n"
            f"🛑 <i>Full-screen warning displayed on user's phone advising them to hang up immediately.</i>"
        )

    async def send_alert(
        self,
        contact_name: Optional[str] = None,
        chat_id: Optional[str] = None,
        score: int = 85,
        tactics: Optional[List[str]] = None,
        advice: str = "Hang up and call the number on your card."
    ) -> bool:
        name = contact_name or "Family Member"
        target_chat_id = chat_id or self.default_chat_id
        tactics_list = tactics or []

        message_text = self.format_alert_message(
            contact_name=name,
            score=score,
            tactics=tactics_list,
            advice=advice
        )

        # If no bot token configured, run in mock/simulation mode
        if not self.bot_token or self.bot_token.startswith("your_"):
            logger.info(
                f"[SIMULATED TELEGRAM ALERT] Target: {name} (Chat ID: {target_chat_id or '12345'})\n"
                f"{message_text}"
            )
            return True

        if not target_chat_id:
            logger.warning("No Telegram chat ID provided; cannot dispatch Telegram alert.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": target_chat_id,
            "text": message_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            client = await self.get_client()
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"Telegram emergency alert successfully dispatched to chat {target_chat_id}")
                return True
            else:
                logger.error(
                    f"Telegram API failed with code {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error dispatching Telegram alert: {e}")
            return False


# Singleton instance
alerts_service = TelegramAlertService()
