"""Session information and appearance preferences view."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk

from controllers.auth_controller import AuthController
from models.user import User
from utils.theme_manager import ThemeManager


class SettingsView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        auth_controller: AuthController,
        actor: User,
        theme_manager: ThemeManager,
        on_theme_change: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._auth_controller = auth_controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._on_theme_change = on_theme_change
        self._theme_var = ctk.StringVar(value=theme_manager.mode)
        self._theme_status_var = ctk.StringVar(value=self._theme_caption(theme_manager.mode))
        self._build()

    def _build(self) -> None:
        colors = self._theme_manager.colors
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=4, pady=(0, 16), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Configuracoes",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="Sessao ativa e preferencias visuais",
            text_color=colors["muted_text"],
        ).grid(row=1, column=0, pady=(4, 0), sticky="w")

        theme_badge = ctk.CTkFrame(
            header,
            fg_color=colors["surface_alt"],
            corner_radius=6,
        )
        theme_badge.grid(row=0, column=1, rowspan=2, padx=(16, 0), sticky="e")
        ctk.CTkLabel(
            theme_badge,
            text=self._theme_caption(self._theme_manager.mode),
            text_color=colors["muted_text"],
            height=28,
        ).pack(padx=12, pady=2)

        session_card = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        session_card.grid(row=1, column=0, pady=(0, 14), sticky="ew")
        session_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            session_card,
            text="Informacoes da sessao",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=22, pady=(20, 14), sticky="w")

        login_at = self._auth_controller.current_login_at
        user = self._auth_controller.current_user or self._actor
        session_items = (
            ("Nome do usuario logado", user.nome),
            ("Username", user.username),
            ("Cargo", user.cargo),
            ("Tipo de usuario", user.user_type),
            (
                "Data/hora do login atual",
                login_at.strftime("%d/%m/%Y %H:%M:%S") if login_at else "-",
            ),
        )
        for index, (label, value) in enumerate(session_items):
            row = 1 + index // 2
            column = index % 2
            field = ctk.CTkFrame(session_card, fg_color="transparent")
            field.grid(
                row=row,
                column=column,
                padx=(22, 10 if column == 0 else 22),
                pady=(0, 16),
                sticky="ew",
            )
            ctk.CTkLabel(field, text=label, text_color=colors["muted_text"]).pack(
                anchor="w"
            )
            ctk.CTkLabel(
                field,
                text=value,
                anchor="w",
                font=ctk.CTkFont(size=15, weight="bold"),
                wraplength=360,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))

        appearance_card = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        appearance_card.grid(row=2, column=0, sticky="new")
        appearance_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            appearance_card,
            text="Aparencia",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=22, pady=(20, 6), sticky="w")
        ctk.CTkLabel(
            appearance_card,
            text=f"Tema salvo para {user.username}",
            text_color=colors["muted_text"],
        ).grid(row=1, column=0, padx=22, pady=(0, 16), sticky="w")

        toggle_line = ctk.CTkFrame(appearance_card, fg_color="transparent")
        toggle_line.grid(row=2, column=0, padx=22, pady=(0, 22), sticky="ew")
        toggle_line.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            toggle_line,
            textvariable=self._theme_status_var,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        self._theme_switch = ctk.CTkSwitch(
            toggle_line,
            text="Light Mode",
            command=self._toggle_theme,
            onvalue="Light",
            offvalue="Dark",
            variable=self._theme_var,
            fg_color=colors["secondary_button"],
            progress_color=colors["primary"],
            button_color=colors["surface"],
            button_hover_color=colors["surface_alt"],
            text_color=colors["muted_text"],
        )
        self._theme_switch.grid(row=0, column=1, sticky="e")

    def _toggle_theme(self) -> None:
        theme = self._theme_var.get()
        try:
            self._auth_controller.save_theme_preference(self._actor, theme)
        except (PermissionError, ValueError) as exc:
            messagebox.showerror("Tema nao salvo", str(exc))
            self._theme_var.set(self._theme_manager.mode)
            self._theme_status_var.set(self._theme_caption(self._theme_manager.mode))
            return
        self._theme_status_var.set(self._theme_caption(theme))
        self._on_theme_change(theme)

    def _theme_caption(self, theme: str) -> str:
        return "Light Mode ativo" if theme == "Light" else "Dark Mode ativo"
