"""Login screen."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from controllers.auth_controller import AuthController
from models.user import User
from utils.theme_manager import ThemeManager
from utils.validators import ValidationError


class LoginView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        auth_controller: AuthController,
        on_login: Callable[[User], None],
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color=theme_manager.colors["app_bg"])
        self._auth_controller = auth_controller
        self._on_login = on_login
        self._theme_manager = theme_manager
        self._status_var = ctk.StringVar(value="")
        self._username_var = ctk.StringVar()
        self._password_var = ctk.StringVar()
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        colors = self._theme_manager.colors
        panel = ctk.CTkFrame(
            self,
            width=420,
            height=470,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["strong_border"],
        )
        panel.grid(row=0, column=0)
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Cyber Incident Manager",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, padx=34, pady=(44, 8), sticky="w")

        ctk.CTkLabel(
            panel,
            text="Acesso ao centro de incidentes",
            font=ctk.CTkFont(size=14),
            text_color=colors["muted_text"],
        ).grid(row=1, column=0, padx=34, pady=(0, 30), sticky="w")

        self._username_entry = ctk.CTkEntry(
            panel,
            textvariable=self._username_var,
            placeholder_text="Username",
            height=42,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
        )
        self._username_entry.grid(row=2, column=0, padx=34, pady=8, sticky="ew")

        password_entry = ctk.CTkEntry(
            panel,
            textvariable=self._password_var,
            placeholder_text="Senha",
            show="*",
            height=42,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
        )
        password_entry.grid(row=3, column=0, padx=34, pady=8, sticky="ew")
        password_entry.bind("<Return>", lambda _event: self._submit())

        ctk.CTkButton(
            panel,
            text="Entrar",
            command=self._submit,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        ).grid(row=4, column=0, padx=34, pady=(18, 10), sticky="ew")

        ctk.CTkLabel(
            panel,
            textvariable=self._status_var,
            text_color="#fca5a5",
            wraplength=335,
            justify="left",
        ).grid(row=5, column=0, padx=34, pady=(2, 10), sticky="w")

        ctk.CTkLabel(
            panel,
            text="Entre com suas credenciais.",
            text_color=colors["subtle_text"],
            font=ctk.CTkFont(size=12),
        ).grid(row=6, column=0, padx=34, pady=(26, 0), sticky="w")

        self.after(120, self._username_entry.focus_set)

    def _submit(self) -> None:
        self._status_var.set("")
        try:
            user = self._auth_controller.login(
                self._username_var.get(),
                self._password_var.get(),
            )
        except (PermissionError, ValidationError) as exc:
            self._status_var.set(str(exc))
            return

        self._password_var.set("")
        self._on_login(user)
