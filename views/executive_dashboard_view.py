"""Executive dashboard with complementary indicators."""

from __future__ import annotations

from tkinter import ttk

import customtkinter as ctk

from controllers.executive_dashboard_controller import ExecutiveDashboardController
from models.user import User
from utils.table_helpers import add_scrollbars, configure_columns, fit_columns
from utils.theme_manager import ThemeManager


class ExecutiveDashboardView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        controller: ExecutiveDashboardController,
        actor: User,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._controller = controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._cards: dict[str, ctk.CTkLabel] = {}
        self._build()
        self._refresh()

    def _build(self) -> None:
        colors = self._theme_manager.colors
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, pady=(0, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="Dashboard Executivo",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=4, sticky="w")
        ctk.CTkButton(
            header,
            text="Atualizar",
            command=self._refresh,
            width=112,
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        ).grid(row=0, column=1, sticky="e")

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, pady=(0, 14), sticky="ew")
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._metric_card(cards, "Mais incidentes atribuidos", "top_assignee", 0)
        self._metric_card(cards, "Ataque mais frequente", "top_attack", 1)
        self._metric_card(cards, "Severidade mais comum", "common_severity", 2)
        self._metric_card(cards, "Mais resolvidos", "most_resolved", 3)

        table_frame = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
        )
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            table_frame,
            text="Total de incidentes por responsavel",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=18, pady=(18, 10), sticky="w")

        self._widths = {"responsavel": 320, "total": 120, "resolvidos": 140}
        self._table = ttk.Treeview(
            table_frame,
            columns=("responsavel", "total", "resolvidos"),
            show="headings",
            style="CIM.Treeview",
        )
        configure_columns(
            self._table,
            {"responsavel": "Responsavel", "total": "Atribuidos", "resolvidos": "Resolvidos"},
            self._widths,
            {"total", "resolvidos"},
        )
        self._theme_manager.configure_table_tags(self._table)
        add_scrollbars(self._table, table_frame, 1, 0)

    def _metric_card(self, parent: ctk.CTkFrame, title: str, key: str, column: int) -> None:
        colors = self._theme_manager.colors
        card = ctk.CTkFrame(
            parent,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
        )
        card.grid(row=0, column=column, padx=(0 if column == 0 else 8, 0), sticky="ew")
        ctk.CTkLabel(card, text=title, text_color=colors["muted_text"]).pack(
            anchor="w",
            padx=16,
            pady=(14, 4),
        )
        value = ctk.CTkLabel(card, text="-", font=ctk.CTkFont(size=18, weight="bold"))
        value.pack(anchor="w", padx=16, pady=(0, 14))
        self._cards[key] = value

    def _refresh(self) -> None:
        data = self._controller.get_executive_data(self._actor)
        for key in ("top_assignee", "top_attack", "common_severity", "most_resolved"):
            item = data[key]
            self._cards[key].configure(text=f"{item['nome']} ({item['total']})")

        for item_id in self._table.get_children():
            self._table.delete(item_id)
        for index, row in enumerate(data["by_responsible"]):
            self._table.insert(
                "",
                "end",
                values=(row["responsavel"], row["total"], row["resolvidos"] or 0),
                tags=("odd" if index % 2 else "even",),
            )
        fit_columns(self._table, self._widths)
