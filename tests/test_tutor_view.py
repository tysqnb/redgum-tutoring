"""Tutor's read-only view of their own sessions."""

from datetime import date, time, timedelta

from app.models import Session, Tutor


def test_tutor_can_view_own_upcoming_sessions(tutor_client, make_session):
    session = make_session(subject="Physics")
    response = tutor_client.get("/my-sessions")
    assert response.status_code == 200
    assert session.student.name in response.text
    assert "Physics" in response.text


def test_my_sessions_hides_other_tutors_sessions(
    tutor_client, make_session, db_session, make_student
):
    other = Tutor(
        name="Grace Thompson", phone="0400 222 333", subjects="English"
    )
    db_session.add(other)
    db_session.commit()
    student = make_student(name="Other Student")
    db_session.add(
        Session(
            student_id=student.id,
            tutor_id=other.id,
            date=date.today() + timedelta(days=1),
            start_time=time(16, 0),
            duration_minutes=60,
            subject="Someone Else's",
            status="BOOKED",
        )
    )
    db_session.commit()
    response = tutor_client.get("/my-sessions")
    assert "Someone Else's" not in response.text


def test_my_sessions_hides_past_sessions(tutor_client, make_session):
    make_session(
        subject="Past Physics", date=date.today() - timedelta(days=3)
    )
    response = tutor_client.get("/my-sessions")
    assert "Past Physics" not in response.text


def test_my_sessions_hides_cancelled(tutor_client, make_session):
    make_session(subject="Cancelled Physics", status="CANCELLED")
    response = tutor_client.get("/my-sessions")
    assert "Cancelled Physics" not in response.text


def test_my_sessions_requires_login(client):
    response = client.get("/my-sessions", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_tutor_gets_403_on_students(tutor_client):
    assert tutor_client.get("/students").status_code == 403


def test_tutor_gets_403_on_tutors(tutor_client):
    assert tutor_client.get("/tutors").status_code == 403


def test_tutor_gets_403_on_schedule(tutor_client):
    assert tutor_client.get("/schedule").status_code == 403
