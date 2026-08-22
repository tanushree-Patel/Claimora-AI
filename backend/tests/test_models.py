import uuid

import pytest
from sqlalchemy import select

from app.db.models import IndianHealthClaim, IndianMedicalCode
from app.db.session import AsyncSessionLocal


@pytest.mark.asyncio
async def test_create_and_read_medical_code():
    async with AsyncSessionLocal() as session:
        code = IndianMedicalCode(
            code_system="ICD-10", code=f"TEST-{uuid.uuid4().hex[:6]}", display_name="Test condition"
        )
        session.add(code)
        await session.commit()

        result = await session.execute(
            select(IndianMedicalCode).where(IndianMedicalCode.code == code.code)
        )
        fetched = result.scalar_one()
        assert fetched.display_name == "Test condition"

        # Cleanup test row
        await session.delete(fetched)
        await session.commit()


@pytest.mark.asyncio
async def test_create_health_claim_defaults_to_draft_status():
    async with AsyncSessionLocal() as session:
        claim = IndianHealthClaim(session_id=f"session-{uuid.uuid4().hex[:8]}")
        session.add(claim)
        await session.commit()
        assert claim.status == "DRAFT"

        # Cleanup test row
        await session.delete(claim)
        await session.commit()