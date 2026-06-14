@echo off
setlocal
cd /d "%~dp0"
set "PORTABLE_DB=dist\Cyber Incident Manager\data\cyber_incident_manager.db"
set "BUILD_DB_BACKUP=build\cyber_incident_manager_preserved.db"

echo Preparando ambiente de build...
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
)

set "PROJECT_PYTHON=.venv\Scripts\python.exe"
"%PROJECT_PYTHON%" -m pip install --upgrade pip
"%PROJECT_PYTHON%" -m pip install -r requirements-build.txt

if exist "%PORTABLE_DB%" (
    echo Preservando o banco portatil atual...
    if not exist "build" mkdir "build"
    copy /y "%PORTABLE_DB%" "%BUILD_DB_BACKUP%" >nul
)

echo Gerando a pasta portatil com o executavel...
"%PROJECT_PYTHON%" -m PyInstaller --noconfirm --clean CyberIncidentManager.spec
if errorlevel 1 exit /b 1

if exist "%BUILD_DB_BACKUP%" (
    echo Restaurando o banco portatil preservado...
    if not exist "dist\Cyber Incident Manager\data" mkdir "dist\Cyber Incident Manager\data"
    copy /y "%BUILD_DB_BACKUP%" "%PORTABLE_DB%" >nul
) else (
    echo Inicializando o banco portatil...
    "%PROJECT_PYTHON%" -c "from database.connection import DatabaseConnection; from database.init_db import initialize_database; initialize_database(DatabaseConnection(r'dist\Cyber Incident Manager\data\cyber_incident_manager.db'))"
    if errorlevel 1 exit /b 1
)

echo.
echo Build concluido.
echo Copie a pasta "dist\Cyber Incident Manager" inteira para o pendrive.
echo O executavel esta dentro dela: "Cyber Incident Manager.exe"
