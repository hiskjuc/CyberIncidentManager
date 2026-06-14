"""Central light and dark styling for CustomTkinter, ttk and charts."""

from __future__ import annotations

from tkinter import ttk
from typing import Any

import customtkinter as ctk


class ThemeManager:
    """Keeps application colors and ttk styles consistent between views."""

    VALID_MODES = ("Dark", "Light")

    def __init__(self, mode: str = "Dark") -> None:
        self._mode = self._clean_mode(mode)
        ctk.set_default_color_theme("blue")
        self.apply_mode(self._mode)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def is_dark(self) -> bool:
        return self._mode == "Dark"

    @property
    def colors(self) -> dict[str, tuple[str, str]]:
        # Tuples are ordered as light then dark for CustomTkinter.
        return {
            "app_bg": ("#f4f7fb", "#090d16"),
            "surface": ("#ffffff", "#111827"),
            "surface_alt": ("#eef3f8", "#0f172a"),
            "surface_hover": ("#f8fbff", "#172033"),
            "sidebar": ("#15324f", "#0f172a"),
            "sidebar_border": ("#0f2742", "#1e293b"),
            "sidebar_text": ("#f8fbff", "#f8fafc"),
            "sidebar_muted_text": ("#bfd0e3", "#9fb0c6"),
            "sidebar_subtle_text": ("#9fb4ca", "#72839b"),
            "sidebar_button": ("#21476f", "#16243b"),
            "sidebar_button_hover": ("#2c5c8a", "#1d4ed8"),
            "sidebar_button_active": ("#0f6cbd", "#2563eb"),
            "sidebar_button_active_hover": ("#115ea3", "#1d4ed8"),
            "sidebar_button_text": ("#f8fbff", "#eaf2ff"),
            "primary": ("#0f6cbd", "#2563eb"),
            "primary_hover": ("#115ea3", "#1d4ed8"),
            "primary_text": ("#ffffff", "#ffffff"),
            "secondary_button": ("#e4ebf5", "#334155"),
            "secondary_button_hover": ("#d1dceb", "#475569"),
            "secondary_text": ("#172033", "#f8fafc"),
            "input_bg": ("#ffffff", "#0f172a"),
            "input_border": ("#b8c7dc", "#334155"),
            "input_focus": ("#0f6cbd", "#3b82f6"),
            "muted_text": ("#47566b", "#9fb0c6"),
            "subtle_text": ("#6b7a90", "#72839b"),
            "border": ("#d7e1ee", "#263246"),
            "strong_border": ("#b8c7dc", "#334155"),
            "teal": ("#0f766e", "#0f766e"),
            "teal_hover": ("#115e59", "#115e59"),
            "danger": ("#b91c1c", "#b91c1c"),
            "danger_hover": ("#991b1b", "#991b1b"),
            "success": ("#0f766e", "#14b8a6"),
            "warning": ("#b45309", "#f59e0b"),
        }

    def value(self, key: str) -> str:
        light, dark = self.colors[key]
        return dark if self.is_dark else light

    def apply_mode(self, mode: str) -> None:
        self._mode = self._clean_mode(mode)
        ctk.set_appearance_mode(self._mode.lower())
        self.configure_ttk_styles()

    def configure_ttk_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        palette = self.table_palette()
        style.configure(
            "CIM.Treeview",
            background=palette["background"],
            fieldbackground=palette["background"],
            foreground=palette["foreground"],
            bordercolor=palette["border"],
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
            rowheight=34,
        )
        style.configure(
            "CIM.Treeview.Heading",
            background=palette["heading"],
            foreground=palette["heading_text"],
            bordercolor=palette["border"],
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 7),
        )
        style.map(
            "CIM.Treeview",
            background=[("selected", palette["selection"])],
            foreground=[("selected", palette["selected_text"])],
        )
        style.map(
            "CIM.Treeview.Heading",
            background=[("active", palette["heading_active"])],
        )
        for orientation in ("Vertical", "Horizontal"):
            style.configure(
                f"CIM.{orientation}.TScrollbar",
                background=palette["scroll_thumb"],
                troughcolor=palette["scroll_track"],
                bordercolor=palette["scroll_track"],
                arrowcolor=palette["foreground"],
                lightcolor=palette["scroll_thumb"],
                darkcolor=palette["scroll_thumb"],
                arrowsize=13,
                relief="flat",
                troughrelief="flat",
            )
            style.map(
                f"CIM.{orientation}.TScrollbar",
                background=[("active", palette["scroll_active"])],
            )

    def table_palette(self) -> dict[str, str]:
        if self.is_dark:
            return {
                "background": "#0f172a",
                "foreground": "#e2e8f0",
                "heading": "#24324a",
                "heading_active": "#2e3f5e",
                "heading_text": "#f8fafc",
                "border": "#24324a",
                "selection": "#2563eb",
                "selected_text": "#ffffff",
                "scroll_track": "#111827",
                "scroll_thumb": "#334155",
                "scroll_active": "#475569",
                "row_even": "#0f172a",
                "row_odd": "#111c31",
            }
        return {
            "background": "#ffffff",
            "foreground": "#172033",
            "heading": "#e6eef8",
            "heading_active": "#d6e5f5",
            "heading_text": "#1f2f46",
            "border": "#d7e1ee",
            "selection": "#0f6cbd",
            "selected_text": "#ffffff",
            "scroll_track": "#eef3f8",
            "scroll_thumb": "#9fb3cc",
            "scroll_active": "#6f8fb2",
            "row_even": "#ffffff",
            "row_odd": "#f7faff",
        }

    def configure_table_tags(self, table: ttk.Treeview) -> None:
        """Apply alternating row colors after the table has been created."""
        palette = self.table_palette()
        table.tag_configure("even", background=palette["row_even"])
        table.tag_configure("odd", background=palette["row_odd"])

    def chart_palette(self) -> dict[str, Any]:
        if self.is_dark:
            return {
                "surface": "#111827",
                "text": "#f8fafc",
                "ticks": "#cbd5e1",
                "axis": "#475569",
                "grid": "#24324a",
                "severity": ["#38bdf8", "#22c55e", "#f59e0b", "#ef4444"],
                "status": "#14b8a6",
            }
        return {
            "surface": "#ffffff",
            "text": "#172033",
            "ticks": "#40536d",
            "axis": "#9bb0cc",
            "grid": "#d8e4f4",
            "severity": ["#0f6cbd", "#008a00", "#ffaa44", "#c50f1f"],
            "status": "#0052cc",
        }

    def _clean_mode(self, mode: str) -> str:
        normalized = str(mode or "Dark").title()
        return normalized if normalized in self.VALID_MODES else "Dark"
