from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.approval_requests import router as approval_router
from app.core.logging import setup_log_masking
from app.database import engine

setup_log_masking()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title="approval-service",
    description="Backend сервис согласования контента",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(approval_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ok"}
