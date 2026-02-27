"""客户标签管理API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.sys.user import User
from app.schemas.customer.tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
)
from app.schemas.common import CommonResponse
from app.core.utils.response import success_response

router = APIRouter()


@router.get("", response_model=TagListResponse, summary="获取标签列表")
async def get_tags(
    tag_type: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取标签列表

    - **tag_type**: 标签类型筛选（system/custom）
    """
    # TODO: 实现标签列表查询
    from app.models.customer.tag import CustomerTag
    from sqlalchemy import select

    query = select(CustomerTag)
    if tag_type:
        query = query.where(CustomerTag.tag_type == tag_type)

    query = query.order_by(CustomerTag.sort_order, CustomerTag.created_at)

    result = await db.execute(query)
    tags = result.scalars().all()

    return TagListResponse(
        items=list(tags),
        total=len(tags),
    )


@router.post("", response_model=TagResponse, summary="创建标签", status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建新标签

    - **tag_name**: 标签名称（必填）
    - **tag_type**: 标签类型（system/custom）
    - **tag_color**: 标签颜色
    """
    from app.models.customer.tag import CustomerTag

    # 检查标签名是否已存在
    from sqlalchemy import select
    result = await db.execute(
        select(CustomerTag).where(CustomerTag.tag_name == tag_data.tag_name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名称已存在",
        )

    db_tag = CustomerTag(
        tag_name=tag_data.tag_name,
        tag_color=tag_data.tag_color,
        tag_type=tag_data.tag_type,
        sort_order=tag_data.sort_order,
    )

    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)

    return db_tag


@router.put("/{tag_id}", response_model=TagResponse, summary="更新标签")
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新标签信息

    只更新提供的字段
    """
    from app.models.customer.tag import CustomerTag
    from sqlalchemy import select

    result = await db.execute(
        select(CustomerTag).where(CustomerTag.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在",
        )

    update_data = tag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    await db.commit()
    await db.refresh(tag)

    return tag


@router.delete("/{tag_id}", response_model=CommonResponse, summary="删除标签")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除标签

    系统标签不可删除
    """
    from app.models.customer.tag import CustomerTag
    from sqlalchemy import select

    result = await db.execute(
        select(CustomerTag).where(CustomerTag.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在",
        )

    if tag.tag_type == "system":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统标签不可删除",
        )

    await db.delete(tag)
    await db.commit()

    return success_response(message="标签删除成功")
