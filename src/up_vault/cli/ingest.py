import asyncio

import typer

from up_vault.database import SessionLocal
from up_vault.services.embeddings.factory import create_embedding_provider
from up_vault.services.ingestion import IngestionService

app = typer.Typer()


@app.command()
def file(path: str) -> None:
    asyncio.run(ingest_file(path))


async def ingest_file(path: str) -> None:
    provider = create_embedding_provider()
    try:
        async with SessionLocal() as session:
            service = IngestionService(session, provider)

            document = await service.ingest(path)

            typer.echo(f"Document created: {document.id}")
    finally:
        await provider.aclose()
