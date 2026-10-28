import pytest
from app.services.alerts import TelegramAlertService


@pytest.mark.asyncio
async def test_telegram_alert_simulation_when_unconfigured():
    # Service with no token should cleanly simulate without crashing
    service = TelegramAlertService(bot_token="", default_chat_id="")
    result = await service.send_alert(
        contact_name="Sarah (Daughter)",
        chat_id="123456789",
        score=90,
        tactics=["One-Time Passcode Request", "Artificial Urgency"],
        advice="Banks never ask for your code."
    )
    assert result is True


def test_telegram_message_formatting():
    service = TelegramAlertService()
    msg = service.format_alert_message(
        contact_name="Grandma Rose",
        score=95,
        tactics=["AnyDesk Installation", "Target Gift Card Demand"],
        advice="Do not install software or purchase gift cards."
    )

    assert "Grandma Rose" in msg
    assert "95/100" in msg
    assert "AnyDesk Installation" in msg
    assert "Target Gift Card Demand" in msg
    assert "Do not install software" in msg
