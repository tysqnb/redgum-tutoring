"""Coordinator tutor roll tests."""

from app.models import Tutor


def test_list_renders_tutors(admin_client, tutor_record):
    response = admin_client.get("/tutors")
    assert response.status_code == 200
    assert "Tomás Ferreira" in response.text


def test_search_filters_by_name(admin_client, tutor_record, db_session):
    db_session.add(
        Tutor(name="Grace Thompson", phone="0400 222 333", subjects="English")
    )
    db_session.commit()
    response = admin_client.get("/tutors?q=Grace")
    assert "Grace Thompson" in response.text
    assert "Tomás Ferreira" not in response.text


def test_search_matches_subjects(admin_client, tutor_record):
    assert "Tomás Ferreira" in admin_client.get("/tutors?q=Physics").text
    assert "Tomás Ferreira" not in admin_client.get("/tutors?q=Nuclear").text


def test_create_tutor_redirects_and_shows_row(admin_client, db_session):
    response = admin_client.post(
        "/tutors/new",
        data={"name": "New Tutor", "phone": "0400 999 999", "subjects": "Maths"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert db_session.query(Tutor).count() == 1
    assert "New Tutor" in admin_client.get("/tutors").text


def test_create_requires_name(admin_client, db_session):
    response = admin_client.post(
        "/tutors/new",
        data={"name": "", "phone": "0400 999 999", "subjects": "Maths"},
    )
    assert response.status_code == 400
    assert "Tutor name is required." in response.text
    assert db_session.query(Tutor).count() == 0


def test_create_requires_phone(admin_client):
    response = admin_client.post(
        "/tutors/new",
        data={"name": "No Phone", "phone": "", "subjects": "Maths"},
    )
    assert response.status_code == 400
    assert "Phone is required." in response.text


def test_create_requires_subjects(admin_client):
    response = admin_client.post(
        "/tutors/new",
        data={"name": "No Subjects", "phone": "0400 999 999", "subjects": ""},
    )
    assert response.status_code == 400
    assert "Subjects is required." in response.text


def test_phone_at_the_length_boundary(admin_client, db_session):
    accepted = admin_client.post(
        "/tutors/new",
        data={
            "name": "Boundary Tutor",
            "phone": "0" * 20,
            "subjects": "Maths",
        },
        follow_redirects=False,
    )
    assert accepted.status_code == 303
    rejected = admin_client.post(
        "/tutors/new",
        data={
            "name": "Too Long",
            "phone": "0" * 21,
            "subjects": "Maths",
        },
    )
    assert rejected.status_code == 400
    assert "Phone must be 20 characters or fewer." in rejected.text


def test_edit_tutor_updates_row(admin_client, tutor_record, db_session):
    response = admin_client.post(
        f"/tutors/{tutor_record.id}/edit",
        data={"name": "Updated Tutor", "phone": "0400 111 222", "subjects": "Maths"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(tutor_record)
    assert tutor_record.name == "Updated Tutor"


def test_edit_form_shows_current_values(admin_client, tutor_record):
    response = admin_client.get(f"/tutors/{tutor_record.id}/edit")
    assert response.status_code == 200
    assert 'value="Tomás Ferreira"' in response.text


def test_edit_unknown_tutor_is_404(admin_client):
    response = admin_client.get("/tutors/999/edit")
    assert response.status_code == 404


def test_availability_page_lists_windows(admin_client, tutor_record):
    response = admin_client.get(f"/tutors/{tutor_record.id}/availability")
    assert response.status_code == 200
    assert "Tuesday" in response.text
    assert "3:30 pm" in response.text
    assert response.text.index("Tuesday") < response.text.index("Thursday")


def test_add_window(admin_client, tutor_record, db_session):
    response = admin_client.post(
        f"/tutors/{tutor_record.id}/availability",
        data={
            "day_of_week": "WEDNESDAY",
            "start_time": "15:00",
            "end_time": "17:00",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert len(tutor_record.windows) == 3


def test_add_window_end_before_start_is_rejected(admin_client, tutor_record):
    response = admin_client.post(
        f"/tutors/{tutor_record.id}/availability",
        data={
            "day_of_week": "WEDNESDAY",
            "start_time": "17:00",
            "end_time": "15:00",
        },
    )
    assert response.status_code == 400
    assert "End time must be after start time." in response.text
