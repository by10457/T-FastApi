"""
健康检查接口测试

运行：
    uv run pytest tests/ -v
    uv run pytest tests/ -v --asyncio-mode=auto
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
