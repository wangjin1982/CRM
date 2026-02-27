"""系统模块数据模型"""
from .user import User
from .role import Role, UserRole, RolePermission
from .permission import Permission

__all__ = [
    "User",
    "Role",
    "UserRole",
    "RolePermission",
    "Permission",
]
