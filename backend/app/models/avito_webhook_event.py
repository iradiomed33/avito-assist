from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint, Index
from sqlalchemy.sql import func

from app.db.base import Base


class AvitoWebhookEvent(Base):
    __tablename__ = "avito_webhook_events"

    id = Column(Integer, primary_key=True, index=True)

    # можно расширить под multi-project позже
    project_id = Column(Integer, nullable=True)
    avito_account_id = Column(Integer, nullable=True)

    source = Column(String(32), nullable=False, default="avito")
    event_type = Column(String(64), nullable=True)

    # защита от дублей (если Avito будет ретраить)
    dedup_key = Column(String(128), nullable=False)

    payload_json = Column(Text, nullable=False)

    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(32), nullable=False, default="new")
    error = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "dedup_key", name="uq_webhook_source_dedup"),
        Index("ix_webhook_received_at", "received_at"),
    )
