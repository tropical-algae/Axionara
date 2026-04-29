from datetime import datetime

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
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
    original_filename: str = Field(sa_column=Column("original_filename", String(255)))
    storage_uri: str = Field(sa_column=Column("storage_uri", String(255)))
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
    update_date: datetime | None = Field(
        default=None,
        sa_column=Column(
            "update_date",
            TIMESTAMP,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        ),
    )
