"""Executive analytics that complement the existing dashboard."""

from __future__ import annotations

from typing import Any

from database.connection import DatabaseConnection
from models.user import User


class ExecutiveDashboardController:
    def __init__(self, database: DatabaseConnection) -> None:
        self._database = database

    def get_executive_data(self, actor: User) -> dict[str, Any]:
        self._require_session(actor)
        with self._database.connect() as connection:
            top_assignee = connection.execute(
                """
                SELECT COALESCE(u.nome, 'Nao atribuido') AS nome, COUNT(i.id) AS total
                FROM incidentes AS i
                LEFT JOIN usuarios AS u ON u.id = i.responsavel_id
                GROUP BY i.responsavel_id
                ORDER BY total DESC, nome ASC
                LIMIT 1
                """
            ).fetchone()
            top_attack = connection.execute(
                """
                SELECT tipo_ataque AS nome, COUNT(*) AS total
                FROM incidentes
                GROUP BY tipo_ataque
                ORDER BY total DESC, nome ASC
                LIMIT 1
                """
            ).fetchone()
            common_severity = connection.execute(
                """
                SELECT severidade AS nome, COUNT(*) AS total
                FROM incidentes
                GROUP BY severidade
                ORDER BY total DESC, nome ASC
                LIMIT 1
                """
            ).fetchone()
            by_responsible = connection.execute(
                """
                SELECT
                    COALESCE(u.nome, 'Nao atribuido') AS responsavel,
                    COUNT(i.id) AS total,
                    SUM(CASE WHEN i.status = 'Resolvido' THEN 1 ELSE 0 END) AS resolvidos
                FROM incidentes AS i
                LEFT JOIN usuarios AS u ON u.id = i.responsavel_id
                GROUP BY i.responsavel_id
                ORDER BY total DESC, responsavel ASC
                """
            ).fetchall()
            most_resolved = connection.execute(
                """
                SELECT COALESCE(u.nome, 'Nao atribuido') AS nome, COUNT(i.id) AS total
                FROM incidentes AS i
                LEFT JOIN usuarios AS u ON u.id = i.responsavel_id
                WHERE i.status = 'Resolvido'
                GROUP BY i.responsavel_id
                ORDER BY total DESC, nome ASC
                LIMIT 1
                """
            ).fetchone()

        return {
            "top_assignee": self._row_or_empty(top_assignee),
            "top_attack": self._row_or_empty(top_attack),
            "common_severity": self._row_or_empty(common_severity),
            "by_responsible": [dict(row) for row in by_responsible],
            "most_resolved": self._row_or_empty(most_resolved),
        }

    def _row_or_empty(self, row) -> dict[str, Any]:
        return dict(row) if row else {"nome": "-", "total": 0}

    def _require_session(self, actor: User | None) -> None:
        if actor is None:
            raise PermissionError("Sessao expirada. Faca login novamente.")
