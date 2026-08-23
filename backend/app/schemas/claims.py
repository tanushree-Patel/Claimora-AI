from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.extraction import ExtractedClaimData


class ClaimStatus(StrEnum):
    DRAFT = "DRAFT"
    EXTRACTED = "EXTRACTED"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"


class DocumentUploadRequest(BaseModel):
    raw_text: str = Field(..., min_length=10, description="Raw clinical text to extract from")


class DocumentUploadResponse(BaseModel):
    session_id: str
    status: ClaimStatus
    extracted_data: ExtractedClaimData | None = None