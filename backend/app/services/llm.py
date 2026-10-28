import json
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import httpx
from app.config import settings
from app.models.schemas import TacticItem

logger = logging.getLogger("scamguard.llm")

FIREWORKS_CHAT_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

SYSTEM_PROMPT = """You are the ScamGuard Real-Time Intent Judge.
Your job is to analyze live transcripts of incoming phone calls to protect vulnerable people from scams, fraud, and social engineering in real time.

Analyze the given conversation window and identify any malicious or manipulative tactics used by the caller, including:
- "Artificial Urgency & Threat" (e.g., must act right now, arrest warrant, account suspended immediately)
- "Authority Claim & Impersonation" (e.g., claiming to be FBI, IRS, fraud prevention officer, tech support)
- "Secrecy & Isolation" (e.g., don't tell the teller, stay on the line, keep this confidential)
- "Credential Harvesting" (e.g., asking for 2FA/OTP codes, PINs, passwords, SSN)
- "Coerced Financial Transfer" (e.g., wire to a safe locker, gift card purchase, Bitcoin ATM deposit)
- "Remote Access Demand" (e.g., asking to install AnyDesk, TeamViewer)

If the call appears to be benign or normal customer service, return an empty tactics array and 0 risk_increment.

Respond ONLY with a valid JSON object with the following schema:
{
  "caller_intent": "string summarizing intent",
  "tactics": [
    {
      "name": "Tactic Name",
      "evidence": "exact short quoted phrase from transcript",
      "confidence": 0.85
    }
  ],
  "risk_increment": 25,
  "advice": "short, direct advice for the user"
}
"""


@dataclass
class LLMJudgeResult:
    caller_intent: str = ""
    tactics: List[TacticItem] = field(default_factory=list)
    risk_increment: int = 0
    advice: Optional[str] = None


class LLMJudgeService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.FIREWORKS_API_KEY
        self.model = model or settings.FIREWORKS_LLM_MODEL
        # Short timeout for real-time responsiveness (1.5s circuit breaker)
        self.timeout = 1.5
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def evaluate_context(self, transcript_window: List[str]) -> LLMJudgeResult:
        result = LLMJudgeResult()
        if not transcript_window:
            return result

        full_context = "\n".join(transcript_window)
        if not full_context.strip():
            return result

        if not self.api_key or self.api_key.startswith("your_"):
            logger.debug("No Fireworks API key configured; skipping LLM judge.")
            return result

        client = await self.get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Recent call transcript window:\n---\n{full_context}\n---"
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 400
        }

        try:
            response = await client.post(
                FIREWORKS_CHAT_URL,
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                result.caller_intent = parsed.get("caller_intent", "")
                result.risk_increment = int(parsed.get("risk_increment", 0))
                result.advice = parsed.get("advice")

                for t in parsed.get("tactics", []):
                    item = TacticItem(
                        name=t.get("name", "Suspicious Activity"),
                        evidence=t.get("evidence", ""),
                        confidence=float(t.get("confidence", 0.8)),
                        source="llm"
                    )
                    result.tactics.append(item)

                logger.info(
                    f"LLM Judge detected {len(result.tactics)} tactics (Risk +{result.risk_increment})"
                )
            else:
                logger.warning(
                    f"Fireworks LLM returned status {response.status_code}: {response.text}"
                )
        except httpx.TimeoutException:
            logger.warning(f"Fireworks LLM timed out after {self.timeout}s (circuit breaker tripped).")
        except Exception as e:
            logger.error(f"Fireworks LLM evaluation error: {e}")

        return result


# Singleton instance
llm_judge = LLMJudgeService()
