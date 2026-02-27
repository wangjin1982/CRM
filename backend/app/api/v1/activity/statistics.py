"""销售行为统计API"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.utils.response import ApiResponse
from app.models.activity import FollowRecord, TaskInfo, VisitRecord

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_activity_statistics(
    startDate: Optional[date] = Query(None, description="开始日期"),
    endDate: Optional[date] = Query(None, description="结束日期"),
    ownerId: Optional[int] = Query(None, description="负责人"),
    db: AsyncSession = Depends(get_db),
):
    """销售行为统计"""
    end_date = endDate or date.today()
    start_date = startDate or (end_date - timedelta(days=29))

    visit_conditions = [
        VisitRecord.visit_date >= start_date,
        VisitRecord.visit_date <= end_date,
    ]
    follow_conditions = [
        func.date(FollowRecord.created_at) >= start_date,
        func.date(FollowRecord.created_at) <= end_date,
    ]
    task_conditions = [
        TaskInfo.due_date >= start_date,
        TaskInfo.due_date <= end_date,
    ]

    if ownerId:
        visit_conditions.append(VisitRecord.created_by == ownerId)
        follow_conditions.append(FollowRecord.created_by == ownerId)
        task_conditions.append(TaskInfo.assigned_to == ownerId)

    total_visits = (await db.execute(
        select(func.count(VisitRecord.id)).where(and_(*visit_conditions))
    )).scalar() or 0

    total_follows = (await db.execute(
        select(func.count(FollowRecord.id)).where(and_(*follow_conditions))
    )).scalar() or 0

    total_tasks = (await db.execute(
        select(func.count(TaskInfo.id)).where(and_(*task_conditions))
    )).scalar() or 0

    completed_tasks = (await db.execute(
        select(func.count(TaskInfo.id)).where(and_(*task_conditions, TaskInfo.status == "completed"))
    )).scalar() or 0

    overdue_tasks = (await db.execute(
        select(func.count(TaskInfo.id)).where(
            and_(
                TaskInfo.due_date < date.today(),
                TaskInfo.status.in_(["pending", "in_progress"]),
            )
        )
    )).scalar() or 0

    follow_type_result = await db.execute(
        select(FollowRecord.follow_type, func.count(FollowRecord.id))
        .where(and_(*follow_conditions))
        .group_by(FollowRecord.follow_type)
    )
    follow_type_distribution = {
        row[0] or "unknown": row[1] for row in follow_type_result.all()
    }

    visit_trend_result = await db.execute(
        select(VisitRecord.visit_date, func.count(VisitRecord.id))
        .where(and_(*visit_conditions))
        .group_by(VisitRecord.visit_date)
        .order_by(VisitRecord.visit_date)
    )
    visit_trend = [{"date": str(row[0]), "count": row[1]} for row in visit_trend_result.all()]

    task_completion_rate = round((completed_tasks / total_tasks * 100), 2) if total_tasks else 0

    return ApiResponse.success(data={
        "summary": {
            "total_visits": total_visits,
            "total_follows": total_follows,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
        },
        "visit_trend": visit_trend,
        "follow_type_distribution": follow_type_distribution,
        "task_completion_rate": task_completion_rate,
        "overdue_tasks": overdue_tasks,
    })
