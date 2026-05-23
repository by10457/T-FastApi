"""配置中心测试。"""

from core.config import Settings


def test_tortoise_orm_uses_app_timezone() -> None:
    settings = Settings(_env_file=None)

    assert settings.TIMEZONE == "Asia/Shanghai"
    assert settings.TORTOISE_ORM["timezone"] == "Asia/Shanghai"

