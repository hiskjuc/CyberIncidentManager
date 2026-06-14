"""Create a populated SQLite database for demonstrations and tests."""

from __future__ import annotations

import sys
from pathlib import Path

from database.connection import DatabaseConnection
from database.init_db import initialize_database
from utils.security import hash_password


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "banco_teste" / "cyber_incident_manager_teste.db"

TEST_USERS = (
    {
        "nome": "Administrador de Testes",
        "username": "admin",
        "password": "admin123",
        "cargo": "Coordenacao SOC",
        "tipo_usuario": "Administrador",
    },
    {
        "nome": "Carla Menezes",
        "username": "carla.soc",
        "password": "analista123",
        "cargo": "Analista SOC N2",
        "tipo_usuario": "Analista",
    },
    {
        "nome": "Rafael Lima",
        "username": "rafael.ir",
        "password": "analista123",
        "cargo": "Analista de Resposta",
        "tipo_usuario": "Analista",
    },
    {
        "nome": "Beatriz Costa",
        "username": "beatriz.threat",
        "password": "analista123",
        "cargo": "Threat Hunter",
        "tipo_usuario": "Analista",
    },
)

TEST_INCIDENTS = (
    {
        "titulo": "Phishing contra equipe financeira",
        "descricao": "Usuarios reportaram e-mails com link falso para atualizacao de senha.",
        "tipo_ataque": "Phishing",
        "severidade": "Alta",
        "status": "Em analise",
        "data_incidente": "2026-05-21",
        "ip_relacionado": "10.20.4.18",
        "responsavel": "carla.soc",
        "criado_por": "admin",
    },
    {
        "titulo": "Ransomware bloqueado em estacao",
        "descricao": "EDR interrompeu execucao suspeita e a maquina foi isolada.",
        "tipo_ataque": "Ransomware",
        "severidade": "Critica",
        "status": "Contido",
        "data_incidente": "2026-05-20",
        "ip_relacionado": "10.20.8.44",
        "responsavel": "rafael.ir",
        "criado_por": "admin",
    },
    {
        "titulo": "Tentativas de brute force no VPN",
        "descricao": "Picos de autenticacoes falhas foram correlacionados no gateway remoto.",
        "tipo_ataque": "Brute force",
        "severidade": "Media",
        "status": "Aberto",
        "data_incidente": "2026-05-19",
        "ip_relacionado": "172.16.10.33",
        "responsavel": "beatriz.threat",
        "criado_por": "carla.soc",
    },
    {
        "titulo": "Exfiltracao suspeita via DNS",
        "descricao": "Consultas DNS longas e repetitivas foram identificadas em servidor interno.",
        "tipo_ataque": "Exfiltracao",
        "severidade": "Critica",
        "status": "Em analise",
        "data_incidente": "2026-05-18",
        "ip_relacionado": "10.30.2.9",
        "responsavel": "beatriz.threat",
        "criado_por": "admin",
    },
    {
        "titulo": "Malware removido de notebook",
        "descricao": "Arquivo malicioso foi removido apos varredura e redefinicao de credenciais.",
        "tipo_ataque": "Malware",
        "severidade": "Alta",
        "status": "Resolvido",
        "data_incidente": "2026-05-17",
        "ip_relacionado": "192.168.15.77",
        "responsavel": "rafael.ir",
        "criado_por": "rafael.ir",
    },
    {
        "titulo": "Acesso indevido a painel legado",
        "descricao": "Conta antiga acessou area administrativa fora da janela de manutencao.",
        "tipo_ataque": "Acesso indevido",
        "severidade": "Alta",
        "status": "Contido",
        "data_incidente": "2026-05-16",
        "ip_relacionado": "10.10.1.25",
        "responsavel": "carla.soc",
        "criado_por": "admin",
    },
    {
        "titulo": "Varredura de portas no segmento DMZ",
        "descricao": "Firewall detectou varredura concentrada em servicos publicados.",
        "tipo_ataque": "Reconhecimento",
        "severidade": "Baixa",
        "status": "Resolvido",
        "data_incidente": "2026-05-15",
        "ip_relacionado": "172.20.0.14",
        "responsavel": "beatriz.threat",
        "criado_por": "beatriz.threat",
    },
    {
        "titulo": "Credencial exposta em repositorio",
        "descricao": "Token de teste foi encontrado em commit e revogado pela equipe.",
        "tipo_ataque": "Vazamento de credencial",
        "severidade": "Media",
        "status": "Resolvido",
        "data_incidente": "2026-05-13",
        "ip_relacionado": None,
        "responsavel": "carla.soc",
        "criado_por": "carla.soc",
    },
    {
        "titulo": "Alerta de SQL injection em portal",
        "descricao": "WAF bloqueou payloads repetidos em parametro de busca do portal.",
        "tipo_ataque": "SQL injection",
        "severidade": "Alta",
        "status": "Em analise",
        "data_incidente": "2026-05-12",
        "ip_relacionado": "10.50.3.61",
        "responsavel": "rafael.ir",
        "criado_por": "admin",
    },
    {
        "titulo": "DDoS curto em API publica",
        "descricao": "Volume anormal foi mitigado pelo provedor antes de indisponibilidade prolongada.",
        "tipo_ataque": "DDoS",
        "severidade": "Critica",
        "status": "Resolvido",
        "data_incidente": "2026-05-10",
        "ip_relacionado": "172.18.4.90",
        "responsavel": "rafael.ir",
        "criado_por": "admin",
    },
    {
        "titulo": "Login impossivel em conta corporativa",
        "descricao": "Acesso foi observado em regioes incompativeis dentro de poucos minutos.",
        "tipo_ataque": "Comprometimento de conta",
        "severidade": "Media",
        "status": "Aberto",
        "data_incidente": "2026-05-08",
        "ip_relacionado": "192.168.40.12",
        "responsavel": "carla.soc",
        "criado_por": "beatriz.threat",
    },
    {
        "titulo": "Macro suspeita recebida por e-mail",
        "descricao": "Documento foi colocado em quarentena antes de execucao.",
        "tipo_ataque": "Anexo malicioso",
        "severidade": "Baixa",
        "status": "Resolvido",
        "data_incidente": "2026-05-06",
        "ip_relacionado": None,
        "responsavel": "carla.soc",
        "criado_por": "carla.soc",
    },
    {
        "titulo": "Servidor com beaconing recorrente",
        "descricao": "Telemetria mostrou conexoes periodicas a destino nao catalogado.",
        "tipo_ataque": "Command and control",
        "severidade": "Critica",
        "status": "Em analise",
        "data_incidente": "2026-05-05",
        "ip_relacionado": "10.60.7.12",
        "responsavel": "beatriz.threat",
        "criado_por": "admin",
    },
    {
        "titulo": "Dispositivo sem patch explorado",
        "descricao": "Tentativa de exploracao foi contida e patch emergencial foi aplicado.",
        "tipo_ataque": "Exploracao de vulnerabilidade",
        "severidade": "Alta",
        "status": "Contido",
        "data_incidente": "2026-05-03",
        "ip_relacionado": "10.70.1.3",
        "responsavel": "rafael.ir",
        "criado_por": "rafael.ir",
    },
    {
        "titulo": "Arquivo confidencial compartilhado",
        "descricao": "Compartilhamento externo foi removido apos alerta DLP.",
        "tipo_ataque": "Exposicao de dados",
        "severidade": "Media",
        "status": "Resolvido",
        "data_incidente": "2026-05-02",
        "ip_relacionado": None,
        "responsavel": "carla.soc",
        "criado_por": "admin",
    },
)


def create_test_database(output_path: Path = DEFAULT_OUTPUT) -> Path:
    """Create a fresh demo database without touching application data."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    database = initialize_database(DatabaseConnection(output_path))

    with database.connect() as connection:
        connection.execute("DELETE FROM incidentes")
        connection.execute("DELETE FROM logs")
        connection.execute("DELETE FROM usuarios")
        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name IN ('usuarios', 'incidentes', 'logs')"
        )

        user_ids: dict[str, int] = {}
        for user in TEST_USERS:
            cursor = connection.execute(
                """
                INSERT INTO usuarios (nome, username, password_hash, cargo, tipo_usuario)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user["nome"],
                    user["username"],
                    hash_password(user["password"]),
                    user["cargo"],
                    user["tipo_usuario"],
                ),
            )
            user_ids[user["username"]] = int(cursor.lastrowid)

        for incident in TEST_INCIDENTS:
            connection.execute(
                """
                INSERT INTO incidentes (
                    titulo,
                    descricao,
                    tipo_ataque,
                    severidade,
                    status,
                    data_incidente,
                    ip_relacionado,
                    responsavel_id,
                    criado_por_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident["titulo"],
                    incident["descricao"],
                    incident["tipo_ataque"],
                    incident["severidade"],
                    incident["status"],
                    incident["data_incidente"],
                    incident["ip_relacionado"],
                    user_ids[incident["responsavel"]],
                    user_ids[incident["criado_por"]],
                ),
            )

        logs = (
            (
                user_ids["admin"],
                "IMPORTAR_BASE_TESTE",
                "Base demonstrativa criada para testes do Cyber Incident Manager.",
            ),
            (
                user_ids["carla.soc"],
                "LOGIN",
                "Login demonstrativo registrado para Carla Menezes.",
            ),
            (
                user_ids["rafael.ir"],
                "ALTERAR_INCIDENTE",
                "Incidente de malware marcado como resolvido durante triagem.",
            ),
            (
                user_ids["beatriz.threat"],
                "CRIAR_INCIDENTE",
                "Novo incidente de beaconing adicionado a fila de investigacao.",
            ),
        )
        connection.executemany(
            "INSERT INTO logs (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
            logs,
        )

    return output_path


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    print(create_test_database(target))
