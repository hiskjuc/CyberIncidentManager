"""Incident management view."""

from __future__ import annotations

from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from controllers.auth_controller import AuthController
from controllers.incident_controller import IncidentController
from models.incident import Incident
from models.user import User
from utils.helpers import today_iso
from utils.table_helpers import add_scrollbars, configure_columns, fit_columns, format_table_text
from utils.theme_manager import ThemeManager
from utils.validators import ALLOWED_SEVERITIES, ALLOWED_STATUSES, ValidationError


class IncidentsView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        incident_controller: IncidentController,
        auth_controller: AuthController,
        actor: User,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._incident_controller = incident_controller
        self._auth_controller = auth_controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._selected_incident_id: int | None = None
        self._incidents_by_id: dict[str, Incident] = {}
        self._responsible_options: dict[str, int | None] = {}
        self._form_controls: list[ctk.CTkBaseClass] = []
        self._can_edit = actor.can_edit_incidents()
        self._can_create = actor.can_create_incidents()

        self._title_var = ctk.StringVar()
        self._attack_var = ctk.StringVar()
        self._severity_var = ctk.StringVar(value=ALLOWED_SEVERITIES[2])
        self._status_var = ctk.StringVar(value=ALLOWED_STATUSES[0])
        self._date_var = ctk.StringVar(value=today_iso())
        self._ip_var = ctk.StringVar()
        self._responsible_var = ctk.StringVar(value="Nao atribuido")
        self._search_var = ctk.StringVar()
        self._status_filter_var = ctk.StringVar(value="Todos")
        self._severity_filter_var = ctk.StringVar(value="Todas")
        self._feedback_var = ctk.StringVar(value="")

        self._load_responsibles()
        self._build()
        self._search_var.trace_add("write", lambda *_args: self._refresh_table())
        self._refresh_table()

    def _build(self) -> None:
        colors = self._theme_manager.colors
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(
            self,
            text="Incidentes",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=4, pady=(0, 14), sticky="w")
        self._feedback_label = ctk.CTkLabel(
            self,
            textvariable=self._feedback_var,
            text_color=colors["success"],
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._feedback_label.grid(row=0, column=1, padx=4, pady=(0, 14), sticky="e")

        toolbar = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        toolbar.grid(row=1, column=0, columnspan=2, pady=(0, 14), sticky="ew")
        toolbar.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(
            toolbar,
            textvariable=self._search_var,
            placeholder_text="Buscar por titulo, descricao, ataque, IP ou responsavel",
            height=38,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
        ).grid(row=0, column=0, padx=14, pady=14, sticky="ew")

        ctk.CTkOptionMenu(
            toolbar,
            values=["Todos", *ALLOWED_STATUSES],
            variable=self._status_filter_var,
            command=lambda _value: self._refresh_table(),
            width=150,
            height=38,
            fg_color=colors["secondary_button"],
            button_color=colors["primary"],
            button_hover_color=colors["primary_hover"],
            text_color=colors["secondary_text"],
        ).grid(row=0, column=1, padx=(0, 10), pady=14)

        ctk.CTkOptionMenu(
            toolbar,
            values=["Todas", *ALLOWED_SEVERITIES],
            variable=self._severity_filter_var,
            command=lambda _value: self._refresh_table(),
            width=140,
            height=38,
            fg_color=colors["secondary_button"],
            button_color=colors["primary"],
            button_hover_color=colors["primary_hover"],
            text_color=colors["secondary_text"],
        ).grid(row=0, column=2, padx=(0, 10), pady=14)

        ctk.CTkButton(
            toolbar,
            text="Exportar CSV",
            command=self._export_csv,
            width=132,
            height=38,
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        ).grid(row=0, column=3, padx=(0, 14), pady=14)

        form = ctk.CTkScrollableFrame(
            self,
            width=372,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        form.grid(row=2, column=0, padx=(0, 14), sticky="nsew")
        form.configure(height=800)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form,
            text="Registro do incidente",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(16, 10), sticky="w")

        self._form_entry(form, "Titulo", self._title_var, 1)
        self._form_entry(form, "Tipo de ataque", self._attack_var, 3)

        options = ctk.CTkFrame(form, fg_color="transparent")
        options.grid(row=5, column=0, padx=16, pady=(8, 4), sticky="ew")
        options.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(options, text="Severidade").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(options, text="Status").grid(row=0, column=1, padx=(8, 0), sticky="w")
        severity_menu = ctk.CTkOptionMenu(
            options,
            values=list(ALLOWED_SEVERITIES),
            variable=self._severity_var,
            height=36,
            fg_color=colors["secondary_button"],
            button_color=colors["primary"],
            button_hover_color=colors["primary_hover"],
            text_color=colors["secondary_text"],
        )
        severity_menu.grid(row=1, column=0, pady=(4, 0), sticky="ew")
        status_menu = ctk.CTkOptionMenu(
            options,
            values=list(ALLOWED_STATUSES),
            variable=self._status_var,
            height=36,
            fg_color=colors["secondary_button"],
            button_color=colors["primary"],
            button_hover_color=colors["primary_hover"],
            text_color=colors["secondary_text"],
        )
        status_menu.grid(row=1, column=1, padx=(8, 0), pady=(4, 0), sticky="ew")
        self._form_controls.extend([severity_menu, status_menu])

        self._form_entry(form, "Data AAAA-MM-DD", self._date_var, 6)
        self._form_entry(form, "IP relacionado", self._ip_var, 8)

        ctk.CTkLabel(form, text="Responsavel").grid(
            row=10,
            column=0,
            padx=16,
            pady=(8, 4),
            sticky="w",
        )
        self._responsible_menu = ctk.CTkOptionMenu(
            form,
            values=list(self._responsible_options.keys()),
            variable=self._responsible_var,
            height=36,
            fg_color=colors["secondary_button"],
            button_color=colors["primary"],
            button_hover_color=colors["primary_hover"],
            text_color=colors["secondary_text"],
        )
        self._responsible_menu.grid(row=11, column=0, padx=16, pady=(0, 4), sticky="ew")
        self._form_controls.append(self._responsible_menu)

        ctk.CTkLabel(form, text="Descricao").grid(
            row=12,
            column=0,
            padx=16,
            pady=(8, 4),
            sticky="w",
        )
        self._description_text = ctk.CTkTextbox(
            form,
            height=118,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1,
        )
        self._description_text.grid(row=13, column=0, padx=16, pady=(0, 10), sticky="ew")
        self._form_controls.append(self._description_text)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=14, column=0, padx=16, pady=(0, 16), sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)
        self._create_button = ctk.CTkButton(
            actions,
            text="Criar",
            command=self._create_incident,
            height=38,
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        )
        self._create_button.grid(row=0, column=0, padx=(0, 6), pady=(0, 8), sticky="ew")
        self._edit_button = ctk.CTkButton(
            actions,
            text="Editar",
            command=self._update_incident,
            height=38,
            fg_color=colors["teal"],
            hover_color=colors["teal_hover"],
        )
        self._edit_button.grid(row=0, column=1, padx=(6, 0), pady=(0, 8), sticky="ew")
        self._delete_button = ctk.CTkButton(
            actions,
            text="Excluir",
            command=self._delete_incident,
            height=38,
            fg_color=colors["danger"],
            hover_color=colors["danger_hover"],
        )
        self._delete_button.grid(row=1, column=0, padx=(0, 6), sticky="ew")
        self._clear_button = ctk.CTkButton(
            actions,
            text="Limpar",
            command=self._clear_form,
            height=38,
            fg_color=colors["secondary_button"],
            hover_color=colors["secondary_button_hover"],
            text_color=colors["secondary_text"],
        )
        self._clear_button.grid(row=1, column=1, padx=(6, 0), sticky="ew")

        if not self._can_create:
            self._create_button.configure(state="disabled")
        if not self._can_edit:
            self._edit_button.configure(state="disabled")
            self._clear_button.configure(state="disabled")
            for control in self._form_controls:
                control.configure(state="disabled")
        if not self._actor.can_delete_incidents():
            self._delete_button.configure(state="disabled")

        table_frame = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        table_frame.grid(row=2, column=1, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            table_frame,
            text="Fila monitorada",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(16, 10), sticky="w")

        self._table = ttk.Treeview(
            table_frame,
            columns=("id", "titulo", "ataque", "severidade", "status", "data", "ip", "resp"),
            show="headings",
            selectmode="browse",
            style="CIM.Treeview",
        )
        headings = {
            "id": "ID",
            "titulo": "Titulo",
            "ataque": "Ataque",
            "severidade": "Severidade",
            "status": "Status",
            "data": "Data",
            "ip": "IP",
            "resp": "Responsavel",
        }
        self._column_widths = {
            "id": 58,
            "titulo": 270,
            "ataque": 170,
            "severidade": 118,
            "status": 138,
            "data": 112,
            "ip": 152,
            "resp": 250,
        }
        configure_columns(self._table, headings, self._column_widths, {"id"})
        self._theme_manager.configure_table_tags(self._table)
        self._table.bind("<<TreeviewSelect>>", self._on_table_select)
        self._table.bind("<Double-1>", self._show_selected_incident_details)
        add_scrollbars(
            self._table,
            table_frame,
            1,
            0,
            padx=(16, 0),
            pady=(0, 16),
        )

    def _form_entry(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.StringVar,
        row: int,
    ) -> None:
        ctk.CTkLabel(parent, text=label).grid(
            row=row,
            column=0,
            padx=16,
            pady=(6, 4),
            sticky="w",
        )
        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
            height=36,
            fg_color=self._theme_manager.colors["input_bg"],
            border_color=self._theme_manager.colors["input_border"],
        )
        entry.grid(
            row=row + 1,
            column=0,
            padx=16,
            pady=(0, 2),
            sticky="ew",
        )
        self._form_controls.append(entry)

    def _payload(self) -> dict[str, object]:
        return {
            "titulo": self._title_var.get(),
            "descricao": self._description_text.get("1.0", "end").strip(),
            "tipo_ataque": self._attack_var.get(),
            "severidade": self._severity_var.get(),
            "status": self._status_var.get(),
            "data_incidente": self._date_var.get(),
            "ip_relacionado": self._ip_var.get(),
            "responsavel_id": self._responsible_options.get(self._responsible_var.get()),
        }

    def _create_incident(self) -> None:
        if not self._can_create:
            messagebox.showerror("Permissao negada", "Seu perfil nao permite criar incidentes.")
            return
        try:
            incident = self._incident_controller.create_incident(self._actor, self._payload())
        except (PermissionError, ValidationError, ValueError) as exc:
            self._notify(False, f"Erro ao criar incidente: {exc}")
            messagebox.showerror("Incidente nao criado", str(exc))
            return

        self._notify(True, f"Operacao realizada com sucesso: incidente #{incident.id} criado.")
        messagebox.showinfo("Incidente criado", f"Incidente #{incident.id} cadastrado.")
        self._clear_form()
        self._refresh_table()

    def _update_incident(self) -> None:
        if not self._can_edit:
            messagebox.showerror("Permissao negada", "Seu perfil nao permite editar incidentes.")
            return
        if self._selected_incident_id is None:
            messagebox.showwarning("Selecao necessaria", "Selecione um incidente para editar.")
            return

        try:
            incident = self._incident_controller.update_incident(
                self._actor,
                self._selected_incident_id,
                self._payload(),
            )
        except (PermissionError, ValidationError, ValueError) as exc:
            self._notify(False, f"Erro ao editar incidente: {exc}")
            messagebox.showerror("Atualizacao recusada", str(exc))
            return

        self._notify(True, f"Operacao realizada com sucesso: incidente #{incident.id} atualizado.")
        messagebox.showinfo("Incidente editado", f"Incidente #{incident.id} atualizado.")
        self._refresh_table()

    def _delete_incident(self) -> None:
        if self._selected_incident_id is None:
            messagebox.showwarning("Selecao necessaria", "Selecione um incidente para excluir.")
            return

        confirmed = messagebox.askyesno(
            "Confirmar exclusao",
            f"Excluir o incidente #{self._selected_incident_id}?",
        )
        if not confirmed:
            return

        try:
            self._incident_controller.delete_incident(self._actor, self._selected_incident_id)
        except (PermissionError, ValueError) as exc:
            self._notify(False, f"Erro ao excluir incidente: {exc}")
            messagebox.showerror("Exclusao recusada", str(exc))
            return

        self._notify(True, "Operacao realizada com sucesso: incidente removido.")
        messagebox.showinfo("Incidente excluido", "O registro foi removido.")
        self._clear_form()
        self._refresh_table()

    def _export_csv(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Exportar incidentes",
            defaultextension=".csv",
            initialfile="incidentes.csv",
            filetypes=[("Arquivos CSV", "*.csv")],
        )
        if not file_path:
            return

        try:
            total = self._incident_controller.export_to_csv(
                self._actor,
                file_path,
                self._search_var.get(),
                self._status_filter_var.get(),
                self._severity_filter_var.get(),
            )
        except (PermissionError, OSError, ValueError) as exc:
            messagebox.showerror("Exportacao recusada", str(exc))
            return

        messagebox.showinfo("CSV exportado", f"{total} incidente(s) exportado(s).")

    def _refresh_table(self) -> None:
        for item_id in self._table.get_children():
            self._table.delete(item_id)
        self._incidents_by_id.clear()

        incidents = self._incident_controller.list_incidents(
            self._actor,
            self._search_var.get(),
            self._status_filter_var.get(),
            self._severity_filter_var.get(),
        )
        for index, incident in enumerate(incidents):
            item_id = str(incident.id)
            self._incidents_by_id[item_id] = incident
            self._table.insert(
                "",
                "end",
                iid=item_id,
                values=(
                    incident.id,
                    format_table_text(incident.titulo, 96),
                    format_table_text(incident.tipo_ataque, 64),
                    incident.severidade,
                    incident.status,
                    incident.data_incidente,
                    format_table_text(incident.ip_relacionado, 40),
                    format_table_text(incident.responsavel_nome or "Nao atribuido", 82),
                ),
                tags=("odd" if index % 2 else "even",),
            )
        fit_columns(self._table, self._column_widths)

    def _on_table_select(self, _event: object) -> None:
        selected = self._table.selection()
        if not selected:
            return

        incident = self._incidents_by_id[selected[0]]
        self._selected_incident_id = incident.id
        self._title_var.set(incident.titulo)
        self._attack_var.set(incident.tipo_ataque)
        self._severity_var.set(incident.severidade)
        self._status_var.set(incident.status)
        self._date_var.set(incident.data_incidente)
        self._ip_var.set(incident.ip_relacionado or "")
        self._responsible_var.set(incident.responsavel_nome or "Nao atribuido")
        self._set_description(incident.descricao)

    def _clear_form(self) -> None:
        if not self._can_edit and not self._can_create:
            return
        self._selected_incident_id = None
        self._title_var.set("")
        self._attack_var.set("")
        self._severity_var.set(ALLOWED_SEVERITIES[2])
        self._status_var.set(ALLOWED_STATUSES[0])
        self._date_var.set(today_iso())
        self._ip_var.set("")
        self._responsible_var.set("Nao atribuido")
        self._set_description("")
        for item_id in self._table.selection():
            self._table.selection_remove(item_id)

    def _set_description(self, value: str) -> None:
        current_state = self._description_text.cget("state")
        if current_state == "disabled":
            self._description_text.configure(state="normal")
        self._description_text.delete("1.0", "end")
        if value:
            self._description_text.insert("1.0", value)
        if current_state == "disabled":
            self._description_text.configure(state="disabled")

    def _load_responsibles(self) -> None:
        self._responsible_options = {"Nao atribuido": None}
        for user in self._auth_controller.list_assignable_users(self._actor):
            label = f"{user['nome']} ({user['username']})"
            self._responsible_options[label] = int(user["id"])

    def _show_selected_incident_details(self, _event: object | None = None) -> None:
        selected = self._table.selection()
        if not selected:
            return
        incident = self._incidents_by_id[selected[0]]
        IncidentDetailsDialog(
            self,
            incident,
            self._incident_controller,
            self._actor,
            self._theme_manager,
        )

    def _notify(self, success: bool, message: str) -> None:
        self._feedback_label.configure(
            text_color=(
                self._theme_manager.colors["success"]
                if success
                else self._theme_manager.colors["danger"]
            )
        )
        self._feedback_var.set(message)


class IncidentDetailsDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        incident: Incident,
        incident_controller: IncidentController,
        actor: User,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(master)
        self._incident = incident
        self._incident_controller = incident_controller
        self._actor = actor
        self._theme_manager = theme_manager
        self._comment_text: ctk.CTkTextbox | None = None
        self._comments_frame: ctk.CTkScrollableFrame | None = None
        self._history_frame: ctk.CTkScrollableFrame | None = None
        self._timeline_frame: ctk.CTkScrollableFrame | None = None
        self.title(f"Incidente #{incident.id}")
        self.geometry("920x760")
        self.minsize(780, 640)
        self.configure(fg_color=theme_manager.colors["app_bg"])
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self._build()
        self.after(100, self.focus_force)

    def _build(self) -> None:
        colors = self._theme_manager.colors
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(22, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text=self._incident.titulo,
            font=ctk.CTkFont(size=22, weight="bold"),
            wraplength=620,
            justify="left",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            header,
            text="Fechar",
            command=self.destroy,
            width=92,
            height=34,
            fg_color=colors["secondary_button"],
            hover_color=colors["secondary_button_hover"],
            text_color=colors["secondary_text"],
        ).grid(row=0, column=1, padx=(16, 0), sticky="e")

        body = ctk.CTkScrollableFrame(
            self,
            corner_radius=8,
            fg_color=colors["surface"],
            border_width=1,
            border_color=colors["border"],
        )
        body.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")
        body.grid_columnconfigure((0, 1), weight=1)

        items = (
            ("Tipo de ataque", self._incident.tipo_ataque),
            ("Severidade", self._incident.severidade),
            ("Status", self._incident.status),
            ("Data do incidente", self._incident.data_incidente),
            ("IP relacionado", self._incident.ip_relacionado or "-"),
            ("Responsavel", self._incident.responsavel_nome or "Nao atribuido"),
            ("Data de criacao", self._incident.criado_em or "-"),
            ("Ultima atualizacao", self._incident.atualizado_em or "-"),
        )

        ctk.CTkLabel(
            body,
            text="Descricao completa",
            text_color=colors["muted_text"],
        ).grid(row=0, column=0, columnspan=2, padx=18, pady=(18, 4), sticky="w")
        description = ctk.CTkTextbox(
            body,
            height=180,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1,
            wrap="word",
        )
        description.grid(row=1, column=0, columnspan=2, padx=18, pady=(0, 18), sticky="ew")
        description.insert("1.0", self._incident.descricao)
        description.configure(state="disabled")

        for index, (label, value) in enumerate(items):
            row = 2 + index // 2
            column = index % 2
            field = ctk.CTkFrame(body, fg_color="transparent")
            field.grid(
                row=row,
                column=column,
                padx=(18, 8 if column == 0 else 18),
                pady=(0, 16),
                sticky="ew",
            )
            ctk.CTkLabel(field, text=label, text_color=colors["muted_text"]).pack(anchor="w")
            ctk.CTkLabel(
                field,
                text=str(value),
                font=ctk.CTkFont(size=14, weight="bold"),
                wraplength=300,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))

        tabs = ctk.CTkTabview(
            body,
            fg_color=colors["surface_alt"],
            segmented_button_fg_color=colors["secondary_button"],
            segmented_button_selected_color=colors["primary"],
            segmented_button_selected_hover_color=colors["primary_hover"],
        )
        tabs.grid(row=7, column=0, columnspan=2, padx=18, pady=(4, 18), sticky="ew")
        tabs.add("SLA")
        tabs.add("Comentarios")
        tabs.add("Historico")
        tabs.add("Timeline")

        self._build_sla_tab(tabs.tab("SLA"))
        self._build_comments_tab(tabs.tab("Comentarios"))
        self._build_history_tab(tabs.tab("Historico"))
        self._build_timeline_tab(tabs.tab("Timeline"))

    def _build_sla_tab(self, parent: ctk.CTkFrame) -> None:
        colors = self._theme_manager.colors
        parent.grid_columnconfigure((0, 1, 2), weight=1)
        sla = self._incident_controller.get_incident_sla(self._actor, int(self._incident.id or 0))
        cards = (
            ("Tempo aberto", sla["tempo_aberto"]),
            ("Tempo ate resolucao", sla["tempo_resolucao"]),
            ("Situacao", sla["situacao"]),
            ("Limite", f"{sla['limite_horas']}h"),
            ("Resolvido em", sla["resolvido_em"]),
        )
        for index, (label, value) in enumerate(cards):
            card = ctk.CTkFrame(
                parent,
                fg_color=colors["surface"],
                border_color=colors["border"],
                border_width=1,
                corner_radius=8,
            )
            card.grid(
                row=index // 3,
                column=index % 3,
                padx=8,
                pady=8,
                sticky="ew",
            )
            ctk.CTkLabel(card, text=label, text_color=colors["muted_text"]).pack(
                anchor="w",
                padx=14,
                pady=(12, 4),
            )
            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=15, weight="bold"),
            ).pack(anchor="w", padx=14, pady=(0, 12))

    def _build_comments_tab(self, parent: ctk.CTkFrame) -> None:
        colors = self._theme_manager.colors
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        self._comment_text = ctk.CTkTextbox(
            parent,
            height=86,
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1,
            wrap="word",
        )
        self._comment_text.grid(row=0, column=0, padx=8, pady=(8, 6), sticky="ew")
        comment_button = ctk.CTkButton(
            parent,
            text="Adicionar comentario",
            command=self._add_comment,
            fg_color=colors["primary"],
            hover_color=colors["primary_hover"],
            text_color=colors["primary_text"],
        )
        comment_button.grid(row=0, column=1, padx=(0, 8), pady=(8, 6), sticky="s")
        if not self._actor.can_edit_incidents():
            self._comment_text.configure(state="disabled")
            comment_button.configure(state="disabled")

        self._comments_frame = ctk.CTkScrollableFrame(
            parent,
            height=220,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
        )
        self._comments_frame.grid(row=1, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="nsew")
        self._refresh_comments()

    def _build_history_tab(self, parent: ctk.CTkFrame) -> None:
        colors = self._theme_manager.colors
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        self._history_frame = ctk.CTkScrollableFrame(
            parent,
            height=250,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
        )
        self._history_frame.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self._refresh_history()

    def _build_timeline_tab(self, parent: ctk.CTkFrame) -> None:
        colors = self._theme_manager.colors
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        self._timeline_frame = ctk.CTkScrollableFrame(
            parent,
            height=250,
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
        )
        self._timeline_frame.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self._refresh_timeline()

    def _add_comment(self) -> None:
        if self._comment_text is None:
            return
        comment = self._comment_text.get("1.0", "end").strip()
        try:
            self._incident_controller.add_comment(self._actor, int(self._incident.id or 0), comment)
        except (PermissionError, ValueError) as exc:
            messagebox.showerror("Comentario nao salvo", str(exc))
            return
        self._comment_text.delete("1.0", "end")
        self._refresh_comments()
        self._refresh_history()
        self._refresh_timeline()

    def _refresh_comments(self) -> None:
        if self._comments_frame is None:
            return
        self._clear_frame(self._comments_frame)
        comments = self._incident_controller.list_comments(self._actor, int(self._incident.id or 0))
        if not comments:
            self._empty_label(self._comments_frame, "Nenhum comentario registrado.")
            return
        for comment in comments:
            self._event_card(
                self._comments_frame,
                f"{comment['autor_nome']} ({comment['autor_username']})",
                comment["comentario"],
                comment["criado_em"],
            )

    def _refresh_history(self) -> None:
        if self._history_frame is None:
            return
        self._clear_frame(self._history_frame)
        history = self._incident_controller.list_history(self._actor, int(self._incident.id or 0))
        if not history:
            self._empty_label(self._history_frame, "Nenhuma alteracao registrada.")
            return
        for row in history:
            detail = row["detalhes"]
            if row["campo"]:
                detail = f"{detail} {row['valor_anterior'] or '-'} -> {row['valor_novo'] or '-'}"
            self._event_card(
                self._history_frame,
                f"{row['acao']} por {row['usuario_nome']}",
                detail,
                row["criado_em"],
            )

    def _refresh_timeline(self) -> None:
        if self._timeline_frame is None:
            return
        self._clear_frame(self._timeline_frame)
        events = self._incident_controller.get_timeline(self._actor, int(self._incident.id or 0))
        if not events:
            self._empty_label(self._timeline_frame, "Timeline vazia.")
            return
        for event in events:
            self._event_card(
                self._timeline_frame,
                event["tipo"],
                event["descricao"],
                event["data"],
            )

    def _event_card(self, parent: ctk.CTkFrame, title: str, body: str, date_text: str) -> None:
        colors = self._theme_manager.colors
        card = ctk.CTkFrame(
            parent,
            fg_color=colors["surface_alt"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
        )
        card.pack(fill="x", padx=8, pady=7)
        ctk.CTkLabel(
            card,
            text=f"{title} - {date_text}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 2))
        ctk.CTkLabel(
            card,
            text=body,
            text_color=colors["muted_text"],
            wraplength=760,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 10))

    def _empty_label(self, parent: ctk.CTkFrame, text: str) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
            text_color=self._theme_manager.colors["muted_text"],
        ).pack(anchor="w", padx=12, pady=12)

    def _clear_frame(self, frame: ctk.CTkFrame) -> None:
        for child in frame.winfo_children():
            child.destroy()
