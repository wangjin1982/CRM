"""销售阶段API"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.utils.response import ApiResponse
from app.schemas.opportunity.stage import StageDefCreate, StageDefUpdate, StageDefResponse
from app.services.opportunity import StageService

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_stages(
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """获取所有阶段"""
    stages = await StageService.get_all_stages(db, is_active)
    items = [StageDefResponse.model_validate(stage).model_dump() for stage in stages]
    return ApiResponse.success(data=items)


@router.get("/{stage_id}", response_model=ApiResponse)
async def get_stage(
    stage_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取阶段详情"""
    stage = await StageService.get_stage_by_id(db, stage_id)
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阶段不存在"
        )
    return ApiResponse.success(data=StageDefResponse.model_validate(stage).model_dump())


@router.post("", response_model=ApiResponse)
async def create_stage(
    data: StageDefCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建阶段"""
    stage = await StageService.create_stage(db, data)
    return ApiResponse.success(
        data={"id": stage.id},
        message="创建成功"
    )


@router.put("/{stage_id}", response_model=ApiResponse)
async def update_stage(
    stage_id: int,
    data: StageDefUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新阶段"""
    stage = await StageService.update_stage(db, stage_id, data)
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阶段不存在"
        )
    return ApiResponse.success(message="更新成功")


@router.delete("/{stage_id}", response_model=ApiResponse)
async def delete_stage(
    stage_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除阶段"""
    success = await StageService.delete_stage(db, stage_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阶段不存在"
        )
    return ApiResponse.success(message="删除成功")
