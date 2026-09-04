from pydantic import BaseModel

from app.schemas.retrieval import CodeCandidate


class ProcessClaimRequest(BaseModel):
    raw_text: str


class ProcessClaimResponse(BaseModel):
    session_id: str
    status: str
    candidates: list[CodeCandidate] = []
    validation_errors: list[str] = []
    irdai_pdf_url: str | None = None


class ResumeClaimRequest(BaseModel):
    approved_codes: list[str]
    reviewer_notes: str | None = None


class ResumeClaimResponse(BaseModel):
    session_id: str
    status: str
    irdai_pdf_url: str | None = None