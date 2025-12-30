"""add avito_webhook_events

Revision ID: 20251228_add_webhook_events
Revises: <PUT_YOUR_CURRENT_HEAD_REVISION_HERE>
Create Date: 2025-12-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20251228_add_webhook_events"
down_revision = "49e51714d74d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "avito_webhook_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("avito_account_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=True),
        sa.Column("dedup_key", sa.String(length=128), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.UniqueConstraint("source", "dedup_key", name="uq_webhook_source_dedup"),
    )
    op.create_index("ix_webhook_received_at", "avito_webhook_events", ["received_at"])


def downgrade() -> None:
    op.drop_index("ix_webhook_received_at", table_name="avito_webhook_events")
    op.drop_table("avito_webhook_events")
