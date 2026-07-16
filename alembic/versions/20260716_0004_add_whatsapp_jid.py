"""Add whatsapp_jid to pessoas

Revision ID: 20260716_0004
Revises: 20260713_0003
Create Date: 2026-07-16 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260716_0004"
down_revision: Union[str, None] = "20260713_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "pessoas",
        sa.Column("whatsapp_jid", sa.String(length=80), nullable=True),
    )
    op.create_index(
        "ix_pessoas_whatsapp_jid",
        "pessoas",
        ["whatsapp_jid"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pessoas_whatsapp_jid", table_name="pessoas")
    op.drop_column("pessoas", "whatsapp_jid")
