"""客户管理服务"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer.info import CustomerInfo
from app.models.customer.contact import ContactInfo
from app.models.customer.interaction import CustomerInteraction
from app.models.sys.user import User
from app.schemas.customer.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerQueryParams,
    CustomerTransfer,
)
from app.core.utils.helpers import generate_customer_no, tags_to_string, string_to_tags, json_to_string


class CustomerService:
    """客户管理服务类"""

    @staticmethod
    async def _resolve_owner_name(
        db: AsyncSession,
        owner_id: Optional[int],
    ) -> Optional[str]:
        """根据 owner_id 解析负责人姓名"""
        if not owner_id:
            return None
        result = await db.execute(
            select(User).where(
                User.id == owner_id,
                User.deleted_at.is_(None),
            )
        )
        owner = result.scalar_one_or_none()
        if not owner:
            return None
        return owner.real_name or owner.username

    @staticmethod
    async def create_customer(
        db: AsyncSession,
        customer_data: CustomerCreate,
        creator_id: int,
        owner_name: Optional[str] = None,
    ) -> CustomerInfo:
        """创建客户"""
        # 生成客户编号
        customer_no = await generate_customer_no(db)
        resolved_owner_id = customer_data.owner_id or creator_id
        resolved_owner_name = await CustomerService._resolve_owner_name(db, resolved_owner_id)
        if not resolved_owner_name:
            resolved_owner_name = owner_name

        # 创建客户对象
        db_customer = CustomerInfo(
            customer_no=customer_no,
            customer_name=customer_data.customer_name,
            customer_name_en=customer_data.customer_name_en,
            region=customer_data.region,
            customer_type_3=customer_data.customer_type_3,
            customer_level_3=customer_data.customer_level_3,
            deal_customer_5=customer_data.deal_customer_5,
            electrical_engineer_count_5=customer_data.electrical_engineer_count_5,
            owner_name_3=customer_data.owner_name_3 or resolved_owner_name,
            customer_type=customer_data.customer_type,
            industry=customer_data.industry,
            company_size=customer_data.company_size,
            legal_person=customer_data.legal_person,
            registered_capital=customer_data.registered_capital,
            establish_date=customer_data.establish_date,
            province=customer_data.province,
            city=customer_data.city,
            district=customer_data.district,
            address=customer_data.address,
            website=customer_data.website,
            company_info=customer_data.company_info,
            product_info=customer_data.product_info,
            source=customer_data.source,
            level=customer_data.level,
            owner_id=resolved_owner_id,
            owner_name=resolved_owner_name,
            tags=tags_to_string(customer_data.tags),
            remarks=customer_data.remarks,
            created_by=creator_id,
            updated_by=creator_id,
        )

        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer

    @staticmethod
    async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[CustomerInfo]:
        """根据ID获取客户"""
        result = await db.execute(
            select(CustomerInfo)
            .options(selectinload(CustomerInfo.contacts))
            .where(CustomerInfo.id == customer_id, CustomerInfo.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customer_by_no(db: AsyncSession, customer_no: str) -> Optional[CustomerInfo]:
        """根据编号获取客户"""
        result = await db.execute(
            select(CustomerInfo)
            .where(CustomerInfo.customer_no == customer_no, CustomerInfo.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customers_paginated(
        db: AsyncSession,
        params: CustomerQueryParams,
    ) -> tuple[List[CustomerInfo], int]:
        """分页查询客户列表"""
        # 构建查询条件
        conditions = [CustomerInfo.deleted_at.is_(None)]

        if params.keyword:
            keyword_filter = f"%{params.keyword}%"
            conditions.append(
                or_(
                    CustomerInfo.customer_name.ilike(keyword_filter),
                    CustomerInfo.customer_name_en.ilike(keyword_filter),
                )
            )

        if params.customer_type:
            conditions.append(CustomerInfo.customer_type == params.customer_type)

        if params.level:
            conditions.append(CustomerInfo.level == params.level)

        if params.status:
            conditions.append(CustomerInfo.status == params.status)

        if params.owner_id:
            conditions.append(CustomerInfo.owner_id == params.owner_id)

        if params.tags:
            # SQLite兼容：标签以逗号分隔存储，使用like查询
            tag_conditions = []
            for tag in params.tags:
                tag_conditions.append(CustomerInfo.tags.like(f"%{tag}%"))
            if tag_conditions:
                conditions.append(or_(*tag_conditions))

        if params.industry:
            conditions.append(CustomerInfo.industry == params.industry)

        if params.region:
            conditions.append(CustomerInfo.region == params.region)

        if params.source:
            conditions.append(CustomerInfo.source == params.source)

        # 构建查询
        query = select(CustomerInfo).where(and_(*conditions))

        # 排序
        sort_column = getattr(CustomerInfo, params.sort_by, CustomerInfo.created_at)
        if params.sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 获取总数
        count_query = select(func.count(CustomerInfo.id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        # 执行查询
        result = await db.execute(query)
        customers = result.scalars().all()

        return list(customers), total

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        customer: CustomerInfo,
        customer_data: CustomerUpdate,
        updater_id: int,
        owner_name: Optional[str] = None,
    ) -> CustomerInfo:
        """更新客户信息"""
        update_data = customer_data.model_dump(exclude_unset=True)
        owner_id_for_resolve: Optional[int] = None

        for field, value in update_data.items():
            # 特殊处理tags字段
            if field == "tags" and value is not None:
                setattr(customer, field, tags_to_string(value))
            elif field == "owner_id":
                owner_id_for_resolve = value
                setattr(customer, field, value)
            else:
                setattr(customer, field, value)

        if owner_id_for_resolve is not None:
            resolved_owner_name = await CustomerService._resolve_owner_name(db, owner_id_for_resolve)
            if resolved_owner_name:
                customer.owner_name = resolved_owner_name
                if not customer.owner_name_3:
                    customer.owner_name_3 = resolved_owner_name
        elif update_data.get("owner_name_3"):
            customer.owner_name = update_data.get("owner_name_3")
        elif owner_name and not update_data.get("owner_id"):
            customer.owner_name = owner_name

        customer.updated_by = updater_id
        customer.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def delete_customer(db: AsyncSession, customer: CustomerInfo) -> bool:
        """软删除客户"""
        customer.deleted_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def transfer_customer(
        db: AsyncSession,
        customer: CustomerInfo,
        transfer_data: CustomerTransfer,
    ) -> CustomerInfo:
        """转移客户"""
        customer.owner_id = transfer_data.to_user_id
        customer.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def batch_transfer(
        db: AsyncSession,
        customer_ids: List[int],
        to_user_id: int,
    ) -> int:
        """批量转移客户"""
        result = await db.execute(
            select(CustomerInfo)
            .where(
                and_(
                    CustomerInfo.id.in_(customer_ids),
                    CustomerInfo.deleted_at.is_(None),
                )
            )
        )
        customers = result.scalars().all()

        count = 0
        for customer in customers:
            customer.owner_id = to_user_id
            customer.updated_at = datetime.utcnow()
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def batch_assign_tags(
        db: AsyncSession,
        customer_ids: List[int],
        tags: List[str],
    ) -> int:
        """批量分配标签（覆盖写入）"""
        result = await db.execute(
            select(CustomerInfo)
            .where(
                and_(
                    CustomerInfo.id.in_(customer_ids),
                    CustomerInfo.deleted_at.is_(None),
                )
            )
        )
        customers = result.scalars().all()

        count = 0
        tags_value = tags_to_string(tags)
        for customer in customers:
            customer.tags = tags_value
            customer.updated_at = datetime.utcnow()
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def batch_change_level(
        db: AsyncSession,
        customer_ids: List[int],
        level: str,
    ) -> int:
        """批量修改客户级别"""
        result = await db.execute(
            select(CustomerInfo)
            .where(
                and_(
                    CustomerInfo.id.in_(customer_ids),
                    CustomerInfo.deleted_at.is_(None),
                )
            )
        )
        customers = result.scalars().all()

        count = 0
        for customer in customers:
            customer.level = level
            customer.updated_at = datetime.utcnow()
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def batch_change_status(
        db: AsyncSession,
        customer_ids: List[int],
        status: str,
    ) -> int:
        """批量修改客户状态"""
        result = await db.execute(
            select(CustomerInfo)
            .where(
                and_(
                    CustomerInfo.id.in_(customer_ids),
                    CustomerInfo.deleted_at.is_(None),
                )
            )
        )
        customers = result.scalars().all()

        count = 0
        for customer in customers:
            customer.status = status
            customer.updated_at = datetime.utcnow()
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def get_customer_360_view(
        db: AsyncSession,
        customer_id: int,
    ) -> Dict[str, Any]:
        """获取客户360度视图"""
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return None

        # 获取联系人
        contacts_result = await db.execute(
            select(ContactInfo)
            .where(ContactInfo.customer_id == customer_id, ContactInfo.deleted_at.is_(None))
            .order_by(ContactInfo.is_primary.desc(), ContactInfo.created_at)
        )
        contacts = contacts_result.scalars().all()

        # 获取最近的交互记录
        interactions_result = await db.execute(
            select(CustomerInteraction)
            .where(CustomerInteraction.customer_id == customer_id)
            .order_by(CustomerInteraction.created_at.desc())
            .limit(10)
        )
        interactions = interactions_result.scalars().all()

        # 构建时间轴
        timeline = []
        for interaction in interactions:
            timeline.append({
                "type": interaction.interaction_type,
                "title": f"{interaction.interaction_type.title()}",
                "content": interaction.subject or interaction.content or "",
                "created_at": interaction.created_at,
            })

        return {
            "customer": customer,
            "contacts": list(contacts),
            "interactions": list(interactions),
            "timeline": timeline,
        }

    @staticmethod
    async def update_statistics(
        db: AsyncSession,
        customer_id: int,
    ) -> None:
        """更新客户统计信息"""
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return

        # 更新商机数量
        # TODO: 实现商机统计

        # 更新拜访次数
        # TODO: 实现拜访统计

        await db.commit()
