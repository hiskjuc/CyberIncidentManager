"""Internal knowledge base view."""

from __future__ import annotations

from tkinter import messagebox, ttk

import customtkinter as ctk

from controllers.knowledge_controller import KnowledgeController
from models.user import User
from utils.table_helpers import add_scrollbars, configure_columns, fit_columns, format_table_text
from utils.theme_manager import ThemeManager


class KnowledgeBaseView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        controller: KnowledgeController,
        actor: User,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._controller = controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._selected_id: int | None = None
        self._can_edit = actor.can_edit_incidents()
        self._search_var = ctk.StringVar()
        self._category_filter_var = ctk.StringVar(value="Todas")
        self._title_var = ctk.StringVar()
        self._category_var = ctk.StringVar()
        self._build()
        self._search_var.trace_add("write", lambda *_args: self._refresh_table())
        self._refresh_categories()
        self._refresh_table()

    def _build(self) -> None:
        colors = self._theme_manager.colors
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(
            self,
            text="Base de Conhecimento",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=4, pady=(0, 14), sticky="w")

        toolbar = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
        )
        toolbar.grid(row=1, column=0, columnspan=2, pady=(0, 14), sticky="ew")
        toolbar.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(
            toolbar,
            textvariable=self._search_var,
            placeholder_text="Buscar artigo, categoria, descricao ou solucao",
            height=38,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
        ).grid(row=0, column=0, padx=14, pady=14, sticky="ew")
        self._category_filter = ctk.CTkOptionMenu(
            toolbar,
            values=["Todas"],
            variable=self._category_filter_var,
            command=lambda _value: self._refresh_table(),
            width=180,
            fg_color=colors["secondary_button"],
            button_color=colors["primary"],
            button_hover_color=colors["primary_hover"],
            text_color=colors["secondary_text"],
        )
        self._category_filter.grid(row=0, column=1, padx=(0, 14), pady=14)

        form = ctk.CTkScrollableFrame(
            self,
            width=390,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
        )
        form.grid(row=2, column=0, padx=(0, 14), sticky="nsew")
        form.configure(height=700)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form,
            text="Artigo interno",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(16, 10), sticky="w")
        self._entry(form, "Titulo", self._title_var, 1)
        self._entry(form, "Categoria", self._category_var, 3)
        ctk.CTkLabel(form, text="Descricao").grid(row=5, column=0, padx=16, pady=(8, 4), sticky="w")
        self._description_text = self._textbox(form, 6, 118)
        ctk.CTkLabel(form, text="Solucao aplicada").grid(
            row=7,
            column=0,
            padx=16,
            pady=(8, 4),
            sticky="w",
        )
        self._solution_text = self._textbox(form, 8, 140)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=9, column=0, padx=16, pady=(12, 16), sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)
        self._save_button = ctk.CTkButton(
            actions,
            text="Salvar",
            command=self._save,
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        )
        self._save_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self._delete_button = ctk.CTkButton(
            actions,
            text="Excluir",
            command=self._delete,
            fg_color=colors["danger"],
            hover_color=colors["danger_hover"],
        )
        self._delete_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        ctk.CTkButton(
            actions,
            text="Limpar",
            command=self._clear_form,
            fg_color=colors["secondary_button"],
            hover_color=colors["secondary_button_hover"],
            text_color=colors["secondary_text"],
        ).grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="ew")
        if not self._can_edit:
            for widget in (
                self._save_button,
                self._delete_button,
                self._description_text,
                self._solution_text,
            ):
                widget.configure(state="disabled")

        table_frame = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
        )
        table_frame.grid(row=2, column=1, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            table_frame,
            text="Artigos cadastrados",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(16, 10), sticky="w")

        self._widths = {
            "id": 60,
            "titulo": 280,
            "categoria": 160,
            "autor": 180,
            "atualizado": 170,
        }
        self._table = ttk.Treeview(
            table_frame,
            columns=("id", "titulo", "categoria", "autor", "atualizado"),
            show="headings",
            style="CIM.Treeview",
        )
        configure_columns(
            self._table,
            {
                "id": "ID",
                "titulo": "Titulo",
                "categoria": "Categoria",
                "autor": "Autor",
                "atualizado": "Atualizado em",
            },
            self._widths,
            {"id"},
        )
        self._theme_manager.configure_table_tags(self._table)
        self._table.bind("<<TreeviewSelect>>", self._on_select)
        add_scrollbars(self._table, table_frame, 1, 0, padx=(16, 0), pady=(0, 16))

    def _entry(self, parent: ctk.CTkFrame, label: str, variable: ctk.StringVar, row: int) -> None:
        colors = self._theme_manager.colors
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=16, pady=(8, 4), sticky="w")
        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
            height=36,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
        )
        entry.grid(row=row + 1, column=0, padx=16, pady=(0, 2), sticky="ew")
        if not self._can_edit:
            entry.configure(state="disabled")

    def _textbox(self, parent: ctk.CTkFrame, row: int, height: int) -> ctk.CTkTextbox:
        colors = self._theme_manager.colors
        textbox = ctk.CTkTextbox(
            parent,
            height=height,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1,
            wrap="word",
        )
        textbox.grid(row=row, column=0, padx=16, pady=(0, 2), sticky="ew")
        return textbox

    def _payload(self) -> dict[str, str]:
        return {
            "titulo": self._title_var.get(),
            "categoria": self._category_var.get(),
            "descricao": self._description_text.get("1.0", "end").strip(),
            "solucao": self._solution_text.get("1.0", "end").strip(),
        }

    def _save(self) -> None:
        try:
            if self._selected_id is None:
                self._controller.create_article(self._actor, self._payload())
            else:
                self._controller.update_article(self._actor, self._selected_id, self._payload())
        except (PermissionError, ValueError) as exc:
            messagebox.showerror("Artigo nao salvo", str(exc))
            return
        self._clear_form()
        self._refresh_categories()
        self._refresh_table()

    def _delete(self) -> None:
        if self._selected_id is None:
            messagebox.showwarning("Selecao necessaria", "Selecione um artigo para excluir.")
            return
        if not messagebox.askyesno("Confirmar exclusao", "Excluir este artigo?"):
            return
        try:
            self._controller.delete_article(self._actor, self._selected_id)
        except (PermissionError, ValueError) as exc:
            messagebox.showerror("Exclusao recusada", str(exc))
            return
        self._clear_form()
        self._refresh_categories()
        self._refresh_table()

    def _refresh_categories(self) -> None:
        values = ["Todas", *self._controller.list_categories(self._actor)]
        self._category_filter.configure(values=values)
        if self._category_filter_var.get() not in values:
            self._category_filter_var.set("Todas")

    def _refresh_table(self) -> None:
        self._articles = {
            int(row["id"]): row
            for row in self._controller.list_articles(
                self._actor,
                self._search_var.get(),
                self._category_filter_var.get(),
            )
        }
        for item_id in self._table.get_children():
            self._table.delete(item_id)
        for index, row in enumerate(self._articles.values()):
            self._table.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["id"],
                    format_table_text(row["titulo"], 80),
                    row["categoria"],
                    row["autor_nome"],
                    row["atualizado_em"],
                ),
                tags=("odd" if index % 2 else "even",),
            )
        fit_columns(self._table, self._widths)

    def _on_select(self, _event: object) -> None:
        selected = self._table.selection()
        if not selected:
            return
        article = self._articles[int(selected[0])]
        self._selected_id = int(article["id"])
        self._title_var.set(article["titulo"])
        self._category_var.set(article["categoria"])
        self._set_text(self._description_text, article["descricao"])
        self._set_text(self._solution_text, article["solucao"])

    def _clear_form(self) -> None:
        self._selected_id = None
        self._title_var.set("")
        self._category_var.set("")
        self._set_text(self._description_text, "")
        self._set_text(self._solution_text, "")
        for item_id in self._table.selection():
            self._table.selection_remove(item_id)

    def _set_text(self, textbox: ctk.CTkTextbox, value: str) -> None:
        current_state = textbox.cget("state")
        if current_state == "disabled":
            textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        if value:
            textbox.insert("1.0", value)
        if current_state == "disabled":
            textbox.configure(state="disabled")
