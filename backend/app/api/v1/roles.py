"""角色管理API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.core.utils.response import ApiResponse
from app.models.sys.role import Role, RolePermission
from app.models.sys.permission import Permission
from app.schemas.sys.role import RoleCreate, RoleUpdate, RoleResponse, RoleListResponse
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取角色列表"""
    # 构建查询
    stmt = select(Role)
    count_stmt = select(func.count(Role.id))

    # 添加过滤条件
    if keyword:
        stmt = stmt.where(
            (Role.name.ilike(f"%{keyword}%")) | (Role.code.ilike(f"%{keyword}%"))
        )
        count_stmt = count_stmt.where(
            (Role.name.ilike(f"%{keyword}%")) | (Role.code.ilike(f"%{keyword}%"))
        )

    # 获取总数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页查询
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    stmt = stmt.options(selectinload(Role.permissions))
    result = await db.execute(stmt)
    roles = result.scalars().all()

    # 转换为响应格式
    items = []
    for role in roles:
        role_dict = RoleListResponse.model_validate(role).model_dump()
        role_dict["permissions"] = [perm.code for perm in role.permissions]
        # TODO: 获取用户数量
        role_dict["user_count"] = 0
        items.append(role_dict)

    return ApiResponse.success(data=PageResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    ).model_dump())


@router.get("/{role_id}", response_model=ApiResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取角色详情"""
    stmt = select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    role_dict = RoleListResponse.model_validate(role).model_dump()
    role_dict["permissions"] = [perm.code for perm in role.permissions]
    role_dict["user_count"] = 0

    return ApiResponse.success(data=role_dict)


@router.post("", response_model=ApiResponse)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建角色"""
    # 检查角色名是否存在
    stmt = select(Role).where(Role.name == role_data.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名已存在"
        )

    # 检查角色代码是否存在
    stmt = select(Role).where(Role.code == role_data.code)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色代码已存在"
        )

    # 创建角色
    role = Role(
        name=role_data.name,
        code=role_data.code,
        description=role_data.description,
    )

    db.add(role)
    await db.flush()

    # 分配权限
    if role_data.permission_ids:
        for perm_id in role_data.permission_ids:
            role_perm = RolePermission(role_id=role.id, permission_id=perm_id, created_at=datetime.utcnow())
            db.add(role_perm)

    await db.commit()

    return ApiResponse.success(data={"id": role.id}, message="创建成功")


@router.put("/{role_id}", response_model=ApiResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新角色"""
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    # 更新字段
    update_data = role_data.model_dump(exclude_unset=True, exclude={"permission_ids"})
    for field, value in update_data.items():
        setattr(role, field, value)

    # 更新权限
    if role_data.permission_ids is not None:
        # 删除旧权限
        await db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
        # 添加新权限
        for perm_id in role_data.permission_ids:
            role_perm = RolePermission(role_id=role.id, permission_id=perm_id, created_at=datetime.utcnow())
            db.add(role_perm)

    await db.commit()

    return ApiResponse.success(message="更新成功")


@router.delete("/{role_id}", response_model=ApiResponse)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除角色"""
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    await db.delete(role)
    await db.commit()

    return ApiResponse.success(message="删除成功")


@router.post("/{role_id}/permissions", response_model=ApiResponse)
async def assign_permissions(
    role_id: int,
    permission_ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """分配角色权限"""
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    # 删除旧权限
    await db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))

    # 添加新权限
    for perm_id in permission_ids:
        role_perm = RolePermission(role_id=role.id, permission_id=perm_id, created_at=datetime.utcnow())
        db.add(role_perm)

    await db.commit()

    return ApiResponse.success(message="权限分配成功")
