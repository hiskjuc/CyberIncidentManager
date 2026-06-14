import sqlite3

conn = sqlite3.connect(r"data\cyber_incident_manager.db")
cursor = conn.cursor()

incidentes = [
    ("Phishing contra equipe financeira", "Email fraudulento direcionado ao setor financeiro.", "Phishing", "Alta", "Em analise", "2026-05-01", "192.168.1.10"),
    ("Ransomware bloqueado em estação", "Tentativa de ransomware detectada e contida.", "Ransomware", "Critica", "Contido", "2026-05-03", "10.0.0.15"),
    ("Brute force na VPN", "Diversas tentativas de login detectadas.", "Brute Force", "Media", "Aberto", "2026-05-04", "45.22.18.7"),
    ("Exfiltração via DNS", "Possível vazamento de dados identificado.", "Exfiltracao", "Critica", "Em analise", "2026-05-05", "172.16.0.20"),
    ("Malware removido", "Malware detectado e removido do equipamento.", "Malware", "Alta", "Resolvido", "2026-05-06", "192.168.1.25"),
    ("Acesso indevido", "Usuário não autorizado acessou sistema legado.", "Acesso Indevido", "Alta", "Contido", "2026-05-07", "10.0.0.40"),
    ("Varredura de portas", "Reconhecimento identificado na DMZ.", "Reconhecimento", "Baixa", "Resolvido", "2026-05-08", "201.10.20.30"),
    ("Credencial exposta", "Senha encontrada em repositório público.", "Vazamento", "Media", "Resolvido", "2026-05-09", "192.168.50.1"),
    ("SQL Injection", "Tentativa bloqueada pelo WAF.", "SQL Injection", "Alta", "Em analise", "2026-05-10", "177.45.22.90"),
    ("Ataque DDoS", "Volume anormal de tráfego detectado.", "DDoS", "Critica", "Resolvido", "2026-05-11", "8.8.8.8"),
    ("Login impossível", "Acesso suspeito de localização incomum.", "Conta Comprometida", "Media", "Aberto", "2026-05-12", "189.22.11.4"),
    ("Macro suspeita", "Documento malicioso recebido por e-mail.", "Anexo Malicioso", "Baixa", "Resolvido", "2026-05-13", "192.168.1.55"),
    ("Beaconing recorrente", "Comunicação suspeita com C2.", "Command and Control", "Critica", "Em analise", "2026-05-14", "34.120.0.1"),
    ("Exploração de vulnerabilidade", "Host sem patch explorado.", "Exploracao", "Alta", "Contido", "2026-05-15", "10.10.10.10"),
    ("Arquivo confidencial exposto", "Compartilhamento indevido detectado.", "Exposicao de Dados", "Media", "Resolvido", "2026-05-16", "172.20.1.5"),
]

for incidente in incidentes:
    cursor.execute("""
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
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)
    """, incidente)

conn.commit()
conn.close()

print("15 incidentes inseridos com sucesso.")