import pytest
from httpx import AsyncClient

from tests.conftest import SAMPLE_REQUEST_BODY


async def _create_request(client: AsyncClient, auth_header: dict) -> str:
    resp = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=SAMPLE_REQUEST_BODY,
        headers=auth_header,
    )
    return resp.json()["id"]


@pytest.mark.anyio
async def test_approve_pending_request(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "Looks good"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "APPROVED"


@pytest.mark.anyio
async def test_reject_pending_request(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/reject",
        json={"reason": "Brand tone is wrong"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "REJECTED"


@pytest.mark.anyio
async def test_cancel_pending_request(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={"reason": "Draft was removed"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELED"


@pytest.mark.anyio
async def test_cannot_double_approve(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "First approval"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "Second approval"},
        headers=auth_header,
    )
    assert resp.status_code == 400
    assert "APPROVED" in resp.json()["detail"]


@pytest.mark.anyio
async def test_cannot_reject_approved(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "Approved"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/reject",
        json={"reason": "Try to reject"},
        headers=auth_header,
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_cannot_cancel_approved(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "Approved"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={"reason": "Try to cancel"},
        headers=auth_header,
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_cannot_approve_rejected(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/reject",
        json={"reason": "Rejected"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "Try to approve"},
        headers=auth_header,
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_cannot_double_reject(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/reject",
        json={"reason": "First rejection"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/reject",
        json={"reason": "Second rejection"},
        headers=auth_header,
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_cannot_approve_canceled(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={"reason": "Canceled"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/approve",
        json={"comment": "Try to approve"},
        headers=auth_header,
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_cannot_double_cancel(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={"reason": "First cancel"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={"reason": "Second cancel"},
        headers=auth_header,
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_cannot_reject_canceled(client: AsyncClient, auth_header: dict):
    request_id = await _create_request(client, auth_header)

    await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/cancel",
        json={"reason": "Canceled"},
        headers=auth_header,
    )

    resp = await client.post(
        f"/api/v1/workspaces/ws_1/approval-requests/{request_id}/reject",
        json={"reason": "Try to reject"},
        headers=auth_header,
    )
    assert resp.status_code == 400
