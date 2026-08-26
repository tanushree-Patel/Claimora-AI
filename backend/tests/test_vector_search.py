import pytest
from sqlalchemy import select, update

from app.db.models import IndianMedicalCode
from app.db.session import AsyncSessionLocal
from app.repositories.codes_repository import CodesRepository


@pytest.mark.asyncio
async def test_vector_search_returns_closest_first():
    async with AsyncSessionLocal() as session:
        # Ensure we have at least two codes seeded
        result = await session.execute(select(IndianMedicalCode).limit(2))
        codes = result.scalars().all()
        assert len(codes) >= 2, "Seed data must run before this test"

        # Give them distinguishable embeddings for this test
        codes[0].embedding = [1.0] + [0.0] * 767
        codes[1].embedding = [0.0] + [1.0] * 767
        await session.commit()

        try:
            repo = CodesRepository(session)
            query_embedding = [1.0] + [0.0] * 767
            matches = await repo.vector_search(query_embedding, limit=2)

            assert len(matches) >= 2
            assert matches[0][0].id == codes[0].id
            assert matches[0][1] > 0.99
        finally:
            # Clean up/reset their embeddings to None so we don't pollute subsequent runs
            codes[0].embedding = None
            codes[1].embedding = None
            await session.commit()