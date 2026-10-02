"""Application settings, read from REDGUM_* environment variables.

Every value has a safe development default so a clean checkout boots
without a .env file. Production deployments inject real values through
the container runtime (see docker-compose.yml).
"""

import os


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """Settings loaded once at import time."""

    def __init__(self) -> None:
        self.secret_key: str = os.getenv(
            "REDGUM_SECRET_KEY", "dev-secret-key-change-me"
        )
        self.database_url: str = os.getenv(
            "REDGUM_DATABASE_URL", "sqlite:///redgum.db"
        )
        self.cookie_secure: bool = _as_bool(
            os.getenv("REDGUM_COOKIE_SECURE"), False
        )
        self.seed_demo: bool = _as_bool(os.getenv("REDGUM_SEED"), True)


settings = Settings()
