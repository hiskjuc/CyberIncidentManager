"""SQLite connection management."""

from __future__ import annotations

import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class DatabaseConnection:
    """Owns the SQLite database path and transaction lifecycle."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        default_path = self._portable_default_path()
        self._db_path = Path(db_path) if db_path else default_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        return self._db_path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Provide a committed transaction with row dictionaries enabled."""
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _portable_default_path(self) -> Path:
        """Keep mutable data with the source project or the packaged app."""
        if getattr(sys, "frozen", False):
            app_root = Path(sys.executable).resolve().parent
        else:
            app_root = Path(__file__).resolve().parents[1]
        return app_root / "data" / "cyber_incident_manager.db"
