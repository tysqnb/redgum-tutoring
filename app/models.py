"""Domain models: students, tutors, availability windows, sessions and logins."""

from datetime import date, time

from sqlalchemy import Date, ForeignKey, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    school: Mapped[str | None] = mapped_column(String(120))
    year_level: Mapped[str | None] = mapped_column(String(10))
    contact_name: Mapped[str] = mapped_column(String(100))
    contact_phone: Mapped[str] = mapped_column(String(20))
    contact_email: Mapped[str | None] = mapped_column(String(120))
    subjects: Mapped[str | None] = mapped_column(String(200))

    sessions: Mapped[list["Session"]] = relationship(back_populates="student")


class Tutor(Base):
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    subjects: Mapped[str] = mapped_column(String(200))

    windows: Mapped[list["AvailabilityWindow"]] = relationship(
        back_populates="tutor", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["Session"]] = relationship(back_populates="tutor")


class AvailabilityWindow(Base):
    __tablename__ = "availability_windows"
    __table_args__ = (
        UniqueConstraint(
            "tutor_id",
            "day_of_week",
            "start_time",
            "end_time",
            name="uq_window",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutors.id"))
    day_of_week: Mapped[str] = mapped_column(String(9))
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    tutor: Mapped[Tutor] = relationship(back_populates="windows")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutors.id"))
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(default=60)
    subject: Mapped[str] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(10), default="BOOKED")

    student: Mapped[Student] = relationship(back_populates="sessions")
    tutor: Mapped[Tutor] = relationship(back_populates="sessions")


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(10), default="USER")
    tutor_id: Mapped[int | None] = mapped_column(ForeignKey("tutors.id"))

    tutor: Mapped[Tutor | None] = relationship()
