import logging
from typing import List, Optional, Set
from app.config import settings
from app.models.schemas import RiskEvent, RiskLevel, RiskBreakdown, AlertEvent
from app.services.rules import RulesResult
from app.services.llm import LLMJudgeResult

logger = logging.getLogger("scamguard.scoring")


class RiskScoringEngine:
    def __init__(
        self,
        alert_threshold: Optional[int] = None,
        warning_threshold: Optional[int] = None
    ):
        self.alert_threshold = alert_threshold or settings.RISK_THRESHOLD_ALERT
        self.warning_threshold = warning_threshold or settings.RISK_THRESHOLD_WARNING
        self.score: int = 0
        self.hard_flags_count: int = 0
        self.llm_tactics_count: int = 0
        self.dampeners_count: int = 0
        self.detected_tactics: Set[str] = set()
        self.alert_triggered: bool = False
        self.last_advice: str = "Hang up immediately and call the number on the back of your official card."

    def reset(self):
        self.score = 0
        self.hard_flags_count = 0
        self.llm_tactics_count = 0
        self.dampeners_count = 0
        self.detected_tactics.clear()
        self.alert_triggered = False

    def get_risk_level(self, score: int) -> RiskLevel:
        if score >= 85:
            return "critical"
        elif score >= self.alert_threshold:  # 70
            return "high"
        elif score >= self.warning_threshold:  # 40
            return "medium"
        elif score >= 20:
            return "low"
        return "safe"

    def update(
        self,
        rules_result: RulesResult,
        llm_result: Optional[LLMJudgeResult] = None,
        duration_seconds: float = 0.0
    ) -> RiskEvent:
        # 1. Tally new tactics
        for hf in rules_result.hard_flags:
            self.hard_flags_count += 1
            self.detected_tactics.add(hf.name)
            if rules_result.top_advice:
                self.last_advice = rules_result.top_advice

        for ss in rules_result.soft_signals:
            self.detected_tactics.add(ss.name)

        if llm_result:
            for lt in llm_result.tactics:
                self.llm_tactics_count += 1
                self.detected_tactics.add(lt.name)
            if llm_result.advice:
                self.last_advice = llm_result.advice

        self.dampeners_count += len(rules_result.dampeners)

        # 2. Score progression
        delta = rules_result.score_delta
        if llm_result:
            delta += llm_result.risk_increment

        # Multi-tactic velocity: Having multiple distinct tactics indicates coordinated social engineering
        if len(self.detected_tactics) >= 2 and (rules_result.hard_flags or (llm_result and llm_result.tactics)):
            delta += 10

        new_score = self.score + delta
        # If dampeners fire without hard flags, pull score down aggressively
        if rules_result.dampeners and not rules_result.hard_flags:
            new_score = max(0, new_score - 30)

        # Clamp between 0 and 100
        self.score = max(0, min(100, new_score))
        level = self.get_risk_level(self.score)

        breakdown = RiskBreakdown(
            hard_flags=self.hard_flags_count,
            llm_tactics=self.llm_tactics_count,
            call_duration_seconds=duration_seconds,
            detected_tactics=list(self.detected_tactics)
        )

        return RiskEvent(
            type="risk",
            score=self.score,
            level=level,
            breakdown=breakdown
        )

    def should_trigger_alert(self) -> bool:
        """Determines if the critical full-screen intervention should fire."""
        if self.alert_triggered:
            return False

        # Condition A: Score crossed alert threshold (70+)
        if self.score >= self.alert_threshold:
            self.alert_triggered = True
            return True

        # Condition B: Any 1 Hard Flag (e.g. OTP code theft) + at least 1 other tactic
        if self.hard_flags_count >= 1 and len(self.detected_tactics) >= 2:
            self.score = max(self.score, self.alert_threshold)
            self.alert_triggered = True
            return True

        return False

    def create_alert_event(self, contact_notified: bool = False) -> AlertEvent:
        return AlertEvent(
            type="alert",
            advice=self.last_advice,
            action="Hang up now and call the official customer service number on your card or bill.",
            contact_notified=contact_notified,
            severity="critical"
        )
