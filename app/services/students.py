"""Student roll: search, validation and persistence."""

from sqlalchemy import or_, select

from app.db import OrmSession
from app.models import Session, Student


def list_students(db: OrmSession, q: str = "") -> list[Student]:
    stmt = select(Student).order_by(Student.name)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(Student.name.ilike(like), Student.contact_name.ilike(like))
        )
    return list(db.scalars(stmt).all())


def validate_student_form(
    name: str,
    school: str,
    year_level: str,
    contact_name: str,
    contact_phone: str,
    contact_email: str,
    subjects: str,
) -> tuple[dict, list[str]]:
    data: dict = {}
    errors: list[str] = []

    name = name.strip()
    if not name:
        errors.append("Student name is required.")
    elif len(name) > 100:
        errors.append("Student name must be 100 characters or fewer.")
    data["name"] = name

    school = school.strip()
    if len(school) > 120:
        errors.append("School must be 120 characters or fewer.")
    data["school"] = school

    year_level = year_level.strip()
    if not year_level:
        errors.append("Year level is required.")
    data["year_level"] = year_level

    contact_name = contact_name.strip()
    if not contact_name:
        errors.append("Family contact name is required.")
    elif len(contact_name) > 100:
        errors.append("Family contact name must be 100 characters or fewer.")
    data["contact_name"] = contact_name

    contact_phone = contact_phone.strip()
    if not contact_phone:
        errors.append("Family contact phone is required.")
    elif len(contact_phone) > 20:
        errors.append("Family contact phone must be 20 characters or fewer.")
    data["contact_phone"] = contact_phone

    contact_email = contact_email.strip()
    if len(contact_email) > 120:
        errors.append("Family contact email must be 120 characters or fewer.")
    data["contact_email"] = contact_email

    subjects = subjects.strip()
    if len(subjects) > 200:
        errors.append("Subjects must be 200 characters or fewer.")
    data["subjects"] = subjects

    return data, errors


def create_student(db: OrmSession, data: dict) -> Student:
    student = Student(**data)
    db.add(student)
    db.commit()
    return student


def update_student(db: OrmSession, student: Student, data: dict) -> Student:
    for field, value in data.items():
        setattr(student, field, value)
    db.commit()
    return student


def sessions_for_student(db: OrmSession, student_id: int) -> list[Session]:
    stmt = (
        select(Session)
        .where(Session.student_id == student_id)
        .order_by(Session.date.desc(), Session.start_time)
    )
    return list(db.scalars(stmt).all())
