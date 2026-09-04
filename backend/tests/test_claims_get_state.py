from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.extraction import ClinicalInfo, ExtractedClaimData, HospitalInfo, PatientInfo
from app.graph.checkpointer import init_checkpointer, close_checkpointer

@pytest.fixture(autouse=True)
async def manage_checkpointer():
    await init_checkpointer()
    yield
    await close_checkpointer()

FAKE_EXTRACTION = ExtractedClaimData(
    patient=PatientInfo(full_name="Asha Rao"),
    hospital=HospitalInfo(hospital_name="Apollo Hospital"),
    clinical=ClinicalInfo(diagnosis_text="essential hypertension"),
)


@pytest.mark.asyncio
async def test_get_claim_state_returns_pending_review():
    with patch(
        "app.graph.nodes_extraction.ExtractionService.extract", new=AsyncMock(return_value=FAKE_EXTRACTION)
    ), patch("app.graph.nodes_review.RetrievalService.search") as mock_search:
        mock_search.return_value.candidates = []
        mock_search.return_value.query = "essential hypertension"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            start = await client.post("/api/v1/claims/process", json={"raw_text": "Asha Rao, essential hypertension."})
            session_id = start.json()["session_id"]

            state_response = await client.get(f"/api/v1/claims/{session_id}")

    assert state_response.status_code == 200
    assert state_response.json()["status"] == "PENDING_REVIEW"


@pytest.mark.asyncio
async def test_get_claim_state_404_for_unknown_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/claims/nonexistent-session-id")
    assert response.status_code == 404