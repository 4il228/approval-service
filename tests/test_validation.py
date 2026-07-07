import pytest
from httpx import AsyncClient

from tests.conftest import SAMPLE_REQUEST_BODY, make_auth_header


@pytest.mark.anyio
async def test_missing_auth_header_returns_422(client: AsyncClient):
    response = await client.get("/api/v1/workspaces/ws_1/approval-requests")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_invalid_auth_header_returns_401(client: AsyncClient):
    response = await client.get(
        "/api/v1/workspaces/ws_1/approval-requests",
        headers={"X-Auth-Mock": "not-json"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_auth_header_missing_user_id_returns_401(client: AsyncClient):
    import json

    payload = {"workspace_id": "ws_1", "permissions": ["approval:read"]}
    response = await client.get(
        "/api/v1/workspaces/ws_1/approval-requests",
        headers={"X-Auth-Mock": json.dumps(payload)},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_auth_header_missing_workspace_id_returns_401(client: AsyncClient):
    import json

    payload = {"user_id": "usr_1", "permissions": ["approval:read"]}
    response = await client.get(
        "/api/v1/workspaces/ws_1/approval-requests",
        headers={"X-Auth-Mock": json.dumps(payload)},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_workspace_mismatch_returns_403(client: AsyncClient):
    auth = make_auth_header(workspace_id="ws_other")
    response = await client.get(
        "/api/v1/workspaces/ws_1/approval-requests",
        headers=auth,
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_missing_create_permission_returns_403(client: AsyncClient):
    auth = make_auth_header(permissions=["approval:read"])
    response = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=SAMPLE_REQUEST_BODY,
        headers=auth,
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_missing_read_permission_returns_403(client: AsyncClient):
    auth = make_auth_header(permissions=["approval:create"])
    response = await client.get(
        "/api/v1/workspaces/ws_1/approval-requests",
        headers=auth,
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_missing_decide_permission_returns_403(
    client: AsyncClient, sample_request_body: dict
):
    auth = make_auth_header(permissions=["approval:create", "approval:read"])
    create_resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth,
    )
    request_id = create_resp.json()["id"]

    approve_auth = make_auth_header(permissions=["approval:read"])
    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "test"},
        headers=approve_auth,
    )
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_missing_cancel_permission_returns_403(
    client: AsyncClient, sample_request_body: dict
):
    auth = make_auth_header(permissions=["approval:create", "approval:read"])
    create_resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth,
    )
    request_id = create_resp.json()["id"]

    cancel_auth = make_auth_header(permissions=["approval:read"])
    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={"reason": "test"},
        headers=cancel_auth,
    )
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_no_permissions_returns_403(client: AsyncClient):
    auth = make_auth_header(permissions=[])
    response = await client.get(
        "/api/v1/workspaces/ws_1/approval-requests",
        headers=auth,
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_invalid_source_type_returns_422(client: AsyncClient, auth_header: dict):
    body = SAMPLE_REQUEST_BODY.copy()
    body["source_type"] = "invalid_type"
    response = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=body,
        headers=auth_header,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_missing_required_fields_returns_422(
    client: AsyncClient, auth_header: dict
):
    response = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json={},
        headers=auth_header,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_approve_without_comment_returns_422(
    client: AsyncClient, sample_request_body: dict
):
    auth = make_auth_header()
    create_resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth,
    )
    request_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={},
        headers=auth,
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_reject_without_reason_returns_422(
    client: AsyncClient, sample_request_body: dict
):
    auth = make_auth_header()
    create_resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth,
    )
    request_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/reject",
        json={},
        headers=auth,
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_cancel_without_reason_returns_422(
    client: AsyncClient, sample_request_body: dict
):
    auth = make_auth_header()
    create_resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth,
    )
    request_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={},
        headers=auth,
    )
    assert resp.status_code == 422
