import uuid

from fastapi import APIRouter, Depends, HTTPException
from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.graph.builder import build_claim_graph
from app.repositories.claims_repository import ClaimsRepository
from app.schemas.graph import (
    ProcessClaimRequest,
    ProcessClaimResponse,
    ResumeClaimRequest,
    ResumeClaimResponse,
)

router = APIRouter(tags=["claims"])


@router.post("/claims/process", response_model=ProcessClaimResponse)
async def process_claim(
    payload: ProcessClaimRequest, db: AsyncSession = Depends(get_db)
) -> ProcessClaimResponse:
    session_id = str(uuid.uuid4())
    repo = ClaimsRepository(db)
    await repo.create_claim(session_id=session_id)

    graph = build_claim_graph()
    config = {"configurable": {"thread_id": session_id}}

    result = await graph.ainvoke({"raw_text": payload.raw_text, "session_id": session_id}, config=config)

    return ProcessClaimResponse(
        session_id=session_id,
        status=result.get("status", "UNKNOWN"),
        candidates=result.get("candidates", []),
        validation_errors=result.get("validation_errors", []),
    )


@router.post("/claims/{session_id}/resume", response_model=ResumeClaimResponse)
async def resume_claim(session_id: str, payload: ResumeClaimRequest) -> ResumeClaimResponse:
    graph = build_claim_graph()
    config = {"configurable": {"thread_id": session_id}}

    state = await graph.aget_state(config)
    if state is None or not state.next:
        raise HTTPException(status_code=404, detail="No paused claim found for this session_id")

    result = await graph.ainvoke(Command(resume=payload.model_dump()), config=config)
    return ResumeClaimResponse(session_id=session_id, status=result.get("status", "UNKNOWN"))


@router.get("/claims/{session_id}", response_model=ProcessClaimResponse)
async def get_claim_state(session_id: str) -> ProcessClaimResponse:
    graph = build_claim_graph()
    config = {"configurable": {"thread_id": session_id}}

    state = await graph.aget_state(config)
    if state is None or not state.values:
        raise HTTPException(status_code=404, detail="No claim found for this session_id")

    values = state.values
    return ProcessClaimResponse(
        session_id=session_id,
        status=values.get("status", "UNKNOWN"),
        candidates=values.get("candidates", []),
        validation_errors=values.get("validation_errors", []),
    )