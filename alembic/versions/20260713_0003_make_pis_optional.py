"""Make PIS optional on pessoas

Revision ID: 20260713_0003
Revises: 20260707_0002
Create Date: 2026-07-13 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260713_0003"
down_revision: Union[str, None] = "20260707_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "pessoas",
        "pis",
        existing_type=sa.String(length=14),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "pessoas",
        "pis",
        existing_type=sa.String(length=14),
        nullable=False,
    )
