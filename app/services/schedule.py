"""Schedule queries shared by the schedule and my-sessions views."""

from datetime import date, timedelta

from sqlalchemy import select

from app.db import OrmSession
from app.models import Session


def week_start(anchor: date) -> date:
    """Monday of the week containing anchor."""
    return anchor - timedelta(days=anchor.weekday())


def week_days(start: date) -> list[date]:
    """The seven dates starting at start."""
    return [start + timedelta(days=i) for i in range(7)]


def sessions_between(
    db: OrmSession,
    start: date,
    end: date,
    tutor_id: int | None = None,
) -> list[Session]:
    stmt = select(Session).where(Session.date >= start, Session.date <= end)
    if tutor_id is not None:
        stmt = stmt.where(Session.tutor_id == tutor_id)
    stmt = stmt.order_by(Session.date, Session.start_time)
    return list(db.scalars(stmt).all())


def sessions_on(sessions: list[Session], day: date) -> list[Session]:
    return [s for s in sessions if s.date == day]


def upcoming_for_tutor(
    db: OrmSession,
    tutor_id: int,
    today: date,
    until: date | None = None,
) -> list[Session]:
    stmt = select(Session).where(
        Session.tutor_id == tutor_id,
        Session.status == "BOOKED",
        Session.date >= today,
    )
    if until is not None:
        stmt = stmt.where(Session.date <= until)
    stmt = stmt.order_by(Session.date, Session.start_time)
    return list(db.scalars(stmt).all())
