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

    # Process all steps in the scenario
    for step in scenario.steps:
        await session.process_transcript_text(step.text, is_final=step.is_final)

    event_types = [e.get("type") for e in captured_events]
    assert "transcript" in event_types
    assert "tactics" in event_types
    assert "risk" in event_types
    assert "alert" in event_types, "Alert event must have been emitted for scam scenario"

    # Verify score escalation
    risk_scores = [e.get("score") for e in captured_events if e.get("type") == "risk"]
    assert len(risk_scores) > 0
    assert max(risk_scores) >= 70, f"Expected final risk score >= 70, got {max(risk_scores)}"

    # Verify alert contents
    alert_event = next(e for e in captured_events if e.get("type") == "alert")
    assert "Hang up" in alert_event.get("action")


@pytest.mark.asyncio
async def test_legit_bank_replay_pipeline_direct():
    """Verify that a legitimate bank verification call does not trigger false alerts."""
    mock_ws = AsyncMock()
    session = CallSession(mock_ws)
    session.is_active = True
    session.scoring_engine.reset()

    # Load legit_bank_verification scenario
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
