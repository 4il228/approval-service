import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./approval.db",
    )
    db_echo: bool = False


settings = Settings()
