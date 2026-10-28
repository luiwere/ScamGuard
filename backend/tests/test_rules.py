from app.services.rules import rules_engine


def test_rules_detect_otp_request():
    text = "Please read back the 6-digit one-time passcode sent to your phone."
    result = rules_engine.evaluate(text)

    assert len(result.hard_flags) >= 1
    flag = result.hard_flags[0]
    assert "Passcode" in flag.name or "OTP" in flag.name
    assert result.score_delta >= 50
    assert result.top_advice is not None


def test_rules_detect_remote_access():
    text = "We need you to install AnyDesk so we can connect to your computer and clean the virus."
    result = rules_engine.evaluate(text)

    assert any("Remote Access" in hf.name for hf in result.hard_flags)
    assert result.score_delta >= 40


def test_rules_detect_gift_card():
    text = "To pay the fine, go to Target and buy a $500 gift card right now."
    result = rules_engine.evaluate(text)

    assert any("Payment" in hf.name for hf in result.hard_flags)


def test_rules_detect_urgency():
    text = "Do not hang up! There is an arrest warrant out for you."
    result = rules_engine.evaluate(text)

    assert any("Urgency" in ss.name for ss in result.soft_signals)


def test_rules_detect_dampener():
    text = "Bank representatives will never ask you for your PIN or passcode over the phone."
    result = rules_engine.evaluate(text)

    assert len(result.dampeners) >= 1
    assert result.score_delta < 0


def test_rules_benign_text():
    text = "Hello, I am calling to inquire about your store hours tomorrow."
    result = rules_engine.evaluate(text)

    assert len(result.hard_flags) == 0
    assert len(result.soft_signals) == 0
    assert result.score_delta == 0
