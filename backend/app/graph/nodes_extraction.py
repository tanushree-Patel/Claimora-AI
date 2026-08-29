from app.graph.state import ClaimGraphState
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
    return {"extracted_data": result.model_dump(mode="json"), "status": "EXTRACTED"}


async def validate_compliance(state: ClaimGraphState) -> dict:
    data = state.get("extracted_data") or {}
    errors = [
        f"Missing required field: {section}.{field}"
        for section, field in REQUIRED_FIELDS
        if not data.get(section, {}).get(field)
    ]
    status = "VALIDATION_FAILED" if errors else "VALIDATED"
    return {"validation_errors": errors, "status": status}