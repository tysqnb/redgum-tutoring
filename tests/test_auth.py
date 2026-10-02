"""Authentication, session cookie and role separation."""

import pytest

from app.config import Settings
from app.models import AppUser
from app.security import (
    hash_password,
    verify_password,
)

ANONYMOUS_PATHS = [
    "/",
    "/students",
    "/students/new",
    "/students/1/edit",
    "/students/1/sessions",
    "/tutors",
    "/tutors/new",
    "/tutors/1/edit",
    "/tutors/1/availability",
    "/schedule",
    "/my-sessions",
]

ADMIN_ONLY_PATHS = [
    "/students",
    "/students/new",
    "/students/1/edit",
    "/students/1/sessions",
    "/tutors",
    "/tutors/new",
    "/tutors/1/edit",
    "/tutors/1/availability",
    "/schedule",
]


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Username" in response.text


def test_login_success_redirects_to_dashboard(admin_client):
    response = admin_client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.text


def test_login_page_redirects_when_already_signed_in(admin_client):
    response = admin_client.get("/login", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_dashboard_shows_counts(admin_client, make_student, tutor_record):
    make_student(name="Counted Student")
    response = admin_client.get("/")
    assert response.status_code == 200
    assert "Counted Student" not in response.text
    assert "Students on the roll" in response.text


def test_login_wrong_password_shows_error(client, session_factory):
    with session_factory() as db:
        db.add(
            AppUser(
                username="admin",
                password_hash=hash_password("password"),
                role="ADMIN",
            )
        )
        db.commit()
    response = client.post(
        "/login", data={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 400
    assert "Invalid username or password." in response.text


def test_login_unknown_user_shows_error(client):
    response = client.post(
        "/login", data={"username": "nobody", "password": "whatever"}
    )
    assert response.status_code == 400
    assert "Invalid username or password." in response.text


def test_login_blank_fields_shows_error(client):
    response = client.post("/login", data={"username": "", "password": ""})
    assert response.status_code == 400
    assert "Invalid username or password." in response.text


def test_logout_clears_session(admin_client):
    response = admin_client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert admin_client.get("/", follow_redirects=False).status_code == 303


@pytest.mark.parametrize("path", ANONYMOUS_PATHS)
def test_anonymous_users_are_redirected(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


@pytest.mark.parametrize("path", ADMIN_ONLY_PATHS)
def test_tutor_is_forbidden_from_admin_pages(tutor_client, path):
    assert tutor_client.get(path).status_code == 403


def test_password_hash_roundtrip():
    stored = hash_password("redgum123")
    assert verify_password("redgum123", stored)


def test_password_hash_is_salted():
    first = hash_password("same")
    second = hash_password("same")
    assert first != second


def test_verify_wrong_password_is_false():
    stored = hash_password("right")
    assert not verify_password("wrong", stored)


def test_verify_malformed_hash_is_false():
    assert not verify_password("anything", "not-a-valid-hash")


def test_session_cookie_is_http_only(client, session_factory):
    with session_factory() as db:
        db.add(
            AppUser(
                username="admin",
                password_hash=hash_password("password"),
                role="ADMIN",
            )
        )
        db.commit()
    response = client.post(
        "/login",
        data={"username": "admin", "password": "password"},
        follow_redirects=False,
    )
    set_cookie = response.headers["set-cookie"].lower()
    assert "httponly" in set_cookie


def test_session_cookie_uses_lax_samesite(client, session_factory):
    with session_factory() as db:
        db.add(
            AppUser(
                username="admin",
                password_hash=hash_password("password"),
                role="ADMIN",
            )
        )
        db.commit()
    response = client.post(
        "/login",
        data={"username": "admin", "password": "password"},
        follow_redirects=False,
    )
    set_cookie = response.headers["set-cookie"].lower()
    assert "samesite=lax" in set_cookie


def test_tampered_session_cookie_is_rejected(admin_client):
    admin_client.cookies.set("redgum_session", "tampered-value")
    response = admin_client.get("/", follow_redirects=False)
    assert response.status_code == 303


def test_config_reads_env_override(monkeypatch):
    monkeypatch.setenv("REDGUM_COOKIE_SECURE", "true")
    settings = Settings()
    assert settings.cookie_secure is True


def test_config_uses_safe_defaults(monkeypatch):
    monkeypatch.delenv("REDGUM_COOKIE_SECURE", raising=False)
    settings = Settings()
    assert settings.cookie_secure is False
    assert settings.secret_key
