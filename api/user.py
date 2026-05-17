from fastapi import APIRouter, Depends

from api.dependencies.auth import get_current_user
from models.user import User
from schemas.common import Response

router = APIRouter()


def _build_user_info(user: User) -> dict[str, object]:
    username = user.username
    real_name = user.nickname or username
    return {
        "userId": str(user.id),
        "username": username,
        "realName": real_name,
        "avatar": user.avatar or "",
        "roles": ["admin"] if username.lower() in {"admin", "administrator"} else ["user"],
        "homePath": "/workspace",
        "desc": user.email,
        "token": "",
    }


@router.get("/info", response_model=Response[dict[str, object]], summary="查询当前用户信息")
async def get_user_info(current_user: User = Depends(get_current_user)) -> Response[dict[str, object]]:
    return Response.ok(data=_build_user_info(current_user))
