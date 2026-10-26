from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from up_vault.database import get_db
from up_vault.schemas.query import QueryRequest, QueryResponse, QuerySource
from up_vault.services.embeddings.factory import create_embedding_provider
from up_vault.services.retrieval import RetrievalService

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    session: AsyncSession = Depends(get_db),
) -> QueryResponse:
    provider = create_embedding_provider()

    try:
        service = RetrievalService(session, provider)
        chunks = await service.search(request.question, limit=request.limit)

        return QueryResponse(
            sources=[
                QuerySource(
                    document_id=chunk.document_id,
                    filename=chunk.document.filename,
                    chunk_index=chunk.chunk_index,
                )
                for chunk in chunks
            ]
        )
    finally:
        await provider.aclose()
