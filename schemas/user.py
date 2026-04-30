"""
用户相关的 Pydantic Schema

命名约定：
- XxxCreate   : 创建请求体（POST）
- XxxUpdate   : 更新请求体（PUT/PATCH），字段通常 Optional
- XxxResponse : 响应体（对外暴露，不含敏感字段）
- XxxInDB     : 数据库完整字段（含 hashed_password 等，内部用）
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="明文密码（服务端哈希存储）")


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=2, max_length=64)
    email: EmailStr | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # 支持从 ORM 对象直接转换


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
