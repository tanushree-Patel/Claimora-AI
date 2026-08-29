from google import genai
from google.genai import types

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.exceptions import ExtractionError

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model_name = settings.embedding_model_name

    async def embed_text(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        try:
            result = await self._client.aio.models.embed_content(
                model=self._model_name,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=768,
                ),
            )
        except Exception as exc:
            logger.error("Embedding call failed: %s", exc)
            raise ExtractionError("Failed to generate embedding") from exc

        embedding = result.embeddings[0].values if result.embeddings else None
        if not embedding or len(embedding) != 768:
            raise ExtractionError(f"Unexpected embedding shape: {len(embedding) if embedding else 0}")
        return embedding