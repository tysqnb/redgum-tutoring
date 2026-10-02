"""Jinja filters used by the templates."""

from datetime import time


def time12(value) -> str:
    """Render a time or HH:MM string as 12-hour time, e.g. 15:30 -> 3:30 pm."""
    if isinstance(value, time):
        hour, minute = value.hour, value.minute
    else:
        parts = str(value).split(":")
        hour, minute = int(parts[0]), int(parts[1])
    suffix = "am" if hour < 12 else "pm"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour}:{minute:02d} {suffix}"
