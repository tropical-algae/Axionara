from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.common.config import settings
from axionara.common.logging import logger
from axionara.core.db.models import *


def normalize_database_uri(database_uri: str) -> str:
    if database_uri.startswith("sqlite://"):
        return database_uri.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if database_uri.startswith("mysql+pymysql://"):
        return database_uri.replace("mysql+pymysql://", "mysql+asyncmy://", 1)
    return database_uri


engine_kwargs: dict = {
    "pool_pre_ping": settings.SQL_POOL_PRE_PING,
    "echo": settings.DEBUG,
}
normalized_database_uri = normalize_database_uri(settings.SQL_DATABASE_URI)
if not normalized_database_uri.startswith("sqlite"):
    engine_kwargs.update(
        pool_size=settings.SQL_POOL_SIZE,
        max_overflow=settings.SQL_MAX_OVERFLOW,
        pool_timeout=settings.SQL_POOL_TIMEOUT,
        pool_recycle=settings.SQL_POOL_RECYCLE,
    )

local_engine = create_async_engine(url=normalized_database_uri, **engine_kwargs)
async_session_factory = async_sessionmaker(
    bind=local_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def local_session() -> AsyncSession:
    return async_session_factory()


async def init_db_models() -> None:
    logger.info("Check SQL table structure and fix the missing.")
    async with local_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
