"""Shared fixtures: an in-memory database and logged-in test clients."""

import itertools
import os
from datetime import date, time, timedelta

# Read before importing the app so the file database is never touched by tests.
os.environ["REDGUM_SEED"] = "0"
os.environ["REDGUM_DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import create_app
from app.models import AppUser, AvailabilityWindow, Session, Student, Tutor
from app.security import hash_password


@pytest.fixture()
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    yield session
    session.close()


@pytest.fixture()
def app(engine, session_factory):
    application = create_app()

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    application.dependency_overrides[get_db] = override_get_db
    yield application
    application.dependency_overrides.clear()


@pytest.fixture()
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_client(app, session_factory):
    with TestClient(app) as test_client:
        with session_factory() as db:
            db.add(
                AppUser(
                    username="admin",
                    password_hash=hash_password("password"),
                    role="ADMIN",
                )
            )
            db.commit()
        response = test_client.post(
            "/login",
            data={"username": "admin", "password": "password"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        yield test_client


@pytest.fixture()
def tutor_client(app, session_factory, tutor_record):
    with TestClient(app) as test_client:
        with session_factory() as db:
            db.add(
                AppUser(
                    username="tomas",
                    password_hash=hash_password("password"),
                    role="USER",
                    tutor_id=tutor_record.id,
                )
            )
            db.commit()
        response = test_client.post(
            "/login",
            data={"username": "tomas", "password": "password"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        yield test_client


@pytest.fixture()
def make_student(db_session):
    counter = itertools.count(1)

    def _make(**overrides):
        number = next(counter)
        defaults = {
            "name": f"Student {number}",
            "school": "Redgum High",
            "year_level": "10",
            "contact_name": f"Contact {number}",
            "contact_phone": f"0400 000 {number:03d}",
            "contact_email": f"contact{number}@example.com",
            "subjects": "Maths",
        }
        defaults.update(overrides)
        student = Student(**defaults)
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)
        return student

    return _make


@pytest.fixture()
def tutor_record(db_session):
    tutor = Tutor(
        name="Tomás Ferreira", phone="0400 111 222", subjects="Physics, Maths"
    )
    db_session.add(tutor)
    db_session.commit()
    windows = [
        AvailabilityWindow(
            tutor_id=tutor.id,
            day_of_week="TUESDAY",
            start_time=time(15, 30),
            end_time=time(19, 0),
        ),
        AvailabilityWindow(
            tutor_id=tutor.id,
            day_of_week="THURSDAY",
            start_time=time(16, 0),
            end_time=time(18, 30),
        ),
    ]
    db_session.add_all(windows)
    db_session.commit()
    db_session.refresh(tutor)
    return tutor


@pytest.fixture()
def make_session(db_session, make_student, tutor_record):
    counter = itertools.count(1)

    def _make(**overrides):
        number = next(counter)
        student = make_student(name=f"Session Student {number}")
        defaults = {
            "student_id": student.id,
            "tutor_id": tutor_record.id,
            "date": date.today() + timedelta(days=number),
            "start_time": time(16, 0),
            "duration_minutes": 60,
            "subject": "Physics",
            "notes": None,
            "status": "BOOKED",
        }
        defaults.update(overrides)
        session = Session(**defaults)
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        return session

    return _make
