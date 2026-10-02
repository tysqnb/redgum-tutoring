"""Tutor availability pages: list, add and remove weekly windows."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.db import OrmSession, get_db
from app.dependencies import get_or_404, require_admin
from app.flash import flash
from app.models import AppUser, AvailabilityWindow, Tutor
from app.services import availability as availability_service
from app.templating import render

router = APIRouter()


@router.get("/tutors/{tutor_id}/availability")
def availability_page(
    tutor_id: int,
    request: Request,
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    tutor = get_or_404(db, Tutor, tutor_id, "Tutor")
    windows = availability_service.windows_for_tutor(db, tutor_id)
    return render(
        request,
        "tutors/availability.html",
        {
            "tutor": tutor,
            "windows": windows,
            "form": {},
            "errors": [],
        },
    )


@router.post("/tutors/{tutor_id}/availability")
def add_window(
    tutor_id: int,
    request: Request,
    day_of_week: str = Form(""),
    start_time: str = Form(""),
    end_time: str = Form(""),
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    tutor = get_or_404(db, Tutor, tutor_id, "Tutor")
    data, errors = availability_service.validate_window_form(
        day_of_week, start_time, end_time
    )
    form = {
        "day_of_week": day_of_week,
        "start_time": start_time,
        "end_time": end_time,
    }
    if errors:
        return render(
            request,
            "tutors/availability.html",
            {
                "tutor": tutor,
                "windows": availability_service.windows_for_tutor(db, tutor_id),
                "form": form,
                "errors": errors,
            },
            status_code=400,
        )
    if availability_service.window_exists(
        db,
        tutor_id,
        data["day_of_week"],
        data["start_time"],
        data["end_time"],
    ):
        errors.append("That availability window already exists.")
        return render(
            request,
            "tutors/availability.html",
            {
                "tutor": tutor,
                "windows": availability_service.windows_for_tutor(db, tutor_id),
                "form": form,
                "errors": errors,
            },
            status_code=400,
        )
    availability_service.add_window(db, tutor_id, **data)
    flash(request, "Availability added.")
    return RedirectResponse(
        f"/tutors/{tutor_id}/availability", status_code=303
    )


@router.post("/availability/{window_id}/delete")
def delete_window(
    window_id: int,
    request: Request,
    db: OrmSession = Depends(get_db),
    user: AppUser = Depends(require_admin),
):
    window = get_or_404(
        db, AvailabilityWindow, window_id, "Availability window"
    )
    tutor_id = window.tutor_id
    availability_service.delete_window(db, window)
    flash(request, "Availability removed.")
    return RedirectResponse(
        f"/tutors/{tutor_id}/availability", status_code=303
    )


@router.get("/availability/{window_id}/edit")
def edit_window_form(
    window_id: int,
    request: Request,
    user: AppUser = Depends(require_admin),
    db: OrmSession = Depends(get_db),
):
    window = get_or_404(
        db, AvailabilityWindow, window_id, "Availability window"
    )
    form = {
        "day_of_week": window.day_of_week,
        "start_time": window.start_time.strftime("%H:%M"),
        "end_time": window.end_time.strftime("%H:%M"),
    }
    return render(
        request,
        "tutors/availability_edit.html",
        {
            "window": window,
            "tutor": window.tutor,
            "form": form,
            "errors": [],
        },
    )


@router.post("/availability/{window_id}/edit")
def edit_window(
    window_id: int,
    request: Request,
    day_of_week: str = Form(""),
    start_time: str = Form(""),
    end_time: str = Form(""),
    user: AppUser = Depends(require_admin),
    db: OrmSession = Depends(get_db),
):
    window = get_or_404(
        db, AvailabilityWindow, window_id, "Availability window"
    )
    data, errors = availability_service.validate_window_form(
        day_of_week, start_time, end_time
    )
    form = {
        "day_of_week": day_of_week,
        "start_time": start_time,
        "end_time": end_time,
    }
    if errors:
        return render(
            request,
            "tutors/availability_edit.html",
            {
                "window": window,
                "tutor": window.tutor,
                "form": form,
                "errors": errors,
            },
            status_code=400,
        )
    if availability_service.window_exists(
        db,
        window.tutor_id,
        data["day_of_week"],
        data["start_time"],
        data["end_time"],
        exclude_id=window.id,
    ):
        errors.append("That availability window already exists.")
        return render(
            request,
            "tutors/availability_edit.html",
            {
                "window": window,
                "tutor": window.tutor,
                "form": form,
                "errors": errors,
            },
            status_code=400,
        )
    availability_service.update_window(db, window, **data)
    flash(request, "Availability updated.")
    return RedirectResponse(
        f"/tutors/{window.tutor_id}/availability", status_code=303
    )
