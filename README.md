# CRM系统

基于FastAPI + Vue3的智能CRM客户关系管理系统。

## V1说明书

- 销售总监SOP与V1模块功能说明：
  - [`10-CRM系统V1销售SOP与版本说明书.md`](./10-CRM系统V1销售SOP与版本说明书.md)

## 技术栈

### 后端
- FastAPI 0.109.0
- SQLAlchemy 2.0 (异步ORM)
- PostgreSQL / SQLite
- Redis
- JWT认证
- Pydantic 2.0

### 前端
- Vue 3.4
- TypeScript 5.3
- Vite 5.0
- Pinia (状态管理)
- Vue Router 4.2
- Tailwind CSS
- Axios

## 快速开始

### 前置要求
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (可选，可使用SQLite)

### 一键初始化与启动（推荐）

在项目根目录执行：

```bash
./scripts/dev_bootstrap.sh
./scripts/dev_run.sh
```

说明：
- `dev_bootstrap.sh`：按顺序安装后端依赖、初始化数据库、安装前端依赖。
- `dev_run.sh`：启动后端与前端开发服务，并输出日志到 `logs/`。
- `smoke_test.sh`：运行后端冒烟测试。

```bash
./scripts/smoke_test.sh
```

> 若本机 Node.js 为 23+（如 25），`vue-tsc` 构建可能报兼容问题。建议切换到 Node.js 20 LTS 做前端 build/type-check。

### 外部报表导入（客户/商机/活动）

在项目根目录执行：

```bash
./scripts/import_reports.sh
```

仅演练不落库：

```bash
./scripts/import_reports.sh --dry-run
```

导入脚本会读取根目录下导出的 Excel 报表，并自动写入：
- 客户信息
- 商机信息（含阶段）
- 活动记录（拜访/跟进/任务/日程）

### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows使用 venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接等
```

4. 初始化数据库
```bash
python scripts/init_db.py
```

5. 启动开发服务器
```bash
uvicorn app.main:app --reload --port 8000
```

后端API文档: http://localhost:8000/docs

### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

前端访问地址: http://localhost:5173

### 使用Docker Compose

1. 启动所有服务
```bash
docker-compose up -d
```

2. 初始化数据库
```bash
docker-compose exec backend python scripts/init_db.py
```

## 默认账号

- 用户名: `admin`
- 密码: `admin123456`

## 项目结构

```
CRM/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── core/           # 核心模块
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── api/            # API路由
│   │   └── services/       # 业务逻辑
│   ├── alembic/            # 数据库迁移
│   ├── scripts/            # 脚本
│   └── requirements.txt
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── core/           # 核心模块
│   │   ├── views/          # 页面组件
│   │   └── assets/         # 静态资源
│   └── package.json
└── docker-compose.yml
```

## 开发指南

### 后端开发
- API路由位于 `app/api/` 目录
- 数据模型位于 `app/models/` 目录
- 业务逻辑位于 `app/services/` 目录

### 前端开发
- 页面组件位于 `src/views/` 目录
- API请求位于 `src/core/api/` 目录
- 状态管理位于 `src/core/stores/` 目录

## 测试

### 后端测试
```bash
cd backend
pytest
```

或在根目录执行：
```bash
./scripts/smoke_test.sh
```

### 前端测试
```bash
cd frontend
npm run test
```

## 部署

### 后端部署
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端部署
```bash
cd frontend
npm run build
# 构建产物在 dist/ 目录
```

## 许可证

MIT License
