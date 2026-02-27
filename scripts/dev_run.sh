#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p logs

if [ ! -d "backend/venv" ]; then
  echo "未检测到 backend/venv，请先执行: ./scripts/dev_bootstrap.sh"
  exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
  echo "未检测到 frontend/node_modules，请先执行: ./scripts/dev_bootstrap.sh"
  exit 1
fi

free_port() {
  local port="$1"
  local pids
  pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "检测到端口 $port 被占用，正在释放: $pids"
    kill $pids >/dev/null 2>&1 || true
    sleep 1
  fi
}

free_port 8000
free_port 5173

echo "启动后端服务..."
pushd backend >/dev/null
source venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
deactivate
popd >/dev/null
echo "后端 PID: $BACKEND_PID"

sleep 2
if ! kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
  echo "后端启动失败，请检查 logs/backend.log"
  tail -n 40 logs/backend.log || true
  exit 1
fi

echo "启动前端服务..."
pushd frontend >/dev/null
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
popd >/dev/null
echo "前端 PID: $FRONTEND_PID"

sleep 2
if ! kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
  echo "前端启动失败，请检查 logs/frontend.log"
  tail -n 40 logs/frontend.log || true
  kill "$BACKEND_PID" >/dev/null 2>&1 || true
  exit 1
fi

echo "======================================"
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:5173"
echo "API文档: http://localhost:8000/docs"
echo "日志文件: logs/backend.log, logs/frontend.log"
echo "======================================"

cleanup() {
  echo ""
  echo "停止服务..."
  kill "$BACKEND_PID" "$FRONTEND_PID" >/dev/null 2>&1 || true
}

trap cleanup INT TERM EXIT
wait "$BACKEND_PID" "$FRONTEND_PID"
