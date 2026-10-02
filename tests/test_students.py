"""Coordinator student roll tests."""

from app.models import Student


def test_list_renders_students(admin_client, make_student):
    make_student(name="Ella Nguyen")
    response = admin_client.get("/students")
    assert response.status_code == 200
    assert "Ella Nguyen" in response.text


def test_search_filters_by_name(admin_client, make_student):
    make_student(name="Ella Nguyen")
    make_student(name="Kai Lombardo")
    response = admin_client.get("/students?q=Ella")
    assert "Ella Nguyen" in response.text
    assert "Kai Lombardo" not in response.text


def test_search_is_case_insensitive(admin_client, make_student):
    make_student(name="Amelia Chen")
    response = admin_client.get("/students?q=amelia")
    assert "Amelia Chen" in response.text


def test_search_matches_the_family_contact_name(admin_client, make_student):
    make_student(name="Ella Nguyen", contact_name="Mai Nguyen")
    make_student(name="Kai Lombardo", contact_name="Gina Lombardo")
    r = admin_client.get("/students?q=Gina")
    assert "Kai Lombardo" in r.text
    assert "Ella Nguyen" not in r.text


def test_create_student_redirects_and_shows_row(admin_client, db_session):
    response = admin_client.post(
        "/students/new",
        data={
            "name": "New Student",
            "year_level": "9",
            "contact_name": "A Parent",
            "contact_phone": "0400 000 000",
            "school": "",
            "contact_email": "",
            "subjects": "English",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert db_session.query(Student).count() == 1
    assert "New Student" in admin_client.get("/students").text


def test_create_requires_name(admin_client, db_session):
    response = admin_client.post(
        "/students/new",
        data={
            "name": "",
            "year_level": "9",
            "contact_name": "A Parent",
            "contact_phone": "0400 000 000",
        },
    )
    assert response.status_code == 400
    assert "Student name is required." in response.text
    assert db_session.query(Student).count() == 0


def test_over_length_name_is_rejected(admin_client, db_session):
    r = admin_client.post(
        "/students/new",
        data={
            "name": "x" * 101,
            "year_level": "11",
            "contact_name": "Y",
            "contact_phone": "0400",
        },
    )
    assert r.status_code == 400
    assert "Student name must be 100 characters or fewer." in r.text
    assert db_session.query(Student).count() == 0


def test_create_requires_year_level(admin_client):
    response = admin_client.post(
        "/students/new",
        data={
            "name": "No Year",
            "year_level": "",
            "contact_name": "A Parent",
            "contact_phone": "0400 000 000",
        },
    )
    assert response.status_code == 400
    assert "Year level is required." in response.text


def test_create_requires_contact_name(admin_client):
    response = admin_client.post(
        "/students/new",
        data={
            "name": "No Contact",
            "year_level": "9",
            "contact_name": "",
            "contact_phone": "0400 000 000",
        },
    )
    assert response.status_code == 400
    assert "Family contact name is required." in response.text


def test_create_requires_contact_phone(admin_client):
    response = admin_client.post(
        "/students/new",
        data={
            "name": "No Phone",
            "year_level": "9",
            "contact_name": "A Parent",
            "contact_phone": "",
        },
    )
    assert response.status_code == 400
    assert "Family contact phone is required." in response.text


def test_edit_student_updates_row(admin_client, make_student, db_session):
    student = make_student(name="Old Name")
    response = admin_client.post(
        f"/students/{student.id}/edit",
        data={
            "name": "Updated Name",
            "year_level": "11",
            "contact_name": "A Parent",
            "contact_phone": "0400 000 000",
            "school": "",
            "contact_email": "",
            "subjects": "Maths",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(student)
    assert student.name == "Updated Name"
    assert "Updated Name" in admin_client.get("/students").text


def test_edit_form_shows_current_values(admin_client, make_student):
    student = make_student(name="Ella Nguyen", year_level="11")
    response = admin_client.get(f"/students/{student.id}/edit")
    assert response.status_code == 200
    assert 'value="Ella Nguyen"' in response.text
    assert ">11</option>" in response.text or '"11" selected' in response.text


def test_edit_unknown_student_is_404(admin_client):
    response = admin_client.get("/students/999/edit")
    assert response.status_code == 404


def test_session_history_lists_sessions(admin_client, make_session):
    session = make_session(subject="Chemistry")
    response = admin_client.get(f"/students/{session.student_id}/sessions")
    assert response.status_code == 200
    assert "Chemistry" in response.text
    assert "Tomás Ferreira" in response.text


def test_session_history_unknown_student_is_404(admin_client):
    response = admin_client.get("/students/999/sessions")
    assert response.status_code == 404


def test_optional_fields_can_be_blank(admin_client, db_session):
    response = admin_client.post(
        "/students/new",
        data={
            "name": "Minimal Student",
            "year_level": "8",
            "contact_name": "A Parent",
            "contact_phone": "0400 000 000",
            "school": "",
            "contact_email": "",
            "subjects": "",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert db_session.query(Student).count() == 1
