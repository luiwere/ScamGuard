import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from app.models.schemas import TacticItem

logger = logging.getLogger("scamguard.rules")


@dataclass
class RulesResult:
    hard_flags: List[TacticItem] = field(default_factory=list)
    soft_signals: List[TacticItem] = field(default_factory=list)
    dampeners: List[str] = field(default_factory=list)
    score_delta: int = 0
    top_advice: Optional[str] = None

    @property
    def all_tactics(self) -> List[TacticItem]:
        return self.hard_flags + self.soft_signals


class RulesEngine:
    def __init__(self, patterns_path: Optional[Path] = None):
        if patterns_path is None:
            patterns_path = Path(__file__).resolve().parent.parent.parent / "data" / "patterns.json"
        self.patterns_path = patterns_path
        self.hard_flag_rules = []
        self.soft_signal_rules = []
        self.dampener_rules = []
        self.load_patterns()

    def load_patterns(self):
        try:
            with open(self.patterns_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.hard_flag_rules = [
                {
                    **rule,
                    "compiled": re.compile(rule["regex"], re.IGNORECASE)
                }
                for rule in data.get("hard_flags", [])
            ]

            self.soft_signal_rules = [
                {
                    **rule,
                    "compiled": re.compile(rule["regex"], re.IGNORECASE)
                }
                for rule in data.get("soft_signals", [])
            ]

            self.dampener_rules = [
                {
                    **rule,
                    "compiled": re.compile(rule["regex"], re.IGNORECASE)
                }
                for rule in data.get("dampeners", [])
            ]

            logger.info(
                f"Loaded rules: {len(self.hard_flag_rules)} hard flags, "
                f"{len(self.soft_signal_rules)} soft signals, "
                f"{len(self.dampener_rules)} dampeners."
            )
        except Exception as e:
            logger.error(f"Failed to load patterns from {self.patterns_path}: {e}")

    def evaluate(self, text: str) -> RulesResult:
        result = RulesResult()
        if not text or not text.strip():
            return result

        # 1. Check Hard Flags
        for rule in self.hard_flag_rules:
            match = rule["compiled"].search(text)
            if match:
                evidence = match.group(0)
                item = TacticItem(
                    name=rule["name"],
                    evidence=evidence,
                    confidence=0.98,
                    source="rules"
                )
                result.hard_flags.append(item)
                result.score_delta += rule.get("weight", 50)
                if not result.top_advice and rule.get("advice"):
                    result.top_advice = rule["advice"]

        # 2. Check Soft Signals
        for rule in self.soft_signal_rules:
            match = rule["compiled"].search(text)
            if match:
                evidence = match.group(0)
                item = TacticItem(
                    name=rule["name"],
                    evidence=evidence,
                    confidence=0.85,
                    source="rules"
                )
                result.soft_signals.append(item)
                result.score_delta += rule.get("weight", 15)

        # 3. Check Dampeners (Benign disclaimers that reduce false alarms)
        for rule in self.dampener_rules:
            match = rule["compiled"].search(text)
            if match:
                result.dampeners.append(rule["name"])
                result.score_delta += rule.get("weight", -40)

        return result


# Singleton instance
rules_engine = RulesEngine()
