"""Schedule service and views."""

from datetime import date, time, timedelta

from app.models import Session
from app.services.schedule import upcoming_for_tutor, week_days, week_start


def test_week_start_returns_monday():
    assert week_start(date(2026, 10, 2)) == date(2026, 9, 28)


def test_week_days_spans_seven_days():
    days = week_days(date(2026, 9, 28))
    assert len(days) == 7
    assert days[0] == date(2026, 9, 28)
    assert days[-1] == date(2026, 10, 4)


def test_schedule_week_view_lists_sessions(admin_client, make_session):
    session = make_session(subject="Biology")
    response = admin_client.get("/schedule?view=week")
    assert response.status_code == 200
    assert session.student.name in response.text


def test_schedule_day_view_filters_to_one_day(admin_client, make_session):
    today = date.today()
    make_session(date=today, subject="Today Session")
    make_session(date=today + timedelta(days=2), subject="Later Session")
    response = admin_client.get(f"/schedule?view=day&date={today.isoformat()}")
    assert "Today Session" in response.text
    assert "Later Session" not in response.text


def test_schedule_requires_admin(tutor_client):
    response = tutor_client.get("/schedule")
    assert response.status_code == 403


def test_upcoming_for_tutor_filters_status_and_date(
    db_session, tutor_record, make_student
):
    today = date.today()
    student = make_student(name="Filter Student")
    db_session.add_all(
        [
            Session(
                student_id=student.id,
                tutor_id=tutor_record.id,
                date=today - timedelta(days=1),
                start_time=time(16, 0),
                duration_minutes=60,
                subject="Past",
                status="BOOKED",
            ),
            Session(
                student_id=student.id,
                tutor_id=tutor_record.id,
                date=today + timedelta(days=1),
                start_time=time(16, 0),
                duration_minutes=60,
                subject="Future",
                status="BOOKED",
            ),
            Session(
                student_id=student.id,
                tutor_id=tutor_record.id,
                date=today + timedelta(days=2),
                start_time=time(16, 0),
                duration_minutes=60,
                subject="Cancelled",
                status="CANCELLED",
            ),
        ]
    )
    db_session.commit()
    upcoming = upcoming_for_tutor(db_session, tutor_record.id, today)
    assert [s.subject for s in upcoming] == ["Future"]

