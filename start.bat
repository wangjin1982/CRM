@echo off
chcp 65001 >nul
echo ======================================
echo CRM系统启动脚本 (Windows)
echo ======================================
echo.

REM 检查Python虚拟环境
if not exist "backend\venv" (
    echo 创建Python虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

REM 激活虚拟环境并安装后端依赖
echo 检查后端依赖...
call backend\venv\Scripts\activate.bat
pip install -q -r backend\requirements.txt

REM 检查前端依赖
if not exist "frontend\node_modules" (
    echo 安装前端依赖...
    cd frontend
    npm install
    cd ..
)

REM 初始化数据库（如果需要）
if not exist "backend\data\crm.db" (
    echo 初始化数据库...
    cd backend
    python scripts/init_db.py
    cd ..
)

echo.
echo ======================================
echo 启动后端服务...
echo ======================================

REM 启动后端（新窗口）
start "CRM Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app:app --reload --port 8000"

REM 等待后端启动
timeout /t 3 /nobreak >nul

echo.
echo ======================================
echo 启动前端服务...
echo ======================================

REM 启动前端（新窗口）
start "CRM Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================
echo 系统启动成功！
echo ======================================
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:5173
echo API文档: http://localhost:8000/docs
echo.
echo 默认账号:
echo   用户名: admin
echo   密码: admin123456
echo.
echo ======================================
pause
