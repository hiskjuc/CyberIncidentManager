"""Input validation and normalization."""

from __future__ import annotations

import ipaddress
import re
from datetime import datetime
from typing import Any


ALLOWED_USER_TYPES = ("Administrador", "Analista", "Visualizador")
ALLOWED_SEVERITIES = ("Baixa", "Media", "Alta", "Critica")
ALLOWED_STATUSES = ("Aberto", "Em analise", "Contido", "Resolvido")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,40}$")


class ValidationError(ValueError):
    """Raised when user supplied data is not ready for persistence."""


def _required_text(value: Any, field_name: str, max_length: int) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValidationError(f"{field_name} e obrigatorio.")
    if len(cleaned) > max_length:
        raise ValidationError(f"{field_name} deve ter no maximo {max_length} caracteres.")
    return cleaned


def validate_login(username: str, password: str) -> tuple[str, str]:
    cleaned_username = _required_text(username, "Username", 40)
    cleaned_password = _required_text(password, "Senha", 128)
    return cleaned_username, cleaned_password


def validate_user_payload(payload: dict[str, Any]) -> dict[str, str]:
    nome = _required_text(payload.get("nome"), "Nome", 120)
    username = _required_text(payload.get("username"), "Username", 40)
    password = _required_text(payload.get("password"), "Senha", 128)
    cargo = _required_text(payload.get("cargo"), "Cargo", 80)
    tipo_usuario = _required_text(payload.get("tipo_usuario"), "Tipo de usuario", 40)

    if not USERNAME_PATTERN.fullmatch(username):
        raise ValidationError(
            "Username deve ter 3 a 40 caracteres e usar letras, numeros, ponto, traco ou underline."
        )
    if len(password) < 8:
        raise ValidationError("Senha deve ter pelo menos 8 caracteres.")
    if tipo_usuario not in ALLOWED_USER_TYPES:
        raise ValidationError("Tipo de usuario invalido.")

    return {
        "nome": nome,
        "username": username,
        "password": password,
        "cargo": cargo,
        "tipo_usuario": tipo_usuario,
    }


def validate_user_update_payload(payload: dict[str, Any]) -> dict[str, str]:
    nome = _required_text(payload.get("nome"), "Nome", 120)
    cargo = _required_text(payload.get("cargo"), "Cargo", 80)
    tipo_usuario = _required_text(payload.get("tipo_usuario"), "Tipo de usuario", 40)
    password = str(payload.get("password") or "").strip()

    if tipo_usuario not in ALLOWED_USER_TYPES:
        raise ValidationError("Tipo de usuario invalido.")
    if password and len(password) < 8:
        raise ValidationError("Senha deve ter pelo menos 8 caracteres.")

    return {
        "nome": nome,
        "password": password,
        "cargo": cargo,
        "tipo_usuario": tipo_usuario,
    }


def validate_incident_payload(payload: dict[str, Any]) -> dict[str, Any]:
    titulo = _required_text(payload.get("titulo"), "Titulo", 160)
    descricao = _required_text(payload.get("descricao"), "Descricao", 3000)
    tipo_ataque = _required_text(payload.get("tipo_ataque"), "Tipo de ataque", 100)
    severidade = _required_text(payload.get("severidade"), "Severidade", 20)
    status = _required_text(payload.get("status"), "Status", 30)
    data_incidente = _required_text(payload.get("data_incidente"), "Data", 10)
    ip_relacionado = str(payload.get("ip_relacionado") or "").strip()
    responsavel_id = payload.get("responsavel_id")

    if severidade not in ALLOWED_SEVERITIES:
        raise ValidationError("Severidade invalida.")
    if status not in ALLOWED_STATUSES:
        raise ValidationError("Status invalido.")

    try:
        datetime.strptime(data_incidente, "%Y-%m-%d")
    except ValueError as exc:
        raise ValidationError("Data deve estar no formato AAAA-MM-DD.") from exc

    if ip_relacionado:
        try:
            ipaddress.ip_address(ip_relacionado)
        except ValueError as exc:
            raise ValidationError("IP relacionado invalido.") from exc

    if responsavel_id in ("", None):
        responsavel_id = None
    elif not isinstance(responsavel_id, int):
        raise ValidationError("Responsavel invalido.")

    return {
        "titulo": titulo,
        "descricao": descricao,
        "tipo_ataque": tipo_ataque,
        "severidade": severidade,
        "status": status,
        "data_incidente": data_incidente,
        "ip_relacionado": ip_relacionado or None,
        "responsavel_id": responsavel_id,
    }
