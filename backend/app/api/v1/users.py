"""用户管理API"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user_id
from app.core.security import jwt_manager
from app.core.utils.response import ApiResponse
from app.models.sys.user import User
from app.models.sys.role import UserRole
from app.schemas.sys.user import UserCreate, UserUpdate, UserResponse, UserListResponse, ChangePasswordRequest
from app.schemas.common import PageParams, PageResponse

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    # 构建查询
    stmt = select(User).where(User.deleted_at.is_(None))
    count_stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))

    # 添加过滤条件
    conditions = []
    if keyword:
        conditions.append(
            or_(
                User.username.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
                User.real_name.ilike(f"%{keyword}%"),
            )
        )
    if status is not None:
        conditions.append(User.status == status)

    if conditions:
        stmt = stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    # 获取总数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页查询
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    stmt = stmt.options(selectinload(User.roles))
    result = await db.execute(stmt)
    users = result.scalars().all()

    # 转换为响应格式
    items = []
    for user in users:
        user_dict = UserListResponse.model_validate(user).model_dump()
        user_dict["roles"] = [role.code for role in user.roles]
        items.append(user_dict)

    return ApiResponse.success(data=PageResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    ).model_dump())


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None)).options(selectinload(User.roles))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    user_dict = UserListResponse.model_validate(user).model_dump()
    user_dict["roles"] = [role.code for role in user.roles]

    return ApiResponse.success(data=user_dict)


@router.post("", response_model=ApiResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    # 检查用户名是否存在
    stmt = select(User).where(User.username == user_data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否存在
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )

    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        real_name=user_data.real_name,
        password_hash=jwt_manager.hash_password(user_data.password),
        department_id=user_data.department_id,
        position=user_data.position,
    )

    db.add(user)
    await db.flush()

    # 分配角色
    if user_data.role_ids:
        for role_id in user_data.role_ids:
            user_role = UserRole(user_id=user.id, role_id=role_id, created_at=datetime.utcnow())
            db.add(user_role)

    await db.commit()

    return ApiResponse.success(data={"id": user.id}, message="创建成功")


@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新用户"""
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新字段
    update_data = user_data.model_dump(exclude_unset=True, exclude={"role_ids"})
    for field, value in update_data.items():
        setattr(user, field, value)

    # 更新角色
    if user_data.role_ids is not None:
        # 删除旧角色
        await db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        # 添加新角色
        for role_id in user_data.role_ids:
            user_role = UserRole(user_id=user.id, role_id=role_id, created_at=datetime.utcnow())
            db.add(user_role)

    await db.commit()

    return ApiResponse.success(message="更新成功")


@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除用户（软删除）"""
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 软删除
    from datetime import datetime
    user.deleted_at = datetime.utcnow()
    user.status = 0

    await db.commit()

    return ApiResponse.success(message="删除成功")


@router.post("/{user_id}/roles", response_model=ApiResponse)
async def assign_roles(
    user_id: int,
    role_ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """分配用户角色"""
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 删除旧角色
    await db.execute(delete(UserRole).where(UserRole.user_id == user_id))

    # 添加新角色
    for role_id in role_ids:
        user_role = UserRole(user_id=user.id, role_id=role_id, created_at=datetime.utcnow())
        db.add(user_role)

    await db.commit()

    return ApiResponse.success(message="角色分配成功")


@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    stmt = select(User).where(User.id == current_user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 验证旧密码
    if not jwt_manager.verify_password(password_data.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    user.password_hash = jwt_manager.hash_password(password_data.new_password)
    await db.commit()

    return ApiResponse.success(message="密码修改成功")
