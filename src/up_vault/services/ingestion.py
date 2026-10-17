from sqlalchemy.ext.asyncio import AsyncSession

from up_vault.models.chunk import Chunk
from up_vault.models.document import Document
from up_vault.services.chunking import estimate_token_count, split_text
from up_vault.services.embeddings.base import EmbeddingProvider
from up_vault.services.hashing import HashService
from up_vault.services.loaders.text import TextLoader


class IngestionService:
    def __init__(
        self, session: AsyncSession, embedding_provider: EmbeddingProvider
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider

    async def ingest(self, path: str) -> Document:
        loader = TextLoader()
        content = await loader.load(path)
        content_hash = HashService.sha256(content)
        document = Document(
            filename=path, source_type="text", content_hash=content_hash
        )
        chunks = split_text(content)

        try:
            embeddings = await self.embedding_provider.embed_batch(chunks)

            self.session.add(document)
            await self.session.flush()

            for index, (chunk_text, embedding) in enumerate(
                zip(chunks, embeddings, strict=True)
            ):
                chunk = Chunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=index,
                    token_count=estimate_token_count(chunk_text),
                    embedding=embedding,
                )
                self.session.add(chunk)

            await self.session.commit()
        except Exception:
            # Ingestion is all-or-nothing: leave no partial document behind.
            await self.session.rollback()
            raise

        return document
