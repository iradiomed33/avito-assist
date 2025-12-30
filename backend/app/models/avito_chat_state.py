from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.base import Base


class AvitoChatState(Base):
    __tablename__ = "avito_chat_state"

    id = Column(Integer, primary_key=True)
    avito_account_id = Column(Integer, ForeignKey("avito_accounts.id"), nullable=False, index=True)

    chat_id = Column(String, nullable=False, index=True)
    last_inbound_message_id = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("avito_account_id", "chat_id", name="uq_avito_chat_state_account_chat"),
    )
