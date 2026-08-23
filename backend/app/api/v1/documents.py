import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_db
from app.repositories.claims_repository import ClaimsRepository
from app.schemas.claims import ClaimStatus, DocumentUploadRequest, DocumentUploadResponse
from app.services.exceptions import ExtractionError
from app.services.extraction_service import ExtractionService

router = APIRouter(tags=["documents"])
logger = get_logger(__name__)


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    payload: DocumentUploadRequest,
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    repo = ClaimsRepository(db)
    session_id = str(uuid.uuid4())
    claim = await repo.create_claim(session_id=session_id)

    extraction_service = ExtractionService()
    try:
        extracted = await extraction_service.extract(payload.raw_text)
    except ExtractionError:
        logger.exception("Extraction failed for session_id=%s", session_id)
        await repo.update_extracted_data(claim, extracted_data={}, status=ClaimStatus.EXTRACTION_FAILED)
        raise HTTPException(status_code=422, detail="Failed to extract structured data from the provided text")

    await repo.update_extracted_data(
        claim, extracted_data=extracted.model_dump(mode="json"), status=ClaimStatus.EXTRACTED
    )
    return DocumentUploadResponse(session_id=session_id, status=ClaimStatus.EXTRACTED, extracted_data=extracted)