"""Idempotent demo data: roll, tutors, availability and a diary week."""

from datetime import date, time, timedelta

from sqlalchemy import select

from app.db import OrmSession
from app.models import AppUser, AvailabilityWindow, Session, Student, Tutor
from app.security import hash_password

STUDENTS = [
    {
        "name": "Ella Nguyen",
        "school": "Redgum High",
        "year_level": "11",
        "contact_name": "Mai Nguyen",
        "contact_phone": "0411 222 333",
        "contact_email": "mai.nguyen@example.com",
        "subjects": "Maths Methods, Physics",
    },
    {
        "name": "Kai Lombardo",
        "school": "Redgum High",
        "year_level": "9",
        "contact_name": "Gina Lombardo",
        "contact_phone": "0422 333 444",
        "contact_email": "gina.lombardo@example.com",
        "subjects": "English, History",
    },
    {
        "name": "Priya Sharma",
        "school": "Westvale College",
        "year_level": "12",
        "contact_name": "Ravi Sharma",
        "contact_phone": "0433 444 555",
        "contact_email": "ravi.sharma@example.com",
        "subjects": "Chemistry, Biology",
    },
    {
        "name": "Jack Wilson",
        "school": "Redgum High",
        "year_level": "7",
        "contact_name": "Karen Wilson",
        "contact_phone": "0444 555 666",
        "contact_email": "karen.wilson@example.com",
        "subjects": "Maths",
    },
    {
        "name": "Amelia Chen",
        "school": "St Brigid's College",
        "year_level": "10",
        "contact_name": "Li Chen",
        "contact_phone": "0455 666 777",
        "contact_email": "li.chen@example.com",
        "subjects": "English, Literature",
    },
    {
        "name": "Oliver Zhang",
        "school": "Westvale College",
        "year_level": "8",
        "contact_name": "Mei Zhang",
        "contact_phone": "0466 777 888",
        "contact_email": "mei.zhang@example.com",
        "subjects": "Physics, Maths",
    },
]

TUTORS = [
    {
        "name": "Tomás Ferreira",
        "phone": "0400 111 222",
        "subjects": "Physics, Maths",
    },
    {
        "name": "Grace Thompson",
        "phone": "0400 222 333",
        "subjects": "English, Literature",
    },
    {
        "name": "Malik Hassan",
        "phone": "0400 333 444",
        "subjects": "Chemistry, Biology",
    },
]

WINDOWS = [
    # (tutor index, day, start, end)
    (0, "TUESDAY", time(15, 30), time(19, 0)),
    (0, "THURSDAY", time(16, 0), time(18, 30)),
    (1, "WEDNESDAY", time(15, 30), time(18, 0)),
    (2, "SATURDAY", time(9, 0), time(12, 0)),
]

DIARY_WEEK = [
    # (student index, tutor index, days from next Monday, start, minutes, subject, notes)
    (0, 0, 1, time(16, 0), 60, "Physics", None),
    (1, 0, 1, time(17, 30), 60, "Maths", "Bring last week's worksheet."),
    (2, 2, 5, time(9, 30), 60, "Chemistry", None),
    (3, 0, 3, time(16, 0), 60, "Maths", None),
    (4, 1, 2, time(16, 0), 60, "English", None),
    (5, 1, 2, time(17, 0), 60, "English", "Practice essay due."),
]


def seed_demo(db: OrmSession) -> None:
    """Load demo data once; a second run leaves the database untouched."""
    existing = db.scalar(select(AppUser).limit(1))
    if existing is not None:
        return

    students = [Student(**row) for row in STUDENTS]
    tutors = [Tutor(**row) for row in TUTORS]
    db.add_all(students + tutors)
    db.flush()

    windows = [
        AvailabilityWindow(
            tutor_id=tutors[tutor_index].id,
            day_of_week=day,
            start_time=start,
            end_time=end,
        )
        for tutor_index, day, start, end in WINDOWS
    ]
    db.add_all(windows)

    admin = AppUser(
        username="deb",
        password_hash=hash_password("redgum123"),
        role="ADMIN",
    )
    tutor_login = AppUser(
        username="tomas",
        password_hash=hash_password("redgum123"),
        role="USER",
        tutor_id=tutors[0].id,
    )
    db.add_all([admin, tutor_login])

    monday = _next_monday(date.today())
    sessions = [
        Session(
            student_id=students[student_index].id,
            tutor_id=tutors[tutor_index].id,
            date=monday + timedelta(days=day_offset),
            start_time=start,
            duration_minutes=minutes,
            subject=subject,
            notes=notes,
            status="BOOKED",
        )
        for (
            student_index,
            tutor_index,
            day_offset,
            start,
            minutes,
            subject,
            notes,
        ) in DIARY_WEEK
    ]
    db.add_all(sessions)
    db.commit()


def _next_monday(today: date) -> date:
    return today + timedelta(days=(7 - today.weekday()) % 7)
