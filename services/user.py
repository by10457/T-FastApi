"""
用户业务逻辑层

原则：
- Service 层只处理业务逻辑，不直接接触 HTTP Request/Response
- 数据库操作通过 ORM 模型完成
- 缓存操作通过 core.redis 模块中的 redis_client 完成
- 接口层（api/）只做参数校验和调用 service，不写业务逻辑
"""

from core import redis as redis_module
from core.logger import logger
from core.security import hash_password
from models.user import User
from schemas.user import UserCreate, UserUpdate

CACHE_PREFIX = "user:"
CACHE_TTL = 60 * 10  # 10 分钟


class UserService:
    @staticmethod
    async def get_by_id(user_id: int) -> User | None:
        # 先查缓存
        cache_key = f"{CACHE_PREFIX}{user_id}"
        if (client := redis_module.redis_client) is not None:
            cached = await client.get(cache_key)
            if cached:
                logger.debug(f"用户 {user_id} 命中缓存")
                # 实际项目中可以用 orjson 序列化整个对象
                # 这里简化演示
        return await User.filter(id=user_id).first()

    @staticmethod
    async def get_by_username(username: str) -> User | None:
        return await User.filter(username=username).first()

    @staticmethod
    async def create(data: UserCreate) -> User:
        user = await User.create(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        logger.info(f"新用户注册：{user.username} (id={user.id})")
        return user

    @staticmethod
    async def update(user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await user.update_from_dict(update_data).save()
            # 清除缓存
            if (client := redis_module.redis_client) is not None:
                await client.delete(f"{CACHE_PREFIX}{user.id}")
        return user

    @staticmethod
    async def delete(user_id: int) -> bool:
        deleted = await User.filter(id=user_id).delete()
        if deleted and (client := redis_module.redis_client) is not None:
            await client.delete(f"{CACHE_PREFIX}{user_id}")
        return bool(deleted)
