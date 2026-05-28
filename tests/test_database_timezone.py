"""数据库时区配置测试。"""

import os

import pytest

from core import database
from core.config import settings


class _FakeConnection:
    """测试用数据库连接。"""

    async def execute_query(self, query: str) -> None:
        """模拟数据库探测查询。"""
        return None


@pytest.mark.asyncio
async def test_init_db_passes_timezone_to_tortoise(monkeypatch: pytest.MonkeyPatch) -> None:
    received_config: dict[str, object] = {}

    async def fake_init(config: dict[str, object]) -> None:
        """模拟 Tortoise 初始化时同步时区环境变量。"""
        received_config.update(config)
        os.environ["USE_TZ"] = str(config["use_tz"])
        os.environ["TIMEZONE"] = str(config["timezone"])
        return None

    monkeypatch.delenv("TIMEZONE", raising=False)
    monkeypatch.delenv("USE_TZ", raising=False)
    monkeypatch.setattr(settings, "TIMEZONE", "Asia/Shanghai")
    monkeypatch.setattr(database.Tortoise, "init", fake_init)
    monkeypatch.setattr(database.connections, "get", lambda name: _FakeConnection())

    await database.init_db()

    assert received_config["timezone"] == "Asia/Shanghai"
    assert received_config["use_tz"] is False
    assert os.environ["TIMEZONE"] == "Asia/Shanghai"
    assert os.environ["USE_TZ"] == "False"
