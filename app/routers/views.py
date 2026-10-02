"""Dashboard, schedule and tutor's own session views."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select

from app.db import OrmSession, get_db
from app.dependencies import require_admin, require_user
from app.models import AppUser, Session, Student, Tutor
from app.services import schedule as schedule_service
from app.templating import render

router = APIRouter()


@router.get("/")
def dashboard(
    request: Request,
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_user),
):
    student_count = db.scalar(select(func.count()).select_from(Student)) or 0
    tutor_count = db.scalar(select(func.count()).select_from(Tutor)) or 0
    this_week = schedule_service.week_start(date.today())
    next_week = this_week + timedelta(days=6)
    session_count = len(
        schedule_service.sessions_between(db, this_week, next_week)
    )
    return render(
        request,
        "dashboard.html",
        {
            "user": user,
            "student_count": student_count,
            "tutor_count": tutor_count,
            "session_count": session_count,
        },
    )


@router.get("/schedule")
def schedule_view(
    request: Request,
    view: str = "week",
    date_str: str = "",
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    view = view if view in {"day", "week"} else "week"
    try:
        anchor = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        anchor = date.today()

    if view == "day":
        start, end = anchor, anchor
        days = [anchor]
    else:
        start = schedule_service.week_start(anchor)
        end = start + timedelta(days=6)
        days = schedule_service.week_days(start)

    sessions = schedule_service.sessions_between(db, start, end)
    by_day = {
        day: schedule_service.sessions_on(sessions, day) for day in days
    }
    return render(
        request,
        "schedule.html",
        {
            "view": view,
            "anchor": anchor.isoformat(),
            "days": days,
            "by_day": by_day,
        },
    )


@router.get("/my-sessions")
def my_sessions(
    request: Request,
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_user),
):
    tutor_id = user.tutor_id
    sessions = []
    if tutor_id is not None:
        sessions = schedule_service.upcoming_for_tutor(
            db, tutor_id, date.today()
        )
    return render(
        request,
        "my_sessions.html",
        {"user": user, "sessions": sessions},
    )
