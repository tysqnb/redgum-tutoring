"""Tutor roll: search, validation and persistence."""

from sqlalchemy import or_, select

from app.db import OrmSession
from app.models import Tutor


def list_tutors(db: OrmSession, q: str = "") -> list[Tutor]:
    stmt = select(Tutor).order_by(Tutor.name)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(Tutor.name.ilike(like), Tutor.subjects.ilike(like))
        )
    return list(db.scalars(stmt).all())


def validate_tutor_form(
    name: str, phone: str, subjects: str
) -> tuple[dict, list[str]]:
    data: dict = {}
    errors: list[str] = []

    name = name.strip()
    if not name:
        errors.append("Tutor name is required.")
    elif len(name) > 100:
        errors.append("Tutor name must be 100 characters or fewer.")
    data["name"] = name

    phone = phone.strip()
    if not phone:
        errors.append("Phone is required.")
    elif len(phone) > 20:
        errors.append("Phone must be 20 characters or fewer.")
    data["phone"] = phone

    subjects = subjects.strip()
    if not subjects:
        errors.append("Subjects is required.")
    elif len(subjects) > 200:
        errors.append("Subjects must be 200 characters or fewer.")
    data["subjects"] = subjects

    return data, errors


def create_tutor(db: OrmSession, data: dict) -> Tutor:
    tutor = Tutor(**data)
    db.add(tutor)
    db.commit()
    return tutor


def update_tutor(db: OrmSession, tutor: Tutor, data: dict) -> Tutor:
    for field, value in data.items():
        setattr(tutor, field, value)
    db.commit()
    return tutor
