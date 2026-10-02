"""Password hashing and signed session-cookie helpers."""

import hashlib
import json
import os

from fastapi import Request, Response
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

from app.config import settings

SESSION_COOKIE = "redgum_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30


def hash_password(password: str) -> str:
    """Hash a password with scrypt and a per-password random salt."""
    salt = os.urandom(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=64,
    )
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Check a password against a stored salt$digest value."""
    try:
        salt_hex, digest_hex = stored.split("$", 1)
    except ValueError:
        return False
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt_hex),
        n=2**14,
        r=8,
        p=1,
        dklen=64,
    )
    return digest.hex() == digest_hex


def _signer() -> TimestampSigner:
    return TimestampSigner(settings.secret_key, salt="redgum-session")


def load_session_payload(request: Request) -> dict:
    """Decode and verify the session cookie, returning a dict payload."""
    cookie = request.cookies.get(SESSION_COOKIE, "")
    if not cookie:
        return {}
    try:
        raw = _signer().unsign(cookie, max_age=SESSION_MAX_AGE).decode("utf-8")
        payload = json.loads(raw)
    except (BadSignature, SignatureExpired, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def write_session_cookie(response: Response, payload: dict) -> None:
    """Sign a payload and store it as the session cookie."""
    if payload.get("uid") is None:
        response.delete_cookie(SESSION_COOKIE)
        return
    raw = json.dumps(payload, separators=(",", ":"))
    token = _signer().sign(raw.encode("utf-8")).decode("utf-8")
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


def pending_payload(request: Request) -> dict:
    """Return the mutable payload staged for the outgoing response."""
    if not hasattr(request.state, "session_payload"):
        request.state.session_payload = load_session_payload(request)
    return request.state.session_payload
