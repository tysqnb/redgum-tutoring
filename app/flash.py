"""One-shot flash messages carried inside the signed session cookie."""

from fastapi import Request

from app.security import pending_payload


def flash(request: Request, message: str) -> None:
    """Queue a message for the next rendered page."""
    payload = pending_payload(request)
    payload.setdefault("flashes", []).append(message)


def take_flashes(request: Request) -> list[str]:
    """Pop and return any queued messages."""
    payload = pending_payload(request)
    return payload.pop("flashes", [])
