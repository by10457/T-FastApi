"""
安全工具：JWT 生成/验证、密码哈希
"""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import bcrypt
from jose import JWTError, jwt

from core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 天
MAX_BCRYPT_PASSWORD_BYTES = 72


def _password_to_bytes(password: str) -> bytes:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("密码 UTF-8 编码后不能超过 72 字节")
    return password_bytes


def hash_password(password: str) -> str:
    password_bytes = _password_to_bytes(password)
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_password_to_bytes(plain), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(
    subject: Any,
    expires_delta: timedelta | None = None,
    extra_data: dict[str, Any] | None = None,
) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(subject), "exp": expire}
    if extra_data:
        payload.update(extra_data)
    return cast(str, jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM))


def create_refresh_token(subject: Any, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(subject), "exp": expire, "typ": "refresh"}
    return cast(str, jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM))


def decode_access_token(token: str) -> dict[str, Any]:
    """解码 JWT，失败时抛出 JWTError（由调用方处理）。"""
    return cast(dict[str, Any], jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM]))


def decode_refresh_token(token: str) -> dict[str, Any]:
    """解码 refresh token，失败时抛出 JWTError（由调用方处理）。"""
    payload = cast(dict[str, Any], jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM]))
    if payload.get("typ") != "refresh":
        raise JWTError("Invalid token type")
    return payload
