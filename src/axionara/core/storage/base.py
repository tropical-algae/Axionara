from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class StoredObject:
    bucket: str
    object_key: str
    size: int
    etag: str | None = None
    content_type: str | None = None

    @property
    def uri(self) -> str:
        return f"{self.bucket}/{self.object_key}"


class StorageService(ABC):
    @abstractmethod
    def save_bytes(
        self,
        bucket: str,
        object_key: str,
        content: bytes,
        content_type: str | None = None,
    ) -> StoredObject:
        raise NotImplementedError

    @abstractmethod
    def get_bytes(self, bucket: str, object_key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def stat_object(self, bucket: str, object_key: str) -> StoredObject:
        raise NotImplementedError
