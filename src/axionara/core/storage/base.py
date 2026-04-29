from abc import ABC, abstractmethod
from pathlib import Path


class StorageService(ABC):
    @abstractmethod
    async def save_bytes(self, relative_path: str, content: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def resolve_path(self, relative_path: str) -> Path:
        raise NotImplementedError
