"""Route dependencies: current user and role guards."""

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.db import OrmSession, get_db
from app.models import AppUser
from app.security import load_session_payload


def current_user(
    request: Request, db: OrmSession = Depends(get_db)
) -> AppUser | None:
    payload = load_session_payload(request)
    uid = payload.get("uid")
    if uid is None:
        return None
    return db.scalars(select(AppUser).where(AppUser.id == uid)).first()


def require_user(user: AppUser | None = Depends(current_user)) -> AppUser:
    if user is None:
        raise _redirect_login()
    return user


def require_admin(user: AppUser | None = Depends(current_user)) -> AppUser:
    if user is None:
        raise _redirect_login()
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access only")
    return user


def _redirect_login() -> HTTPException:
    return HTTPException(
        status_code=303,
        detail="Login required",
        headers={"Location": "/login"},
    )


def get_or_404(db: OrmSession, model, object_id: int, label: str):
    """Fetch one row by id or raise a plain 404."""
    obj = db.get(model, object_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return obj
