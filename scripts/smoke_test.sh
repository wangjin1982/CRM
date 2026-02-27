#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d "backend/venv" ]; then
  echo "未检测到 backend/venv，请先执行: ./scripts/dev_bootstrap.sh"
  exit 1
fi

echo "运行后端冒烟测试..."
pushd backend >/dev/null
source venv/bin/activate
pytest -q tests
deactivate
popd >/dev/null
