"""客户交互记录API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.utils.response import success_response
from app.models.sys.user import User
from app.schemas.customer.interaction import (
    InteractionCreate,
    InteractionListResponse,
    InteractionResponse,
)
from app.services.customer import InteractionService

router = APIRouter()


@router.get("/customer/{customer_id}", response_model=InteractionListResponse, summary="获取客户交互记录")
async def get_interactions_by_customer(
    customer_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取客户交互记录列表"""
    interactions, total = await InteractionService.get_by_customer(
        db, customer_id, page, page_size
    )

    items = []
    for item in interactions:
        response_item = InteractionResponse.model_validate(item).model_dump()
        attachments = item.attachments.split(",") if item.attachments else []
        response_item["attachments"] = [a for a in attachments if a]
        items.append(InteractionResponse(**response_item))

    return InteractionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/customer/{customer_id}",
    response_model=InteractionResponse,
    summary="创建客户交互记录",
    status_code=status.HTTP_201_CREATED,
)
async def create_interaction(
    customer_id: int,
    data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建客户交互记录"""
    interaction = await InteractionService.create(
        db,
        customer_id,
        data,
        created_by=current_user.id,
    )
    await db.commit()
    await db.refresh(interaction)

    response_item = InteractionResponse.model_validate(interaction).model_dump()
    attachments = interaction.attachments.split(",") if interaction.attachments else []
    response_item["attachments"] = [a for a in attachments if a]
    return InteractionResponse(**response_item)


@router.delete("/{interaction_id}", summary="删除交互记录")
async def delete_interaction(
    interaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除客户交互记录"""
    success = await InteractionService.delete(db, interaction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交互记录不存在",
        )
    await db.commit()
    return success_response(message="删除成功")
