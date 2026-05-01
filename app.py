"""
FastAPI 应用实例 + 生命周期管理

【生命周期顺序】
startup:
  1. 初始化日志（import 即生效）
  2. 连接 MySQL
  3. 连接 Redis
  4. 开发环境注册并启动定时任务

shutdown（反序）:
  1. 停止开发环境定时任务
  2. 关闭 Redis
  3. 关闭 MySQL
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 路由注册（按版本组织）
from api.v1 import router as v1_router
from core.config import settings
from core.database import close_db, init_db
from core.logger import logger
from core.redis import close_redis, init_redis
from tasks.scheduler import register_jobs, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    应用生命周期管理。
    yield 前 = startup，yield 后 = shutdown。
    """
    # ── Startup ───────────────────────────────────────────
    logger.info(f"🚀 {settings.APP_NAME} 启动中 [env={settings.APP_ENV}]")

    await init_db()
    await init_redis()

    if settings.APP_DEBUG:
        register_jobs()
        scheduler.start()
        logger.info("⏰ 开发环境定时任务调度器已启动")

    logger.info("✅ 应用启动完成，开始接收请求")
    yield

    # ── Shutdown ──────────────────────────────────────────
    logger.info("🛑 应用正在关闭...")

    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("⏰ 定时任务调度器已停止")

    await close_redis()
    await close_db()

    logger.info("👋 应用已安全关闭")


# ── FastAPI 实例 ──────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.APP_DEBUG else None,  # 生产环境关闭文档
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
)

# ── 中间件 ────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 静态文件 ──────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="public"), name="static")

# ── 路由挂载 ──────────────────────────────────────────────────

app.include_router(v1_router, prefix="/api/v1")
