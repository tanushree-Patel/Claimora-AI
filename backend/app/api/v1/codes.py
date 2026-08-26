
# backend/app/api/v1/codes.py
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.retrieval import RetrievalResult
from app.services.retrieval_service import RetrievalService

from app.db.models import IndianMedicalCode
from app.db.session import get_db

router = APIRouter(tags=["codes"])


@router.get("/codes/count")
async def count_codes(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(func.count()).select_from(IndianMedicalCode))
    return {"count": result.scalar_one()}


@router.get("/codes/search", response_model=RetrievalResult)
async def search_codes(query: str, db: AsyncSession = Depends(get_db)) -> RetrievalResult:
    service = RetrievalService(db)
    return await service.search(query)