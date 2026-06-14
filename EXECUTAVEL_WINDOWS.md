# Executavel Windows

O build portatil fica em `dist\Cyber Incident Manager`.

Essa pasta contem o arquivo `Cyber Incident Manager.exe` e os arquivos internos
necessarios para a interface CustomTkinter. Copie a pasta inteira para o
pendrive e execute o `.exe` dentro dela no outro computador.

## Gerar o build

No Windows, abra a pasta do projeto e execute:

```bat
build_exe.bat
```

O script cria uma `.venv`, instala as dependencias de build, executa o
PyInstaller com `CyberIncidentManager.spec` e inicializa o banco dentro da
pasta portatil quando ainda nao ha banco. Se a distribuicao ja tiver um banco
em `dist`, ele e preservado durante o rebuild.

## Dados portateis

Ao iniciar, o programa cria automaticamente:

```text
data\cyber_incident_manager.db
```

Quando o aplicativo roda empacotado, a pasta `data` fica ao lado do executavel.
Copiar `dist\Cyber Incident Manager` preserva usuarios, incidentes e logs.

## Primeiro acesso

```text
usuario: admin
senha: admin123
```
