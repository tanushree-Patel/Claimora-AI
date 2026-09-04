from langgraph.types import interrupt

from app.db.session import AsyncSessionLocal
from app.graph.state import ClaimGraphState
from app.services.retrieval_service import RetrievalService
from app.repositories.claims_repository import ClaimsRepository

async def retrieve_codes(state: ClaimGraphState) -> dict:
    diagnosis_text = state["extracted_data"]["clinical"]["diagnosis_text"]
    async with AsyncSessionLocal() as session:
        result = await RetrievalService(session).search(diagnosis_text)
    return {"candidates": [c.model_dump() for c in result.candidates], "status": "PENDING_REVIEW"}


async def human_review(state: ClaimGraphState) -> dict:
    decision = interrupt(
        {
            "message": "Review the candidate codes and approve or correct them.",
            "candidates": state["candidates"],
        }
    )
    return {"review_decision": decision, "status": "REVIEWED"}

async def finalize(state: ClaimGraphState) -> dict:
    decision = state.get("review_decision") or {}
    approved_codes = decision.get("approved_codes", [])
    session_id = state.get("session_id")

    if session_id:
        async with AsyncSessionLocal() as session:
            repo = ClaimsRepository(session)
            claim = await repo.get_by_session_id(session_id)
            if claim:
                claim.verified_codes = {"approved_codes": approved_codes, "notes": decision.get("reviewer_notes")}
                claim.status = "APPROVED"
                await session.commit()

    return {"status": "APPROVED"}