from pathlib import Path

from axionara.core.storage.base import StorageService, StoredObject


class LocalStorageService(StorageService):
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save_bytes(
        self,
        bucket: str,
        object_key: str,
        content: bytes,
        content_type: str | None = None,
    ) -> StoredObject:
        target_path = self.resolve_path(bucket=bucket, object_key=object_key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)
        return StoredObject(
            bucket=bucket,
            object_key=object_key,
            size=len(content),
            content_type=content_type,
        )

    def get_bytes(self, bucket: str, object_key: str) -> bytes:
        return self.resolve_path(bucket=bucket, object_key=object_key).read_bytes()

    def stat_object(self, bucket: str, object_key: str) -> StoredObject:
        target_path = self.resolve_path(bucket=bucket, object_key=object_key)
        return StoredObject(
            bucket=bucket,
            object_key=object_key,
            size=target_path.stat().st_size,
        )

    def resolve_path(self, bucket: str, object_key: str) -> Path:
        normalized = Path(bucket) / object_key
        if normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError("Invalid storage path")
        return (self.root_dir / normalized).resolve()
