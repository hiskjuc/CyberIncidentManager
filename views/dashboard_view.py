"""Application shell and dashboard view."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from controllers.auth_controller import AuthController
from controllers.dashboard_controller import DashboardController
from controllers.executive_dashboard_controller import ExecutiveDashboardController
from controllers.incident_controller import IncidentController
from controllers.knowledge_controller import KnowledgeController
from controllers.search_controller import SearchController
from models.user import User
from utils.helpers import center_window
from utils.table_helpers import add_scrollbars, configure_columns, fit_columns, format_table_text
from utils.theme_manager import ThemeManager
from views.executive_dashboard_view import ExecutiveDashboardView
from views.global_search_view import GlobalSearchView
from views.incidents_view import IncidentsView
from views.knowledge_base_view import KnowledgeBaseView
from views.login_view import LoginView
from views.settings_view import SettingsView
from views.users_view import UsersView


class CyberIncidentManagerApp(ctk.CTk):
    def __init__(
        self,
        auth_controller: AuthController,
        incident_controller: IncidentController,
        dashboard_controller: DashboardController,
        search_controller: SearchController,
        executive_dashboard_controller: ExecutiveDashboardController,
        knowledge_controller: KnowledgeController,
    ) -> None:
        super().__init__()
        self._theme_manager = ThemeManager()
        self._auth_controller = auth_controller
        self._incident_controller = incident_controller
        self._dashboard_controller = dashboard_controller
        self._search_controller = search_controller
        self._executive_dashboard_controller = executive_dashboard_controller
        self._knowledge_controller = knowledge_controller
        self.title("Cyber Incident Manager")
        self.configure(fg_color=self._theme_manager.colors["app_bg"])
        self.minsize(1080, 660)
        width = min(1360, max(1080, self.winfo_screenwidth() - 46))
        height = min(860, max(660, self.winfo_screenheight() - 92))
        center_window(self, width, height)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._show_login()

    def _clear_root(self) -> None:
        for child in self.winfo_children():
            child.destroy()

    def _show_login(self) -> None:
        self._clear_root()
        self.configure(fg_color=self._theme_manager.colors["app_bg"])
        LoginView(self, self._auth_controller, self._open_workspace, self._theme_manager).pack(
            fill="both",
            expand=True,
        )

    def _open_workspace(self, user: User) -> None:
        self._theme_manager.apply_mode(user.theme_preference)
        self.configure(fg_color=self._theme_manager.colors["app_bg"])
        self._clear_root()
        WorkspaceShell(
            self,
            user,
            self._auth_controller,
            self._incident_controller,
            self._dashboard_controller,
            self._search_controller,
            self._executive_dashboard_controller,
            self._knowledge_controller,
            self._show_login,
            self._theme_manager,
        ).pack(fill="both", expand=True)

    def _close(self) -> None:
        self._auth_controller.logout()
        self.destroy()


class WorkspaceShell(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        user: User,
        auth_controller: AuthController,
        incident_controller: IncidentController,
        dashboard_controller: DashboardController,
        search_controller: SearchController,
        executive_dashboard_controller: ExecutiveDashboardController,
        knowledge_controller: KnowledgeController,
        on_logout: Callable[[], None],
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color=theme_manager.colors["app_bg"])
        self._user = user
        self._auth_controller = auth_controller
        self._incident_controller = incident_controller
        self._dashboard_controller = dashboard_controller
        self._search_controller = search_controller
        self._executive_dashboard_controller = executive_dashboard_controller
        self._knowledge_controller = knowledge_controller
        self._on_logout = on_logout
        self._theme_manager = theme_manager
        self._current_page = "dashboard"
        self._content: ctk.CTkFrame | None = None
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._build()
        self._show_current_page()

    def _build(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._nav_buttons.clear()
        colors = self._theme_manager.colors
        sidebar = ctk.CTkFrame(
            self,
            width=270,
            corner_radius=0,
            fg_color=colors["sidebar"],
            border_width=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(12, weight=1)

        ctk.CTkFrame(sidebar, height=4, corner_radius=0, fg_color=colors["primary"]).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        ctk.CTkLabel(
            sidebar,
            text="Cyber Incident\nManager",
            justify="left",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["sidebar_text"],
        ).grid(row=1, column=0, padx=22, pady=(28, 18), sticky="w")

        ctk.CTkLabel(
            sidebar,
            text=f"{self._user.nome}\n{self._user.user_type} - {self._user.cargo}",
            justify="left",
            wraplength=205,
            text_color=colors["sidebar_muted_text"],
        ).grid(row=2, column=0, padx=22, pady=(0, 24), sticky="w")

        self._nav_button(sidebar, "Dashboard", "dashboard", self._show_dashboard, 3)
        self._nav_button(sidebar, "Incidentes", "incidents", self._show_incidents, 4)
        if self._user.can_manage_users():
            self._nav_button(sidebar, "Usuarios", "users", self._show_users, 5)
        self._nav_button(sidebar, "Pesquisa Global", "search", self._show_global_search, 6)
        self._nav_button(
            sidebar,
            "Dashboard Executivo",
            "executive_dashboard",
            self._show_executive_dashboard,
            7,
        )
        self._nav_button(
            sidebar,
            "Base de Conhecimento",
            "knowledge_base",
            self._show_knowledge_base,
            8,
        )
        self._nav_button(sidebar, "Configuracoes", "settings", self._show_settings, 9)

        ctk.CTkLabel(
            sidebar,
            text=self._user.role_description(),
            wraplength=205,
            justify="left",
            text_color=colors["sidebar_subtle_text"],
        ).grid(row=12, column=0, padx=22, pady=18, sticky="sw")

        ctk.CTkButton(
            sidebar,
            text="Sair",
            command=self._logout,
            height=40,
            fg_color=colors["secondary_button"],
            hover_color=colors["secondary_button_hover"],
            text_color=colors["secondary_text"],
        ).grid(row=13, column=0, padx=22, pady=(0, 26), sticky="ew")

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.grid(row=0, column=1, padx=28, pady=26, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

    def _nav_button(
        self,
        parent: ctk.CTkFrame,
        label: str,
        page_key: str,
        command: Callable[[], None],
        row: int,
    ) -> None:
        button = ctk.CTkButton(
            parent,
            text=label,
            command=command,
            anchor="w",
            height=42,
            corner_radius=6,
            text_color=self._theme_manager.colors["sidebar_button_text"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        button.grid(row=row, column=0, padx=22, pady=5, sticky="ew")
        self._nav_buttons[page_key] = button
        self._sync_nav_buttons()

    def _show_page(self, page: ctk.CTkFrame) -> None:
        if self._content is None:
            return
        for child in self._content.winfo_children():
            if child is not page:
                child.destroy()
        page.grid(row=0, column=0, sticky="nsew")
        self._sync_nav_buttons()

    def _show_current_page(self) -> None:
        if self._current_page == "dashboard":
            self._show_dashboard()
        elif self._current_page == "incidents":
            self._show_incidents()
        elif self._current_page == "users" and self._user.can_manage_users():
            self._show_users()
        elif self._current_page == "search":
            self._show_global_search()
        elif self._current_page == "executive_dashboard":
            self._show_executive_dashboard()
        elif self._current_page == "knowledge_base":
            self._show_knowledge_base()
        else:
            self._show_settings()

    def _show_dashboard(self) -> None:
        if self._content is not None:
            self._current_page = "dashboard"
            self._show_page(
                DashboardHomeView(
                    self._content,
                    self._dashboard_controller,
                    self._user,
                    self._theme_manager,
                )
            )

    def _show_incidents(self) -> None:
        if self._content is not None:
            self._current_page = "incidents"
            self._show_page(
                IncidentsView(
                    self._content,
                    self._incident_controller,
                    self._auth_controller,
                    self._user,
                    self._theme_manager,
                )
            )

    def _show_users(self) -> None:
        if self._content is not None:
            self._current_page = "users"
            self._show_page(
                UsersView(self._content, self._auth_controller, self._user, self._theme_manager)
            )

    def _show_global_search(self) -> None:
        if self._content is not None:
            self._current_page = "search"
            self._show_page(
                GlobalSearchView(
                    self._content,
                    self._search_controller,
                    self._user,
                    self._theme_manager,
                )
            )

    def _show_executive_dashboard(self) -> None:
        if self._content is not None:
            self._current_page = "executive_dashboard"
            self._show_page(
                ExecutiveDashboardView(
                    self._content,
                    self._executive_dashboard_controller,
                    self._user,
                    self._theme_manager,
                )
            )

    def _show_knowledge_base(self) -> None:
        if self._content is not None:
            self._current_page = "knowledge_base"
            self._show_page(
                KnowledgeBaseView(
                    self._content,
                    self._knowledge_controller,
                    self._user,
                    self._theme_manager,
                )
            )

    def _show_settings(self) -> None:
        if self._content is not None:
            self._current_page = "settings"
            self._show_page(
                SettingsView(
                    self._content,
                    self._auth_controller,
                    self._user,
                    self._theme_manager,
                    self._apply_theme,
                )
            )

    def _apply_theme(self, theme: str) -> None:
        current_page = self._current_page
        self._theme_manager.apply_mode(theme)
        self._current_page = current_page
        colors = self._theme_manager.colors
        self.configure(fg_color=colors["app_bg"])
        self.master.configure(fg_color=colors["app_bg"])
        for child in self.winfo_children():
            child.destroy()
        self._content = None
        self._build()
        self._show_current_page()

    def _sync_nav_buttons(self) -> None:
        colors = self._theme_manager.colors
        for page_key, button in self._nav_buttons.items():
            is_active = page_key == self._current_page
            button.configure(
                fg_color=(
                    colors["sidebar_button_active"] if is_active else colors["sidebar_button"]
                ),
                hover_color=(
                    colors["sidebar_button_active_hover"]
                    if is_active
                    else colors["sidebar_button_hover"]
                ),
            )

    def _logout(self) -> None:
        self._auth_controller.logout()
        self._on_logout()


class DashboardHomeView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        dashboard_controller: DashboardController,
        actor: User,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._dashboard_controller = dashboard_controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._chart_canvas: FigureCanvasTkAgg | None = None
        self._metric_labels: dict[str, ctk.CTkLabel] = {}
        self._build()
        self._refresh()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, pady=(0, 16), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        colors = self._theme_manager.colors
        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            header,
            text="Atualizar",
            command=self._refresh,
            width=112,
            height=36,
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        ).grid(row=0, column=1, sticky="e")

        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=1, column=0, columnspan=2, pady=(0, 14), sticky="ew")
        metrics.grid_columnconfigure((0, 1, 2), weight=1)
        self._metric_card(metrics, "Total de incidentes", "total", "#2563eb", 0)
        self._metric_card(metrics, "Incidentes criticos", "criticos", "#dc2626", 1)
        self._metric_card(metrics, "Resolvidos", "resolvidos", "#0f766e", 2)

        self._chart_frame = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        self._chart_frame.grid(row=2, column=0, padx=(0, 14), sticky="nsew")
        self._chart_frame.grid_columnconfigure(0, weight=1)
        self._chart_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            self._chart_frame,
            text="Distribuicao dos incidentes",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=18, pady=(18, 4), sticky="w")

        recent_frame = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        recent_frame.grid(row=2, column=1, sticky="nsew")
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            recent_frame,
            text="Ultimos incidentes",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=18, pady=(18, 10), sticky="w")

        self._recent_table = ttk.Treeview(
            recent_frame,
            columns=("id", "titulo", "severidade", "status", "data", "resp"),
            show="headings",
            style="CIM.Treeview",
        )
        headings = {
            "id": "ID",
            "titulo": "Titulo",
            "severidade": "Severidade",
            "status": "Status",
            "data": "Data",
            "resp": "Responsavel",
        }
        self._recent_widths = {
            "id": 58,
            "titulo": 200,
            "severidade": 110,
            "status": 126,
            "data": 108,
            "resp": 180,
        }
        configure_columns(self._recent_table, headings, self._recent_widths, {"id"})
        self._theme_manager.configure_table_tags(self._recent_table)
        add_scrollbars(self._recent_table, recent_frame, 1, 0)

    def _metric_card(
        self,
        parent: ctk.CTkFrame,
        title: str,
        key: str,
        accent: str,
        column: int,
    ) -> None:
        card = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color=self._theme_manager.colors["surface"],
            border_width=1,
            border_color=self._theme_manager.colors["border"],
        )
        card.grid(row=0, column=column, padx=(0 if column == 0 else 7, 0), sticky="ew")
        ctk.CTkFrame(card, height=4, corner_radius=0, fg_color=accent).pack(fill="x")
        ctk.CTkLabel(card, text=title, text_color=self._theme_manager.colors["muted_text"]).pack(
            anchor="w",
            padx=18,
            pady=(16, 5),
        )
        label = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=34, weight="bold"))
        label.pack(anchor="w", padx=18, pady=(0, 16))
        self._metric_labels[key] = label

    def _refresh(self) -> None:
        data = self._dashboard_controller.get_dashboard_data(self._actor)
        metrics = data["metrics"]
        for key, label in self._metric_labels.items():
            label.configure(text=str(metrics[key]))

        for item_id in self._recent_table.get_children():
            self._recent_table.delete(item_id)
        for index, row in enumerate(data["recent_incidents"]):
            self._recent_table.insert(
                "",
                "end",
                values=(
                    row["id"],
                    format_table_text(row["titulo"], 58),
                    row["severidade"],
                    row["status"],
                    row["data_incidente"],
                    format_table_text(row["responsavel"], 38),
                ),
                tags=("odd" if index % 2 else "even",),
            )
        fit_columns(self._recent_table, self._recent_widths)

        self._draw_chart(data["severity_counts"], data["status_counts"])

    def _draw_chart(self, severity_counts: dict[str, int], status_counts: dict[str, int]) -> None:
        if self._chart_canvas is not None:
            self._chart_canvas.get_tk_widget().destroy()

        palette = self._theme_manager.chart_palette()
        figure = Figure(figsize=(7.2, 4.8), dpi=100, facecolor=palette["surface"])
        severity_axis, status_axis = figure.subplots(1, 2)
        for axis in (severity_axis, status_axis):
            axis.set_facecolor(palette["surface"])
            axis.tick_params(colors=palette["ticks"], labelsize=9)
            axis.spines[["top", "right", "left"]].set_visible(False)
            axis.spines["bottom"].set_color(palette["axis"])
            axis.grid(axis="y", color=palette["grid"], linewidth=0.7)
            axis.set_axisbelow(True)

        severity_axis.bar(
            list(severity_counts.keys()),
            list(severity_counts.values()),
            color=palette["severity"],
            width=0.62,
        )
        severity_axis.set_title("Por severidade", color=palette["text"], fontsize=11)
        severity_axis.tick_params(axis="x", rotation=25)

        status_axis.barh(
            list(status_counts.keys()),
            list(status_counts.values()),
            color=palette["status"],
            height=0.55,
        )
        status_axis.set_title("Por status", color=palette["text"], fontsize=11)
        status_axis.grid(axis="x", color=palette["grid"], linewidth=0.7)
        status_axis.grid(axis="y", visible=False)

        figure.tight_layout(pad=2)
        self._chart_canvas = FigureCanvasTkAgg(figure, master=self._chart_frame)
        self._chart_canvas.draw()
        self._chart_canvas.get_tk_widget().grid(
            row=1,
            column=0,
            padx=12,
            pady=(0, 12),
            sticky="nsew",
        )
