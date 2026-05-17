from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, status
from fastapi import Response as HttpResponse
from fastapi.responses import JSONResponse
from jose import JWTError
from pydantic import BaseModel

from api.dependencies.auth import get_current_user
from core.config import settings
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from models.user import User
from schemas.common import Response
from services.user import UserService

router = APIRouter()

REFRESH_COOKIE_NAME = "jwt"


class LoginParams(BaseModel):
    username: str
    password: str
    captcha: bool | None = None


def _auth_error(message: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=Response.error(code=status_code, message=message).model_dump(),
    )


def _set_refresh_cookie(response: HttpResponse, refresh_token: str) -> None:
    secure = not settings.APP_DEBUG
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        max_age=30 * 24 * 60 * 60,
        path="/",
        samesite="none" if secure else "lax",
        secure=secure,
    )


def _clear_refresh_cookie(response: HttpResponse) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="none" if not settings.APP_DEBUG else "lax",
        secure=not settings.APP_DEBUG,
    )


@router.post("/login", response_model=Response[dict[str, str]], summary="登录")
async def login(data: LoginParams, response: HttpResponse) -> Response[dict[str, str]]:
    user = await UserService.get_by_username(data.username)
    if user is None:
        user = await UserService.ensure_development_admin(data.username, data.password)
    if not user or not verify_password(data.password, user.hashed_password):
        _clear_refresh_cookie(response)
        response.status_code = status.HTTP_403_FORBIDDEN
        return Response.error(code=status.HTTP_403_FORBIDDEN, message="用户名或密码错误")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    _set_refresh_cookie(response, refresh_token)

    return Response.ok(data={"accessToken": access_token})


@router.post("/refresh", response_model=None, summary="刷新 accessToken")
async def refresh_token(jwt: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None) -> str | JSONResponse:
    if not jwt:
        return _auth_error("refreshToken 不存在")

    try:
        payload = decode_refresh_token(jwt)
        subject = payload.get("sub")
        if not isinstance(subject, str):
            return _auth_error("refreshToken 无效")
        user_id = int(subject)
    except (JWTError, ValueError):
        return _auth_error("refreshToken 无效")

    user = await User.filter(id=user_id).first()
    if user is None:
        return _auth_error("用户不存在")

    return create_access_token(subject=user.id)


@router.post("/logout", response_model=Response[None], summary="退出登录")
async def logout(response: HttpResponse) -> Response[None]:
    _clear_refresh_cookie(response)
    return Response.ok()


@router.get("/codes", response_model=Response[list[str]], summary="获取用户权限码")
async def get_access_codes(_request: Request, current_user: User = Depends(get_current_user)) -> Response[list[str]]:
    if current_user.username.lower() in {"admin", "administrator"}:
        codes = [
            "System:Menu:List",
            "System:Menu:Create",
            "System:Menu:Edit",
            "System:Menu:Delete",
            "System:User:List",
            "System:User:Create",
            "System:User:Edit",
            "System:User:Delete",
        ]
    else:
        codes = ["System:User:List"]
    return Response.ok(data=codes)
