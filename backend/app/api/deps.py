"""依赖注入模块"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config.database import async_session_maker
from app.core.security import get_auth_data
from app.models.sys.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user_id(auth_data: dict = Depends(get_auth_data)) -> int:
    """获取当前用户ID"""
    return auth_data.user_id


async def get_current_username(auth_data: dict = Depends(get_auth_data)) -> str:
    """获取当前用户名"""
    return auth_data.username


async def get_current_user(
    auth_data: dict = Depends(get_auth_data),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    user_id = auth_data.user_id

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被删除"
        )

    return user
