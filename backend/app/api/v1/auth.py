"""认证相关API"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import jwt_manager, get_auth_data
from app.core.utils.response import ApiResponse
from app.models.sys.user import User
from app.schemas.sys.auth import LoginRequest, LoginResponse, RefreshTokenRequest

router = APIRouter()


@router.post("/login", response_model=ApiResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查询用户（支持用户名或邮箱登录）
    stmt = select(User).where(
        (User.username == credentials.username) | (User.email == credentials.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # 验证用户
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not jwt_manager.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查用户状态
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # 生成token
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }

    access_token = jwt_manager.create_access_token(token_data)
    refresh_token = jwt_manager.create_refresh_token(token_data)

    return ApiResponse.success(data=LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=60 * 60 * 2,  # 2小时
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "real_name": user.real_name,
            "avatar": user.avatar,
            "is_admin": user.is_admin,
        }
    ))


@router.post("/logout", response_model=ApiResponse)
async def logout():
    """用户登出"""
    # TODO: 将token加入黑名单
    return ApiResponse.success(message="登出成功")


@router.post("/refresh", response_model=ApiResponse)
async def refresh(request: RefreshTokenRequest):
    """刷新访问令牌"""
    # 验证刷新令牌
    payload = jwt_manager.verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    # 生成新的访问令牌
    token_data = {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "email": payload.get("email"),
    }

    access_token = jwt_manager.create_access_token(token_data)

    return ApiResponse.success(data={
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 60 * 60 * 2,  # 2小时
    })


@router.get("/me", response_model=ApiResponse)
async def get_current_user(auth_data: dict = Depends(get_auth_data)):
    """获取当前用户信息"""
    return ApiResponse.success(data=auth_data)
