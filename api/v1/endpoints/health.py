from fastapi import APIRouter
from tortoise import connections

from core.redis import redis_client
from schemas.common import Response

router = APIRouter()


@router.get("", summary="健康检查")
async def health_check():
    """
    检查应用、数据库、Redis 连接状态。
    运维监控、K8s 探针可调用此接口。
    """
    db_ok = False
    redis_ok = False

    try:
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        db_ok = True
    except Exception:
        pass

    try:
        if redis_client:
            await redis_client.ping()
            redis_ok = True
    except Exception:
        pass

    return Response.ok(
        data={
            "status": "ok" if (db_ok and redis_ok) else "degraded",
            "mysql": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
        }
    )
