from io import BytesIO

from minio import Minio

from axionara.core.storage.base import StorageService, StoredObject


class MinioStorageService(StorageService):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def save_bytes(
        self,
        bucket: str,
        object_key: str,
        content: bytes,
        content_type: str | None = None,
    ) -> StoredObject:
        self.ensure_bucket(bucket=bucket)
        result = self.client.put_object(
            bucket_name=bucket,
            object_name=object_key,
            data=BytesIO(content),
            length=len(content),
            content_type=content_type or "application/octet-stream",
        )
        return StoredObject(
            bucket=bucket,
            object_key=object_key,
            size=len(content),
            etag=result.etag,
            content_type=content_type,
        )

    def get_bytes(self, bucket: str, object_key: str) -> bytes:
        response = self.client.get_object(bucket_name=bucket, object_name=object_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def stat_object(self, bucket: str, object_key: str) -> StoredObject:
        stat = self.client.stat_object(bucket_name=bucket, object_name=object_key)
        return StoredObject(
            bucket=bucket,
            object_key=object_key,
            size=stat.size or 0,
            etag=stat.etag,
            content_type=stat.content_type,
        )

    def ensure_bucket(self, bucket: str) -> None:
        if not self.client.bucket_exists(bucket_name=bucket):
            self.client.make_bucket(bucket_name=bucket)

    def health_check(self, buckets: list[str]) -> dict:
        bucket_status = {}
        for bucket in buckets:
            try:
                bucket_status[bucket] = {
                    "exists": self.client.bucket_exists(bucket_name=bucket),
                    "error": None,
                }
            except Exception as err:  # noqa: PERF203
                bucket_status[bucket] = {"exists": False, "error": str(err)}  # type: ignore
        return {"buckets": bucket_status}
