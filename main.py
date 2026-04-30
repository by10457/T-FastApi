"""
启动入口

开发环境：
    uv run python main.py
    或
    uv run uvicorn app:app --reload

生产环境（建议配合 supervisor/systemd）：
    uv run uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
"""

import uvicorn

from core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,  # 开发环境热重载
        log_level=settings.LOG_LEVEL.lower(),
    )
