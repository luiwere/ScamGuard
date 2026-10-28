import pytest
from app.services.llm import LLMJudgeService, LLMJudgeResult


@pytest.mark.asyncio
async def test_llm_fallback_without_key():
    service = LLMJudgeService(api_key="")
    context = ["Hello, this is officer Miller.", "We need your security passcode."]
    result = await service.evaluate_context(context)

    assert isinstance(result, LLMJudgeResult)
    assert len(result.tactics) == 0
    assert result.risk_increment == 0


@pytest.mark.asyncio
async def test_llm_empty_context():
    service = LLMJudgeService(api_key="fake-key")
    result = await service.evaluate_context([])
    assert len(result.tactics) == 0
