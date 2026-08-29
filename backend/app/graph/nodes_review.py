from langgraph.types import interrupt

from app.db.session import AsyncSessionLocal
from app.graph.state import ClaimGraphState
from app.services.retrieval_service import RetrievalService


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
    return {"status": "APPROVED"}