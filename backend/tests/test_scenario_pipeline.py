import json
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from app.ws.call_stream import CallSession
from app.models.schemas import Scenario


@pytest.mark.asyncio
async def test_scam_replay_pipeline_direct():
    """Verify that processing the scam bank fraud scenario triggers escalating risk and alert."""
    mock_ws = AsyncMock()
    session = CallSession(mock_ws)
    session.is_active = True
    session.scoring_engine.reset()

    # Load scam_bank_fraud scenario
    scenario_file = Path(__file__).resolve().parent.parent / "data" / "scenarios" / "scam_bank_fraud.json"
    with open(scenario_file, "r") as f:
        data = json.load(f)
    scenario = Scenario(**data)

    captured_events = []
    async def capture_event(payload_str):
        captured_events.append(json.loads(payload_str))

    mock_ws.send_text.side_effect = capture_event

    for step in scenario.steps:
        await session.process_transcript_text(step.text, is_final=step.is_final)

    event_types = [e.get("type") for e in captured_events]
    assert "transcript" in event_types
    assert "tactics" in event_types
    assert "risk" in event_types
    assert "alert" in event_types, "Alert event must have been emitted for scam scenario"

    risk_scores = [e.get("score") for e in captured_events if e.get("type") == "risk"]
    assert len(risk_scores) > 0
    assert max(risk_scores) >= 70, f"Expected final risk score >= 70, got {max(risk_scores)}"

    alert_event = next(e for e in captured_events if e.get("type") == "alert")
    assert "Hang up" in alert_event.get("action")


@pytest.mark.asyncio
async def test_tech_support_gift_card_pipeline_direct():
    """Verify that AnyDesk and Gift Card scam triggers critical alert."""
    mock_ws = AsyncMock()
    session = CallSession(mock_ws)
    session.is_active = True
    session.scoring_engine.reset()

    scenario_file = Path(__file__).resolve().parent.parent / "data" / "scenarios" / "scam_gift_card.json"
    with open(scenario_file, "r") as f:
        data = json.load(f)
    scenario = Scenario(**data)

    captured_events = []
    async def capture_event(payload_str):
        captured_events.append(json.loads(payload_str))

    mock_ws.send_text.side_effect = capture_event

    for step in scenario.steps:
        await session.process_transcript_text(step.text, is_final=step.is_final)

    event_types = [e.get("type") for e in captured_events]
    assert "alert" in event_types, "Alert event must have been emitted for tech support scam"

    # Verify detected tactics include remote access or payment
    tactics_events = [e for e in captured_events if e.get("type") == "tactics"]
    all_tactic_names = [item["name"] for te in tactics_events for item in te.get("items", [])]
    assert any("Remote Access" in name or "Payment" in name for name in all_tactic_names)


@pytest.mark.asyncio
async def test_legit_bank_replay_pipeline_direct():
    """Verify that a legitimate bank verification call does not trigger false alerts."""
    mock_ws = AsyncMock()
    session = CallSession(mock_ws)
    session.is_active = True
    session.scoring_engine.reset()

    scenario_file = Path(__file__).resolve().parent.parent / "data" / "scenarios" / "legit_bank_verification.json"
    with open(scenario_file, "r") as f:
        data = json.load(f)
    scenario = Scenario(**data)

    captured_events = []
    async def capture_event(payload_str):
        captured_events.append(json.loads(payload_str))

    mock_ws.send_text.side_effect = capture_event

    for step in scenario.steps:
        await session.process_transcript_text(step.text, is_final=step.is_final)

    event_types = [e.get("type") for e in captured_events]
    assert "alert" not in event_types, "Legitimate bank call must never trigger an alert"

    risk_scores = [e.get("score") for e in captured_events if e.get("type") == "risk"]
    assert max(risk_scores) < 40, f"Expected risk score to stay low (<40), got {max(risk_scores)}"
