"""
安全工具：JWT 生成/验证、密码哈希
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    subject: Any,
    expires_delta: timedelta | None = None,
    extra_data: dict | None = None,
) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(subject), "exp": expire}
    if extra_data:
        payload.update(extra_data)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码 JWT，失败时抛出 JWTError（由调用方处理）。"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
