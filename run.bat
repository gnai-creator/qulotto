@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"
set "VENV_DIR=%ROOT_DIR%.venv"
set "PYTHON_BIN="

where py >nul 2>nul
if %errorlevel%==0 (
  py -3.12 --version >nul 2>nul
  if !errorlevel!==0 (
    set "PYTHON_BIN=py -3.12"
  )
)

if not defined PYTHON_BIN (
  where python >nul 2>nul
  if %errorlevel%==0 (
    for /f "usebackq delims=" %%i in (`python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"`) do set "PY_VERSION=%%i"
    if "!PY_VERSION!"=="3.12" (
      set "PYTHON_BIN=python"
    )
  )
)

if not defined PYTHON_BIN (
  echo Python 3.12 nao encontrado. Tentando instalar com winget...
  where winget >nul 2>nul
  if %errorlevel%==0 (
    winget install -e --id Python.Python.3.12
  ) else (
    echo winget nao esta disponivel. Instale o Python 3.12 manualmente.
    exit /b 1
  )
)

if not defined PYTHON_BIN (
  py -3.12 --version >nul 2>nul
  if %errorlevel%==0 (
    set "PYTHON_BIN=py -3.12"
  )
)

if not defined PYTHON_BIN (
  echo Python 3.12 continua indisponivel apos a tentativa de instalacao.
  exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  call %PYTHON_BIN% -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r "%ROOT_DIR%requirements.txt"
python -m main %*
