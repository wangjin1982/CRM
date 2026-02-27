"""权限检查模块"""
from typing import List, Optional, Set
from functools import wraps
from fastapi import Request, HTTPException, status

from app.core.utils.response import ErrorResponse


class PermissionChecker:
    """权限检查器"""

    def __init__(self):
        # 缓存用户权限：{user_id: set(permissions)}
        self._user_permissions_cache: dict = {}

    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """获取用户所有权限"""
        # 从缓存获取
        if user_id in self._user_permissions_cache:
            return self._user_permissions_cache[user_id]

        # 从数据库加载
        from sqlalchemy import select
        from app.models.sys.role import UserRole, RolePermission
        from app.models.sys.permission import Permission
        from app.core.config.database import async_session_maker

        async with async_session_maker() as session:
            # 查询用户角色权限
            stmt = (
                select(Permission.code)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .join(UserRole, RolePermission.role_id == UserRole.role_id)
                .where(UserRole.user_id == user_id, Permission.status == 1)
            )
            result = await session.execute(stmt)
            permissions = {row[0] for row in result}

        self._user_permissions_cache[user_id] = permissions
        return permissions

    def clear_user_permissions_cache(self, user_id: int):
        """清除用户权限缓存"""
        if user_id in self._user_permissions_cache:
            del self._user_permissions_cache[user_id]

    async def has_permission(self, user_id: int, permission: str) -> bool:
        """检查用户是否有指定权限"""
        permissions = await self.get_user_permissions(user_id)
        return permission in permissions

    async def has_any_permission(self, user_id: int, permissions: List[str]) -> bool:
        """检查用户是否有任意一个权限"""
        user_permissions = await self.get_user_permissions(user_id)
        return bool(set(permissions) & user_permissions)

    async def has_all_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """检查用户是否有所有权限"""
        user_permissions = await self.get_user_permissions(user_id)
        return set(permissions).issubset(user_permissions)


# 全局权限检查器实例
permission_checker = PermissionChecker()


def require_permission(permission: str):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # 从请求中获取当前用户
            user_id = getattr(request.state, "user_id", None)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证"
                )

            # 检查权限
            if not await permission_checker.has_permission(user_id, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {permission}"
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permissions(permissions: List[str], require_all: bool = False):
    """多权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # 从请求中获取当前用户
            user_id = getattr(request.state, "user_id", None)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证"
                )

            # 检查权限
            if require_all:
                if not await permission_checker.has_all_permissions(user_id, permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"缺少权限: {', '.join(permissions)}"
                    )
            else:
                if not await permission_checker.has_any_permission(user_id, permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"缺少权限: {', '.join(permissions)} 中的至少一个"
                    )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
