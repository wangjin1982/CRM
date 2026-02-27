# 任务管理API
from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.utils.response import ApiResponse
from app.models.activity import TaskInfo
from app.schemas.activity.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskCompleteRequest, TaskCancelRequest
)
from app.schemas.common import PageResponse

router = APIRouter()


def generate_task_no() -> str:
    """生成任务编号"""
    import time
    timestamp = int(time.time() * 1000)
    return f"T{timestamp}"


@router.get("", response_model=ApiResponse)
async def get_tasks(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    customerId: Optional[int] = None,
    opportunityId: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignedTo: Optional[int] = None,
    dueDateStart: Optional[date] = None,
    dueDateEnd: Optional[date] = None,
    overdue: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    # 构建查询
    stmt = select(TaskInfo)
    count_stmt = select(func.count(TaskInfo.id))

    # 添加过滤条件
    conditions = []
    if customerId:
        conditions.append(TaskInfo.customer_id == customerId)
    if opportunityId:
        conditions.append(TaskInfo.opportunity_id == opportunityId)
    if status:
        conditions.append(TaskInfo.status == status)
    if priority:
        conditions.append(TaskInfo.priority == priority)
    if assignedTo:
        conditions.append(TaskInfo.assigned_to == assignedTo)
    if dueDateStart:
        conditions.append(TaskInfo.due_date >= dueDateStart)
    if dueDateEnd:
        conditions.append(TaskInfo.due_date <= dueDateEnd)
    if overdue:
        conditions.append(
            and_(
                TaskInfo.due_date < date.today(),
                TaskInfo.status.in_(["pending", "in_progress"])
            )
        )

    if conditions:
        stmt = stmt.where(and_(*conditions))
        count_stmt = count_stmt.where(and_(*conditions))

    # 获取总数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页查询
    stmt = stmt.order_by(TaskInfo.due_date.asc(), TaskInfo.created_at.desc())
    stmt = stmt.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    # 转换为响应格式
    items = []
    for task in tasks:
        task_dict = TaskListResponse.model_validate(task).model_dump()
        # 检查是否逾期
        if task.due_date < date.today() and task.status in ["pending", "in_progress"]:
            task_dict["is_overdue"] = True
        items.append(task_dict)

    return ApiResponse.success(data=PageResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=pageSize
    ).model_dump())


@router.get("/{task_id}", response_model=ApiResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情"""
    stmt = select(TaskInfo).where(TaskInfo.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    return ApiResponse.success(data=TaskResponse.model_validate(task).model_dump())


@router.post("", response_model=ApiResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建任务"""
    task = TaskInfo(
        task_no=generate_task_no(),
        **task_data.model_dump()
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return ApiResponse.success(data={"id": task.id}, message="创建成功")


@router.put("/{task_id}", response_model=ApiResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    stmt = select(TaskInfo).where(TaskInfo.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    # 更新字段
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()

    return ApiResponse.success(message="更新成功")


@router.post("/{task_id}/complete", response_model=ApiResponse)
async def complete_task(
    task_id: int,
    complete_data: TaskCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """完成任务"""
    stmt = select(TaskInfo).where(TaskInfo.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    task.status = "completed"
    task.completed_at = datetime.utcnow()
    task.completion_note = complete_data.completion_note

    await db.commit()

    return ApiResponse.success(message="任务已完成")


@router.post("/{task_id}/cancel", response_model=ApiResponse)
async def cancel_task(
    task_id: int,
    cancel_data: TaskCancelRequest,
    db: AsyncSession = Depends(get_db)
):
    """取消任务"""
    stmt = select(TaskInfo).where(TaskInfo.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    task.status = "cancelled"
    task.notes = f"取消原因: {cancel_data.cancel_reason}" if cancel_data.cancel_reason else ""

    await db.commit()

    return ApiResponse.success(message="任务已取消")


@router.delete("/{task_id}", response_model=ApiResponse)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    stmt = select(TaskInfo).where(TaskInfo.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    await db.delete(task)
    await db.commit()

    return ApiResponse.success(message="删除成功")
