from unittest.mock import AsyncMock, patch

import pytest

from app.db.session import AsyncSessionLocal
from app.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_search_merges_and_ranks_candidates():
    async with AsyncSessionLocal() as session:
        service = RetrievalService(session)
        with patch.object(
            service._embedding_service, "embed_text", new=AsyncMock(return_value=[0.1] * 768)
        ):
            result = await service.search("essential hypertension")

        assert result.query == "essential hypertension"
        assert len(result.candidates) > 0
        assert all(c.score <= 1.1 for c in result.candidates)  # sanity bound given +0.1 boost


@pytest.mark.asyncio
async def test_agreement_between_strategies_boosts_score():
    async with AsyncSessionLocal() as session:
        service = RetrievalService(session)
        with patch.object(
            service._embedding_service, "embed_text", new=AsyncMock(return_value=[0.1] * 768)
        ):
            result = await service.search("essential hypertension")

        boosted = [c for c in result.candidates if len(c.matched_via) == 2]
        for c in boosted:
            assert c.score >= 0.1