#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "======================================"
echo "CRM 开发环境初始化"
echo "======================================"

mkdir -p logs

if [ ! -d "backend/venv" ]; then
  echo "[1/5] 创建 Python 虚拟环境..."
  python3 -m venv backend/venv
fi

echo "[2/5] 安装后端依赖..."
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt
deactivate

echo "[3/5] 初始化数据库..."
pushd backend >/dev/null
source venv/bin/activate
python scripts/init_db.py
deactivate
popd >/dev/null

echo "[4/5] 安装前端依赖..."
pushd frontend >/dev/null
npm install
popd >/dev/null

NODE_MAJOR="$(node -v | sed -E 's/^v([0-9]+).*/\1/')"
if [ "$NODE_MAJOR" -ge 23 ]; then
  echo "[5/5] 警告: 当前 Node.js 版本 $(node -v) 与 vue-tsc 可能存在兼容问题。"
  echo "      建议使用 Node.js 20 LTS 进行 build / type-check。"
else
  echo "[5/5] Node.js 版本检查通过: $(node -v)"
fi

echo "======================================"
echo "初始化完成"
echo "======================================"
