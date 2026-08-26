from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.embedding_service import EmbeddingService
from app.services.exceptions import ExtractionError


@pytest.mark.asyncio
async def test_embed_text_returns_768_dim_vector():
    service = EmbeddingService()
    fake_embedding = [0.1] * 768
    
    mock_result = MagicMock()
    mock_emb = MagicMock()
    mock_emb.values = fake_embedding
    mock_result.embeddings = [mock_emb]
    
    with patch.object(service._client.aio.models, "embed_content", new_callable=AsyncMock, return_value=mock_result) as mock_embed:
        result = await service.embed_text("essential hypertension")
        
    assert result == fake_embedding
    mock_embed.assert_called_once()


@pytest.mark.asyncio
async def test_embed_text_raises_on_wrong_dimension():
    service = EmbeddingService()
    
    mock_result = MagicMock()
    mock_emb = MagicMock()
    mock_emb.values = [0.1] * 10
    mock_result.embeddings = [mock_emb]
    
    with patch.object(service._client.aio.models, "embed_content", new_callable=AsyncMock, return_value=mock_result):
        with pytest.raises(ExtractionError):
            await service.embed_text("bad input")