"""Login and logout routes."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.db import OrmSession, get_db
from app.dependencies import current_user
from app.flash import flash
from app.models import AppUser
from app.security import load_session_payload, verify_password, write_session_cookie
from app.templating import render

router = APIRouter()


@router.get("/login")
def login_form(
    request: Request, user: AppUser | None = Depends(current_user)
):
    if user is not None:
        response = RedirectResponse("/", status_code=303)
        write_session_cookie(response, load_session_payload(request))
        return response
    return render(request, "login.html", {"username": ""})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    db: OrmSession = Depends(get_db),
):
    username = username.strip()
    user = db.scalars(
        select(AppUser).where(AppUser.username == username)
    ).first()
    if user is None or not verify_password(password, user.password_hash):
        flash(request, "Invalid username or password.")
        return render(
            request,
            "login.html",
            {"username": username},
            status_code=400,
        )
    response = RedirectResponse("/", status_code=303)
    write_session_cookie(
        response, {"uid": user.id, "flashes": [f"Welcome back, {user.username}."]}
    )
    return response


@router.post("/logout")
def logout(request: Request):
    response = RedirectResponse("/login", status_code=303)
    write_session_cookie(response, {"uid": None, "flashes": []})
    return response
