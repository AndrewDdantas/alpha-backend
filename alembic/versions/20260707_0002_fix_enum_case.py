"""fix enum case to lowercase

Revision ID: 20260707_0002
Revises: 20260626_0001
Create Date: 2026-07-07 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260707_0002"
down_revision: Union[str, None] = "20260626_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ENUM_RENAMES = [
    ("tipopessoa", [
        ("COLABORADOR", "colaborador"),
        ("SUPERVISOR", "supervisor"),
        ("ADMIN", "admin"),
    ]),
    ("statusdiaria", [
        ("ABERTA", "aberta"),
        ("FECHADA", "fechada"),
        ("EM_ANDAMENTO", "em_andamento"),
        ("CONCLUIDA", "concluida"),
        ("CANCELADA", "cancelada"),
    ]),
    ("statusinscricao", [
        ("PENDENTE", "pendente"),
        ("CONFIRMADA", "confirmada"),
        ("CANCELADA", "cancelada"),
        ("REJEITADA", "rejeitada"),
        ("CONCLUIDA", "concluida"),
        ("FALTA", "falta"),
    ]),
]


def _rename_enum_value(conn, enum_name: str, old_value: str, new_value: str) -> None:
    row = conn.execute(
        sa.text(
            "SELECT 1 FROM pg_enum e "
            "JOIN pg_type t ON e.enumtypid = t.oid "
            "WHERE t.typname = :enum_name AND e.enumlabel = :old_value"
        ),
        {"enum_name": enum_name, "old_value": old_value},
    ).fetchone()

    if row:
        conn.execute(
            sa.text(f"ALTER TYPE {enum_name} RENAME VALUE '{old_value}' TO '{new_value}'")
        )


def upgrade() -> None:
    conn = op.get_bind()

    for enum_name, renames in ENUM_RENAMES:
        for old_value, new_value in renames:
            _rename_enum_value(conn, enum_name, old_value, new_value)


def downgrade() -> None:
    conn = op.get_bind()

    for enum_name, renames in ENUM_RENAMES:
        for old_value, new_value in renames:
            _rename_enum_value(conn, enum_name, new_value, old_value)
