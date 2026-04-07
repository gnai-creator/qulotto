#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

find_python312() {
  if command -v python3.12 >/dev/null 2>&1; then
    command -v python3.12
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    local version
    version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    if [[ "$version" == "3.12" ]]; then
      command -v python3
      return 0
    fi
  fi

  return 1
}

install_python312() {
  echo "Python 3.12 nao encontrado. Tentando instalar..."

  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3.12 python3.12-venv
    return 0
  fi

  if command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3.12
    return 0
  fi

  if command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm python
    return 0
  fi

  if command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y python312 python312-venv
    return 0
  fi

  if command -v brew >/dev/null 2>&1; then
    brew install python@3.12
    return 0
  fi

  echo "Nao foi possivel instalar Python 3.12 automaticamente neste sistema."
  exit 1
}

PYTHON_BIN="$(find_python312 || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  install_python312
  PYTHON_BIN="$(find_python312 || true)"
fi

if [[ -z "$PYTHON_BIN" ]]; then
  echo "Python 3.12 continua indisponivel apos a tentativa de instalacao."
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r "$ROOT_DIR/requirements.txt"

RETRY_DELAY_SECONDS=15

while true; do
  if python -c "import runpy; runpy.run_path('src/scripts/001_fetch.py', run_name='__main__')"; then
    exit 0
  fi

  echo "Falha temporaria ao atualizar os concursos. Nova tentativa em ${RETRY_DELAY_SECONDS}s..."
  sleep "$RETRY_DELAY_SECONDS"
done
