from app.db.session import AsyncSessionLocal
from app.graph.state import ClaimGraphState
from app.repositories.claims_repository import ClaimsRepository
from app.schemas.claims import ClaimStatus
from app.services.exceptions import ExtractionError
from app.services.extraction_service import ExtractionService

REQUIRED_FIELDS = [
    ("patient", "full_name"),
    ("hospital", "hospital_name"),
    ("clinical", "diagnosis_text"),
]


async def extract_data(state: ClaimGraphState) -> dict:
    service = ExtractionService()
    try:
        result = await service.extract(state["raw_text"])
    except ExtractionError:
        return {"status": "EXTRACTION_FAILED", "validation_errors": ["LLM extraction failed"]}
    
    extracted_dict = result.model_dump(mode="json")
    session_id = state.get("session_id")
    if session_id:
        async with AsyncSessionLocal() as session:
            repo = ClaimsRepository(session)
            claim = await repo.get_by_session_id(session_id)
            if claim:
                await repo.update_extracted_data(claim, extracted_data=extracted_dict, status=ClaimStatus.EXTRACTED)
                await session.commit()

    return {"extracted_data": extracted_dict, "status": "EXTRACTED"}


async def validate_compliance(state: ClaimGraphState) -> dict:
    data = state.get("extracted_data") or {}
    errors = [
        f"Missing required field: {section}.{field}"
        for section, field in REQUIRED_FIELDS
        if not data.get(section, {}).get(field)
    ]
    status = "VALIDATION_FAILED" if errors else "VALIDATED"
    return {"validation_errors": errors, "status": status}