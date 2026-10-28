from app.services.scoring import RiskScoringEngine
from app.services.rules import RulesResult
from app.services.llm import LLMJudgeResult
from app.models.schemas import TacticItem


def test_scoring_initial_state():
    engine = RiskScoringEngine()
    assert engine.score == 0
    assert engine.get_risk_level(0) == "safe"
    assert engine.should_trigger_alert() is False


def test_scoring_hard_flag_triggers_alert():
    engine = RiskScoringEngine()

    otp_item = TacticItem(
        name="One-Time Passcode Request",
        evidence="give me the code",
        confidence=0.98,
        source="rules"
    )
    rules_res = RulesResult(
        hard_flags=[otp_item],
        score_delta=55,
        top_advice="Banks never ask for your code."
    )

    # First signal: score is 55 (medium/high)
    event1 = engine.update(rules_result=rules_res)
    assert event1.score == 55
    assert event1.level == "medium"
    assert engine.hard_flags_count == 1

    # Add second tactic (urgency via LLM)
    urgency_item = TacticItem(
        name="Artificial Urgency & Threat",
        evidence="act right now",
        confidence=0.85,
        source="llm"
    )
    llm_res = LLMJudgeResult(
        tactics=[urgency_item],
        risk_increment=20
    )

    event2 = engine.update(rules_result=RulesResult(), llm_result=llm_res)
    # Score 55 + 20 + 10 (velocity bonus for >=2 tactics) = 85
    assert event2.score >= 70
    assert event2.level in ["high", "critical"]

    # Now alert should trigger
    assert engine.should_trigger_alert() is True
    alert_event = engine.create_alert_event()
    assert alert_event.type == "alert"
    assert "Hang up" in alert_event.action


def test_scoring_dampener_suppression():
    engine = RiskScoringEngine()

    # Mild suspicion (+15)
    rules_res = RulesResult(
        soft_signals=[
            TacticItem(name="Authority Claim", evidence="fraud department", confidence=0.8, source="rules")
        ],
        score_delta=15
    )
    engine.update(rules_result=rules_res)
    assert engine.score == 15

    # Benign dampener (-40)
    dampener_res = RulesResult(
        dampeners=["Legitimate Bank Disclaimer"],
        score_delta=-40
    )
    event = engine.update(rules_result=dampener_res)
    assert event.score == 0
    assert event.level == "safe"
    assert engine.should_trigger_alert() is False
