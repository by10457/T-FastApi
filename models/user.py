"""
用户模型示例
"""

from tortoise import fields

from models.base import BaseModel


class User(BaseModel):
    username = fields.CharField(max_length=64, unique=True, description="用户名")
    email = fields.CharField(max_length=128, unique=True, description="邮箱")
    hashed_password = fields.CharField(max_length=256, description="哈希密码")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_superuser = fields.BooleanField(default=False, description="是否超级管理员")

    class Meta:
        table = "users"
        table_description = "用户表"

    def __str__(self) -> str:
        return f"User(id={self.id}, username={self.username})"
