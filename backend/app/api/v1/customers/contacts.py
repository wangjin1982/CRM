"""联系人管理API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.sys.user import User
from app.schemas.customer.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
)
from app.schemas.common import CommonResponse
from app.services.customer.contact_service import ContactService
from app.core.utils.response import success_response

router = APIRouter()


@router.get("/customer/{customer_id}", response_model=ContactListResponse, summary="获取客户联系人列表")
async def get_contacts_by_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定客户的所有联系人

    主要联系人会排在前面
    """
    contacts = await ContactService.get_contacts_by_customer(db, customer_id)

    return ContactListResponse(
        items=contacts,
        total=len(contacts),
    )


@router.get("/{contact_id}", response_model=ContactResponse, summary="获取联系人详情")
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取联系人详情"""
    contact = await ContactService.get_contact_by_id(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在",
        )

    return contact


@router.post(
    "/customer/{customer_id}",
    response_model=ContactResponse,
    summary="创建联系人",
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    customer_id: int,
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    为指定客户创建新联系人

    - **name**: 姓名（必填）
    - **is_primary**: 是否主要联系人
    - **is_decision_maker**: 是否决策人
    """
    contact = await ContactService.create_contact(
        db,
        customer_id,
        contact_data,
        creator_id=current_user.id,
    )

    return contact


@router.put("/{contact_id}", response_model=ContactResponse, summary="更新联系人")
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新联系人信息

    只更新提供的字段
    """
    contact = await ContactService.get_contact_by_id(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在",
        )

    updated_contact = await ContactService.update_contact(
        db,
        contact,
        contact_data,
        updater_id=current_user.id,
    )

    return updated_contact


@router.delete("/{contact_id}", response_model=CommonResponse, summary="删除联系人")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除联系人（软删除）

    联系人数据不会被物理删除，只是标记为已删除
    """
    contact = await ContactService.get_contact_by_id(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在",
        )

    await ContactService.delete_contact(db, contact)

    return success_response(message="联系人删除成功")


@router.post("/{contact_id}/set-primary", response_model=ContactResponse, summary="设置主要联系人")
async def set_primary_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    设置联系人为主要联系人

    同一客户只能有一个主要联系人，设置时会自动取消其他主要联系人标记
    """
    contact = await ContactService.get_contact_by_id(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在",
        )

    updated_contact = await ContactService.set_primary_contact(db, contact)

    return updated_contact
