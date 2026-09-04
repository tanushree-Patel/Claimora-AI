import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
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
from app.services.document_ingestion_service import DocumentIngestionService
from app.services.exceptions import ExtractionError

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
        irdai_pdf_url=result.get("irdai_pdf_url"),
    )


@router.post("/claims/process-file", response_model=ProcessClaimResponse)
async def process_claim_file(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> ProcessClaimResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    file_bytes = await file.read()
    ingestion = DocumentIngestionService()
    try:
        raw_text = ingestion.extract_text(file_bytes)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return await process_claim(ProcessClaimRequest(raw_text=raw_text), db=db)


@router.post("/claims/{session_id}/resume", response_model=ResumeClaimResponse)
async def resume_claim(session_id: str, payload: ResumeClaimRequest) -> ResumeClaimResponse:
    graph = build_claim_graph()
    config = {"configurable": {"thread_id": session_id}}

    state = await graph.aget_state(config)
    if state is None or not state.next:
        raise HTTPException(status_code=404, detail="No paused claim found for this session_id")

    result = await graph.ainvoke(Command(resume=payload.model_dump()), config=config)
    return ResumeClaimResponse(
        session_id=session_id,
        status=result.get("status", "UNKNOWN"),
        irdai_pdf_url=result.get("irdai_pdf_url"),
    )


@router.get("/claims/{session_id}", response_model=ProcessClaimResponse)
async def get_claim_state(
    session_id: str, db: AsyncSession = Depends(get_db)
) -> ProcessClaimResponse:
    graph = build_claim_graph()
    config = {"configurable": {"thread_id": session_id}}

    state = await graph.aget_state(config)
    if state is None or not state.values:
        raise HTTPException(status_code=404, detail="No claim found for this session_id")

    values = state.values
    pdf_url = values.get("irdai_pdf_url")
    if not pdf_url:
        repo = ClaimsRepository(db)
        claim = await repo.get_by_session_id(session_id)
        if claim:
            pdf_url = claim.irdai_pdf_url

    return ProcessClaimResponse(
        session_id=session_id,
        status=values.get("status", "UNKNOWN"),
        candidates=values.get("candidates", []),
        validation_errors=values.get("validation_errors", []),
        irdai_pdf_url=pdf_url,
    )
