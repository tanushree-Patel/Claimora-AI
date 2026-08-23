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