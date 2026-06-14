"""Authentication and user administration logic."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from database.connection import DatabaseConnection
from models.user import User, user_from_row
from utils.security import hash_password
from utils.validators import (
    ValidationError,
    validate_login,
    validate_user_payload,
    validate_user_update_payload,
)


class AuthController:
    """Controls login state and administrator-only user registration."""

    def __init__(self, database: DatabaseConnection) -> None:
        self._database = database
        self._current_user: User | None = None
        self._current_login_at: datetime | None = None

    @property
    def current_user(self) -> User | None:
        return self._current_user

    @property
    def current_login_at(self) -> datetime | None:
        return self._current_login_at

    def login(self, username: str, password: str) -> User:
        username, password = validate_login(username, password)
        authenticated_user: User | None = None

        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM usuarios WHERE username = ?",
                (username,),
            ).fetchone()

            if row is not None:
                candidate = user_from_row(row)
                if candidate.verify_password(password):
                    authenticated_user = candidate
                    self._write_log(
                        connection,
                        candidate.id,
                        "LOGIN",
                        f"Login realizado por {candidate.username}.",
                    )

            if authenticated_user is None:
                self._write_log(
                    connection,
                    row["id"] if row else None,
                    "LOGIN_FALHO",
                    f"Tentativa de login recusada para o username {username}.",
                )

        if authenticated_user is None:
            raise PermissionError("Usuario ou senha invalidos.")

        self._current_user = authenticated_user
        self._current_login_at = datetime.now()
        return authenticated_user

    def logout(self) -> None:
        if self._current_user is None:
            return

        with self._database.connect() as connection:
            self._write_log(
                connection,
                self._current_user.id,
                "LOGOUT",
                f"Sessao encerrada por {self._current_user.username}.",
            )

        self._current_user = None
        self._current_login_at = None

    def save_theme_preference(self, actor: User, theme: str) -> None:
        self._require_session(actor)
        if theme not in ("Dark", "Light"):
            raise ValueError("Tema invalido.")

        with self._database.connect() as connection:
            connection.execute(
                "UPDATE usuarios SET tema_preferido = ? WHERE id = ?",
                (theme, actor.id),
            )
            self._write_log(
                connection,
                actor.id,
                "ALTERAR_TEMA",
                f"Preferencia visual alterada para {theme}.",
            )
        actor.set_theme_preference(theme)

    def create_user(self, actor: User, payload: dict[str, Any]) -> User:
        self._require_user_manager(actor)
        validated = validate_user_payload(payload)

        try:
            with self._database.connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO usuarios (nome, username, password_hash, cargo, tipo_usuario)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        validated["nome"],
                        validated["username"],
                        hash_password(validated["password"]),
                        validated["cargo"],
                        validated["tipo_usuario"],
                    ),
                )
                row = connection.execute(
                    "SELECT * FROM usuarios WHERE id = ?",
                    (cursor.lastrowid,),
                ).fetchone()
                self._write_log(
                    connection,
                    actor.id,
                    "CRIAR_USUARIO",
                    f"Usuario {validated['username']} criado como {validated['tipo_usuario']}.",
                )
        except sqlite3.IntegrityError as exc:
            raise ValidationError("Username ja cadastrado.") from exc

        if row is None:
            raise RuntimeError("Usuario criado, mas nao foi possivel recarrega-lo.")
        return user_from_row(row)

    def list_users(self, actor: User) -> list[User]:
        self._require_user_manager(actor)
        with self._database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM usuarios ORDER BY nome COLLATE NOCASE"
            ).fetchall()
        return [user_from_row(row) for row in rows]

    def get_user(self, actor: User, user_id: int) -> User:
        self._require_user_manager(actor)
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM usuarios WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            raise ValueError("Usuario nao encontrado.")
        return user_from_row(row)

    def update_user(self, actor: User, user_id: int, payload: dict[str, Any]) -> User:
        self._require_user_manager(actor)
        validated = validate_user_update_payload(payload)

        with self._database.connect() as connection:
            current = connection.execute(
                "SELECT * FROM usuarios WHERE id = ?",
                (user_id,),
            ).fetchone()
            if current is None:
                raise ValueError("Usuario nao encontrado.")

            if (
                current["tipo_usuario"] == "Administrador"
                and validated["tipo_usuario"] != "Administrador"
                and self._admin_count(connection) <= 1
            ):
                raise PermissionError("Nao e permitido remover o ultimo administrador.")

            if validated["password"]:
                cursor = connection.execute(
                    """
                    UPDATE usuarios
                    SET nome = ?, password_hash = ?, cargo = ?, tipo_usuario = ?
                    WHERE id = ?
                    """,
                    (
                        validated["nome"],
                        hash_password(validated["password"]),
                        validated["cargo"],
                        validated["tipo_usuario"],
                        user_id,
                    ),
                )
            else:
                cursor = connection.execute(
                    """
                    UPDATE usuarios
                    SET nome = ?, cargo = ?, tipo_usuario = ?
                    WHERE id = ?
                    """,
                    (
                        validated["nome"],
                        validated["cargo"],
                        validated["tipo_usuario"],
                        user_id,
                    ),
                )

            if cursor.rowcount == 0:
                raise ValueError("Usuario nao encontrado.")

            row = connection.execute(
                "SELECT * FROM usuarios WHERE id = ?",
                (user_id,),
            ).fetchone()
            self._write_log(
                connection,
                actor.id,
                "ALTERAR_USUARIO",
                f"Usuario {current['username']} atualizado.",
            )

        if row is None:
            raise RuntimeError("Usuario atualizado, mas nao foi possivel recarrega-lo.")
        updated_user = user_from_row(row)
        if self._current_user and self._current_user.id == updated_user.id:
            self._current_user = updated_user
        return updated_user

    def delete_user(self, actor: User, user_id: int) -> None:
        self._require_user_manager(actor)

        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM usuarios WHERE id = ?",
                (user_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Usuario nao encontrado.")
            if row["tipo_usuario"] == "Administrador" and self._admin_count(connection) <= 1:
                raise PermissionError("Nao e permitido excluir o ultimo administrador.")
            if actor.id == user_id:
                raise PermissionError("Nao e permitido excluir o proprio usuario logado.")

            connection.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
            self._write_log(
                connection,
                actor.id,
                "EXCLUIR_USUARIO",
                f"Usuario {row['username']} excluido.",
            )

    def list_assignable_users(self, actor: User) -> list[dict[str, Any]]:
        self._require_session(actor)
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, nome, username, tipo_usuario
                FROM usuarios
                WHERE tipo_usuario IN ('Administrador', 'Analista')
                ORDER BY nome COLLATE NOCASE
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def _require_session(self, actor: User | None) -> None:
        if actor is None:
            raise PermissionError("Sessao expirada. Faca login novamente.")

    def _require_user_manager(self, actor: User | None) -> None:
        self._require_session(actor)
        if actor is None or not actor.can_manage_users():
            raise PermissionError("Somente administradores podem gerenciar usuarios.")

    def _write_log(
        self,
        connection: sqlite3.Connection,
        user_id: int | None,
        action: str,
        details: str,
    ) -> None:
        try:
            connection.execute(
                """
                INSERT INTO logs (usuario_id, acao, detalhes)
                VALUES (?, ?, ?)
                """,
                (user_id, action, details),
            )
        except sqlite3.Error:
            return

    def _admin_count(self, connection: sqlite3.Connection) -> int:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM usuarios WHERE tipo_usuario = 'Administrador'"
        ).fetchone()
        return int(row["total"] if row else 0)
