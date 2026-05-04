from axionara.common.config import settings
from axionara.core.storage import LocalStorageService, StorageService


def get_storage_service() -> StorageService:
    if settings.STORAGE_BACKEND == "local":
        return LocalStorageService(root_dir=settings.LOCAL_STORAGE_ROOT)
    from axionara.core.storage.minio import MinioStorageService

    return MinioStorageService(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )
