import asyncio

from sqlalchemy import select

from app.db.models import IndianMedicalCode
from app.db.session import AsyncSessionLocal
from app.services.embedding_service import EmbeddingService


async def backfill() -> None:
    embedding_service = EmbeddingService()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IndianMedicalCode).where(IndianMedicalCode.embedding.is_(None))
        )
        codes = result.scalars().all()

        if not codes:
            print("No codes need backfilling.")
            return

        for code in codes:
            text = f"{code.display_name}. {code.description or ''}".strip()
            code.embedding = await embedding_service.embed_text(text, task_type="retrieval_document")

        await session.commit()
        print(f"Backfilled embeddings for {len(codes)} codes.")


if __name__ == "__main__":
    asyncio.run(backfill())