"""initial schema

Revision ID: 20260507_0001
Revises:
Create Date: 2026-05-07 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
from sqlmodel import SQLModel

from axionara.core.db import models

revision: str = "20260507_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SQLModel.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    SQLModel.metadata.drop_all(bind=op.get_bind())
