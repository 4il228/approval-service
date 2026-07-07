import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_idempotent_create_returns_same_request(
    client: AsyncClient, auth_header: dict, sample_request_body: dict
):
    idempotency_key = "idem_key_123"

    resp1 = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers={**auth_header, "Idempotency-Key": idempotency_key},
    )
    assert resp1.status_code == 201
    data1 = resp1.json()

    resp2 = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers={**auth_header, "Idempotency-Key": idempotency_key},
    )
    assert resp2.status_code == 201
    data2 = resp2.json()

    assert data1["id"] == data2["id"]
    assert data1["created_at"] == data2["created_at"]


@pytest.mark.anyio
async def test_different_idempotency_keys_create_different_requests(
    client: AsyncClient, auth_header: dict, sample_request_body: dict
):
    resp1 = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers={**auth_header, "Idempotency-Key": "key_1"},
    )
    resp2 = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers={**auth_header, "Idempotency-Key": "key_2"},
    )

    assert resp1.json()["id"] != resp2.json()["id"]


@pytest.mark.anyio
async def test_no_idempotency_key_always_creates_new(
    client: AsyncClient, auth_header: dict, sample_request_body: dict
):
    resp1 = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth_header,
    )
    resp2 = await client.post(
        "/api/v1/workspaces/ws_1/approval-requests",
        json=sample_request_body,
        headers=auth_header,
    )

    assert resp1.json()["id"] != resp2.json()["id"]
