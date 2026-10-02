"""Database engine, session factory and FastAPI dependency."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base shared by every model."""


def _connect_args(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    settings.database_url, connect_args=_connect_args(settings.database_url)
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Short alias used across services and routers for readability.
OrmSession = Session


def get_db() -> Iterator[Session]:
    """Yield one request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
