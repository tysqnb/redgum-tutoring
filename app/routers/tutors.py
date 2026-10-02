"""Coordinator routes for the tutor roll."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.db import OrmSession, get_db
from app.dependencies import get_or_404, require_admin
from app.flash import flash
from app.models import AppUser, Tutor
from app.services import tutors as tutors_service
from app.templating import render

router = APIRouter()


@router.get("/tutors")
def list_view(
    request: Request,
    q: str = "",
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    tutors = tutors_service.list_tutors(db, q)
    return render(request, "tutors/list.html", {"tutors": tutors, "q": q})


@router.get("/tutors/new")
def new_form(request: Request, user: AppUser = Depends(require_admin)):
    return render(
        request,
        "tutors/form.html",
        {"tutor": None, "form": {}, "errors": []},
    )


@router.post("/tutors/new")
def create(
    request: Request,
    name: str = Form(""),
    phone: str = Form(""),
    subjects: str = Form(""),
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    data, errors = tutors_service.validate_tutor_form(name, phone, subjects)
    form = {"name": name, "phone": phone, "subjects": subjects}
    if errors:
        return render(
            request,
            "tutors/form.html",
            {"tutor": None, "form": form, "errors": errors},
            status_code=400,
        )
    tutors_service.create_tutor(db, data)
    flash(request, "Tutor added.")
    return RedirectResponse("/tutors", status_code=303)


@router.get("/tutors/{tutor_id}/edit")
def edit_form(
    tutor_id: int,
    request: Request,
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    tutor = get_or_404(db, Tutor, tutor_id, "Tutor")
    form = {
        "name": tutor.name,
        "phone": tutor.phone,
        "subjects": tutor.subjects or "",
    }
    return render(
        request,
        "tutors/form.html",
        {"tutor": tutor, "form": form, "errors": []},
    )


@router.post("/tutors/{tutor_id}/edit")
def edit(
    tutor_id: int,
    request: Request,
    name: str = Form(""),
    phone: str = Form(""),
    subjects: str = Form(""),
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    tutor = get_or_404(db, Tutor, tutor_id, "Tutor")
    data, errors = tutors_service.validate_tutor_form(name, phone, subjects)
    form = {"name": name, "phone": phone, "subjects": subjects}
    if errors:
        return render(
            request,
            "tutors/form.html",
            {"tutor": tutor, "form": form, "errors": errors},
            status_code=400,
        )
    tutors_service.update_tutor(db, tutor, data)
    flash(request, "Tutor updated.")
    return RedirectResponse("/tutors", status_code=303)
