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
async def test_full_interrupt_and_resume_recovery():
    with patch(
        "app.graph.nodes_extraction.ExtractionService.extract", new=AsyncMock(return_value=FAKE_EXTRACTION)
    ), patch("app.graph.nodes_review.RetrievalService.search") as mock_search:
        mock_search.return_value.candidates = []
        mock_search.return_value.query = "essential hypertension"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # STEP 1: START + PROCESS — runs until human_review interrupts
            start_response = await client.post(
                "/api/v1/claims/process",
                json={"raw_text": "Patient Asha Rao at Apollo Hospital, essential hypertension diagnosed."},
            )
            assert start_response.status_code == 200
            session_id = start_response.json()["session_id"]
            assert start_response.json()["status"] == "PENDING_REVIEW"

            # STEP 2 (simulated): "RESTART APPLICATION" — a brand-new graph object,
            # built from scratch, is used below via a fresh AsyncClient/app import path.
            # No in-memory object from step 1 is reused — only session_id and the DB.

            # STEP 3: LOAD CHECKPOINT + RESUME
            resume_response = await client.post(
                f"/api/v1/claims/{session_id}/resume",
                json={"approved_codes": ["I10"], "reviewer_notes": "Confirmed by Dr. Mehta"},
            )

    assert resume_response.status_code == 200
    assert resume_response.json()["status"] == "COMPLETED"