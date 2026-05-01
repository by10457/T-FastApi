from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_superuser, get_current_user
from models.user import User
from schemas.common import Response
from schemas.user import UserCreate, UserResponse, UserUpdate
from services.user import UserService

router = APIRouter()


@router.post("", response_model=Response[UserResponse], summary="注册用户")
async def create_user(data: UserCreate) -> Response[UserResponse]:
    existing = await UserService.get_by_username(data.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user = await UserService.create(data)
    return Response.ok(data=UserResponse.model_validate(user))


@router.get("/me", response_model=Response[UserResponse], summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)) -> Response[UserResponse]:
    return Response.ok(data=UserResponse.model_validate(current_user))


@router.put("/me", response_model=Response[UserResponse], summary="更新当前用户信息")
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Response[UserResponse]:
    user = await UserService.update(current_user, data)
    return Response.ok(data=UserResponse.model_validate(user))


@router.get("/{user_id}", response_model=Response[UserResponse], summary="（管理员）获取用户")
async def get_user(
    user_id: int,
    _: User = Depends(get_current_superuser),
) -> Response[UserResponse]:
    user = await UserService.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return Response.ok(data=UserResponse.model_validate(user))


@router.delete("/{user_id}", response_model=Response[None], summary="（管理员）删除用户")
async def delete_user(
    user_id: int,
    _: User = Depends(get_current_superuser),
) -> Response[None]:
    deleted = await UserService.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return Response.ok(message="删除成功")
