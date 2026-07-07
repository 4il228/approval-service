import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class SourceType(StrEnum):
    PUBLICATION = "publication"
    SCENARIO = "scenario"
    EDIT = "edit"
    EXTERNAL = "external"


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"


class CreateApprovalRequest(BaseModel):
    source_type: SourceType
    source_id: str
    title: str
    description: str | None = None
    reviewer_user_ids: list[str]


class ApprovalRequestResponse(BaseModel):
    id: uuid.UUID
    workspace_id: str
    source_type: SourceType
    source_id: str
    title: str
    description: str | None
    reviewers: list[str]
    status: ApprovalStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    comment: str


class RejectRequest(BaseModel):
    reason: str


class CancelRequest(BaseModel):
    reason: str


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    actor_user_id: str
    action: str
    payload: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
