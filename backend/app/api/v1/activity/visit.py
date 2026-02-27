# 拜访记录API
from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.utils.response import ApiResponse
from app.models.activity import VisitRecord
from app.schemas.activity.visit import VisitCreate, VisitUpdate, VisitResponse, VisitListResponse
from app.schemas.common import PageParams, PageResponse

router = APIRouter()


def generate_visit_no() -> str:
    """生成拜访编号"""
    import time
    timestamp = int(time.time() * 1000)
    return f"V{timestamp}"


@router.get("", response_model=ApiResponse)
async def get_visits(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    customerId: Optional[int] = None,
    opportunityId: Optional[int] = None,
    visitType: Optional[str] = None,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
    createdBy: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取拜访记录列表"""
    # 构建查询
    stmt = select(VisitRecord)
    count_stmt = select(func.count(VisitRecord.id))

    # 添加过滤条件
    conditions = []
    if customerId:
        conditions.append(VisitRecord.customer_id == customerId)
    if opportunityId:
        conditions.append(VisitRecord.opportunity_id == opportunityId)
    if visitType:
        conditions.append(VisitRecord.visit_type == visitType)
    if startDate:
        conditions.append(VisitRecord.visit_date >= startDate)
    if endDate:
        conditions.append(VisitRecord.visit_date <= endDate)
    if createdBy:
        conditions.append(VisitRecord.created_by == createdBy)

    if conditions:
        stmt = stmt.where(and_(*conditions))
        count_stmt = count_stmt.where(and_(*conditions))

    # 获取总数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页查询
    stmt = stmt.order_by(VisitRecord.visit_date.desc(), VisitRecord.created_at.desc())
    stmt = stmt.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(stmt)
    visits = result.scalars().all()

    # 转换为响应格式
    items = [VisitListResponse.model_validate(v).model_dump() for v in visits]

    return ApiResponse.success(data=PageResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=pageSize
    ).model_dump())


@router.get("/{visit_id}", response_model=ApiResponse)
async def get_visit(
    visit_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取拜访记录详情"""
    stmt = select(VisitRecord).where(VisitRecord.id == visit_id)
    result = await db.execute(stmt)
    visit = result.scalar_one_or_none()

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="拜访记录不存在"
        )

    return ApiResponse.success(data=VisitResponse.model_validate(visit).model_dump())


@router.post("", response_model=ApiResponse)
async def create_visit(
    visit_data: VisitCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建拜访记录"""
    # 创建拜访记录
    visit = VisitRecord(
        visit_no=generate_visit_no(),
        **visit_data.model_dump()
    )

    db.add(visit)
    await db.commit()
    await db.refresh(visit)

    return ApiResponse.success(data={"id": visit.id}, message="创建成功")


@router.put("/{visit_id}", response_model=ApiResponse)
async def update_visit(
    visit_id: int,
    visit_data: VisitUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新拜访记录"""
    stmt = select(VisitRecord).where(VisitRecord.id == visit_id)
    result = await db.execute(stmt)
    visit = result.scalar_one_or_none()

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="拜访记录不存在"
        )

    # 更新字段
    update_data = visit_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(visit, field, value)

    await db.commit()

    return ApiResponse.success(message="更新成功")


@router.delete("/{visit_id}", response_model=ApiResponse)
async def delete_visit(
    visit_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除拜访记录"""
    stmt = select(VisitRecord).where(VisitRecord.id == visit_id)
    result = await db.execute(stmt)
    visit = result.scalar_one_or_none()

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="拜访记录不存在"
        )

    await db.delete(visit)
    await db.commit()

    return ApiResponse.success(message="删除成功")
