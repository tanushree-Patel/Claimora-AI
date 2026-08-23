import pytest
from pydantic import ValidationError

from app.schemas.extraction import ClinicalInfo, ExtractedClaimData, HospitalInfo, PatientInfo


def test_valid_extracted_claim_data_parses():
    data = ExtractedClaimData(
        patient=PatientInfo(full_name="Asha Rao"),
        hospital=HospitalInfo(hospital_name="Apollo Hospital"),
        clinical=ClinicalInfo(diagnosis_text="essential hypertension"),
    )
    assert data.patient.full_name == "Asha Rao"


def test_missing_required_field_raises():
    with pytest.raises(ValidationError):
        ExtractedClaimData(
            patient=PatientInfo(full_name="Asha Rao"),
            hospital=HospitalInfo(hospital_name="Apollo Hospital"),
            clinical={},  # missing required diagnosis_text
        )


def test_confidence_out_of_range_raises():
    with pytest.raises(ValidationError):
        ExtractedClaimData(
            patient=PatientInfo(full_name="Asha Rao"),
            hospital=HospitalInfo(hospital_name="Apollo Hospital"),
            clinical=ClinicalInfo(diagnosis_text="asthma"),
            extraction_confidence=1.5,  # invalid — must be <= 1.0
        )