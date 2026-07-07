import pytest
from httpx import AsyncClient

from tests.conftest import SAMPLE_REQUEST_BODY, make_auth_header


@pytest.mark.anyio
async def test_workspace_a_cannot_see_workspace_b_requests(
    client: AsyncClient, sample_request_body: dict
):
    auth_a = make_auth_header(workspace_id="ws_a", user_id="usr_a")
    auth_b = make_auth_header(workspace_id="ws_b", user_id="usr_b")

    create_resp = await client.post(
        "/api/v1/workspaces/ws_a/approval-requests",
        json=sample_request_body,
        headers=auth_a,
    )
    assert create_resp.status_code == 201

    list_resp = await client.get(
        "/api/v1/workspaces/ws_b/approval-requests",
        headers=auth_b,
    )
    assert list_resp.status_code == 200
    assert list_resp.json() == []


@pytest.mark.anyio
async def test_workspace_cannot_access_other_workspace_request_by_id(
    client: AsyncClient, sample_request_body: dict
):
    auth_a = make_auth_header(workspace_id="ws_a", user_id="usr_a")
    auth_b = make_auth_header(workspace_id="ws_b", user_id="usr_b")

    create_resp = await client.post(
        "/api/v1/workspaces/ws_a/approval-requests",
        json=sample_request_body,
        headers=auth_a,
    )
    request_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/v1/workspaces/ws_b/approval-requests/{request_id}",
        headers=auth_b,
    )
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_workspace_cannot_approve_other_workspace_request(
    client: AsyncClient, sample_request_body: dict
):
    auth_a = make_auth_header(workspace_id="ws_a", user_id="usr_a")
    auth_b = make_auth_header(workspace_id="ws_b", user_id="usr_b")

    create_resp = await client.post(
        "/api/v1/workspaces/ws_a/approval-requests",
        json=sample_request_body,
        headers=auth_a,
    )
    request_id = create_resp.json()["id"]

    approve_resp = await client.post(
        f"/api/v1/workspaces/ws_b/approval-requests/{request_id}/approve",
        json={"comment": "Approved"},
        headers=auth_b,
    )
    assert approve_resp.status_code == 400


@pytest.mark.anyio
async def test_each_workspace_has_separate_data(client: AsyncClient):
    auth_a = make_auth_header(workspace_id="ws_a", user_id="usr_a")
    auth_b = make_auth_header(workspace_id="ws_b", user_id="usr_b")

    body_a = SAMPLE_REQUEST_BODY.copy()
    body_a["title"] = "Request for A"
    await client.post(
        "/api/v1/workspaces/ws_a/approval-requests",
        json=body_a,
        headers=auth_a,
    )

    body_b = SAMPLE_REQUEST_BODY.copy()
    body_b["title"] = "Request for B"
    await client.post(
        "/api/v1/workspaces/ws_b/approval-requests",
        json=body_b,
        headers=auth_b,
    )

    list_a = await client.get(
        "/api/v1/workspaces/ws_a/approval-requests", headers=auth_a
    )
    list_b = await client.get(
        "/api/v1/workspaces/ws_b/approval-requests", headers=auth_b
    )

    assert len(list_a.json()) == 1
    assert list_a.json()[0]["title"] == "Request for A"
    assert len(list_b.json()) == 1
    assert list_b.json()[0]["title"] == "Request for B"
