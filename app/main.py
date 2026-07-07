from fastapi import FastAPI

app = FastAPI(
    title="approval-service",
    description="Backend сервис согласования контента",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ok"}
