"""客户交互记录服务"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer.interaction import CustomerInteraction
from app.schemas.customer.interaction import InteractionCreate


class InteractionService:
    """客户交互记录服务类"""

    @staticmethod
    async def get_by_customer(
        db: AsyncSession,
        customer_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[CustomerInteraction], int]:
        """分页获取客户交互记录"""
        conditions = [CustomerInteraction.customer_id == customer_id]

        total_result = await db.execute(
            select(func.count(CustomerInteraction.id)).where(and_(*conditions))
        )
        total = total_result.scalar() or 0

        result = await db.execute(
            select(CustomerInteraction)
            .where(and_(*conditions))
            .order_by(CustomerInteraction.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        interaction_id: int,
    ) -> Optional[CustomerInteraction]:
        """根据ID获取交互记录"""
        result = await db.execute(
            select(CustomerInteraction).where(CustomerInteraction.id == interaction_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        customer_id: int,
        data: InteractionCreate,
        created_by: int,
    ) -> CustomerInteraction:
        """创建交互记录"""
        interaction = CustomerInteraction(
            customer_id=customer_id,
            contact_id=data.contact_id,
            interaction_type=data.interaction_type,
            direction=data.direction,
            subject=data.subject,
            content=data.content,
            duration=data.duration,
            attachments=",".join(data.attachments or []) if data.attachments else None,
            next_follow_at=data.next_follow_at,
            next_follow_note=data.next_follow_note,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(interaction)
        await db.flush()
        await db.refresh(interaction)
        return interaction

    @staticmethod
    async def delete(
        db: AsyncSession,
        interaction_id: int,
    ) -> bool:
        """删除交互记录"""
        interaction = await InteractionService.get_by_id(db, interaction_id)
        if not interaction:
            return False
        await db.delete(interaction)
        return True
