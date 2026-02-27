#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

if [ ! -d "$BACKEND_DIR/venv" ]; then
  echo "未检测到 backend/venv，请先执行: ./scripts/dev_bootstrap.sh"
  exit 1
fi

cd "$BACKEND_DIR"
venv/bin/python scripts/import_external_reports.py --workspace-root "$ROOT_DIR" "$@"
