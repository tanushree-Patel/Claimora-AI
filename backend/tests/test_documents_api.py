from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.extraction import ClinicalInfo, ExtractedClaimData, HospitalInfo, PatientInfo

FAKE_EXTRACTION = ExtractedClaimData(
    patient=PatientInfo(full_name="Test Patient"),
    hospital=HospitalInfo(hospital_name="Test Hospital"),
    clinical=ClinicalInfo(diagnosis_text="type 2 diabetes mellitus"),
    extraction_confidence=0.9,
)


@pytest.mark.asyncio
async def test_upload_document_returns_extracted_data():
    with patch(
        "app.api.v1.documents.ExtractionService.extract",
        new=AsyncMock(return_value=FAKE_EXTRACTION),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/documents/upload",
                json={"raw_text": "Patient presented with elevated blood glucose over three months."},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "EXTRACTED"
    assert body["extracted_data"]["patient"]["full_name"] == "Test Patient"


@pytest.mark.asyncio
async def test_upload_document_extraction_failure():
    from app.services.exceptions import ExtractionError
    from app.db.session import AsyncSessionLocal
    from app.repositories.claims_repository import ClaimsRepository

    with patch(
        "app.api.v1.documents.ExtractionService.extract",
        new=AsyncMock(side_effect=ExtractionError("LLM failed")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/documents/upload",
                json={"raw_text": "Failed text"},
            )

    assert response.status_code == 422
    body = response.json()
    assert "Failed to extract structured data" in body["detail"]

    # Verify status in database
    async with AsyncSessionLocal() as session:
        repo = ClaimsRepository(session)
        # We can query the latest claim to verify its status.
        from sqlalchemy import select
        from app.db.models import ClaimEvent, IndianHealthClaim
        result = await session.execute(
            select(IndianHealthClaim).order_by(IndianHealthClaim.created_at.desc()).limit(1)
        )
        latest_claim = result.scalar_one_or_none()
        assert latest_claim is not None
        assert latest_claim.status == "EXTRACTION_FAILED"

        # Cleanup events first due to foreign key constraint
        from sqlalchemy import delete
        await session.execute(
            delete(ClaimEvent).where(ClaimEvent.claim_id == latest_claim.id)
        )
        # Cleanup claim
        await session.delete(latest_claim)
        await session.commit()