"""认证模块"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security.jwt import jwt_manager
from app.core.security.permission import permission_checker

# HTTP Bearer认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前登录用户"""
    token = credentials.credentials

    # 验证token
    payload = jwt_manager.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 获取用户ID
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌格式错误",
        )

    # TODO: 从数据库获取完整用户信息
    # 这里简化处理，直接返回payload中的信息
    return {
        "user_id": user_id,
        "username": payload.get("username"),
        "email": payload.get("email"),
    }


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前活跃用户"""
    # TODO: 检查用户状态是否启用
    return current_user


class AuthData:
    """认证数据类"""

    def __init__(self, user_id: int, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email


async def get_auth_data(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthData:
    """获取认证数据"""
    token = credentials.credentials

    payload = jwt_manager.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
        )

    return AuthData(
        user_id=payload.get("user_id"),
        username=payload.get("username"),
        email=payload.get("email"),
    )
