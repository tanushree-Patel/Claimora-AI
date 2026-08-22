
# backend/tests/test_seed.py
import pytest
from sqlalchemy import select

from app.db.models import IndianMedicalCode
from app.db.session import AsyncSessionLocal
from scripts.seed_codes import seed


@pytest.mark.asyncio
async def test_seed_is_idempotent():
    await seed()
    await seed()  # running twice should not raise or duplicate

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(IndianMedicalCode.code))
        codes = [row[0] for row in result.all()]
        assert len(codes) == len(set(codes))  # no duplicates