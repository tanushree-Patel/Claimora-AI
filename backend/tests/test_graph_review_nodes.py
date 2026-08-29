from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes_review import finalize, retrieve_codes
from app.schemas.retrieval import CodeCandidate, RetrievalResult


@pytest.mark.asyncio
async def test_retrieve_codes_populates_candidates():
    fake_result = RetrievalResult(
        query="essential hypertension",
        candidates=[CodeCandidate(code_system="ICD-10", code="I10", display_name="Essential hypertension", score=0.95, matched_via=["vector"])],
    )
    state = {"extracted_data": {"clinical": {"diagnosis_text": "essential hypertension"}}}
    with patch("app.graph.nodes_review.RetrievalService.search", new=AsyncMock(return_value=fake_result)):
        result = await retrieve_codes(state)
    assert result["status"] == "PENDING_REVIEW"
    assert result["candidates"][0]["code"] == "I10"


@pytest.mark.asyncio
async def test_finalize_sets_approved_status():
    result = await finalize({"review_decision": {"approved_codes": ["I10"]}})
    assert result["status"] == "APPROVED"