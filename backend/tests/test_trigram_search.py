import pytest

from app.db.session import AsyncSessionLocal
from app.repositories.codes_repository import CodesRepository


@pytest.mark.asyncio
async def test_trigram_search_finds_close_text_match():
    async with AsyncSessionLocal() as session:
        repo = CodesRepository(session)
        matches = await repo.trigram_search("essential hypertansion", limit=3)  # deliberate typo
        assert any(m[0].code == "I10" for m in matches)