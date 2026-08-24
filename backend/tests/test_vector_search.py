import pytest
from sqlalchemy import select, update

from app.db.models import IndianMedicalCode
from app.db.session import AsyncSessionLocal
from app.repositories.codes_repository import CodesRepository


@pytest.mark.asyncio
async def test_vector_search_returns_closest_first():
    async with AsyncSessionLocal() as session:
        # Give two existing seeded codes distinguishable embeddings for this test
        result = await session.execute(select(IndianMedicalCode).limit(2))
        codes = result.scalars().all()
        assert len(codes) >= 2, "Seed data + backfill must run before this test"

        repo = CodesRepository(session)
        query_embedding = codes[0].embedding  
        matches = await repo.vector_search(query_embedding, limit=2)

        assert matches[0][0].id == codes[0].id
        assert matches[0][1] > 0.99  