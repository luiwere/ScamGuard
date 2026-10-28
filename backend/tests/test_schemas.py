import json
import re
from pathlib import Path
import pytest
from app.models.schemas import (
    StartCallMessage,
    StopCallMessage,
    TranscriptEvent,
    TacticItem,
    TacticsEvent,
    RiskEvent,
    AlertEvent,
    Scenario,
)


def test_start_message_validation():
    msg = StartCallMessage(
        type="start",
        contact={"name": "Alice", "telegram_chat_id": "12345"},
        scenario="scam_bank_fraud"
    )
    assert msg.type == "start"
    assert msg.contact.name == "Alice"
    assert msg.contact.telegram_chat_id == "12345"
    assert msg.scenario == "scam_bank_fraud"


def test_events_serialization():
    t_event = TranscriptEvent(text="Hello world", is_final=True)
    assert t_event.type == "transcript"

    tactic = TacticItem(name="OTP Request", evidence="passcode", confidence=0.95, source="rules")
    tactics_event = TacticsEvent(items=[tactic])
    assert len(tactics_event.items) == 1

    risk_event = RiskEvent(score=75, level="high")
    assert risk_event.score == 75
    assert risk_event.level == "high"

    alert = AlertEvent(advice="Hang up", action="Call your bank", contact_notified=True)
    assert alert.contact_notified is True


def test_patterns_regex_validity():
    patterns_file = Path(__file__).resolve().parent.parent / "data" / "patterns.json"
    assert patterns_file.exists(), "patterns.json must exist"

    with open(patterns_file, "r") as f:
        data = json.load(f)

    for flag in data.get("hard_flags", []):
        pattern = flag["regex"]
        compiled = re.compile(pattern, re.IGNORECASE)
        assert compiled is not None

    for signal in data.get("soft_signals", []):
        pattern = signal["regex"]
        compiled = re.compile(pattern, re.IGNORECASE)
        assert compiled is not None

    for dampener in data.get("dampeners", []):
        pattern = dampener["regex"]
        compiled = re.compile(pattern, re.IGNORECASE)
        assert compiled is not None


def test_scenarios_validity():
    scenarios_dir = Path(__file__).resolve().parent.parent / "data" / "scenarios"
    assert scenarios_dir.exists()

    files = list(scenarios_dir.glob("*.json"))
    assert len(files) >= 2, "Must have at least 2 demo scenarios"

    for f in files:
        with open(f, "r") as fp:
            data = json.load(fp)
            scenario = Scenario(**data)
            assert len(scenario.steps) > 0
