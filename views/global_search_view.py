"""Global search view for users, incidents and IPs."""

from __future__ import annotations

from tkinter import ttk

import customtkinter as ctk

from controllers.search_controller import SearchController
from models.user import User
from utils.table_helpers import add_scrollbars, configure_columns, fit_columns, format_table_text
from utils.theme_manager import ThemeManager


class GlobalSearchView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        search_controller: SearchController,
        actor: User,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._search_controller = search_controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._search_var = ctk.StringVar()
        self._build()
        self._search_var.trace_add("write", lambda *_args: self._refresh())

    def _build(self) -> None:
        colors = self._theme_manager.colors
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self,
            text="Pesquisa Global",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=4, pady=(0, 14), sticky="w")

        search_bar = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
        )
        search_bar.grid(row=1, column=0, pady=(0, 14), sticky="ew")
        search_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(
            search_bar,
            textvariable=self._search_var,
            placeholder_text="Buscar incidentes, usuarios ou IPs",
            height=40,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
        ).grid(row=0, column=0, padx=16, pady=16, sticky="ew")

        tabs = ctk.CTkTabview(
            self,
            fg_color=colors["surface"],
            segmented_button_fg_color=colors["secondary_button"],
            segmented_button_selected_color=colors["primary"],
            segmented_button_selected_hover_color=colors["primary_hover"],
        )
        tabs.grid(row=2, column=0, sticky="nsew")
        for name in ("Incidentes", "Usuarios", "IPs"):
            tabs.add(name)
            tabs.tab(name).grid_columnconfigure(0, weight=1)
            tabs.tab(name).grid_rowconfigure(0, weight=1)

        self._incident_table = self._make_table(
            tabs.tab("Incidentes"),
            ("id", "titulo", "ataque", "status", "ip", "responsavel"),
            {
                "id": "ID",
                "titulo": "Titulo",
                "ataque": "Ataque",
                "status": "Status",
                "ip": "IP",
                "responsavel": "Responsavel",
            },
            {
                "id": 60,
                "titulo": 300,
                "ataque": 170,
                "status": 130,
                "ip": 160,
                "responsavel": 240,
            },
        )
        self._user_table = self._make_table(
            tabs.tab("Usuarios"),
            ("id", "nome", "username", "cargo", "tipo"),
            {
                "id": "ID",
                "nome": "Nome",
                "username": "Username",
                "cargo": "Cargo",
                "tipo": "Tipo",
            },
            {"id": 60, "nome": 260, "username": 180, "cargo": 260, "tipo": 160},
        )
        self._ip_table = self._make_table(
            tabs.tab("IPs"),
            ("ip", "total", "ultimo"),
            {"ip": "IP", "total": "Total", "ultimo": "Ultimo incidente"},
            {"ip": 220, "total": 120, "ultimo": 180},
        )

    def _make_table(
        self,
        parent: ctk.CTkFrame,
        columns: tuple[str, ...],
        headings: dict[str, str],
        widths: dict[str, int],
    ) -> ttk.Treeview:
        table = ttk.Treeview(parent, columns=columns, show="headings", style="CIM.Treeview")
        configure_columns(table, headings, widths, {"id", "total"})
        self._theme_manager.configure_table_tags(table)
        table._cim_widths = widths  # type: ignore[attr-defined]
        add_scrollbars(table, parent, 0, 0, padx=(12, 0), pady=(12, 12))
        return table

    def _refresh(self) -> None:
        results = self._search_controller.global_search(self._actor, self._search_var.get())
        self._fill_table(
            self._incident_table,
            [
                (
                    row["id"],
                    format_table_text(row["titulo"], 90),
                    row["tipo_ataque"],
                    row["status"],
                    row["ip_relacionado"],
                    format_table_text(row["responsavel"], 80),
                )
                for row in results["incidentes"]
            ],
        )
        self._fill_table(
            self._user_table,
            [
                (row["id"], row["nome"], row["username"], row["cargo"], row["tipo_usuario"])
                for row in results["usuarios"]
            ],
        )
        self._fill_table(
            self._ip_table,
            [
                (row["ip_relacionado"], row["total"], row["ultimo_incidente"])
                for row in results["ips"]
            ],
        )

    def _fill_table(self, table: ttk.Treeview, rows: list[tuple]) -> None:
        for item_id in table.get_children():
            table.delete(item_id)
        for index, values in enumerate(rows):
            table.insert("", "end", values=values, tags=("odd" if index % 2 else "even",))
        fit_columns(table, table._cim_widths)  # type: ignore[attr-defined]
