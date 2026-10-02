"""Jinja environment and the render helper shared by all routers."""

from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.filters import time12
from app.flash import take_flashes
from app.security import write_session_cookie

TEMPLATE_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.filters["time12"] = time12


def render(
    request: Request,
    template: str,
    context: dict | None = None,
    status_code: int = 200,
):
    """Render a template, flushing queued flash messages into the cookie."""
    context = dict(context or {})
    flashes = take_flashes(request)
    context.setdefault("flashes", flashes)
    response = templates.TemplateResponse(
        request, template, context, status_code=status_code
    )
    write_session_cookie(response, request.state.session_payload)
    return response
