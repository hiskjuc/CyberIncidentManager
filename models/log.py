"""System action log model."""

from __future__ import annotations


class ActionLog:
    def __init__(
        self,
        log_id: int | None,
        usuario_id: int | None,
        acao: str,
        detalhes: str,
        criado_em: str | None = None,
    ) -> None:
        self._id = log_id
        self._usuario_id = usuario_id
        self._acao = acao
        self.__detalhes = detalhes
        self._criado_em = criado_em

    @property
    def acao(self) -> str:
        return self._acao

    @property
    def detalhes(self) -> str:
        return self.__detalhes
