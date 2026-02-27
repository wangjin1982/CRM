# 日程管理API
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.utils.response import ApiResponse
from app.models.activity import Schedule
from app.schemas.activity.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleListResponse

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_schedules(
    startDate: Optional[datetime] = None,
    endDate: Optional[datetime] = None,
    customerId: Optional[int] = None,
    opportunityId: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取日程列表"""
    # 构建查询
    stmt = select(Schedule)

    # 添加过滤条件
    if startDate:
        stmt = stmt.where(Schedule.start_time >= startDate)
    if endDate:
        stmt = stmt.where(Schedule.end_time <= endDate)
    if customerId:
        stmt = stmt.where(Schedule.customer_id == customerId)
    if opportunityId:
        stmt = stmt.where(Schedule.opportunity_id == opportunityId)

    # 按时间排序
    stmt = stmt.order_by(Schedule.start_time)
    result = await db.execute(stmt)
    schedules = result.scalars().all()

    # 转换为响应格式
    items = [ScheduleListResponse.model_validate(s).model_dump() for s in schedules]

    return ApiResponse.success(data=items)


@router.get("/{schedule_id}", response_model=ApiResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取日程详情"""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日程不存在"
        )

    return ApiResponse.success(data=ScheduleResponse.model_validate(schedule).model_dump())


@router.post("", response_model=ApiResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建日程"""
    schedule = Schedule(**schedule_data.model_dump())

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    return ApiResponse.success(data={"id": schedule.id}, message="创建成功")


@router.put("/{schedule_id}", response_model=ApiResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新日程"""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日程不存在"
        )

    # 更新字段
    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)

    await db.commit()

    return ApiResponse.success(message="更新成功")


@router.delete("/{schedule_id}", response_model=ApiResponse)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除日程"""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日程不存在"
        )

    await db.delete(schedule)
    await db.commit()

    return ApiResponse.success(message="删除成功")
