from sqlmodel import Session, SQLModel, create_engine

from axionara.common.config import settings
from axionara.common.logging import logger
from axionara.core.db.models import *


def normalize_database_uri(database_uri: str) -> str:
    if database_uri.startswith("sqlite+aiosqlite://"):
        return database_uri.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if database_uri.startswith("mysql+asyncmy://"):
        return database_uri.replace("mysql+asyncmy://", "mysql+pymysql://", 1)
    return database_uri


engine_kwargs: dict = {
    "pool_pre_ping": settings.SQL_POOL_PRE_PING,
    "echo": settings.DEBUG,
}
normalized_database_uri = normalize_database_uri(settings.SQL_DATABASE_URI)
if not normalized_database_uri.startswith("sqlite://"):
    engine_kwargs.update(
        pool_size=settings.SQL_POOL_SIZE,
        max_overflow=settings.SQL_MAX_OVERFLOW,
        pool_timeout=settings.SQL_POOL_TIMEOUT,
        pool_recycle=settings.SQL_POOL_RECYCLE,
    )

local_engine = create_engine(url=normalized_database_uri, **engine_kwargs)


def local_session() -> Session:
    return Session(local_engine)


def init_db_models():
    logger.info("Check SQL table structure and fix the missing.")
    SQLModel.metadata.create_all(local_engine)
