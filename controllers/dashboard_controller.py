"""Dashboard aggregation queries."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

from database.connection import DatabaseConnection
from models.user import User
from utils.validators import ALLOWED_SEVERITIES, ALLOWED_STATUSES


class DashboardController:
    def __init__(self, database: DatabaseConnection) -> None:
        self._database = database

    def get_dashboard_data(self, actor: User) -> dict[str, Any]:
        self._require_session(actor)

        with self._database.connect() as connection:
            metrics = connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN severidade = 'Critica' THEN 1 ELSE 0 END) AS criticos,
                    SUM(CASE WHEN status = 'Resolvido' THEN 1 ELSE 0 END) AS resolvidos
                FROM incidentes
                """
            ).fetchone()
            severity_rows = connection.execute(
                """
                SELECT severidade, COUNT(*) AS total
                FROM incidentes
                GROUP BY severidade
                """
            ).fetchall()
            status_rows = connection.execute(
                """
                SELECT status, COUNT(*) AS total
                FROM incidentes
                GROUP BY status
                """
            ).fetchall()
            recent_rows = connection.execute(
                """
                SELECT
                    i.id,
                    i.titulo,
                    i.severidade,
                    i.status,
                    i.data_incidente,
                    COALESCE(u.nome, 'Nao atribuido') AS responsavel
                FROM incidentes AS i
                LEFT JOIN usuarios AS u ON u.id = i.responsavel_id
                ORDER BY i.id DESC
                LIMIT 6
                """
            ).fetchall()

        severity_counts = OrderedDict((severity, 0) for severity in ALLOWED_SEVERITIES)
        severity_counts.update({row["severidade"]: row["total"] for row in severity_rows})

        status_counts = OrderedDict((status, 0) for status in ALLOWED_STATUSES)
        status_counts.update({row["status"]: row["total"] for row in status_rows})

        return {
            "metrics": {
                "total": int(metrics["total"] or 0),
                "criticos": int(metrics["criticos"] or 0),
                "resolvidos": int(metrics["resolvidos"] or 0),
            },
            "severity_counts": severity_counts,
            "status_counts": status_counts,
            "recent_incidents": [dict(row) for row in recent_rows],
        }

    def _require_session(self, actor: User | None) -> None:
        if actor is None:
            raise PermissionError("Sessao expirada. Faca login novamente.")
