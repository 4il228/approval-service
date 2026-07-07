import json
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, TypeDecorator, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JSONEncodedText(TypeDecorator):
    """Store JSON as Text in SQLite."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


class UUIDType(TypeDecorator):
    """Store UUID as CHAR(36) in SQLite."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=generate_uuid
    )
    workspace_id: Mapped[str] = mapped_column(String(255), index=True)
    source_type: Mapped[str] = mapped_column(String(50))
    source_id: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewers: Mapped[list] = mapped_column(JSONEncodedText(), default=list)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_approval_requests_workspace_status", "workspace_id", "status"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=generate_uuid
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("approval_requests.id", ondelete="CASCADE")
    )
    actor_user_id: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict | None] = mapped_column(JSONEncodedText(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    request: Mapped["ApprovalRequest"] = relationship(back_populates="audit_logs")
