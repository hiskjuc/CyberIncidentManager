"""SQL schema definitions for the application."""

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS usuarios (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS incidentes (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        acao TEXT NOT NULL,
        detalhes TEXT NOT NULL,
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS comentarios_incidentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incidente_id INTEGER NOT NULL,
        autor_id INTEGER,
        comentario TEXT NOT NULL,
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE,
        FOREIGN KEY (autor_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS historico_incidentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incidente_id INTEGER NOT NULL,
        usuario_id INTEGER,
        acao TEXT NOT NULL,
        campo TEXT,
        valor_anterior TEXT,
        valor_novo TEXT,
        detalhes TEXT NOT NULL,
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS base_conhecimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        categoria TEXT NOT NULL,
        descricao TEXT NOT NULL,
        solucao TEXT NOT NULL,
        autor_id INTEGER,
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (autor_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE INDEX IF NOT EXISTS idx_incidentes_status ON incidentes(status)",
    "CREATE INDEX IF NOT EXISTS idx_incidentes_severidade ON incidentes(severidade)",
    "CREATE INDEX IF NOT EXISTS idx_incidentes_data ON incidentes(data_incidente)",
    "CREATE INDEX IF NOT EXISTS idx_logs_criado_em ON logs(criado_em)",
    "CREATE INDEX IF NOT EXISTS idx_comentarios_incidente ON comentarios_incidentes(incidente_id)",
    "CREATE INDEX IF NOT EXISTS idx_historico_incidente ON historico_incidentes(incidente_id)",
    "CREATE INDEX IF NOT EXISTS idx_base_conhecimento_categoria ON base_conhecimento(categoria)",
)
