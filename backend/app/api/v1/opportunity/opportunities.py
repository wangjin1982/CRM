"""商机管理API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.core.utils.response import ApiResponse
from app.schemas.opportunity.info import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityPageParams,
    OpportunityTransferRequest,
)
from app.schemas.opportunity.stage import (
    StageChangeRequest,
    OpportunityWonRequest,
    OpportunityLostRequest,
    StageHistoryResponse,
)
from app.schemas.opportunity.contact import OpportunityContactRequest, OpportunityContactResponse
from app.schemas.opportunity.competitor import CompetitorCreate
from app.services.opportunity import OpportunityService

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    customer_id: Optional[int] = None,
    stage_id: Optional[int] = None,
    status: Optional[str] = None,
    owner_id: Optional[int] = None,
    priority: Optional[str] = None,
    is_stagnant: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """获取商机列表"""
    params = OpportunityPageParams(
        page=page,
        page_size=page_size,
        keyword=keyword,
        customer_id=customer_id,
        stage_id=stage_id,
        status=status,
        owner_id=owner_id,
        priority=priority,
        is_stagnant=is_stagnant,
    )

    opportunities, total = await OpportunityService.get_opportunities(
        db, params, current_user_id
    )

    items = [OpportunityResponse.model_validate(opp).model_dump() for opp in opportunities]

    return ApiResponse.success(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/statistics", response_model=ApiResponse)
async def get_statistics(
    owner_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """获取商机统计"""
    statistics = await OpportunityService.get_opportunity_statistics(
        db, owner_id or current_user_id
    )
    return ApiResponse.success(data=statistics)


@router.get("/{opportunity_id}", response_model=ApiResponse)
async def get_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取商机详情"""
    opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(data=OpportunityResponse.model_validate(opportunity).model_dump())


@router.get("/{opportunity_id}/stage-history", response_model=ApiResponse)
async def get_opportunity_stage_history(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取商机阶段历史"""
    histories = await OpportunityService.get_stage_history(db, opportunity_id)
    if histories is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )
    data = [StageHistoryResponse(**history).model_dump() for history in histories]
    return ApiResponse.success(data=data)


@router.post("", response_model=ApiResponse)
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """创建商机"""
    try:
        opportunity = await OpportunityService.create_opportunity(
            db, data, current_user_id
        )
        return ApiResponse.success(
            data={"id": opportunity.id},
            message="创建成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{opportunity_id}", response_model=ApiResponse)
async def update_opportunity(
    opportunity_id: int,
    data: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """更新商机"""
    opportunity = await OpportunityService.update_opportunity(
        db, opportunity_id, data, current_user_id
    )
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(message="更新成功")


@router.delete("/{opportunity_id}", response_model=ApiResponse)
async def delete_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除商机"""
    success = await OpportunityService.delete_opportunity(db, opportunity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(message="删除成功")


@router.post("/{opportunity_id}/transfer", response_model=ApiResponse)
async def transfer_opportunity(
    opportunity_id: int,
    data: OpportunityTransferRequest,
    db: AsyncSession = Depends(get_db),
):
    """转移商机"""
    opportunity = await OpportunityService.transfer_opportunity(
        db, opportunity_id, data.to_user_id, data.remark
    )
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(message="转移成功")


@router.post("/{opportunity_id}/stage", response_model=ApiResponse)
async def change_stage(
    opportunity_id: int,
    data: StageChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """推进阶段"""
    try:
        opportunity = await OpportunityService.change_stage(
            db, opportunity_id, data.to_stage_id, current_user_id, data.notes
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(message="阶段推进成功")


@router.post("/{opportunity_id}/won", response_model=ApiResponse)
async def mark_as_won(
    opportunity_id: int,
    data: OpportunityWonRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """标记赢单"""
    opportunity = await OpportunityService.mark_as_won(
        db, opportunity_id, data.actual_amount, data.actual_close_date,
        data.notes, current_user_id
    )
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(message="标记赢单成功")


@router.post("/{opportunity_id}/lost", response_model=ApiResponse)
async def mark_as_lost(
    opportunity_id: int,
    data: OpportunityLostRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """标记输单"""
    opportunity = await OpportunityService.mark_as_lost(
        db, opportunity_id, data.lost_reason, data.competitor,
        data.notes, current_user_id
    )
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(message="标记输单成功")


@router.post("/{opportunity_id}/contacts", response_model=ApiResponse)
async def add_contacts(
    opportunity_id: int,
    data: OpportunityContactRequest,
    db: AsyncSession = Depends(get_db),
):
    """关联联系人"""
    success = await OpportunityService.add_contacts(
        db, opportunity_id, data.contact_ids, data.role, data.influence_level
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )

    return ApiResponse.success(message="关联成功")


@router.get("/{opportunity_id}/contacts", response_model=ApiResponse)
async def get_contacts(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取商机关联联系人"""
    contacts = await OpportunityService.get_contacts(db, opportunity_id)
    if contacts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商机不存在"
        )
    data = [OpportunityContactResponse(**item).model_dump() for item in contacts]
    return ApiResponse.success(data=data)


@router.delete("/{opportunity_id}/contacts/{contact_id}", response_model=ApiResponse)
async def remove_contact(
    opportunity_id: int,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
):
    """移除联系人关联"""
    success = await OpportunityService.remove_contact(db, opportunity_id, contact_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联不存在"
        )

    return ApiResponse.success(message="移除成功")


@router.post("/{opportunity_id}/competitors", response_model=ApiResponse)
async def add_competitor(
    opportunity_id: int,
    data: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
):
    """添加竞争对手"""
    try:
        competitor = await OpportunityService.add_competitor(
            db, opportunity_id,
            data.competitor_name,
            data.strength,
            data.weakness,
            data.price_offer,
            data.threat_level,
        )
        return ApiResponse.success(
            data={"id": competitor.id},
            message="添加成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
