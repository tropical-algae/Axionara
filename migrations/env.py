from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from axionara.common.config import settings
from axionara.core.db import models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def normalize_database_uri(database_uri: str) -> str:
    if database_uri.startswith("sqlite+aiosqlite://"):
        return database_uri.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if database_uri.startswith("mysql+asyncmy://"):
        return database_uri.replace("mysql+asyncmy://", "mysql+pymysql://", 1)
    return database_uri


def run_migrations_offline() -> None:
    url = normalize_database_uri(settings.SQL_DATABASE_URI)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = normalize_database_uri(settings.SQL_DATABASE_URI)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
