from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class DatasetSourceFormat(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    TXT = "txt"
    PDF = "pdf"
    SQL = "sql"


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
    category: str | None = None
    source_organization: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    update_frequency: str | None = None
    sensitivity_level: str | None = None
    intended_visibility: str | None = None
    access_policy: str | None = None
    usage_restrictions: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    owner_id: str
    source_format: str
    representation_hint: str | None = None
    original_filename: str
    storage_uri: str
    raw_bucket: str | None = None
    raw_object_key: str | None = None
    content_type: str | None = None
    etag: str | None = None
    file_size_bytes: int
    status: str
    create_date: datetime | None = None
    update_date: datetime | None = None


class AnalysisJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    triggered_by: str
    job_status: str
    current_stage: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    create_date: datetime | None = None


class DatasetAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    job_id: str | None = None
    analysis_version: int
    analysis_status: str
    representation_type: str
    parser_status: str
    cleaning_status: str
    sensitivity_status: str
    summary_status: str
    tag_status: str
    schema_snapshot: dict
    statistics: dict
    issues: dict
    cleaning_actions: dict
    skipped_steps: dict
    export_capabilities: dict
    sensitivity_report: dict
    suggested_tags: dict
    internal_summary: str | None = None
    llm_output_json: dict | None = None
    create_date: datetime | None = None
    update_date: datetime | None = None


class DatasetProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    analysis_id: str
    public_summary: str
    processing_summary: str
    cleaning_summary: str
    risk_summary: str | None = None
    public_statistics: dict
    allowed_export_formats: list[str]
    public_rag_text: str
    tag_summary: str | None = None
    update_date: datetime | None = None


class DatasetReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    analysis_id: str
    reviewer_id: str
    review_status: str
    review_comment: str | None = None
    publish_comment: str | None = None
    reviewed_at: datetime | None = None
    published_at: datetime | None = None
    create_date: datetime | None = None


class ReviewRequest(BaseModel):
    comment: str | None = None


class CatalogDatasetRead(BaseModel):
    dataset: DatasetAssetRead
    profile: DatasetProfileRead
    tags: list[str] = []


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    category: str
    description: str | None = None
    source: str
    is_active: bool


class CatalogRagRequest(BaseModel):
    question: str
    dataset_id: str | None = None
    tag_slug: str | None = None
    limit: int = 3


class CatalogRagMatch(BaseModel):
    dataset_id: str
    title: str
    score: float
    tags: list[str] = []
    snippet: str


class CatalogRagResponse(BaseModel):
    question: str
    answer: str
    matches: list[CatalogRagMatch]
    source_scope: str = "public_dataset_profile"
    raw_content_used: bool = False


class ContentRagRequest(BaseModel):
    question: str
    limit: int = 5


class ContentRagMatch(BaseModel):
    dataset_id: str
    chunk_id: str
    score: float
    snippet: str


class ContentRagResponse(BaseModel):
    question: str
    answer: str
    matches: list[ContentRagMatch]
    source_scope: str = "authorized_dataset_content"
    raw_content_used: bool = True


class AccessGrantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    user_id: str
    grant_method: str
    grant_status: str
    note: str | None = None
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    create_date: datetime | None = None


class MyDatasetRead(BaseModel):
    grant: AccessGrantRead
    dataset: DatasetAssetRead
    profile: DatasetProfileRead
    tags: list[str] = []


class ExportFormat(StrEnum):
    RAW = "raw"
    CSV = "csv"
    JSON = "json"
    SQL = "sql"


class ExportJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ExportRequest(BaseModel):
    target_format: ExportFormat


class ExportJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    user_id: str
    grant_id: str
    target_format: str
    job_status: str
    error_message: str | None = None
    output_bucket: str | None = None
    output_object_key: str | None = None
    output_filename: str | None = None
    output_content_type: str | None = None
    output_size_bytes: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    create_date: datetime | None = None
    update_date: datetime | None = None
