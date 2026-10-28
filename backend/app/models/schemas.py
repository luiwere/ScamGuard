from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


# --- Client -> Server Frames ---

class TrustedContact(BaseModel):
    name: Optional[str] = "Trusted Contact"
    telegram_chat_id: Optional[str] = None
    phone: Optional[str] = None


class StartCallMessage(BaseModel):
    type: Literal["start"] = "start"
    contact: Optional[TrustedContact] = Field(default_factory=TrustedContact)
    scenario: Optional[str] = None  # None for live mic, or scenario id (e.g. "scam_bank_fraud")


class StopCallMessage(BaseModel):
    type: Literal["stop"] = "stop"


# --- Server -> Client Events ---

class TranscriptEvent(BaseModel):
    type: Literal["transcript"] = "transcript"
    text: str
    is_final: bool = False
    timestamp: Optional[float] = None
    speaker: Optional[str] = "caller"


class TacticItem(BaseModel):
    name: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: Literal["rules", "llm"]


class TacticsEvent(BaseModel):
    type: Literal["tactics"] = "tactics"
    items: List[TacticItem] = Field(default_factory=list)


RiskLevel = Literal["safe", "low", "medium", "high", "critical"]


class RiskBreakdown(BaseModel):
    hard_flags: int = 0
    llm_tactics: int = 0
    call_duration_seconds: float = 0.0
    detected_tactics: List[str] = Field(default_factory=list)


class RiskEvent(BaseModel):
    type: Literal["risk"] = "risk"
    score: int = Field(ge=0, le=100)
    level: RiskLevel
    breakdown: Optional[RiskBreakdown] = None


class AlertEvent(BaseModel):
    type: Literal["alert"] = "alert"
    advice: str
    action: str
    contact_notified: bool = False
    severity: Literal["warning", "critical"] = "critical"


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str
    recoverable: bool = True


# --- Scenario Definition Models (for demo mode) ---

class ScenarioStep(BaseModel):
    delay_ms: int
    text: str
    is_final: bool = True
    expected_risk: Optional[int] = None
    expected_tactics: List[str] = Field(default_factory=list)


class Scenario(BaseModel):
    id: str
    title: str
    description: str
    category: Literal["scam", "legitimate"]
    steps: List[ScenarioStep]
