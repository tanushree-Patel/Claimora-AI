
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.repositories.codes_repository import CodesRepository
from app.schemas.retrieval import CodeCandidate, RetrievalResult
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self, db: AsyncSession):
        self._repo = CodesRepository(db)
        self._embedding_service = EmbeddingService()
        self._top_k = get_settings().retrieval_top_k

    async def search(self, query_text: str) -> RetrievalResult:
        query_embedding = await self._embedding_service.embed_text(query_text, task_type="retrieval_query")

        vector_matches = await self._repo.vector_search(query_embedding, limit=self._top_k)
        trigram_matches = await self._repo.trigram_search(query_text, limit=self._top_k)

        merged: dict[str, CodeCandidate] = {}

        for code, score in vector_matches:
            merged[code.code] = CodeCandidate(
                code_system=code.code_system, code=code.code,
                display_name=code.display_name, score=score, matched_via=["vector"],
            )

        for code, score in trigram_matches:
            if code.code in merged:
                existing = merged[code.code]
                existing.score = max(existing.score, score) + 0.1
                existing.matched_via.append("trigram")
            else:
                merged[code.code] = CodeCandidate(
                    code_system=code.code_system, code=code.code,
                    display_name=code.display_name, score=score, matched_via=["trigram"],
                )

        ranked = sorted(merged.values(), key=lambda c: c.score, reverse=True)[: self._top_k]
        return RetrievalResult(query=query_text, candidates=ranked)