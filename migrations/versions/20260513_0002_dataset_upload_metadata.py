"""add dataset upload metadata

Revision ID: 20260513_0002
Revises: 20260507_0001
Create Date: 2026-05-13 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260513_0002"
down_revision: str | None = "20260507_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "dataset_asset", sa.Column("category", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "dataset_asset",
        sa.Column("source_organization", sa.String(length=128), nullable=True),
    )
    op.add_column("dataset_asset", sa.Column("coverage_start", sa.Date(), nullable=True))
    op.add_column("dataset_asset", sa.Column("coverage_end", sa.Date(), nullable=True))
    op.add_column(
        "dataset_asset",
        sa.Column("update_frequency", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "dataset_asset",
        sa.Column("sensitivity_level", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "dataset_asset",
        sa.Column("intended_visibility", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "dataset_asset", sa.Column("access_policy", sa.String(length=32), nullable=True)
    )
    op.add_column(
        "dataset_asset", sa.Column("usage_restrictions", sa.Text(), nullable=True)
    )
    op.add_column(
        "dataset_asset", sa.Column("contact_name", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "dataset_asset", sa.Column("contact_email", sa.String(length=128), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("dataset_asset", "contact_email")
    op.drop_column("dataset_asset", "contact_name")
    op.drop_column("dataset_asset", "usage_restrictions")
    op.drop_column("dataset_asset", "access_policy")
    op.drop_column("dataset_asset", "intended_visibility")
    op.drop_column("dataset_asset", "sensitivity_level")
    op.drop_column("dataset_asset", "update_frequency")
    op.drop_column("dataset_asset", "coverage_end")
    op.drop_column("dataset_asset", "coverage_start")
    op.drop_column("dataset_asset", "source_organization")
    op.drop_column("dataset_asset", "category")
