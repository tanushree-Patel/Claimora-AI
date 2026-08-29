from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes_extraction import extract_data, validate_compliance
from app.schemas.extraction import ClinicalInfo, ExtractedClaimData, HospitalInfo, PatientInfo
from app.services.exceptions import ExtractionError

VALID_EXTRACTION = ExtractedClaimData(
    patient=PatientInfo(full_name="Asha Rao"),
    hospital=HospitalInfo(hospital_name="Apollo Hospital"),
    clinical=ClinicalInfo(diagnosis_text="essential hypertension"),
)


@pytest.mark.asyncio
async def test_extract_data_success_sets_extracted_status():
    with patch(
        "app.graph.nodes_extraction.ExtractionService.extract", new=AsyncMock(return_value=VALID_EXTRACTION)
    ):
        result = await extract_data({"raw_text": "some clinical note"})
    assert result["status"] == "EXTRACTED"


@pytest.mark.asyncio
async def test_extract_data_failure_sets_failed_status():
    with patch(
        "app.graph.nodes_extraction.ExtractionService.extract",
        new=AsyncMock(side_effect=ExtractionError("boom")),
    ):
        result = await extract_data({"raw_text": "garbled text"})
    assert result["status"] == "EXTRACTION_FAILED"


@pytest.mark.asyncio
async def test_validate_compliance_flags_missing_diagnosis():
    state = {"extracted_data": {"patient": {"full_name": "A"}, "hospital": {"hospital_name": "H"}, "clinical": {}}}
    result = await validate_compliance(state)
    assert result["status"] == "VALIDATION_FAILED"
    assert any("diagnosis_text" in e for e in result["validation_errors"])