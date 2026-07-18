"""Create persistent scan history.

Revision ID: 20260718_0001
Revises:
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260718_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("input_target", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(length=253), nullable=False),
        sa.Column("profile", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("stage", sa.String(length=160), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.String(length=16), nullable=True),
        sa.Column("confidence", sa.String(length=16), nullable=True),
        sa.Column("coverage_percent", sa.Float(), nullable=True),
        sa.Column("ruleset_version", sa.String(length=24), nullable=True),
        sa.Column("options_json", sa.JSON(), nullable=False),
        sa.Column("report_json", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scans_created_at", "scans", ["created_at"])
    op.create_index("ix_scans_domain", "scans", ["domain"])
    op.create_index("ix_scans_profile", "scans", ["profile"])
    op.create_index("ix_scans_risk_level", "scans", ["risk_level"])
    op.create_index("ix_scans_status", "scans", ["status"])


def downgrade() -> None:
    op.drop_index("ix_scans_status", table_name="scans")
    op.drop_index("ix_scans_risk_level", table_name="scans")
    op.drop_index("ix_scans_profile", table_name="scans")
    op.drop_index("ix_scans_domain", table_name="scans")
    op.drop_index("ix_scans_created_at", table_name="scans")
    op.drop_table("scans")
