from unittest.mock import MagicMock, patch

import pytest

from app.services.embedding_service import EmbeddingService
from app.services.exceptions import ExtractionError


@pytest.mark.asyncio
async def test_embed_text_returns_768_dim_vector():
    service = EmbeddingService()
    fake_embedding = [0.1] * 768
    with patch("app.services.embedding_service.genai.embed_content", return_value={"embedding": fake_embedding}):
        result = await service.embed_text("essential hypertension")
    assert len(result) == 768


@pytest.mark.asyncio
async def test_embed_text_raises_on_wrong_dimension():
    service = EmbeddingService()
    with patch("app.services.embedding_service.genai.embed_content", return_value={"embedding": [0.1] * 10}):
        with pytest.raises(ExtractionError):
            await service.embed_text("bad input")