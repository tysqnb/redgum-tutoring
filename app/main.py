"""FastAPI application factory and module-level app instance."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401  (registers models on the metadata)
from app.config import settings
from app.db import Base, SessionLocal, engine
from app.routers import auth, availability, students, tutors, views
from app.seed import seed_demo


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    if settings.seed_demo:
        with SessionLocal() as db:
            seed_demo(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Redgum Tutoring", lifespan=lifespan)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(auth.router)
    app.include_router(students.router)
    app.include_router(tutors.router)
    app.include_router(availability.router)
    app.include_router(views.router)

    return app


app = create_app()
