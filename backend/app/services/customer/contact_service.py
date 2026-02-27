"""联系人管理服务"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer.contact import ContactInfo
from app.models.customer.info import CustomerInfo
from app.schemas.customer.contact import ContactCreate, ContactUpdate
from app.core.utils.helpers import generate_contact_no


class ContactService:
    """联系人管理服务类"""

    @staticmethod
    async def create_contact(
        db: AsyncSession,
        customer_id: int,
        contact_data: ContactCreate,
        creator_id: int,
    ) -> ContactInfo:
        """创建联系人"""
        # 生成联系人编号
        contact_no = await generate_contact_no(db)

        # 如果设为主要联系人，先取消该客户的其他主要联系人
        if contact_data.is_primary:
            await ContactService._unset_primary_contact(db, customer_id)

        # 创建联系人对象
        db_contact = ContactInfo(
            contact_no=contact_no,
            customer_id=customer_id,
            name=contact_data.name,
            title=contact_data.title,
            department=contact_data.department,
            gender=contact_data.gender,
            mobile=contact_data.mobile,
            phone=contact_data.phone,
            email=contact_data.email,
            wechat=contact_data.wechat,
            is_decision_maker=contact_data.is_decision_maker,
            is_influencer=contact_data.is_influencer,
            influence_level=contact_data.influence_level,
            relationship=contact_data.relationship,
            preference=contact_data.preference,
            birthday=contact_data.birthday,
            hobbies=contact_data.hobbies,
            linkedin=contact_data.linkedin,
            weibo=contact_data.weibo,
            is_primary=contact_data.is_primary,
            remarks=contact_data.remarks,
            created_by=creator_id,
            updated_by=creator_id,
        )

        db.add(db_contact)
        await db.commit()
        await db.refresh(db_contact)
        return db_contact

    @staticmethod
    async def get_contact_by_id(db: AsyncSession, contact_id: int) -> Optional[ContactInfo]:
        """根据ID获取联系人"""
        result = await db.execute(
            select(ContactInfo)
            .where(ContactInfo.id == contact_id, ContactInfo.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_contacts_by_customer(
        db: AsyncSession,
        customer_id: int,
    ) -> List[ContactInfo]:
        """获取客户的所有联系人"""
        result = await db.execute(
            select(ContactInfo)
            .where(
                and_(
                    ContactInfo.customer_id == customer_id,
                    ContactInfo.deleted_at.is_(None),
                )
            )
            .order_by(ContactInfo.is_primary.desc(), ContactInfo.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_contact(
        db: AsyncSession,
        contact: ContactInfo,
        contact_data: ContactUpdate,
        updater_id: int,
    ) -> ContactInfo:
        """更新联系人信息"""
        update_data = contact_data.model_dump(exclude_unset=True)

        # 如果设为主要联系人，先取消同一客户的其他主要联系人
        if update_data.get("is_primary") and not contact.is_primary:
            await ContactService._unset_primary_contact(db, contact.customer_id)

        for field, value in update_data.items():
            setattr(contact, field, value)

        contact.updated_by = updater_id
        contact.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def delete_contact(db: AsyncSession, contact: ContactInfo) -> bool:
        """软删除联系人"""
        contact.deleted_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def set_primary_contact(
        db: AsyncSession,
        contact: ContactInfo,
    ) -> ContactInfo:
        """设置主要联系人"""
        # 先取消同一客户的其他主要联系人
        await ContactService._unset_primary_contact(db, contact.customer_id)

        contact.is_primary = True
        contact.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def _unset_primary_contact(db: AsyncSession, customer_id: int) -> None:
        """取消客户的所有主要联系人标记（内部方法）"""
        result = await db.execute(
            select(ContactInfo).where(
                and_(
                    ContactInfo.customer_id == customer_id,
                    ContactInfo.is_primary.is_(True),
                    ContactInfo.deleted_at.is_(None),
                )
            )
        )
        contacts = result.scalars().all()

        for contact in contacts:
            contact.is_primary = False
            contact.updated_at = datetime.utcnow()

        await db.commit()
