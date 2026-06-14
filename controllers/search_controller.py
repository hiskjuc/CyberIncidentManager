"""Global search across incidents, users and IP addresses."""

from __future__ import annotations

from typing import Any

from database.connection import DatabaseConnection
from models.user import User


class SearchController:
    def __init__(self, database: DatabaseConnection) -> None:
        self._database = database

    def global_search(self, actor: User, term: str) -> dict[str, list[dict[str, Any]]]:
        self._require_session(actor)
        cleaned = " ".join(str(term or "").split())
        if len(cleaned) < 2:
            return {"usuarios": [], "incidentes": [], "ips": []}

        wildcard = f"%{cleaned}%"
        with self._database.connect() as connection:
            users = connection.execute(
                """
                SELECT id, nome, username, cargo, tipo_usuario
                FROM usuarios
                WHERE nome LIKE ?
                   OR username LIKE ?
                   OR cargo LIKE ?
                   OR tipo_usuario LIKE ?
                ORDER BY nome COLLATE NOCASE
                LIMIT 50
                """,
                (wildcard, wildcard, wildcard, wildcard),
            ).fetchall()
            incidents = connection.execute(
                """
                SELECT
                    i.id,
                    i.titulo,
                    i.tipo_ataque,
                    i.severidade,
                    i.status,
                    i.data_incidente,
                    COALESCE(i.ip_relacionado, '') AS ip_relacionado,
                    COALESCE(u.nome, 'Nao atribuido') AS responsavel
                FROM incidentes AS i
                LEFT JOIN usuarios AS u ON u.id = i.responsavel_id
                WHERE i.titulo LIKE ?
                   OR i.descricao LIKE ?
                   OR i.tipo_ataque LIKE ?
                   OR COALESCE(i.ip_relacionado, '') LIKE ?
                   OR COALESCE(u.nome, '') LIKE ?
                   OR COALESCE(u.username, '') LIKE ?
                ORDER BY i.data_incidente DESC, i.id DESC
                LIMIT 80
                """,
                (wildcard, wildcard, wildcard, wildcard, wildcard, wildcard),
            ).fetchall()
            ips = connection.execute(
                """
                SELECT
                    ip_relacionado,
                    COUNT(*) AS total,
                    MAX(data_incidente) AS ultimo_incidente
                FROM incidentes
                WHERE COALESCE(ip_relacionado, '') LIKE ?
                GROUP BY ip_relacionado
                ORDER BY total DESC, ultimo_incidente DESC
                LIMIT 30
                """,
                (wildcard,),
            ).fetchall()

        return {
            "usuarios": [dict(row) for row in users],
            "incidentes": [dict(row) for row in incidents],
            "ips": [dict(row) for row in ips if row["ip_relacionado"]],
        }

    def _require_session(self, actor: User | None) -> None:
        if actor is None:
            raise PermissionError("Sessao expirada. Faca login novamente.")
