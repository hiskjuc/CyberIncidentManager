"""Incident CRUD, filtering and report export."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from database.connection import DatabaseConnection
from models.incident import Incident
from models.user import User
from utils.validators import validate_incident_payload


class IncidentController:
    def __init__(self, database: DatabaseConnection) -> None:
        self._database = database

    def create_incident(self, actor: User, payload: dict[str, Any]) -> Incident:
        self._require_session(actor)
        if not actor.can_create_incidents():
            raise PermissionError("Seu perfil permite apenas visualizar incidentes.")
        validated = validate_incident_payload(payload)
        incident = Incident(incident_id=None, **validated)

        with self._database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO incidentes (
                    titulo,
                    descricao,
                    tipo_ataque,
                    severidade,
                    status,
                    data_incidente,
                    ip_relacionado,
                    responsavel_id,
                    criado_por_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*incident.to_record(), actor.id),
            )
            self._write_log(
                connection,
                actor.id,
                "CRIAR_INCIDENTE",
                f"Incidente #{cursor.lastrowid} criado: {incident.titulo}.",
            )
            self._write_history(
                connection,
                int(cursor.lastrowid),
                actor.id,
                "CRIACAO",
                None,
                None,
                incident.titulo,
                f"Incidente criado por {actor.username}.",
            )

        return self.get_incident(actor, int(cursor.lastrowid))

    def update_incident(
        self,
        actor: User,
        incident_id: int,
        payload: dict[str, Any],
    ) -> Incident:
        self._require_session(actor)
        if not actor.can_edit_incidents():
            raise PermissionError("Seu perfil nao permite editar incidentes.")
        validated = validate_incident_payload(payload)
        incident = Incident(incident_id=incident_id, **validated)

        with self._database.connect() as connection:
            current = connection.execute(
                "SELECT * FROM incidentes WHERE id = ?",
                (incident_id,),
            ).fetchone()
            if current is None:
                raise ValueError("Incidente nao encontrado.")
            cursor = connection.execute(
                """
                UPDATE incidentes
                SET titulo = ?,
                    descricao = ?,
                    tipo_ataque = ?,
                    severidade = ?,
                    status = ?,
                    data_incidente = ?,
                    ip_relacionado = ?,
                    responsavel_id = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*incident.to_record(), incident_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("Incidente nao encontrado.")
            self._record_incident_changes(connection, incident_id, actor.id, current, validated)
            self._write_log(
                connection,
                actor.id,
                "ALTERAR_INCIDENTE",
                f"Incidente #{incident_id} atualizado: {incident.titulo}.",
            )

        return self.get_incident(actor, incident_id)

    def delete_incident(self, actor: User, incident_id: int) -> None:
        self._require_session(actor)
        if not actor.can_delete_incidents():
            raise PermissionError("Somente administradores podem excluir incidentes.")

        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT titulo FROM incidentes WHERE id = ?",
                (incident_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Incidente nao encontrado.")

            connection.execute("DELETE FROM incidentes WHERE id = ?", (incident_id,))
            self._write_log(
                connection,
                actor.id,
                "EXCLUIR_INCIDENTE",
                f"Incidente #{incident_id} excluido: {row['titulo']}.",
            )

    def get_incident(self, actor: User, incident_id: int) -> Incident:
        self._require_session(actor)
        with self._database.connect() as connection:
            row = connection.execute(
                f"{self._incident_query()} WHERE i.id = ?",
                (incident_id,),
            ).fetchone()

        if row is None:
            raise ValueError("Incidente nao encontrado.")
        return Incident.from_row(row)

    def add_comment(self, actor: User, incident_id: int, comment: str) -> None:
        self._require_session(actor)
        if not actor.can_edit_incidents():
            raise PermissionError("Seu perfil nao permite comentar incidentes.")

        cleaned_comment = " ".join(str(comment or "").split())
        if not cleaned_comment:
            raise ValueError("Comentario e obrigatorio.")
        if len(cleaned_comment) > 1200:
            raise ValueError("Comentario deve ter no maximo 1200 caracteres.")

        with self._database.connect() as connection:
            incident = connection.execute(
                "SELECT id, titulo FROM incidentes WHERE id = ?",
                (incident_id,),
            ).fetchone()
            if incident is None:
                raise ValueError("Incidente nao encontrado.")

            connection.execute(
                """
                INSERT INTO comentarios_incidentes (incidente_id, autor_id, comentario)
                VALUES (?, ?, ?)
                """,
                (incident_id, actor.id, cleaned_comment),
            )
            self._write_history(
                connection,
                incident_id,
                actor.id,
                "COMENTARIO",
                None,
                None,
                cleaned_comment,
                f"Comentario adicionado por {actor.username}.",
            )
            self._write_log(
                connection,
                actor.id,
                "COMENTAR_INCIDENTE",
                f"Comentario adicionado ao incidente #{incident_id}: {incident['titulo']}.",
            )

    def list_comments(self, actor: User, incident_id: int) -> list[dict[str, Any]]:
        self._require_session(actor)
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    c.id,
                    c.comentario,
                    c.criado_em,
                    COALESCE(u.nome, 'Usuario removido') AS autor_nome,
                    COALESCE(u.username, '-') AS autor_username
                FROM comentarios_incidentes AS c
                LEFT JOIN usuarios AS u ON u.id = c.autor_id
                WHERE c.incidente_id = ?
                ORDER BY c.criado_em ASC, c.id ASC
                """,
                (incident_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_history(self, actor: User, incident_id: int) -> list[dict[str, Any]]:
        self._require_session(actor)
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    h.id,
                    h.acao,
                    h.campo,
                    h.valor_anterior,
                    h.valor_novo,
                    h.detalhes,
                    h.criado_em,
                    COALESCE(u.nome, 'Usuario removido') AS usuario_nome,
                    COALESCE(u.username, '-') AS usuario_username
                FROM historico_incidentes AS h
                LEFT JOIN usuarios AS u ON u.id = h.usuario_id
                WHERE h.incidente_id = ?
                ORDER BY h.criado_em ASC, h.id ASC
                """,
                (incident_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_incident_sla(self, actor: User, incident_id: int) -> dict[str, Any]:
        incident = self.get_incident(actor, incident_id)
        created_at = self._parse_datetime(incident.criado_em)
        resolved_at = self._resolution_datetime(actor, incident_id, incident)
        end_at = resolved_at or datetime.now()
        elapsed_hours = max((end_at - created_at).total_seconds() / 3600, 0)
        limit_hours = self._sla_limit_hours(incident.severidade)

        return {
            "tempo_aberto": self._format_duration(elapsed_hours),
            "tempo_resolucao": self._format_duration(elapsed_hours) if resolved_at else "-",
            "limite_horas": limit_hours,
            "situacao": "Dentro do prazo" if elapsed_hours <= limit_hours else "Fora do prazo",
            "resolvido_em": resolved_at.strftime("%d/%m/%Y %H:%M:%S") if resolved_at else "-",
        }

    def get_timeline(self, actor: User, incident_id: int) -> list[dict[str, str]]:
        incident = self.get_incident(actor, incident_id)
        events: list[dict[str, str]] = [
            {
                "data": incident.criado_em or "",
                "tipo": "Criacao",
                "descricao": f"Incidente criado: {incident.titulo}",
            }
        ]

        for row in self.list_history(actor, incident_id):
            events.append(
                {
                    "data": row["criado_em"],
                    "tipo": row["acao"].title(),
                    "descricao": row["detalhes"],
                }
            )

        for row in self.list_comments(actor, incident_id):
            events.append(
                {
                    "data": row["criado_em"],
                    "tipo": "Comentario",
                    "descricao": f"{row['autor_nome']}: {row['comentario']}",
                }
            )

        if incident.status == "Resolvido":
            resolved_at = self._resolution_datetime(actor, incident_id, incident)
            events.append(
                {
                    "data": resolved_at.strftime("%Y-%m-%d %H:%M:%S") if resolved_at else "",
                    "tipo": "Resolucao",
                    "descricao": "Incidente marcado como resolvido.",
                }
            )

        return sorted(events, key=lambda event: event["data"])

    def list_incidents(
        self,
        actor: User,
        search: str = "",
        status: str = "Todos",
        severity: str = "Todas",
    ) -> list[Incident]:
        self._require_session(actor)
        query = f"{self._incident_query()} WHERE 1 = 1"
        parameters: list[Any] = []

        search_term = search.strip()
        if search_term:
            wildcard = f"%{search_term}%"
            query += """
                AND (
                    i.titulo LIKE ?
                    OR i.descricao LIKE ?
                    OR i.tipo_ataque LIKE ?
                    OR COALESCE(i.ip_relacionado, '') LIKE ?
                    OR COALESCE(r.nome, '') LIKE ?
                    OR COALESCE(r.username, '') LIKE ?
                )
            """
            parameters.extend([wildcard] * 6)

        if status != "Todos":
            query += " AND i.status = ?"
            parameters.append(status)

        if severity != "Todas":
            query += " AND i.severidade = ?"
            parameters.append(severity)

        query += " ORDER BY i.data_incidente DESC, i.id DESC"

        with self._database.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [Incident.from_row(row) for row in rows]

    def export_to_csv(
        self,
        actor: User,
        file_path: str | Path,
        search: str = "",
        status: str = "Todos",
        severity: str = "Todas",
    ) -> int:
        incidents = self.list_incidents(actor, search, status, severity)
        rows = [
            {
                "ID": incident.id,
                "Titulo": incident.titulo,
                "Descricao": incident.descricao,
                "Tipo de ataque": incident.tipo_ataque,
                "Severidade": incident.severidade,
                "Status": incident.status,
                "Data": incident.data_incidente,
                "IP relacionado": incident.ip_relacionado or "",
                "Responsavel": incident.responsavel_nome or "",
                "Criado por": incident.criado_por_nome or "",
            }
            for incident in incidents
        ]
        pd.DataFrame(rows).to_csv(file_path, index=False, encoding="utf-8-sig")

        with self._database.connect() as connection:
            self._write_log(
                connection,
                actor.id,
                "EXPORTAR_CSV",
                f"{len(rows)} incidentes exportados para CSV.",
            )
        return len(rows)

    def _incident_query(self) -> str:
        return """
            SELECT
                i.*,
                CASE
                    WHEN r.id IS NULL THEN NULL
                    ELSE r.nome || ' (' || r.username || ')'
                END AS responsavel_nome,
                COALESCE(c.nome, 'Usuario removido') AS criado_por_nome
            FROM incidentes AS i
            LEFT JOIN usuarios AS r ON r.id = i.responsavel_id
            LEFT JOIN usuarios AS c ON c.id = i.criado_por_id
        """

    def _require_session(self, actor: User | None) -> None:
        if actor is None:
            raise PermissionError("Sessao expirada. Faca login novamente.")

    def _write_log(
        self,
        connection: sqlite3.Connection,
        user_id: int | None,
        action: str,
        details: str,
    ) -> None:
        try:
            connection.execute(
                "INSERT INTO logs (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                (user_id, action, details),
            )
        except sqlite3.Error:
            return

    def _record_incident_changes(
        self,
        connection: sqlite3.Connection,
        incident_id: int,
        user_id: int,
        current: sqlite3.Row,
        validated: dict[str, Any],
    ) -> None:
        field_labels = {
            "titulo": "Titulo",
            "descricao": "Descricao",
            "tipo_ataque": "Tipo de ataque",
            "severidade": "Severidade",
            "status": "Status",
            "data_incidente": "Data",
            "ip_relacionado": "IP relacionado",
            "responsavel_id": "Responsavel",
        }
        for field, label in field_labels.items():
            old_value = current[field]
            new_value = validated[field]
            if old_value == new_value:
                continue
            self._write_history(
                connection,
                incident_id,
                user_id,
                "ALTERACAO",
                label,
                "" if old_value is None else str(old_value),
                "" if new_value is None else str(new_value),
                f"{label} alterado.",
            )

    def _write_history(
        self,
        connection: sqlite3.Connection,
        incident_id: int,
        user_id: int | None,
        action: str,
        field: str | None,
        old_value: str | None,
        new_value: str | None,
        details: str,
    ) -> None:
        try:
            connection.execute(
                """
                INSERT INTO historico_incidentes (
                    incidente_id,
                    usuario_id,
                    acao,
                    campo,
                    valor_anterior,
                    valor_novo,
                    detalhes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (incident_id, user_id, action, field, old_value, new_value, details),
            )
        except sqlite3.Error:
            return

    def _resolution_datetime(
        self,
        actor: User,
        incident_id: int,
        incident: Incident,
    ) -> datetime | None:
        if incident.status != "Resolvido":
            return None

        history = self.list_history(actor, incident_id)
        for row in reversed(history):
            if row["campo"] == "Status" and row["valor_novo"] == "Resolvido":
                return self._parse_datetime(row["criado_em"])
        return self._parse_datetime(incident.atualizado_em or incident.criado_em)

    def _parse_datetime(self, value: str | None) -> datetime:
        if not value:
            return datetime.now()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value[:19], fmt)
            except ValueError:
                continue
        return datetime.now()

    def _sla_limit_hours(self, severity: str) -> int:
        return {
            "Critica": 24,
            "Alta": 48,
            "Media": 72,
            "Baixa": 120,
        }.get(severity, 72)

    def _format_duration(self, hours: float) -> str:
        days = int(hours // 24)
        remaining_hours = int(hours % 24)
        if days:
            return f"{days}d {remaining_hours}h"
        return f"{remaining_hours}h"
