import json
import logging
from dataclasses import dataclass

from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    workspace_id: str
    permissions: list[str]


def parse_auth_header(x_auth_mock: str) -> AuthContext:
    try:
        data = json.loads(x_auth_mock)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid auth header format",
        )

    user_id = data.get("user_id")
    workspace_id = data.get("workspace_id")
    permissions = data.get("permissions", [])

    if not user_id or not workspace_id:
        raise HTTPException(
            status_code=401,
            detail="Missing user_id or workspace_id in auth header",
        )

    return AuthContext(
        user_id=user_id,
        workspace_id=workspace_id,
        permissions=permissions,
    )


def require_permission(auth: AuthContext, permission: str) -> None:
    if permission not in auth.permissions:
        logger.warning(
            "Permission denied: user=%s missing=%s",
            auth.user_id,
            permission,
        )
        raise HTTPException(
            status_code=403,
            detail=f"Missing required permission: {permission}",
        )


def validate_workspace_access(auth: AuthContext, workspace_id: str) -> None:
    if auth.workspace_id != workspace_id:
        logger.warning(
            "Workspace access denied: user=%s requested=%s actual=%s",
            auth.user_id,
            workspace_id,
            auth.workspace_id,
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied: workspace mismatch",
        )


async def get_auth_context(
    x_auth_mock: str = Header(..., alias="X-Auth-Mock"),
) -> AuthContext:
    return parse_auth_header(x_auth_mock)
