from app.db.session import AsyncSessionLocal
from app.graph.state import ClaimGraphState
from app.repositories.claims_repository import ClaimsRepository
from app.services.exceptions import ExtractionError
from app.services.pdf_generation_service import PdfGenerationService


async def generate_pdf(state: ClaimGraphState) -> dict:
    session_id = state.get("session_id")
    if not session_id:
        return {"status": "PDF_GENERATION_FAILED"}

    async with AsyncSessionLocal() as session:
        repo = ClaimsRepository(session)
        claim = await repo.get_by_session_id(session_id)
        if claim is None:
            return {"status": "PDF_GENERATION_FAILED"}

        try:
            pdf_service = PdfGenerationService()
            pdf_path = pdf_service.generate(
                extracted_data=claim.extracted_data or {},
                verified_codes=claim.verified_codes or {},
                session_id=state["session_id"],
            )
        except ExtractionError:
            claim.status = "PDF_GENERATION_FAILED"
            await session.commit()
            return {"status": "PDF_GENERATION_FAILED"}

        claim.irdai_pdf_url = pdf_path
        claim.status = "COMPLETED"
        await session.commit()

    return {"status": "COMPLETED", "irdai_pdf_url": pdf_path}