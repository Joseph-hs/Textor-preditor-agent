#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_VENV_DIR="$BACKEND_DIR/venv"
BACKEND_REQUIREMENTS="$BACKEND_DIR/requirements.txt"
BACKEND_STAMP="$BACKEND_VENV_DIR/.deps-installed"
FRONTEND_STAMP="$FRONTEND_DIR/node_modules/.deps-installed"

BACKEND_PID=""
FRONTEND_PID=""

log() {
  printf '\n[%s] %s\n' "$1" "$2"
}

fail() {
  log "error" "$1"
  exit 1
}

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM

  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi

  wait "$BACKEND_PID" 2>/dev/null || true
  wait "$FRONTEND_PID" 2>/dev/null || true

  exit "$exit_code"
}

trap cleanup EXIT INT TERM

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  fail "No encontré Python. Instala Python 3 para ejecutar el backend."
fi

if ! command -v npm >/dev/null 2>&1; then
  fail "No encontré npm. Instala Node.js y npm para ejecutar el frontend."
fi

ensure_port_available() {
  local port="$1"
  local service_name="$2"

  if ! "$PYTHON_BIN" - "$port" <<'PY'
import socket
import sys

port = int(sys.argv[1])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        sys.exit(1)
PY
  then
    fail "El puerto ${port} ya está en uso. Libéralo antes de iniciar ${service_name}."
  fi
}

ensure_backend_dependencies() {
  if [[ ! -d "$BACKEND_VENV_DIR" ]]; then
    log "setup" "Creando entorno virtual del backend..."
    "$PYTHON_BIN" -m venv "$BACKEND_VENV_DIR"
  fi

  if [[ ! -f "$BACKEND_STAMP" || "$BACKEND_REQUIREMENTS" -nt "$BACKEND_STAMP" ]]; then
    log "setup" "Instalando dependencias del backend..."
    "$BACKEND_VENV_DIR/bin/python" -m pip install --upgrade pip
    "$BACKEND_VENV_DIR/bin/python" -m pip install -r "$BACKEND_REQUIREMENTS"
    touch "$BACKEND_STAMP"
  fi
}

ensure_frontend_dependencies() {
  if [[ ! -d "$FRONTEND_DIR/node_modules" || ! -f "$FRONTEND_STAMP" || "$FRONTEND_DIR/package.json" -nt "$FRONTEND_STAMP" || "$FRONTEND_DIR/package-lock.json" -nt "$FRONTEND_STAMP" ]]; then
    log "setup" "Instalando dependencias del frontend..."
    (
      cd "$FRONTEND_DIR"
      npm install
    )
    touch "$FRONTEND_STAMP"
  fi
}

start_backend() {
  log "backend" "Iniciando API en http://localhost:8000 ..."
  (
    cd "$BACKEND_DIR"
    exec "$BACKEND_VENV_DIR/bin/python" app.py
  ) &
  BACKEND_PID=$!
}

start_frontend() {
  log "frontend" "Iniciando app en http://localhost:5173 ..."
  (
    cd "$FRONTEND_DIR"
    exec npm run dev -- --host 0.0.0.0
  ) &
  FRONTEND_PID=$!
}

ensure_backend_dependencies
ensure_frontend_dependencies
ensure_port_available 8000 "el backend"
ensure_port_available 5173 "el frontend"

log "ready" "Levantando Textor Predictor Agent. Usa Ctrl+C para detener backend y frontend."

start_backend
start_frontend

wait -n "$BACKEND_PID" "$FRONTEND_PID"
