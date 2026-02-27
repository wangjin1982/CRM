# 跟进记录API
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.utils.response import ApiResponse
from app.models.activity import FollowRecord
from app.schemas.activity.follow import FollowCreate, FollowUpdate, FollowResponse, FollowListResponse
from app.schemas.common import PageResponse

router = APIRouter()


def generate_follow_no() -> str:
    """生成跟进编号"""
    import time
    timestamp = int(time.time() * 1000)
    return f"F{timestamp}"


@router.get("", response_model=ApiResponse)
async def get_follows(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    customerId: Optional[int] = None,
    opportunityId: Optional[int] = None,
    followType: Optional[str] = None,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取跟进记录列表"""
    # 构建查询
    stmt = select(FollowRecord)
    count_stmt = select(func.count(FollowRecord.id))

    # 添加过滤条件
    conditions = []
    if customerId:
        conditions.append(FollowRecord.customer_id == customerId)
    if opportunityId:
        conditions.append(FollowRecord.opportunity_id == opportunityId)
    if followType:
        conditions.append(FollowRecord.follow_type == followType)
    if startDate:
        conditions.append(FollowRecord.created_at >= startDate)
    if endDate:
        conditions.append(FollowRecord.created_at <= endDate)

    if conditions:
        stmt = stmt.where(and_(*conditions))
        count_stmt = count_stmt.where(and_(*conditions))

    # 获取总数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页查询
    stmt = stmt.order_by(FollowRecord.created_at.desc())
    stmt = stmt.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(stmt)
    follows = result.scalars().all()

    # 转换为响应格式
    items = [FollowListResponse.model_validate(f).model_dump() for f in follows]

    return ApiResponse.success(data=PageResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=pageSize
    ).model_dump())


@router.get("/{follow_id}", response_model=ApiResponse)
async def get_follow(
    follow_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取跟进记录详情"""
    stmt = select(FollowRecord).where(FollowRecord.id == follow_id)
    result = await db.execute(stmt)
    follow = result.scalar_one_or_none()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="跟进记录不存在"
        )

    return ApiResponse.success(data=FollowResponse.model_validate(follow).model_dump())


@router.post("", response_model=ApiResponse)
async def create_follow(
    follow_data: FollowCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建跟进记录"""
    follow = FollowRecord(
        follow_no=generate_follow_no(),
        **follow_data.model_dump()
    )

    db.add(follow)
    await db.commit()
    await db.refresh(follow)

    return ApiResponse.success(data={"id": follow.id}, message="创建成功")


@router.put("/{follow_id}", response_model=ApiResponse)
async def update_follow(
    follow_id: int,
    follow_data: FollowUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新跟进记录"""
    stmt = select(FollowRecord).where(FollowRecord.id == follow_id)
    result = await db.execute(stmt)
    follow = result.scalar_one_or_none()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="跟进记录不存在"
        )

    # 更新字段
    update_data = follow_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(follow, field, value)

    await db.commit()

    return ApiResponse.success(message="更新成功")


@router.delete("/{follow_id}", response_model=ApiResponse)
async def delete_follow(
    follow_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除跟进记录"""
    stmt = select(FollowRecord).where(FollowRecord.id == follow_id)
    result = await db.execute(stmt)
    follow = result.scalar_one_or_none()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="跟进记录不存在"
        )

    await db.delete(follow)
    await db.commit()

    return ApiResponse.success(message="删除成功")
