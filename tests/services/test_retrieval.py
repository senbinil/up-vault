from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Select
from sqlalchemy.dialects import postgresql

from up_vault.models.chunk import EMBEDDING_DIMENSION
from up_vault.services.retrieval import RetrievalService


@pytest.mark.asyncio
async def test_search_returns_matching_chunks():
    query_embedding = [0.1] * EMBEDDING_DIMENSION
    chunks = [MagicMock(), MagicMock()]

    embedding_provider = AsyncMock()
    embedding_provider.embed.return_value = query_embedding

    session = MagicMock()
    result = MagicMock()
    result.all.return_value = chunks
    session.scalars = AsyncMock(return_value=result)

    service = RetrievalService(session, embedding_provider)

    retrieved = await service.search("How do i reset my password?")
    embedding_provider.embed.assert_awaited_once_with("How do i reset my password?")

    statement = session.scalars.await_args.args[0]
    assert isinstance(statement, Select)
    compiled = statement.compile(
        dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False}
    )
    assert "chunks.embedding <=>" in str(compiled)
    assert retrieved == chunks
