
import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "database.db"  # altere se seu banco tiver outro nome

usuarios = [
    ("Administrador de Testes", "admin", "Coordenacao SOC", "Administrador"),
    ("Beatriz Costa", "beatriz.threat", "Threat Hunter", "Analista"),
    ("Carla Menezes", "carla.soc", "Analista SOC N2", "Analista"),
    ("Rafael Lima", "rafael.ir", "Analista de Resposta", "Analista"),
    ("Thaynan", "thay014", "PenTester", "Administrador"),
]

incidentes = [
    ("Phishing contra equipe financeira", "Phishing", "Alta", "Em analise"),
    ("Ransomware bloqueado em estacao", "Ransomware", "Critica", "Contido"),
    ("Tentativas de brute force no VPN", "Brute Force", "Media", "Aberto"),
    ("Exfiltracao suspeita via DNS", "Exfiltracao", "Critica", "Em analise"),
    ("Malware removido de notebook", "Malware", "Alta", "Resolvido"),
    ("Acesso indevido a painel legado", "Acesso indevido", "Alta", "Contido"),
    ("Varredura de portas no segmento DMZ", "Reconhecimento", "Baixa", "Resolvido"),
    ("Credencial exposta em repositorio", "Vazamento de credenciais", "Media", "Resolvido"),
    ("Alerta de SQL injection em portal", "SQL Injection", "Alta", "Em analise"),
    ("DDoS curto em API publica", "DDoS", "Critica", "Resolvido"),
    ("Login impossivel em conta corporativa", "Comprometimento de conta", "Media", "Aberto"),
    ("Macro suspeita recebida por e-mail", "Anexo malicioso", "Baixa", "Resolvido"),
    ("Servidor com beaconing recorrente", "Command and Control", "Critica", "Em analise"),
    ("Dispositivo sem patch explorado", "Exploracao de vulnerabilidade", "Alta", "Contido"),
    ("Arquivo confidencial compartilhado", "Exposicao de dados", "Media", "Resolvido"),
]

descricoes = [
    "Atividade suspeita identificada pelo SOC durante monitoramento contínuo.",
    "Usuário reportou comportamento anormal no dispositivo corporativo.",
    "Detecção automática realizada via regras de correlação.",
    "Incidente escalado para investigação aprofundada.",
    "Evento associado a possível comprometimento de credenciais.",
]

ips = [
    "192.168.0.14",
    "10.0.0.25",
    "172.16.1.44",
    "45.77.21.90",
    "201.33.18.7",
]

def get_existing_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1].lower() for row in cursor.fetchall()]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0].lower() for row in cursor.fetchall()]

    # Inserir usuários
    if "usuarios" in tables:
        cols = get_existing_columns(cursor, "usuarios")

        for nome, username, cargo, tipo in usuarios:
            values = {}
            if "nome" in cols:
                values["nome"] = nome
            if "username" in cols:
                values["username"] = username
            if "cargo" in cols:
                values["cargo"] = cargo
            if "tipo_usuario" in cols:
                values["tipo_usuario"] = tipo
            elif "tipo" in cols:
                values["tipo"] = tipo

            if values:
                columns = ", ".join(values.keys())
                placeholders = ", ".join(["?"] * len(values))
                sql = f"INSERT INTO usuarios ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(values.values()))

    # Inserir incidentes
    if "incidentes" in tables:
        cols = get_existing_columns(cursor, "incidentes")

        for i, (titulo, ataque, severidade, status) in enumerate(incidentes):
            values = {}

            if "titulo" in cols:
                values["titulo"] = titulo

            if "descricao" in cols:
                values["descricao"] = random.choice(descricoes)

            if "tipo_ataque" in cols:
                values["tipo_ataque"] = ataque
            elif "ataque" in cols:
                values["ataque"] = ataque

            if "severidade" in cols:
                values["severidade"] = severidade

            if "status" in cols:
                values["status"] = status

            if "data" in cols:
                data = (datetime.now() - timedelta(days=15 - i)).strftime("%Y-%m-%d")
                values["data"] = data

            if "ip_relacionado" in cols:
                values["ip_relacionado"] = random.choice(ips)

            if "responsavel" in cols:
                values["responsavel"] = random.choice([
                    "Beatriz Costa",
                    "Carla Menezes",
                    "Rafael Lima",
                    "Nao atribuido"
                ])

            columns = ", ".join(values.keys())
            placeholders = ", ".join(["?"] * len(values))
            sql = f"INSERT INTO incidentes ({columns}) VALUES ({placeholders})"

            cursor.execute(sql, list(values.values()))

    conn.commit()
    conn.close()

    print("Dados fictícios inseridos com sucesso.")

if __name__ == "__main__":
    main()
