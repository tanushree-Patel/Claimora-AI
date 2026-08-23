from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    full_name: str | None = Field(default=None, description="Patient's full name")
    age: int | None = Field(default=None, description="Patient's age")
    gender: str | None = Field(default=None, description="Patient's gender")


class HospitalInfo(BaseModel):
    hospital_name: str | None = Field(default=None, description="Name of the hospital")
    admission_date: str | None = Field(default=None, description="Date of admission")
    discharge_date: str | None = Field(default=None, description="Date of discharge")


class ClinicalInfo(BaseModel):
    diagnosis_text: str | None = Field(default=None, description="Primary or secondary diagnosis description")
    symptoms: list[str] | None = Field(default=None, description="List of observed symptoms")


class ExtractedClaimData(BaseModel):
    patient: PatientInfo = Field(default_factory=PatientInfo)
    hospital: HospitalInfo = Field(default_factory=HospitalInfo)
    clinical: ClinicalInfo = Field(default_factory=ClinicalInfo)
