# Cyber Incident Manager - Documentacao do Projeto

## Estrutura MVC

O sistema segue uma organizacao MVC simples, mantendo responsabilidades separadas:

- `models/`: objetos de dominio, como usuarios e incidentes.
- `controllers/`: regras de negocio, permissoes, consultas e persistencia.
- `views/`: telas CustomTkinter e componentes visuais.
- `database/`: conexao SQLite, schema e migracoes de inicializacao.
- `utils/`: validacoes, seguranca, tema, helpers visuais e tabelas.

O ponto de entrada e `main.py`, que inicializa o banco, cria os controllers e abre a interface principal.

## Classes Principais

### Usuarios

`models/user.py` define os perfis do sistema:

- `Administrator`: controle total, incluindo usuarios e exclusao de incidentes.
- `Analyst`: cria, edita e visualiza incidentes.
- `Viewer`: visualiza dashboard e incidentes em modo consulta.

A funcao `user_from_row` converte linhas do SQLite na classe correta conforme `tipo_usuario`.

### Incidentes

`models/incident.py` representa um incidente com titulo, descricao, ataque, severidade, status, data, IP, responsavel, criador e datas de criacao/atualizacao.

### Controllers

`AuthController` gerencia login, logout, usuarios, senha, tema por usuario e permissoes administrativas.

`IncidentController` gerencia criacao, edicao, exclusao, listagem, detalhe e exportacao de incidentes.

`DashboardController` agrega metricas, distribuicoes e ultimos incidentes para o dashboard.

## Banco SQLite

O banco principal fica em:

`data/cyber_incident_manager.db`

Quando empacotado, o executavel usa o banco portatil em:

`dist/Cyber Incident Manager/data/cyber_incident_manager.db`

Tabelas principais:

- `usuarios`: credenciais, cargo, tipo de usuario, tema preferido e data de criacao.
- `incidentes`: dados completos dos incidentes, responsavel, criador, criacao e ultima atualizacao.
- `logs`: trilha de auditoria para login, logout e acoes relevantes.

Na inicializacao, `database/init_db.py` cria o schema quando necessario e aplica migracoes preservando dados existentes, incluindo suporte ao perfil `Visualizador` e preservacao de incidentes quando um usuario e removido.

## Permissoes

Administrador:

- Acessa dashboard, incidentes, usuarios e configuracoes.
- Cria, edita, exclui e visualiza incidentes.
- Cria, edita e exclui usuarios.
- Nao pode excluir o ultimo administrador.

Analista:

- Acessa dashboard, incidentes e configuracoes.
- Cria, edita e visualiza incidentes.
- Nao exclui incidentes.
- Nao gerencia usuarios.

Visualizador:

- Acessa dashboard, incidentes e configuracoes.
- Visualiza incidentes e abre detalhes por duplo clique.
- Nao cria, edita ou exclui incidentes.
- Nao gerencia usuarios.

## Fluxo de Funcionamento

1. `main.py` chama `initialize_database`.
2. O banco SQLite e preparado e migrado sem descartar dados.
3. A tela de login autentica o usuario em `AuthController`.
4. O app aplica o tema salvo no usuario autenticado.
5. A sidebar abre as secoes permitidas para o perfil.
6. As views chamam controllers para validar permissoes e persistir dados.
7. Alteracoes atualizam tabelas automaticamente e registram logs.
8. O executavel portatil usa a mesma estrutura MVC e o banco SQLite local da pasta `data`.
