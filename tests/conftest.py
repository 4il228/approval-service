import json

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_session
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as sess:
        yield sess
        await sess.rollback()


@pytest_asyncio.fixture
async def client(engine):
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_session():
        async with async_session() as sess:
            yield sess

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


def make_auth_header(
    user_id: str = "usr_1",
    workspace_id: str = "ws_1",
    permissions: list[str] | None = None,
) -> dict[str, str]:
    if permissions is None:
        permissions = [
            "approval:read",
            "approval:create",
            "approval:decide",
            "approval:cancel",
        ]
    payload = {
        "user_id": user_id,
        "workspace_id": workspace_id,
        "permissions": permissions,
    }
    return {"X-Auth-Mock": json.dumps(payload)}


@pytest.fixture
def auth_header():
    return make_auth_header()


@pytest.fixture
def auth_header_ws2():
    return make_auth_header(workspace_id="ws_2", user_id="usr_2")


@pytest.fixture
def read_only_auth():
    return make_auth_header(permissions=["approval:read"])


@pytest.fixture
def create_only_auth():
    return make_auth_header(permissions=["approval:create"])


@pytest.fixture
def decide_only_auth():
    return make_auth_header(permissions=["approval:decide"])


@pytest.fixture
def cancel_only_auth():
    return make_auth_header(permissions=["approval:cancel"])


@pytest.fixture
def no_permissions_auth():
    return make_auth_header(permissions=[])


SAMPLE_REQUEST_BODY = {
    "source_type": "publication",
    "source_id": "pub_123",
    "title": "Instagram reel draft",
    "description": "Needs final approval",
    "reviewer_user_ids": ["usr_1", "usr_2"],
}


@pytest.fixture
def sample_request_body():
    return SAMPLE_REQUEST_BODY.copy()
