"""销售漏斗API"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.core.utils.response import ApiResponse
from app.services.opportunity import FunnelService

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_funnel(
    owner_id: Optional[int] = Query(None, description="负责人ID"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """获取销售漏斗数据"""
    data = await FunnelService.get_funnel_data(
        db, owner_id, start_date, end_date
    )

    return ApiResponse.success(data=data)


@router.get("/board", response_model=ApiResponse)
async def get_kanban_board(
    owner_id: Optional[int] = Query(None, description="负责人ID"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """获取看板数据（按阶段分组的商机）"""
    data = await FunnelService.get_stage_distribution(db, owner_id)

    return ApiResponse.success(data=data)


@router.get("/conversion", response_model=ApiResponse)
async def get_conversion_rates(
    owner_id: Optional[int] = Query(None, description="负责人ID"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """获取转化率数据"""
    data = await FunnelService.get_funnel_data(db, owner_id)

    return ApiResponse.success(data=data.get("conversion_rates", {}))
