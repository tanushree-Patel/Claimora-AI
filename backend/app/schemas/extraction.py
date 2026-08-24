from datetime import date

from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    full_name: str
    date_of_birth: date | None = None
    gender: str | None = None
    abha_id: str | None = Field(default=None, description="Ayushman Bharat Health Account ID")
    policy_number: str | None = None


class HospitalInfo(BaseModel):
    hospital_name: str
    hospital_id: str | None = None
    admission_date: date | None = None
    discharge_date: date | None = None


class ClinicalInfo(BaseModel):
    diagnosis_text: str = Field(..., description="Raw diagnosis phrase as stated in the clinical note")
    procedure_text: str | None = None
    symptoms: list[str] = Field(default_factory=list)


class ExtractedClaimData(BaseModel):
    patient: PatientInfo
    hospital: HospitalInfo
    clinical: ClinicalInfo
    extraction_confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Model's self-reported confidence, not clinical certainty"
    )
    