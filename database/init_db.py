"""Database bootstrap script."""

from __future__ import annotations

import sqlite3

from database.connection import DatabaseConnection
from database.models import INDEX_STATEMENTS, SCHEMA_STATEMENTS
from utils.security import hash_password


DEFAULT_ADMIN = {
    "nome": "Administrador Padrao",
    "username": "admin",
    "password": "admin123",
    "cargo": "Gestao de Seguranca",
    "tipo_usuario": "Administrador",
}


def initialize_database(database: DatabaseConnection | None = None) -> DatabaseConnection:
    """Create tables and seed the first administrator when needed."""
    db = database or DatabaseConnection()

    with db.connect() as connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)

        _run_migration_safely(connection, _ensure_user_theme_column)
        _run_migration_safely(connection, _ensure_user_roles)
        _run_migration_safely(connection, _ensure_incident_creator_delete_policy)
        _run_migration_safely(connection, _ensure_log_user_delete_policy)

        for statement in INDEX_STATEMENTS:
            connection.execute(statement)

        existing_admin = connection.execute(
            "SELECT id FROM usuarios WHERE username = ?",
            (DEFAULT_ADMIN["username"],),
        ).fetchone()

        if existing_admin is None:
            cursor = connection.execute(
                """
                INSERT INTO usuarios (nome, username, password_hash, cargo, tipo_usuario)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_ADMIN["nome"],
                    DEFAULT_ADMIN["username"],
                    hash_password(DEFAULT_ADMIN["password"]),
                    DEFAULT_ADMIN["cargo"],
                    DEFAULT_ADMIN["tipo_usuario"],
                ),
            )
            connection.execute(
                """
                INSERT INTO logs (usuario_id, acao, detalhes)
                VALUES (?, ?, ?)
                """,
                (
                    cursor.lastrowid,
                    "CRIAR_ADMIN_PADRAO",
                    "Usuario administrador padrao criado na inicializacao.",
                ),
            )

    return db


def _ensure_user_theme_column(connection) -> None:
    """Migrate existing SQLite files without rebuilding their data."""
    user_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(usuarios)").fetchall()
    }
    if "tema_preferido" not in user_columns:
        connection.execute(
            "ALTER TABLE usuarios ADD COLUMN tema_preferido TEXT NOT NULL DEFAULT 'Dark'"
        )


def _run_migration_safely(connection, migration) -> None:
    try:
        migration(connection)
    except sqlite3.OperationalError as exc:
        if "readonly" not in str(exc).lower():
            raise


def _ensure_user_roles(connection) -> None:
    """Allow the Visualizador role on databases created before this release."""
    create_sql = _table_sql(connection, "usuarios")
    if "Visualizador" in create_sql:
        return

    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute("ALTER TABLE usuarios RENAME TO usuarios_old")
    connection.execute(
        """
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            cargo TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL
                CHECK (tipo_usuario IN ('Administrador', 'Analista', 'Visualizador')),
            tema_preferido TEXT NOT NULL DEFAULT 'Dark'
                CHECK (tema_preferido IN ('Dark', 'Light')),
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute(
        """
        INSERT INTO usuarios (
            id, nome, username, password_hash, cargo, tipo_usuario, tema_preferido, criado_em
        )
        SELECT
            id,
            nome,
            username,
            password_hash,
            cargo,
            CASE
                WHEN tipo_usuario IN ('Administrador', 'Analista', 'Visualizador')
                THEN tipo_usuario
                ELSE 'Analista'
            END,
            COALESCE(tema_preferido, 'Dark'),
            criado_em
        FROM usuarios_old
        """
    )
    connection.execute("DROP TABLE usuarios_old")
    connection.commit()
    connection.execute("PRAGMA foreign_keys = ON")


def _ensure_incident_creator_delete_policy(connection) -> None:
    """Let user deletion preserve incidents by nulling the creator reference."""
    create_sql = _table_sql(connection, "incidentes")
    if "criado_por_id INTEGER NOT NULL" not in create_sql and "ON DELETE RESTRICT" not in create_sql:
        return

    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute("ALTER TABLE incidentes RENAME TO incidentes_old")
    connection.execute(
        """
        CREATE TABLE incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            tipo_ataque TEXT NOT NULL,
            severidade TEXT NOT NULL
                CHECK (severidade IN ('Baixa', 'Media', 'Alta', 'Critica')),
            status TEXT NOT NULL
                CHECK (status IN ('Aberto', 'Em analise', 'Contido', 'Resolvido')),
            data_incidente TEXT NOT NULL,
            ip_relacionado TEXT,
            responsavel_id INTEGER,
            criado_por_id INTEGER,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (responsavel_id) REFERENCES usuarios(id) ON DELETE SET NULL,
            FOREIGN KEY (criado_por_id) REFERENCES usuarios(id) ON DELETE SET NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO incidentes (
            id,
            titulo,
            descricao,
            tipo_ataque,
            severidade,
            status,
            data_incidente,
            ip_relacionado,
            responsavel_id,
            criado_por_id,
            criado_em,
            atualizado_em
        )
        SELECT
            id,
            titulo,
            descricao,
            tipo_ataque,
            severidade,
            status,
            data_incidente,
            ip_relacionado,
            responsavel_id,
            criado_por_id,
            criado_em,
            atualizado_em
        FROM incidentes_old
        """
    )
    connection.execute("DROP TABLE incidentes_old")
    connection.commit()
    connection.execute("PRAGMA foreign_keys = ON")


def _ensure_log_user_delete_policy(connection) -> None:
    """Repair logs foreign keys that may still reference a renamed user table."""
    create_sql = _table_sql(connection, "logs")
    if "usuarios_old" not in create_sql:
        return

    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute("ALTER TABLE logs RENAME TO logs_old")
    connection.execute(
        """
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            acao TEXT NOT NULL,
            detalhes TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO logs (id, usuario_id, acao, detalhes, criado_em)
        SELECT id, usuario_id, acao, detalhes, criado_em
        FROM logs_old
        """
    )
    connection.execute("DROP TABLE logs_old")
    connection.commit()
    connection.execute("PRAGMA foreign_keys = ON")


def _table_sql(connection, table_name: str) -> str:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row["sql"] if row and row["sql"] else ""


if __name__ == "__main__":
    initialized_db = initialize_database()
    print(f"Banco inicializado em: {initialized_db.db_path}")
