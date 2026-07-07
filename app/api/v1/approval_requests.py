import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    AuthContext,
    get_auth_context,
    require_permission,
    validate_workspace_access,
)
from app.database import get_session
from app.schemas.approval_requests import (
    ApprovalRequestResponse,
    ApproveRequest,
    CancelRequest,
    CreateApprovalRequest,
    RejectRequest,
)
from app.services.approval_requests import (
    approve_request,
    cancel_request,
    create_approval_request,
    get_approval_request,
    list_approval_requests,
    reject_request,
)

router = APIRouter()


@router.post(
    "/api/v1/workspaces/{workspace_id}/approval-requests",
    response_model=ApprovalRequestResponse,
    status_code=201,
)
async def create_request(
    workspace_id: str,
    body: CreateApprovalRequest,
    auth: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    validate_workspace_access(auth, workspace_id)
    require_permission(auth, "approval:create")

    request = await create_approval_request(
        session=session,
        workspace_id=workspace_id,
        source_type=body.source_type.value,
        source_id=body.source_id,
        title=body.title,
        description=body.description,
        reviewer_user_ids=body.reviewer_user_ids,
        actor_user_id=auth.user_id,
        idempotency_key=idempotency_key,
    )
    return request


@router.get(
    "/api/v1/workspaces/{workspace_id}/approval-requests",
    response_model=list[ApprovalRequestResponse],
)
async def list_requests(
    workspace_id: str,
    auth: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
):
    validate_workspace_access(auth, workspace_id)
    require_permission(auth, "approval:read")

    return await list_approval_requests(session, workspace_id)


@router.get(
    "/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}",
    response_model=ApprovalRequestResponse,
)
async def get_request(
    workspace_id: str,
    request_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
):
    validate_workspace_access(auth, workspace_id)
    require_permission(auth, "approval:read")

    request = await get_approval_request(session, workspace_id, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return request


@router.post(
    "/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/approve",
    response_model=ApprovalRequestResponse,
)
async def approve(
    workspace_id: str,
    request_id: uuid.UUID,
    body: ApproveRequest,
    auth: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
):
    validate_workspace_access(auth, workspace_id)
    require_permission(auth, "approval:decide")

    try:
        request = await approve_request(
            session=session,
            workspace_id=workspace_id,
            request_id=request_id,
            actor_user_id=auth.user_id,
            comment=body.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return request


@router.post(
    "/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/reject",
    response_model=ApprovalRequestResponse,
)
async def reject(
    workspace_id: str,
    request_id: uuid.UUID,
    body: RejectRequest,
    auth: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
):
    validate_workspace_access(auth, workspace_id)
    require_permission(auth, "approval:decide")

    try:
        request = await reject_request(
            session=session,
            workspace_id=workspace_id,
            request_id=request_id,
            actor_user_id=auth.user_id,
            reason=body.reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return request


@router.post(
    "/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/cancel",
    response_model=ApprovalRequestResponse,
)
async def cancel(
    workspace_id: str,
    request_id: uuid.UUID,
    body: CancelRequest,
    auth: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
):
    validate_workspace_access(auth, workspace_id)
    require_permission(auth, "approval:cancel")

    try:
        request = await cancel_request(
            session=session,
            workspace_id=workspace_id,
            request_id=request_id,
            actor_user_id=auth.user_id,
            reason=body.reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return request
