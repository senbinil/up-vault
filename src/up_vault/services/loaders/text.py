from pathlib import Path

from up_vault.services.loaders.base import DocumentLoader


class TextLoader(DocumentLoader):
    async def load(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")
