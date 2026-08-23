# tests/test_extraction_service.py
from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.extraction import ClinicalInfo, ExtractedClaimData, HospitalInfo, PatientInfo
from app.services.exceptions import ExtractionError
from app.services.extraction_service import ExtractionService

FAKE_RESULT = ExtractedClaimData(
    patient=PatientInfo(full_name="Ravi Kumar"),
    hospital=HospitalInfo(hospital_name="Fortis Hospital"),
    clinical=ClinicalInfo(diagnosis_text="unspecified asthma"),
)


@pytest.mark.asyncio
async def test_extract_returns_validated_model():
    service = ExtractionService()
    with patch.object(service, "_llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=FAKE_RESULT)
        result = await service.extract("Patient has wheezing and shortness of breath.")
    assert result.patient.full_name == "Ravi Kumar"


@pytest.mark.asyncio
async def test_extract_raises_extraction_error_on_llm_failure():
    service = ExtractionService()
    with patch.object(service, "_llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(side_effect=RuntimeError("API timeout"))
        with pytest.raises(ExtractionError):
            await service.extract("some clinical text")