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


def check_storage_health() -> dict:
    buckets = [
        settings.MINIO_BUCKET_RAW,
        settings.MINIO_BUCKET_ANALYSIS,
        settings.MINIO_BUCKET_ARTIFACTS,
    ]
    try:
        service = get_storage_service()
        details = service.health_check(buckets=buckets)
        buckets_detail = details.get("buckets", {})
        bucket_errors = [
            bucket
            for bucket, status in buckets_detail.items()
            if status.get("error") is not None
        ]
        return {
            "status": "unhealth" if bucket_errors else "health",
            "backend": settings.STORAGE_BACKEND,
            "details": details,
        }
    except Exception as err:
        return {
            "status": "unhealth",
            "backend": settings.STORAGE_BACKEND,
            "details": {"error": str(err)},
        }
