"""Weekly availability windows: validation and persistence."""

from datetime import time

from sqlalchemy import select

from app.db import OrmSession
from app.models import AvailabilityWindow

DAYS_OF_WEEK = [
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
]

DAY_INDEX = {day: index for index, day in enumerate(DAYS_OF_WEEK)}


def _parse_time(value: str) -> time | None:
    try:
        hour, minute = value.strip().split(":", 1)
        return time(int(hour), int(minute))
    except (ValueError, AttributeError):
        return None


def validate_window_form(
    day_of_week: str, start_time: str, end_time: str
) -> tuple[dict, list[str]]:
    errors: list[str] = []
    day_of_week = day_of_week.strip()
    start = _parse_time(start_time)
    end = _parse_time(end_time)

    if day_of_week not in DAYS_OF_WEEK:
        errors.append("Choose a day of the week.")
    if start is None:
        errors.append("Enter a start time as HH:MM.")
    if end is None:
        errors.append("Enter an end time as HH:MM.")
    if start is not None and end is not None and end <= start:
        errors.append("End time must be after start time.")

    data = {
        "day_of_week": day_of_week,
        "start_time": start,
        "end_time": end,
    }
    return data, errors


def add_window(db: OrmSession, tutor_id: int, **data) -> AvailabilityWindow:
    window = AvailabilityWindow(tutor_id=tutor_id, **data)
    db.add(window)
    db.commit()
    return window


def delete_window(db: OrmSession, window: AvailabilityWindow) -> None:
    db.delete(window)
    db.commit()


def update_window(
    db: OrmSession, window: AvailabilityWindow, **data
) -> AvailabilityWindow:
    for field, value in data.items():
        setattr(window, field, value)
    db.commit()
    return window


def windows_for_tutor(db: OrmSession, tutor_id: int) -> list[AvailabilityWindow]:
    stmt = (
        select(AvailabilityWindow)
        .where(AvailabilityWindow.tutor_id == tutor_id)
        .order_by(AvailabilityWindow.start_time)
    )
    rows = list(db.scalars(stmt).all())
    return sorted(
        rows,
        key=lambda window: (
            DAY_INDEX.get(window.day_of_week, len(DAYS_OF_WEEK)),
            window.start_time,
        ),
    )


def window_exists(
    db: OrmSession,
    tutor_id: int,
    day_of_week: str,
    start_time: time,
    end_time: time,
    exclude_id: int | None = None,
) -> bool:
    stmt = select(AvailabilityWindow).where(
        AvailabilityWindow.tutor_id == tutor_id,
        AvailabilityWindow.day_of_week == day_of_week,
        AvailabilityWindow.start_time == start_time,
        AvailabilityWindow.end_time == end_time,
    )
    if exclude_id is not None:
        stmt = stmt.where(AvailabilityWindow.id != exclude_id)
    return db.scalars(stmt).first() is not None
