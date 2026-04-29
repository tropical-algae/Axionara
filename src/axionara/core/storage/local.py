from pathlib import Path

from axionara.core.storage.base import StorageService


class LocalStorageService(StorageService):
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    async def save_bytes(self, relative_path: str, content: bytes) -> str:
        target_path = self.resolve_path(relative_path=relative_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)
        return relative_path

    def resolve_path(self, relative_path: str) -> Path:
        normalized = Path(relative_path)
        if normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError("Invalid storage path")
        return (self.root_dir / normalized).resolve()
