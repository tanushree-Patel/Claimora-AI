# backend/app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(text("SELECT 1"))
    db_ok = result.scalar() == 1
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}