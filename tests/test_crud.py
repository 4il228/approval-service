import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import SAMPLE_REQUEST_BODY, make_auth_header


@pytest.mark.anyio
async def test_create_approval_request(client: AsyncClient, auth_header: dict):
    response = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=SAMPLE_REQUEST_BODY,
        headers=auth_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["workspace_id"] == "ws_1"
    assert data["source_type"] == "publication"
    assert data["source_id"] == "pub_123"
    assert data["title"] == "Instagram reel draft"
    assert data["description"] == "Needs final approval"
    assert data["reviewers"] == ["usr_1", "usr_2"]
    assert data["status"] == "PENDING"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_create_approval_request_minimal(client: AsyncClient, auth_header: dict):
    body = {
        "source_type": "scenario",
        "source_id": "scn_456",
        "title": "Quick scenario",
        "reviewer_user_ids": ["usr_3"],
    }
    response = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=body,
        headers=auth_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None
    assert data["source_type"] == "scenario"


@pytest.mark.anyio
async def test_create_and_get_approval_request(
    client: AsyncClient, auth_header: dict, sample_request_body: dict
):
    create_resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth_header,
    )
    assert create_resp.status_code == 201
    request_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}",
        headers=auth_header,
    )
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == request_id
    assert data["title"] == "Instagram reel draft"
    assert data["status"] == "PENDING"


@pytest.mark.anyio
async def test_list_approval_requests(
    client: AsyncClient, auth_header: dict, sample_request_body: dict
):
    for i in range(3):
        body = sample_request_body.copy()
        body["title"] = f"Request {i}"
        await client.post(
            "/api/v1/workspaces/ws_1/approval-requests",
            json=body,
            headers=auth_header,
        )

    response = await client.get(
        "/api/v1/workspaces/ws_1/approval-requests",
        headers=auth_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.anyio
async def test_get_nonexistent_request_returns_404(
    client: AsyncClient, auth_header: dict
):
    fake_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/v1/workspaces/ws_1/approval-requests/{fake_id}",
        headers=auth_header,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_request_from_different_workspace_returns_404(
    client: AsyncClient,
    auth_header: dict,
    auth_header_ws2: dict,
    sample_request_body: dict,
):
    create_resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth_header,
    )
    request_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/workspaces/ws_2/approval-requests/{request_id}",
        headers=auth_header_ws2,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_requests_empty_workspace(client: AsyncClient, auth_header: dict):
    response = await client.get(
        "/api/v1/workspaces/ws_empty/approval-requests",
        headers=make_auth_header(workspace_id="ws_empty"),
    )
    assert response.status_code == 200
    assert response.json() == []
