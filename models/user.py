"""User domain model and role specializations."""

from __future__ import annotations

from sqlite3 import Row

from utils.security import verify_password


class User:
    """Base user with role-specific behavior delegated to subclasses."""

    user_type = "Usuario"

    def __init__(
        self,
        user_id: int,
        nome: str,
        username: str,
        password_hash: str,
        cargo: str,
        theme_preference: str = "Dark",
    ) -> None:
        self._id = user_id
        self._nome = nome
        self._username = username
        self.__password_hash = password_hash
        self._cargo = cargo
        self._theme_preference = theme_preference

    @property
    def id(self) -> int:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def username(self) -> str:
        return self._username

    @property
    def cargo(self) -> str:
        return self._cargo

    @property
    def theme_preference(self) -> str:
        return self._theme_preference

    def set_theme_preference(self, theme: str) -> None:
        self._theme_preference = theme

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.__password_hash)

    def can_manage_users(self) -> bool:
        return False

    def can_create_incidents(self) -> bool:
        return False

    def can_edit_incidents(self) -> bool:
        return False

    def can_delete_incidents(self) -> bool:
        return False

    def role_description(self) -> str:
        return "Acesso operacional aos incidentes."


class Administrator(User):
    user_type = "Administrador"

    def can_manage_users(self) -> bool:
        return True

    def can_create_incidents(self) -> bool:
        return True

    def can_edit_incidents(self) -> bool:
        return True

    def can_delete_incidents(self) -> bool:
        return True

    def role_description(self) -> str:
        return "Gerencia usuarios, incidentes e relatorios."


class Analyst(User):
    user_type = "Analista"

    def can_create_incidents(self) -> bool:
        return True

    def can_edit_incidents(self) -> bool:
        return True

    def role_description(self) -> str:
        return "Cria e atualiza incidentes sob acompanhamento."


class Viewer(User):
    user_type = "Visualizador"

    def role_description(self) -> str:
        return "Visualiza dashboard e incidentes em modo consulta."


def user_from_row(row: Row) -> User:
    """Build the correct subclass from a SQLite user row."""
    role_classes = {
        Administrator.user_type: Administrator,
        Analyst.user_type: Analyst,
        Viewer.user_type: Viewer,
    }
    role_class = role_classes.get(row["tipo_usuario"], Analyst)
    return role_class(
        user_id=row["id"],
        nome=row["nome"],
        username=row["username"],
        password_hash=row["password_hash"],
        cargo=row["cargo"],
        theme_preference=row["tema_preferido"],
    )
