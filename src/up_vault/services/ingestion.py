from sqlalchemy.ext.asyncio import AsyncSession

from up_vault.models.chunk import Chunk
from up_vault.models.document import Document
from up_vault.services.chunking import split_text
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

        self.session.add(document)
        await self.session.flush()

        chunks = split_text(content)

        for index, chunk_text in enumerate(chunks):
            embedding = await self.embedding_provider.embed(chunk_text)
            chunk = Chunk(
                document_id=document.id,
                content=chunk_text,
                chunk_index=index,
                embedding=embedding,
            )
            self.session.add(chunk)
        await self.session.commit()

        return document
