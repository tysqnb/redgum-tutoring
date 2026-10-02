"""Availability window routes and validation."""

from datetime import time

from app.services.availability import validate_window_form


def test_availability_page_requires_admin(tutor_client, tutor_record):
    response = tutor_client.get(f"/tutors/{tutor_record.id}/availability")
    assert response.status_code == 403


def test_availability_page_unknown_tutor_is_404(admin_client):
    response = admin_client.get("/tutors/999/availability")
    assert response.status_code == 404


def test_add_window_renders_on_page(admin_client, tutor_record):
    admin_client.post(
        f"/tutors/{tutor_record.id}/availability",
        data={
            "day_of_week": "WEDNESDAY",
            "start_time": "16:00",
            "end_time": "18:00",
        },
    )
    response = admin_client.get(f"/tutors/{tutor_record.id}/availability")
    assert "Wednesday" in response.text
    assert "4:00 pm" in response.text


def test_remove_window(admin_client, tutor_record, db_session):
    window = tutor_record.windows[0]
    response = admin_client.post(
        f"/availability/{window.id}/delete", follow_redirects=False
    )
    assert response.status_code == 303
    db_session.expire_all()
    assert len(tutor_record.windows) == 1


def test_delete_unknown_window_is_404(admin_client):
    response = admin_client.post("/availability/999/delete")
    assert response.status_code == 404


def test_add_requires_day(admin_client, tutor_record):
    response = admin_client.post(
        f"/tutors/{tutor_record.id}/availability",
        data={"day_of_week": "", "start_time": "15:00", "end_time": "17:00"},
    )
    assert response.status_code == 400
    assert "Choose a day of the week." in response.text


def test_add_requires_valid_start(admin_client, tutor_record):
    response = admin_client.post(
        f"/tutors/{tutor_record.id}/availability",
        data={"day_of_week": "WEDNESDAY", "start_time": "25:99", "end_time": "17:00"},
    )
    assert response.status_code == 400
    assert "Enter a start time as HH:MM." in response.text


def test_add_requires_valid_end(admin_client, tutor_record):
    response = admin_client.post(
        f"/tutors/{tutor_record.id}/availability",
        data={"day_of_week": "WEDNESDAY", "start_time": "15:00", "end_time": "nope"},
    )
    assert response.status_code == 400
    assert "Enter an end time as HH:MM." in response.text


def test_add_end_before_start_is_rejected(admin_client, tutor_record):
    response = admin_client.post(
        f"/tutors/{tutor_record.id}/availability",
        data={"day_of_week": "WEDNESDAY", "start_time": "17:00", "end_time": "15:00"},
    )
    assert response.status_code == 400
    assert "End time must be after start time." in response.text


def test_validate_window_form_parses_times():
    data, errors = validate_window_form("TUESDAY", "15:30", "19:00")
    assert errors == []
    assert data["start_time"] == time(15, 30)
    assert data["end_time"] == time(19, 0)


def test_validate_window_form_rejects_unknown_day():
    data, errors = validate_window_form("FUNDAY", "15:30", "19:00")
    assert "Choose a day of the week." in errors
