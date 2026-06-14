"""Incident domain model."""

from __future__ import annotations

from sqlite3 import Row


class Incident:
    """Represents one security incident tracked by the team."""

    def __init__(
        self,
        incident_id: int | None,
        titulo: str,
        descricao: str,
        tipo_ataque: str,
        severidade: str,
        status: str,
        data_incidente: str,
        ip_relacionado: str | None,
        responsavel_id: int | None,
        responsavel_nome: str | None = None,
        criado_por_nome: str | None = None,
        criado_em: str | None = None,
        atualizado_em: str | None = None,
    ) -> None:
        self._id = incident_id
        self._titulo = titulo
        self.__descricao = descricao
        self._tipo_ataque = tipo_ataque
        self._severidade = severidade
        self._status = status
        self._data_incidente = data_incidente
        self._ip_relacionado = ip_relacionado
        self._responsavel_id = responsavel_id
        self._responsavel_nome = responsavel_nome
        self._criado_por_nome = criado_por_nome
        self._criado_em = criado_em
        self._atualizado_em = atualizado_em

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def descricao(self) -> str:
        return self.__descricao

    @property
    def tipo_ataque(self) -> str:
        return self._tipo_ataque

    @property
    def severidade(self) -> str:
        return self._severidade

    @property
    def status(self) -> str:
        return self._status

    @property
    def data_incidente(self) -> str:
        return self._data_incidente

    @property
    def ip_relacionado(self) -> str | None:
        return self._ip_relacionado

    @property
    def responsavel_id(self) -> int | None:
        return self._responsavel_id

    @property
    def responsavel_nome(self) -> str | None:
        return self._responsavel_nome

    @property
    def criado_por_nome(self) -> str | None:
        return self._criado_por_nome

    @property
    def criado_em(self) -> str | None:
        return self._criado_em

    @property
    def atualizado_em(self) -> str | None:
        return self._atualizado_em

    @classmethod
    def from_row(cls, row: Row) -> "Incident":
        return cls(
            incident_id=row["id"],
            titulo=row["titulo"],
            descricao=row["descricao"],
            tipo_ataque=row["tipo_ataque"],
            severidade=row["severidade"],
            status=row["status"],
            data_incidente=row["data_incidente"],
            ip_relacionado=row["ip_relacionado"],
            responsavel_id=row["responsavel_id"],
            responsavel_nome=row["responsavel_nome"],
            criado_por_nome=row["criado_por_nome"],
            criado_em=row["criado_em"],
            atualizado_em=row["atualizado_em"],
        )

    def to_record(self) -> tuple[str, str, str, str, str, str, str | None, int | None]:
        return (
            self._titulo,
            self.__descricao,
            self._tipo_ataque,
            self._severidade,
            self._status,
            self._data_incidente,
            self._ip_relacionado,
            self._responsavel_id,
        )
