import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApprovalRequest, AuditLog


async def get_request_by_idempotency_key(
    session: AsyncSession, idempotency_key: str
) -> ApprovalRequest | None:
    result = await session.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.idempotency_key == idempotency_key
        )
    )
    return result.scalar_one_or_none()


async def create_approval_request(
    session: AsyncSession,
    workspace_id: str,
    source_type: str,
    source_id: str,
    title: str,
    description: str | None,
    reviewer_user_ids: list[str],
    actor_user_id: str,
    idempotency_key: str | None = None,
) -> ApprovalRequest:
    if idempotency_key:
        existing = await get_request_by_idempotency_key(session, idempotency_key)
        if existing:
            return existing

    request = ApprovalRequest(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        title=title,
        description=description,
        reviewers=reviewer_user_ids,
        status="PENDING",
        idempotency_key=idempotency_key,
    )
    session.add(request)
    await session.flush()

    audit = AuditLog(
        request_id=request.id,
        actor_user_id=actor_user_id,
        action="CREATED",
        payload={
            "source_type": source_type,
            "source_id": source_id,
            "title": title,
            "description": description,
            "reviewers": reviewer_user_ids,
        },
    )
    session.add(audit)
    await session.commit()
    await session.refresh(request)
    return request


async def list_approval_requests(
    session: AsyncSession, workspace_id: str
) -> list[ApprovalRequest]:
    result = await session.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.workspace_id == workspace_id)
        .order_by(ApprovalRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def get_approval_request(
    session: AsyncSession, workspace_id: str, request_id: uuid.UUID
) -> ApprovalRequest | None:
    result = await session.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.id == request_id,
            ApprovalRequest.workspace_id == workspace_id,
        )
    )
    return result.scalar_one_or_none()


async def approve_request(
    session: AsyncSession,
    workspace_id: str,
    request_id: uuid.UUID,
    actor_user_id: str,
    comment: str,
) -> ApprovalRequest:
    request = await get_approval_request(session, workspace_id, request_id)
    if not request:
        raise ValueError("Approval request not found")
    if request.status != "PENDING":
        raise ValueError(f"Cannot approve request in {request.status} status")

    request.status = "APPROVED"
    await session.flush()

    audit = AuditLog(
        request_id=request.id,
        actor_user_id=actor_user_id,
        action="APPROVED",
        payload={"comment": comment},
    )
    session.add(audit)
    await session.commit()
    await session.refresh(request)
    return request


async def reject_request(
    session: AsyncSession,
    workspace_id: str,
    request_id: uuid.UUID,
    actor_user_id: str,
    reason: str,
) -> ApprovalRequest:
    request = await get_approval_request(session, workspace_id, request_id)
    if not request:
        raise ValueError("Approval request not found")
    if request.status != "PENDING":
        raise ValueError(f"Cannot reject request in {request.status} status")

    request.status = "REJECTED"
    await session.flush()

    audit = AuditLog(
        request_id=request.id,
        actor_user_id=actor_user_id,
        action="REJECTED",
        payload={"reason": reason},
    )
    session.add(audit)
    await session.commit()
    await session.refresh(request)
    return request


async def cancel_request(
    session: AsyncSession,
    workspace_id: str,
    request_id: uuid.UUID,
    actor_user_id: str,
    reason: str,
) -> ApprovalRequest:
    request = await get_approval_request(session, workspace_id, request_id)
    if not request:
        raise ValueError("Approval request not found")
    if request.status != "PENDING":
        raise ValueError(f"Cannot cancel request in {request.status} status")

    request.status = "CANCELED"
    await session.flush()

    audit = AuditLog(
        request_id=request.id,
        actor_user_id=actor_user_id,
        action="CANCELED",
        payload={"reason": reason},
    )
    session.add(audit)
    await session.commit()
    await session.refresh(request)
    return request
