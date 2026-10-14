from abc import ABC, abstractmethod


class DocumentLoader(ABC):
    @abstractmethod
    async def load(self, path: str) -> str:
        pass
