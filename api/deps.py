"""
公共依赖注入

FastAPI 的依赖注入系统让你可以把「获取当前用户」
「验证权限」等逻辑抽成可复用的函数，在路由上直接声明使用。

使用方式：
    @router.get("/me")
    async def get_me(current_user: User = Depends(get_current_user)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from core.security import decode_access_token
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    user = await User.filter(id=int(user_id), is_active=True).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    return current_user
