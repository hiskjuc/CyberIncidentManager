"""Administrator user registration view."""

from __future__ import annotations

from tkinter import messagebox, ttk

import customtkinter as ctk

from controllers.auth_controller import AuthController
from models.user import User
from utils.table_helpers import add_scrollbars, configure_columns, fit_columns, format_table_text
from utils.theme_manager import ThemeManager
from utils.validators import ALLOWED_USER_TYPES, ValidationError


class UsersView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        auth_controller: AuthController,
        actor: User,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._auth_controller = auth_controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._selected_user_id: int | None = None
        self._users_by_id: dict[str, User] = {}
        self._name_var = ctk.StringVar()
        self._username_var = ctk.StringVar()
        self._password_var = ctk.StringVar()
        self._job_var = ctk.StringVar()
        self._role_var = ctk.StringVar(value=ALLOWED_USER_TYPES[1])
        self._feedback_var = ctk.StringVar(value="")
        self._build()
        self._refresh_table()

    def _build(self) -> None:
        colors = self._theme_manager.colors
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Usuarios",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=4, pady=(0, 16), sticky="w")
        self._feedback_label = ctk.CTkLabel(
            self,
            textvariable=self._feedback_var,
            text_color=colors["success"],
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._feedback_label.grid(row=0, column=1, padx=4, pady=(0, 16), sticky="e")

        form = ctk.CTkScrollableFrame(
            self,
            width=344,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        form.grid(row=1, column=0, padx=(0, 14), pady=0, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form,
            text="Cadastro e edicao",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=18, pady=(18, 14), sticky="w")

        self._entry(form, "Nome", self._name_var, 1)
        self._entry(form, "Username", self._username_var, 2)
        self._entry(form, "Senha", self._password_var, 3, show="*")
        self._entry(form, "Cargo", self._job_var, 4)

        ctk.CTkLabel(form, text="Tipo de usuario").grid(
            row=9,
            column=0,
            padx=18,
            pady=(10, 4),
            sticky="w",
        )
        ctk.CTkOptionMenu(
            form,
            values=list(ALLOWED_USER_TYPES),
            variable=self._role_var,
            height=38,
            fg_color=colors["secondary_button"],
            button_color=colors["primary"],
            button_hover_color=colors["primary_hover"],
            text_color=colors["secondary_text"],
        ).grid(row=10, column=0, padx=18, pady=(0, 10), sticky="ew")

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=11, column=0, padx=18, pady=(12, 18), sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            actions,
            text="Criar usuario",
            command=self._create_user,
            height=38,
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        ).grid(row=0, column=0, padx=(0, 6), pady=(0, 8), sticky="ew")
        ctk.CTkButton(
            actions,
            text="Editar",
            command=self._update_user,
            height=38,
            fg_color=colors["teal"],
            hover_color=colors["teal_hover"],
        ).grid(row=0, column=1, padx=(6, 0), pady=(0, 8), sticky="ew")
        ctk.CTkButton(
            actions,
            text="Excluir",
            command=self._delete_user,
            height=38,
            fg_color=colors["danger"],
            hover_color=colors["danger_hover"],
        ).grid(row=1, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(
            actions,
            text="Limpar",
            command=self._clear_form,
            height=38,
            fg_color=colors["secondary_button"],
            hover_color=colors["secondary_button_hover"],
            text_color=colors["secondary_text"],
        ).grid(row=1, column=1, padx=(6, 0), sticky="ew")

        self._create_button = actions.grid_slaves(row=0, column=0)[0]

        ctk.CTkLabel(
            form,
            text="Na edicao, deixe a senha vazia para manter a senha atual.",
            text_color=colors["subtle_text"],
            font=ctk.CTkFont(size=12),
            wraplength=285,
            justify="left",
        ).grid(row=12, column=0, padx=18, pady=(0, 18), sticky="w")

        table_frame = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        table_frame.grid(row=1, column=1, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            table_frame,
            text="Equipe cadastrada",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=18, pady=(18, 10), sticky="w")

        self._table = ttk.Treeview(
            table_frame,
            columns=("id", "nome", "username", "cargo", "tipo"),
            show="headings",
            selectmode="browse",
            style="CIM.Treeview",
        )
        headings = {
            "id": "ID",
            "nome": "Nome",
            "username": "Username",
            "cargo": "Cargo",
            "tipo": "Tipo",
        }
        self._column_widths = {
            "id": 60,
            "nome": 220,
            "username": 170,
            "cargo": 230,
            "tipo": 170,
        }
        configure_columns(self._table, headings, self._column_widths, {"id"})
        self._theme_manager.configure_table_tags(self._table)
        self._table.bind("<<TreeviewSelect>>", self._on_table_select)
        add_scrollbars(self._table, table_frame, 1, 0)

    def _entry(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.StringVar,
        row: int,
        show: str | None = None,
    ) -> None:
        ctk.CTkLabel(parent, text=label).grid(
            row=row * 2 - 1,
            column=0,
            padx=18,
            pady=(8, 4),
            sticky="w",
        )
        ctk.CTkEntry(
            parent,
            textvariable=variable,
            show=show,
            height=38,
            fg_color=self._theme_manager.colors["input_bg"],
            border_color=self._theme_manager.colors["input_border"],
        ).grid(
            row=row * 2,
            column=0,
            padx=18,
            pady=(0, 4),
            sticky="ew",
        )

    def _create_user(self) -> None:
        payload = {
            "nome": self._name_var.get(),
            "username": self._username_var.get(),
            "password": self._password_var.get(),
            "cargo": self._job_var.get(),
            "tipo_usuario": self._role_var.get(),
        }
        try:
            user = self._auth_controller.create_user(self._actor, payload)
        except (PermissionError, ValidationError) as exc:
            self._notify(False, f"Erro ao criar usuario: {exc}")
            messagebox.showerror("Cadastro recusado", str(exc))
            return

        self._notify(True, f"Operacao realizada com sucesso: {user.nome} cadastrado.")
        messagebox.showinfo("Usuario criado", f"{user.nome} foi cadastrado.")
        self._clear_form()
        self._refresh_table()

    def _update_user(self) -> None:
        if self._selected_user_id is None:
            messagebox.showwarning("Selecao necessaria", "Selecione um usuario para editar.")
            return

        payload = {
            "nome": self._name_var.get(),
            "password": self._password_var.get(),
            "cargo": self._job_var.get(),
            "tipo_usuario": self._role_var.get(),
        }
        try:
            user = self._auth_controller.update_user(
                self._actor,
                self._selected_user_id,
                payload,
            )
        except (PermissionError, ValidationError, ValueError) as exc:
            self._notify(False, f"Erro ao editar usuario: {exc}")
            messagebox.showerror("Edicao recusada", str(exc))
            return

        self._notify(True, f"Operacao realizada com sucesso: {user.nome} atualizado.")
        messagebox.showinfo("Usuario editado", f"{user.nome} foi atualizado.")
        self._clear_form()
        self._refresh_table()

    def _delete_user(self) -> None:
        if self._selected_user_id is None:
            messagebox.showwarning("Selecao necessaria", "Selecione um usuario para excluir.")
            return

        user = self._users_by_id.get(str(self._selected_user_id))
        label = user.username if user else f"#{self._selected_user_id}"
        confirmed = messagebox.askyesno(
            "Confirmar exclusao",
            f"Excluir o usuario {label}?",
        )
        if not confirmed:
            return

        try:
            self._auth_controller.delete_user(self._actor, self._selected_user_id)
        except (PermissionError, ValueError) as exc:
            self._notify(False, f"Erro ao excluir usuario: {exc}")
            messagebox.showerror("Exclusao recusada", str(exc))
            return

        self._notify(True, "Operacao realizada com sucesso: usuario removido.")
        messagebox.showinfo("Usuario excluido", "O usuario foi removido.")
        self._clear_form()
        self._refresh_table()

    def _refresh_table(self) -> None:
        for item_id in self._table.get_children():
            self._table.delete(item_id)
        self._users_by_id.clear()

        for index, user in enumerate(self._auth_controller.list_users(self._actor)):
            item_id = str(user.id)
            self._users_by_id[item_id] = user
            self._table.insert(
                "",
                "end",
                iid=item_id,
                values=(
                    user.id,
                    format_table_text(user.nome, 70),
                    format_table_text(user.username, 48),
                    format_table_text(user.cargo, 72),
                    user.user_type,
                ),
                tags=("odd" if index % 2 else "even",),
            )
        fit_columns(self._table, self._column_widths)

    def _on_table_select(self, _event: object) -> None:
        selected = self._table.selection()
        if not selected:
            return
        user = self._users_by_id[selected[0]]
        self._selected_user_id = user.id
        self._name_var.set(user.nome)
        self._username_var.set(user.username)
        self._password_var.set("")
        self._job_var.set(user.cargo)
        self._role_var.set(user.user_type)

    def _clear_form(self) -> None:
        self._selected_user_id = None
        self._name_var.set("")
        self._username_var.set("")
        self._password_var.set("")
        self._job_var.set("")
        self._role_var.set(ALLOWED_USER_TYPES[1])
        for item_id in self._table.selection():
            self._table.selection_remove(item_id)

    def _notify(self, success: bool, message: str) -> None:
        self._feedback_label.configure(
            text_color=(
                self._theme_manager.colors["success"]
                if success
                else self._theme_manager.colors["danger"]
            )
        )
        self._feedback_var.set(message)
