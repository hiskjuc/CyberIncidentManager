"""Small helpers shared by controllers and views."""

from __future__ import annotations

from datetime import date
from typing import Any


def today_iso() -> str:
    return date.today().isoformat()


def center_window(window: Any, width: int, height: int) -> None:
    """Place a Tk window near the screen center."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_position = max((screen_width - width) // 2, 0)
    y_position = max((screen_height - height) // 2, 0)
    window.geometry(f"{width}x{height}+{x_position}+{y_position}")


def short_text(value: str | None, limit: int = 64) -> str:
    cleaned = (value or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3]}..."
