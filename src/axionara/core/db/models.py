from datetime import datetime

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    Float,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlmodel import Field, SQLModel


class ChatMemory(SQLModel, table=True):
    __tablename__ = "chat_memory"
    __table_args__ = (
        Index("ix_chat_memory_key", "key"),
        Index("ix_chat_memory_status", "status"),
        Index("ix_chat_memory_timestamp", "timestamp"),
    )

    id: int = Field(sa_column=Column("id", Integer, primary_key=True))
    key: str = Field(sa_column=Column("key", String))
    timestamp: int = Field(sa_column=Column("timestamp", BigInteger))
    role: str = Field(sa_column=Column("role", String))
    status: str = Field(sa_column=Column("status", String))
    data: dict = Field(sa_column=Column("data", JSON))


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_session"

    id: str = Field(sa_column=Column("id", String, primary_key=True))
    user_id: str = Field(sa_column=Column("user_id", String(32)))
    create_date: datetime | None = Field(
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    is_active: bool = Field(sa_column=Column("is_active", Boolean))


class UserAccount(SQLModel, table=True):
    __tablename__ = "user_account"

    __table_args__ = (
        Index("ix_user_email", "email", unique=True),
        Index("ix_user_username", "username", unique=True),
        Index("ix_user_full_name", "full_name"),
        Index("ix_user_id", "id"),
    )

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    username: str = Field(sa_column=Column("username", String(64)))
    email: str = Field(sa_column=Column("email", String(64)))
    password: str = Field(sa_column=Column("password", String(128)))
    scopes: str = Field(default='["consumer"]', sa_column=Column("scopes", String(128)))
    role: str = Field(default="consumer", sa_column=Column("role", String(32)))
    full_name: str = Field(default=None, sa_column=Column("full_name", String(32)))
    is_active: bool = Field(default=None, sa_column=Column("is_active", Boolean))
    is_superuser: bool = Field(default=None, sa_column=Column("is_superuser", Boolean))
    organization: str | None = Field(
        default=None, sa_column=Column("organization", String(128))
    )
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    profile: str | None = Field(default=None, sa_column=Column("profile", String(128)))


class DatasetAsset(SQLModel, table=True):
    __tablename__ = "dataset_asset"
    __table_args__ = (
        Index("ix_dataset_asset_owner_id", "owner_id"),
        Index("ix_dataset_asset_status", "status"),
        Index("ix_dataset_asset_source_format", "source_format"),
    )

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    title: str = Field(sa_column=Column("title", String(128)))
    description: str | None = Field(default=None, sa_column=Column("description", Text))
    owner_id: str = Field(sa_column=Column("owner_id", String(32)))
    source_format: str = Field(sa_column=Column("source_format", String(16)))
    representation_hint: str | None = Field(
        default=None, sa_column=Column("representation_hint", String(32))
    )
    original_filename: str = Field(sa_column=Column("original_filename", String(255)))
    storage_uri: str = Field(sa_column=Column("storage_uri", String(255)))
    raw_bucket: str | None = Field(
        default=None, sa_column=Column("raw_bucket", String(64))
    )
    raw_object_key: str | None = Field(
        default=None, sa_column=Column("raw_object_key", String(255))
    )
    content_type: str | None = Field(
        default=None, sa_column=Column("content_type", String(128))
    )
    etag: str | None = Field(default=None, sa_column=Column("etag", String(128)))
    file_size_bytes: int = Field(
        default=0, sa_column=Column("file_size_bytes", BigInteger)
    )
    status: str = Field(default="uploaded", sa_column=Column("status", String(32)))
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )


class AnalysisJob(SQLModel, table=True):
    __tablename__ = "analysis_job"
    __table_args__ = (
        Index("ix_analysis_job_dataset_id", "dataset_id"),
        Index("ix_analysis_job_status", "job_status"),
    )

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    dataset_id: str = Field(sa_column=Column("dataset_id", String(32)))
    triggered_by: str = Field(sa_column=Column("triggered_by", String(32)))
    job_status: str = Field(default="pending", sa_column=Column("job_status", String(32)))
    current_stage: str | None = Field(
        default=None, sa_column=Column("current_stage", String(64))
    )
    error_message: str | None = Field(
        default=None, sa_column=Column("error_message", Text)
    )
    started_at: datetime | None = Field(
        default=None, sa_column=Column("started_at", TIMESTAMP)
    )
    finished_at: datetime | None = Field(
        default=None, sa_column=Column("finished_at", TIMESTAMP)
    )
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )


class DatasetAnalysis(SQLModel, table=True):
    __tablename__ = "dataset_analysis"
    __table_args__ = (
        Index("ix_dataset_analysis_dataset_id", "dataset_id"),
        Index("ix_dataset_analysis_job_id", "job_id"),
    )

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    dataset_id: str = Field(sa_column=Column("dataset_id", String(32)))
    job_id: str | None = Field(default=None, sa_column=Column("job_id", String(32)))
    analysis_version: int = Field(
        default=1, sa_column=Column("analysis_version", Integer)
    )
    analysis_status: str = Field(sa_column=Column("analysis_status", String(32)))
    representation_type: str = Field(sa_column=Column("representation_type", String(32)))
    parser_status: str = Field(sa_column=Column("parser_status", String(32)))
    cleaning_status: str = Field(sa_column=Column("cleaning_status", String(32)))
    sensitivity_status: str = Field(sa_column=Column("sensitivity_status", String(32)))
    summary_status: str = Field(sa_column=Column("summary_status", String(32)))
    tag_status: str = Field(sa_column=Column("tag_status", String(32)))
    schema_snapshot: dict = Field(
        default_factory=dict, sa_column=Column("schema_snapshot", JSON)
    )
    statistics: dict = Field(default_factory=dict, sa_column=Column("statistics", JSON))
    issues: dict = Field(default_factory=dict, sa_column=Column("issues", JSON))
    cleaning_actions: dict = Field(
        default_factory=dict, sa_column=Column("cleaning_actions", JSON)
    )
    skipped_steps: dict = Field(
        default_factory=dict, sa_column=Column("skipped_steps", JSON)
    )
    export_capabilities: dict = Field(
        default_factory=dict, sa_column=Column("export_capabilities", JSON)
    )
    sensitivity_report: dict = Field(
        default_factory=dict, sa_column=Column("sensitivity_report", JSON)
    )
    suggested_tags: dict = Field(
        default_factory=dict, sa_column=Column("suggested_tags", JSON)
    )
    normalized_bucket: str | None = Field(
        default=None, sa_column=Column("normalized_bucket", String(64))
    )
    normalized_object_key: str | None = Field(
        default=None, sa_column=Column("normalized_object_key", String(255))
    )
    internal_summary: str | None = Field(
        default=None, sa_column=Column("internal_summary", Text)
    )
    llm_output_json: dict | None = Field(
        default=None, sa_column=Column("llm_output_json", JSON)
    )
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    update_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "update_date",
            TIMESTAMP,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        ),
    )


class DatasetProfile(SQLModel, table=True):
    __tablename__ = "dataset_profile"
    __table_args__ = (Index("ix_dataset_profile_dataset_id", "dataset_id", unique=True),)

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    dataset_id: str = Field(sa_column=Column("dataset_id", String(32)))
    analysis_id: str = Field(sa_column=Column("analysis_id", String(32)))
    public_summary: str = Field(sa_column=Column("public_summary", Text))
    processing_summary: str = Field(sa_column=Column("processing_summary", Text))
    cleaning_summary: str = Field(sa_column=Column("cleaning_summary", Text))
    risk_summary: str | None = Field(default=None, sa_column=Column("risk_summary", Text))
    public_statistics: dict = Field(
        default_factory=dict, sa_column=Column("public_statistics", JSON)
    )
    allowed_export_formats: list[str] = Field(
        default_factory=list, sa_column=Column("allowed_export_formats", JSON)
    )
    public_rag_text: str = Field(sa_column=Column("public_rag_text", Text))
    tag_summary: str | None = Field(default=None, sa_column=Column("tag_summary", Text))
    update_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "update_date",
            TIMESTAMP,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        ),
    )


class DatasetReview(SQLModel, table=True):
    __tablename__ = "dataset_review"
    __table_args__ = (Index("ix_dataset_review_dataset_id", "dataset_id"),)

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    dataset_id: str = Field(sa_column=Column("dataset_id", String(32)))
    analysis_id: str = Field(sa_column=Column("analysis_id", String(32)))
    reviewer_id: str = Field(sa_column=Column("reviewer_id", String(32)))
    review_status: str = Field(
        default="pending", sa_column=Column("review_status", String(32))
    )
    review_comment: str | None = Field(
        default=None, sa_column=Column("review_comment", Text)
    )
    publish_comment: str | None = Field(
        default=None, sa_column=Column("publish_comment", Text)
    )
    reviewed_at: datetime | None = Field(
        default=None, sa_column=Column("reviewed_at", TIMESTAMP)
    )
    published_at: datetime | None = Field(
        default=None, sa_column=Column("published_at", TIMESTAMP)
    )
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )


class Tag(SQLModel, table=True):
    __tablename__ = "tag"
    __table_args__ = (Index("ix_tag_slug_category", "slug", "category", unique=True),)

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    name: str = Field(sa_column=Column("name", String(64)))
    slug: str = Field(sa_column=Column("slug", String(64)))
    category: str = Field(sa_column=Column("category", String(32)))
    description: str | None = Field(default=None, sa_column=Column("description", Text))
    source: str = Field(default="system", sa_column=Column("source", String(32)))
    is_active: bool = Field(default=True, sa_column=Column("is_active", Boolean))
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )


class DatasetTag(SQLModel, table=True):
    __tablename__ = "dataset_tag"
    __table_args__ = (
        Index("ix_dataset_tag_dataset_id", "dataset_id"),
        Index("ix_dataset_tag_tag_id", "tag_id"),
    )

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    dataset_id: str = Field(sa_column=Column("dataset_id", String(32)))
    tag_id: str = Field(sa_column=Column("tag_id", String(32)))
    analysis_id: str | None = Field(
        default=None, sa_column=Column("analysis_id", String(32))
    )
    confidence: float | None = Field(default=None, sa_column=Column("confidence", Float))
    generated_by: str = Field(
        default="system", sa_column=Column("generated_by", String(32))
    )
    is_primary: bool = Field(default=False, sa_column=Column("is_primary", Boolean))
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    update_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "update_date",
            TIMESTAMP,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        ),
    )


class AccessGrant(SQLModel, table=True):
    __tablename__ = "access_grant"
    __table_args__ = (
        Index("ix_access_grant_dataset_id", "dataset_id"),
        Index("ix_access_grant_user_id", "user_id"),
        Index("ix_access_grant_status", "grant_status"),
    )

    id: str = Field(sa_column=Column("id", String(32), primary_key=True))
    dataset_id: str = Field(sa_column=Column("dataset_id", String(32)))
    user_id: str = Field(sa_column=Column("user_id", String(32)))
    grant_method: str = Field(
        default="demo_click", sa_column=Column("grant_method", String(32))
    )
    grant_status: str = Field(
        default="granted", sa_column=Column("grant_status", String(32))
    )
    note: str | None = Field(default=None, sa_column=Column("note", Text))
    granted_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            "granted_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    expires_at: datetime | None = Field(
        default=None, sa_column=Column("expires_at", TIMESTAMP)
    )
    create_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "create_date", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
