# FastAPI 项目模板

> 基于 FastAPI + Tortoise-ORM + Redis + APScheduler 的后端服务模板

## 目录结构

```
.
├── main.py                 # 启动入口
├── app.py                  # FastAPI 实例 + 生命周期（连接初始化/关闭、定时任务启动）
├── pyproject.toml          # uv 依赖管理 + aerich 迁移工具配置 + pytest 配置
├── uv.lock                 # uv 锁文件
├── .env.example            # 环境变量模板（提交到仓库）
├── .env                    # 实际环境变量（不提交！）
│
├── api/                    # 接口层：路由定义，只做参数校验和调用 service
│   ├── deps.py             # 公共依赖注入（获取当前用户、权限校验等）
│   └── v1/
│       └── endpoints/      # 按业务模块拆分路由文件
│
├── core/                   # 核心基础设施
│   ├── config.py           # 配置中心（读取 .env，全局唯一 settings 对象）
│   ├── database.py         # MySQL 连接管理（Tortoise-ORM）
│   ├── redis.py            # Redis 连接管理（redis-py asyncio）
│   ├── logger.py           # 日志配置（loguru）
│   └── security.py         # JWT / 密码哈希
│
├── models/                 # ORM 数据库模型（与数据表一一对应）
├── schemas/                # Pydantic 请求/响应类型定义
├── services/               # 业务逻辑层（不含 HTTP 相关代码）
│
├── tasks/                  # 定时任务
│   └── scheduler.py        # 调度器实例 + 任务注册函数
│
├── utils/                  # 通用工具函数
├── scripts/                # 一次性脚本（数据修复等，不部署到生产）
├── sql/                    # SQL 初始化文件（建库、初始数据）
├── public/                 # 静态资源（前端页面、图片等）
├── tests/                  # 测试
└── logs/                   # 日志文件（.gitignored）
```

## 快速开始

```bash
# 1. 复制环境变量并填写
cp .env.example .env

# 2. 同步依赖
uv sync

# 3. 初始化数据库迁移（首次）
uv run aerich init -t core.database.TORTOISE_ORM
uv run aerich init-db

# 4. 启动
uv run python main.py
```

生产环境可在 `.env` 中设置 `APP_DEBUG=false`，并按服务规格显式设置 `WEB_CONCURRENCY` 控制 worker 进程数。未设置 `WEB_CONCURRENCY` 时，模板默认使用 `min(CPU 核心数, 4)`，避免容器或多核机器上自动开出过多进程。

## 常用命令

```bash
# 生成迁移文件（修改 models 后执行）
uv run aerich migrate --name "add_user_table"

# 应用迁移
uv run aerich upgrade

# 运行测试
uv run pytest tests/ -v
```

## 新增业务模块流程

1. `models/` 下新建模型文件，在 `core/config.py` 的 `TORTOISE_ORM.apps.models.models` 列表里注册
2. `schemas/` 下新建对应的 Schema（请求/响应体）
3. `services/` 下新建业务逻辑实现
4. `api/v1/endpoints/` 下新建路由文件
5. 在 `api/v1/__init__.py` 里 `include_router`
6. 执行 `uv run aerich migrate && uv run aerich upgrade` 同步数据库

## 关键设计决策

| 问题 | 决策 |
|------|------|
| MySQL/Redis 连接对象在哪初始化？| `core/database.py` 和 `core/redis.py` 声明，在 `app.py` lifespan 里统一 init/close |
| 定时任务写在哪？| `tasks/scheduler.py`，注册函数 `register_jobs()` 在 lifespan startup 调用 |
| 环境变量怎么管理？| `core/config.py` 用 pydantic-settings 读取，全项目只 import `settings` 对象 |
| 接口统一响应格式？| `schemas/common.py` 的 `Response[T]` 泛型包装 |
| 数据库迁移？| aerich（Tortoise-ORM 官方迁移工具）|
