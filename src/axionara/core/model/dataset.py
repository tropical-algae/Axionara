from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class DatasetSourceFormat(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    TXT = "txt"
    PDF = "pdf"


class DatasetAssetStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING_REVIEW = "processing_review"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class DatasetAssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None = None
    owner_id: str
    source_format: str
    original_filename: str
    storage_uri: str
    file_size_bytes: int
    status: str
    create_date: datetime | None = None
    update_date: datetime | None = None
