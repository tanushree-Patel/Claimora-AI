from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IndianMedicalCode


class CodesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def vector_search(self, query_embedding: list[float], limit: int) -> list[tuple[IndianMedicalCode, float]]:
        # cosine_distance: 0 = identical, 2 = opposite. We convert to a 0-1 similarity score.
        distance = IndianMedicalCode.embedding.cosine_distance(query_embedding)
        stmt = (
            select(IndianMedicalCode, distance.label("distance"))
            .where(IndianMedicalCode.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [(code, 1 - (dist / 2)) for code, dist in rows]

    # Teammate B adds trigram_search() here — see Part B