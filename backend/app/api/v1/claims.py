import uuid

from fastapi import APIRouter, HTTPException
from langgraph.types import Command

from app.graph.builder import build_claim_graph
from app.schemas.graph import (
    ProcessClaimRequest,
    ProcessClaimResponse,
    ResumeClaimRequest,
    ResumeClaimResponse,
)

router = APIRouter(tags=["claims"])


@router.post("/claims/process", response_model=ProcessClaimResponse)
async def process_claim(payload: ProcessClaimRequest) -> ProcessClaimResponse:
    session_id = str(uuid.uuid4())
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