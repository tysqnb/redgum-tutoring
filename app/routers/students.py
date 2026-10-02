"""Coordinator routes for the student roll."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.db import OrmSession, get_db
from app.dependencies import get_or_404, require_admin
from app.flash import flash
from app.models import AppUser, Student
from app.services import students as students_service
from app.templating import render

router = APIRouter()


@router.get("/students")
def list_view(
    request: Request,
    q: str = "",
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    students = students_service.list_students(db, q)
    return render(
        request, "students/list.html", {"students": students, "q": q}
    )


@router.get("/students/new")
def new_form(
    request: Request, user: AppUser = Depends(require_admin)
):
    return render(
        request,
        "students/form.html",
        {"student": None, "form": {}, "errors": []},
    )


@router.post("/students/new")
def create(
    request: Request,
    name: str = Form(""),
    school: str = Form(""),
    year_level: str = Form(""),
    contact_name: str = Form(""),
    contact_phone: str = Form(""),
    contact_email: str = Form(""),
    subjects: str = Form(""),
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    data, errors = students_service.validate_student_form(
        name, school, year_level, contact_name, contact_phone,
        contact_email, subjects,
    )
    form = {
        "name": name, "school": school, "year_level": year_level,
        "contact_name": contact_name, "contact_phone": contact_phone,
        "contact_email": contact_email, "subjects": subjects,
    }
    if errors:
        return render(
            request,
            "students/form.html",
            {"student": None, "form": form, "errors": errors},
            status_code=400,
        )
    students_service.create_student(db, data)
    flash(request, "Student added.")
    return RedirectResponse("/students", status_code=303)


@router.get("/students/{student_id}/edit")
def edit_form(
    student_id: int,
    request: Request,
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    student = get_or_404(db, Student, student_id, "Student")
    form = {
        "name": student.name,
        "school": student.school or "",
        "year_level": student.year_level or "",
        "contact_name": student.contact_name,
        "contact_phone": student.contact_phone,
        "contact_email": student.contact_email or "",
        "subjects": student.subjects or "",
    }
    return render(
        request,
        "students/form.html",
        {"student": student, "form": form, "errors": []},
    )


@router.post("/students/{student_id}/edit")
def edit(
    student_id: int,
    request: Request,
    name: str = Form(""),
    school: str = Form(""),
    year_level: str = Form(""),
    contact_name: str = Form(""),
    contact_phone: str = Form(""),
    contact_email: str = Form(""),
    subjects: str = Form(""),
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    student = get_or_404(db, Student, student_id, "Student")
    data, errors = students_service.validate_student_form(
        name, school, year_level, contact_name, contact_phone,
        contact_email, subjects,
    )
    form = {
        "name": name, "school": school, "year_level": year_level,
        "contact_name": contact_name, "contact_phone": contact_phone,
        "contact_email": contact_email, "subjects": subjects,
    }
    if errors:
        return render(
            request,
            "students/form.html",
            {"student": student, "form": form, "errors": errors},
            status_code=400,
        )
    students_service.update_student(db, student, data)
    flash(request, "Student updated.")
    return RedirectResponse("/students", status_code=303)


@router.get("/students/{student_id}/sessions")
def session_history(
    student_id: int,
    request: Request,
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    student = get_or_404(db, Student, student_id, "Student")
    sessions = students_service.sessions_for_student(db, student_id)
    return render(
        request,
        "students/sessions.html",
        {"student": student, "sessions": sessions},
    )
