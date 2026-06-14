"""Internal knowledge base CRUD."""

from __future__ import annotations

from typing import Any

from database.connection import DatabaseConnection
from models.user import User


class KnowledgeController:
    def __init__(self, database: DatabaseConnection) -> None:
        self._database = database

    def list_articles(self, actor: User, search: str = "", category: str = "Todas") -> list[dict[str, Any]]:
        self._require_session(actor)
        query = """
            SELECT
                b.*,
                COALESCE(u.nome, 'Usuario removido') AS autor_nome
            FROM base_conhecimento AS b
            LEFT JOIN usuarios AS u ON u.id = b.autor_id
            WHERE 1 = 1
        """
        params: list[Any] = []
        cleaned = search.strip()
        if cleaned:
            wildcard = f"%{cleaned}%"
            query += """
                AND (
                    b.titulo LIKE ?
                    OR b.categoria LIKE ?
                    OR b.descricao LIKE ?
                    OR b.solucao LIKE ?
                )
            """
            params.extend([wildcard] * 4)
        if category != "Todas":
            query += " AND b.categoria = ?"
            params.append(category)
        query += " ORDER BY b.atualizado_em DESC, b.id DESC"

        with self._database.connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def list_categories(self, actor: User) -> list[str]:
        self._require_session(actor)
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT categoria
                FROM base_conhecimento
                ORDER BY categoria COLLATE NOCASE
                """
            ).fetchall()
        return [row["categoria"] for row in rows]

    def create_article(self, actor: User, payload: dict[str, Any]) -> int:
        self._require_editor(actor)
        data = self._validate_payload(payload)
        with self._database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO base_conhecimento (
                    titulo, categoria, descricao, solucao, autor_id
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (data["titulo"], data["categoria"], data["descricao"], data["solucao"], actor.id),
            )
            self._write_log(
                connection,
                actor.id,
                "CRIAR_ARTIGO",
                f"Artigo de conhecimento criado: {data['titulo']}.",
            )
        return int(cursor.lastrowid)

    def update_article(self, actor: User, article_id: int, payload: dict[str, Any]) -> None:
        self._require_editor(actor)
        data = self._validate_payload(payload)
        with self._database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE base_conhecimento
                SET titulo = ?,
                    categoria = ?,
                    descricao = ?,
                    solucao = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    data["titulo"],
                    data["categoria"],
                    data["descricao"],
                    data["solucao"],
                    article_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError("Artigo nao encontrado.")
            self._write_log(
                connection,
                actor.id,
                "ALTERAR_ARTIGO",
                f"Artigo de conhecimento atualizado: {data['titulo']}.",
            )

    def delete_article(self, actor: User, article_id: int) -> None:
        self._require_editor(actor)
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT titulo FROM base_conhecimento WHERE id = ?",
                (article_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Artigo nao encontrado.")
            connection.execute("DELETE FROM base_conhecimento WHERE id = ?", (article_id,))
            self._write_log(
                connection,
                actor.id,
                "EXCLUIR_ARTIGO",
                f"Artigo de conhecimento excluido: {row['titulo']}.",
            )

    def _validate_payload(self, payload: dict[str, Any]) -> dict[str, str]:
        fields = {
            "titulo": 160,
            "categoria": 80,
            "descricao": 3000,
            "solucao": 3000,
        }
        data: dict[str, str] = {}
        for field, limit in fields.items():
            value = str(payload.get(field) or "").strip()
            if not value:
                raise ValueError(f"{field.replace('_', ' ').title()} e obrigatorio.")
            if len(value) > limit:
                raise ValueError(f"{field.replace('_', ' ').title()} deve ter no maximo {limit} caracteres.")
            data[field] = value
        return data

    def _require_session(self, actor: User | None) -> None:
        if actor is None:
            raise PermissionError("Sessao expirada. Faca login novamente.")

    def _require_editor(self, actor: User | None) -> None:
        self._require_session(actor)
        if actor is None or not actor.can_edit_incidents():
            raise PermissionError("Seu perfil permite apenas consultar a base de conhecimento.")

    def _write_log(self, connection, user_id: int | None, action: str, details: str) -> None:
        try:
            connection.execute(
                "INSERT INTO logs (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                (user_id, action, details),
            )
        except Exception:
            return
