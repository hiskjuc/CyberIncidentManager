"""Reusable ttk Treeview sizing and scrolling helpers."""

from __future__ import annotations

from tkinter import font, ttk
from typing import Any, Mapping


def configure_columns(
    table: ttk.Treeview,
    headings: Mapping[str, str],
    minimum_widths: Mapping[str, int],
    centered: set[str] | None = None,
) -> None:
    """Set readable column baselines that can grow with cell content."""
    centered = centered or set()
    for column, heading in headings.items():
        anchor = "center" if column in centered else "w"
        table.heading(column, text=heading, anchor=anchor)
        table.column(
            column,
            width=minimum_widths[column],
            minwidth=minimum_widths[column],
            anchor=anchor,
            stretch=True,
        )


def format_table_text(value: Any, limit: int = 96) -> str:
    """Compact multiline or long values so rows stay readable."""
    cleaned = " ".join(str(value or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3]}..."


def fit_columns(
    table: ttk.Treeview,
    minimum_widths: Mapping[str, int],
    maximum_width: int = 380,
) -> None:
    """Grow columns to current content while preserving horizontal scrolling."""
    table_font = font.nametofont("TkDefaultFont")
    for column in table["columns"]:
        heading_width = table_font.measure(table.heading(column)["text"]) + 28
        value_widths = [
            table_font.measure(str(table.set(item_id, column))) + 28
            for item_id in table.get_children("")
        ]
        content_width = max([heading_width, minimum_widths[column], *value_widths])
        table.column(column, width=min(content_width, maximum_width))


def add_scrollbars(
    table: ttk.Treeview,
    parent,
    row: int,
    column: int,
    padx: tuple[int, int] = (18, 0),
    pady: tuple[int, int] = (0, 18),
) -> None:
    """Grid a treeview with styled vertical and horizontal scrollbars."""
    parent.grid_columnconfigure(column, weight=1)
    parent.grid_rowconfigure(row, weight=1)
    table.grid(row=row, column=column, padx=padx, pady=pady, sticky="nsew")
    vertical = ttk.Scrollbar(
        parent,
        orient="vertical",
        command=table.yview,
        style="CIM.Vertical.TScrollbar",
    )
    vertical.grid(row=row, column=column + 1, padx=(0, 18), pady=pady, sticky="ns")
    horizontal = ttk.Scrollbar(
        parent,
        orient="horizontal",
        command=table.xview,
        style="CIM.Horizontal.TScrollbar",
    )
    horizontal.grid(
        row=row + 1,
        column=column,
        padx=padx,
        pady=(0, 18),
        sticky="ew",
    )
    table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
