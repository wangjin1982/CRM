"""商机服务"""
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import select, func, or_, and_, delete, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.models.opportunity import (
    OpportunityInfo,
    StageDef,
    OpportunityContact,
    OpportunityStageHistory,
    Competitor,
)
from app.models.customer import CustomerInfo
from app.models.customer.contact import ContactInfo
from app.models.sys import User
from app.schemas.opportunity.info import OpportunityCreate, OpportunityUpdate, OpportunityPageParams
from app.core.utils.helpers import generate_future_timestamp
from .stage_service import StageService


class OpportunityService:
    """商机服务类"""

    @staticmethod
    async def generate_opportunity_no(db: AsyncSession) -> str:
        """生成商机编号 OPPYYYYMMDDXXXX"""
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"OPP{today}"

        # 查询今天已有的最大编号
        result = await db.execute(
            select(func.max(OpportunityInfo.opportunity_no))
            .where(OpportunityInfo.opportunity_no.like(f"{prefix}%"))
        )
        max_no = result.scalar()

        if max_no:
            # 提取序号并递增
            serial = int(max_no[-4:]) + 1
        else:
            serial = 1

        return f"{prefix}{serial:04d}"

    @staticmethod
    async def get_opportunities(
        db: AsyncSession,
        params: OpportunityPageParams,
        current_user_id: Optional[int] = None,
    ) -> tuple[List[OpportunityInfo], int]:
        """获取商机列表"""

        # 构建查询
        stmt = select(OpportunityInfo).where(OpportunityInfo.deleted_at.is_(None))
        count_stmt = select(func.count(OpportunityInfo.id)).where(OpportunityInfo.deleted_at.is_(None))

        # 添加过滤条件
        conditions = []

        if params.keyword:
            conditions.append(
                or_(
                    OpportunityInfo.opportunity_name.ilike(f"%{params.keyword}%"),
                    OpportunityInfo.opportunity_no.ilike(f"%{params.keyword}%"),
                    OpportunityInfo.customer_name.ilike(f"%{params.keyword}%"),
                )
            )

        if params.customer_id:
            conditions.append(OpportunityInfo.customer_id == params.customer_id)

        if params.stage_id:
            conditions.append(OpportunityInfo.stage_id == params.stage_id)

        if params.status:
            conditions.append(OpportunityInfo.status == params.status)

        if params.owner_id:
            conditions.append(OpportunityInfo.owner_id == params.owner_id)
        elif current_user_id:
            # 非管理员只能看自己的商机
            # TODO: 检查用户权限
            pass

        if params.priority:
            conditions.append(OpportunityInfo.priority == params.priority)

        if params.start_date:
            conditions.append(OpportunityInfo.expected_close_date >= params.start_date)

        if params.end_date:
            conditions.append(OpportunityInfo.expected_close_date <= params.end_date)

        if params.min_amount:
            conditions.append(OpportunityInfo.estimated_amount >= params.min_amount)

        if params.max_amount:
            conditions.append(OpportunityInfo.estimated_amount <= params.max_amount)

        if params.is_stagnant is not None:
            conditions.append(OpportunityInfo.is_stagnant == params.is_stagnant)

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        # 获取总数
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 分页查询
        stmt = stmt.options(selectinload(OpportunityInfo.stage))
        stmt = stmt.order_by(OpportunityInfo.created_at.desc())
        stmt = stmt.offset((params.page - 1) * params.page_size).limit(params.page_size)

        result = await db.execute(stmt)
        opportunities = result.scalars().all()

        return list(opportunities), total

    @staticmethod
    async def get_opportunity_by_id(
        db: AsyncSession,
        opportunity_id: int,
    ) -> Optional[OpportunityInfo]:
        """获取商机详情"""
        stmt = (
            select(OpportunityInfo)
            .where(OpportunityInfo.id == opportunity_id, OpportunityInfo.deleted_at.is_(None))
            .options(
                selectinload(OpportunityInfo.stage),
                selectinload(OpportunityInfo.contacts),
                selectinload(OpportunityInfo.stage_history),
                selectinload(OpportunityInfo.competitors_list),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_opportunity(
        db: AsyncSession,
        data: OpportunityCreate,
        created_by: int,
    ) -> OpportunityInfo:
        """创建商机"""
        await StageService.ensure_default_stages(db)

        # 获取客户信息
        customer_result = await db.execute(
            select(CustomerInfo).where(CustomerInfo.id == data.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer:
            raise ValueError("客户不存在")

        # 获取阶段信息
        stage_result = await db.execute(
            select(StageDef).where(StageDef.id == data.stage_id)
        )
        stage = stage_result.scalar_one_or_none()
        if not stage:
            raise ValueError("阶段不存在")
        if stage.stage_type != "normal":
            raise ValueError("创建商机时只能选择进行中阶段")

        # 获取负责人信息
        owner_name = None
        if data.owner_id:
            user_result = await db.execute(
                select(User).where(User.id == data.owner_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                owner_name = user.real_name or user.username

        # 生成商机编号
        opportunity_no = await OpportunityService.generate_opportunity_no(db)

        # 创建商机
        opportunity = OpportunityInfo(
            opportunity_no=opportunity_no,
            opportunity_name=data.opportunity_name,
            customer_id=data.customer_id,
            customer_name=customer.customer_name,
            primary_contact_id=data.primary_contact_id,
            estimated_amount=data.estimated_amount,
            currency=data.currency,
            stage_id=data.stage_id,
            stage_name=stage.stage_name,
            stage_order=stage.stage_order,
            expected_close_date=data.expected_close_date,
            win_probability=data.win_probability or stage.probability,
            priority=data.priority,
            owner_id=data.owner_id or created_by,
            owner_name=owner_name,
            lead_source=data.lead_source,
            description=data.description,
            tags=data.tags,
            products=data.products,
            created_by=created_by,
            updated_by=created_by,
        )

        db.add(opportunity)
        await db.flush()

        # 关联主要联系人
        if data.primary_contact_id:
            await OpportunityService._add_primary_contact(
                db, opportunity.id, data.primary_contact_id
            )

        # 记录初始阶段历史
        history = OpportunityStageHistory(
            opportunity_id=opportunity.id,
            from_stage_id=None,
            to_stage_id=stage.id,
            stage_duration=0,
            changed_by=created_by,
        )
        db.add(history)

        await db.commit()
        await db.refresh(opportunity)

        return opportunity

    @staticmethod
    async def _add_primary_contact(
        db: AsyncSession,
        opportunity_id: int,
        contact_id: int,
    ):
        """添加主要联系人"""
        # 移除原有的主要联系人标记
        await db.execute(
            update(OpportunityContact)
            .where(OpportunityContact.opportunity_id == opportunity_id)
            .values(is_primary=False)
        )

        # 检查关联是否存在
        existing = await db.execute(
            select(OpportunityContact).where(
                OpportunityContact.opportunity_id == opportunity_id,
                OpportunityContact.contact_id == contact_id,
            )
        )
        contact_rel = existing.scalar_one_or_none()

        if contact_rel:
            contact_rel.is_primary = True
        else:
            new_rel = OpportunityContact(
                opportunity_id=opportunity_id,
                contact_id=contact_id,
                is_primary=True,
            )
            db.add(new_rel)

    @staticmethod
    async def update_opportunity(
        db: AsyncSession,
        opportunity_id: int,
        data: OpportunityUpdate,
        updated_by: int,
    ) -> Optional[OpportunityInfo]:
        """更新商机"""

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return None

        # 更新字段
        update_data = data.model_dump(exclude_unset=True, exclude={"products"})
        for field, value in update_data.items():
            setattr(opportunity, field, value)

        if data.products is not None:
            opportunity.products = data.products

        opportunity.updated_by = updated_by
        opportunity.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(opportunity)

        return opportunity

    @staticmethod
    async def delete_opportunity(
        db: AsyncSession,
        opportunity_id: int,
    ) -> bool:
        """删除商机（软删除）"""

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return False

        opportunity.deleted_at = datetime.utcnow()
        opportunity.status = "abandoned"

        await db.commit()
        return True

    @staticmethod
    async def transfer_opportunity(
        db: AsyncSession,
        opportunity_id: int,
        to_user_id: int,
        remark: Optional[str] = None,
    ) -> Optional[OpportunityInfo]:
        """转移商机"""

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return None

        # 获取新负责人信息
        user_result = await db.execute(
            select(User).where(User.id == to_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("目标用户不存在")

        opportunity.owner_id = to_user_id
        opportunity.owner_name = user.real_name or user.username
        opportunity.updated_at = datetime.utcnow()

        # TODO: 记录转移历史

        await db.commit()
        await db.refresh(opportunity)

        return opportunity

    @staticmethod
    async def change_stage(
        db: AsyncSession,
        opportunity_id: int,
        to_stage_id: int,
        changed_by: int,
        notes: Optional[str] = None,
    ) -> Optional[OpportunityInfo]:
        """变更商机阶段"""

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return None
        if opportunity.status != "open":
            raise ValueError("当前商机已结束，不能再推进阶段")
        if opportunity.stage_id == to_stage_id:
            return opportunity

        # 获取新阶段信息
        stage_result = await db.execute(
            select(StageDef).where(StageDef.id == to_stage_id)
        )
        new_stage = stage_result.scalar_one_or_none()
        if not new_stage:
            raise ValueError("目标阶段不存在")
        if new_stage.stage_type != "normal":
            raise ValueError("只能按顺序推进到下一阶段，赢单/输单请使用专用操作")

        current_stage_order = opportunity.stage_order
        if current_stage_order is None:
            current_stage = (await db.execute(
                select(StageDef).where(StageDef.id == opportunity.stage_id)
            )).scalar_one_or_none()
            current_stage_order = current_stage.stage_order if current_stage else None

        if (
            current_stage_order is not None
            and new_stage.stage_order != current_stage_order + 1
        ):
            raise ValueError("阶段推进必须按顺序进行（仅可推进到下一阶段）")

        from_stage_id = opportunity.stage_id

        # 计算在上一阶段的停留天数
        stage_duration = 0
        last_history = (await db.execute(
            select(OpportunityStageHistory)
            .where(OpportunityStageHistory.opportunity_id == opportunity.id)
            .order_by(desc(OpportunityStageHistory.changed_at))
            .limit(1)
        )).scalar_one_or_none()
        if last_history and last_history.changed_at:
            stage_duration = max((datetime.utcnow() - last_history.changed_at).days, 0)
        elif opportunity.updated_at:
            stage_duration = max((datetime.utcnow() - opportunity.updated_at).days, 0)

        # 更新商机阶段
        opportunity.stage_id = new_stage.id
        opportunity.stage_name = new_stage.stage_name
        opportunity.stage_order = new_stage.stage_order
        opportunity.win_probability = new_stage.probability
        opportunity.days_in_stage = 0
        opportunity.is_stagnant = False
        opportunity.stagnant_alert_sent = False
        opportunity.updated_by = changed_by
        opportunity.updated_at = datetime.utcnow()

        # 更新状态
        if new_stage.stage_type == "won":
            opportunity.status = "won"
            opportunity.actual_close_date = date.today()
        elif new_stage.stage_type == "lost":
            opportunity.status = "lost"

        # 记录阶段历史
        history = OpportunityStageHistory(
            opportunity_id=opportunity.id,
            from_stage_id=from_stage_id,
            to_stage_id=new_stage.id,
            stage_duration=stage_duration,
            changed_by=changed_by,
            notes=notes,
        )
        db.add(history)

        await db.commit()
        await db.refresh(opportunity)

        return opportunity

    @staticmethod
    async def mark_as_won(
        db: AsyncSession,
        opportunity_id: int,
        actual_amount: float,
        actual_close_date: date,
        notes: Optional[str],
        changed_by: int,
    ) -> Optional[OpportunityInfo]:
        """标记赢单"""
        await StageService.ensure_default_stages(db)

        # 获取赢单阶段
        stage_result = await db.execute(
            select(StageDef)
            .where(StageDef.stage_type == "won", StageDef.is_active.is_(True))
            .order_by(desc(StageDef.stage_order))
        )
        won_stage = stage_result.scalar_one_or_none()

        if not won_stage:
            # 如果没有赢单阶段，创建一个
            won_stage = StageDef(
                stage_name="赢单",
                stage_code="won",
                stage_order=999,
                stage_type="won",
                probability=100,
                is_active=True,
            )
            db.add(won_stage)
            await db.flush()

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return None

        from_stage_id = opportunity.stage_id

        # 更新商机
        opportunity.actual_amount = actual_amount
        opportunity.actual_close_date = actual_close_date
        opportunity.stage_id = won_stage.id
        opportunity.stage_name = won_stage.stage_name
        opportunity.stage_order = won_stage.stage_order
        opportunity.win_probability = 100
        opportunity.status = "won"
        opportunity.is_stagnant = False
        opportunity.updated_by = changed_by
        opportunity.updated_at = datetime.utcnow()

        # 记录阶段历史
        history = OpportunityStageHistory(
            opportunity_id=opportunity.id,
            from_stage_id=from_stage_id,
            to_stage_id=won_stage.id,
            changed_by=changed_by,
            notes=notes,
        )
        db.add(history)

        await db.commit()
        await db.refresh(opportunity)

        return opportunity

    @staticmethod
    async def mark_as_lost(
        db: AsyncSession,
        opportunity_id: int,
        lost_reason: str,
        competitor: Optional[str],
        notes: Optional[str],
        changed_by: int,
    ) -> Optional[OpportunityInfo]:
        """标记输单"""
        await StageService.ensure_default_stages(db)

        # 获取输单阶段
        stage_result = await db.execute(
            select(StageDef)
            .where(StageDef.stage_type == "lost", StageDef.is_active.is_(True))
            .order_by(desc(StageDef.stage_order))
        )
        lost_stage = stage_result.scalar_one_or_none()

        if not lost_stage:
            # 如果没有输单阶段，创建一个
            lost_stage = StageDef(
                stage_name="输单",
                stage_code="lost",
                stage_order=998,
                stage_type="lost",
                probability=0,
                is_active=True,
            )
            db.add(lost_stage)
            await db.flush()

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return None

        from_stage_id = opportunity.stage_id

        # 更新商机
        opportunity.lost_reason = lost_reason
        opportunity.competitors = competitor
        opportunity.stage_id = lost_stage.id
        opportunity.stage_name = lost_stage.stage_name
        opportunity.stage_order = lost_stage.stage_order
        opportunity.win_probability = 0
        opportunity.status = "lost"
        opportunity.is_stagnant = False
        opportunity.updated_by = changed_by
        opportunity.updated_at = datetime.utcnow()

        # 记录阶段历史
        history = OpportunityStageHistory(
            opportunity_id=opportunity.id,
            from_stage_id=from_stage_id,
            to_stage_id=lost_stage.id,
            changed_by=changed_by,
            notes=notes,
        )
        db.add(history)

        await db.commit()
        await db.refresh(opportunity)

        return opportunity

    @staticmethod
    async def add_contacts(
        db: AsyncSession,
        opportunity_id: int,
        contact_ids: List[int],
        role: Optional[str] = None,
        influence_level: Optional[int] = None,
    ) -> bool:
        """关联联系人"""

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return False

        for contact_id in contact_ids:
            # 检查是否已关联
            existing = await db.execute(
                select(OpportunityContact).where(
                    OpportunityContact.opportunity_id == opportunity_id,
                    OpportunityContact.contact_id == contact_id,
                )
            )
            if not existing.scalar_one_or_none():
                contact_rel = OpportunityContact(
                    opportunity_id=opportunity_id,
                    contact_id=contact_id,
                    role=role,
                    influence_level=influence_level,
                )
                db.add(contact_rel)

        opportunity.updated_at = datetime.utcnow()
        await db.commit()

        return True

    @staticmethod
    async def get_contacts(
        db: AsyncSession,
        opportunity_id: int,
    ) -> Optional[List[dict]]:
        """获取商机关联联系人"""
        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return None

        stmt = (
            select(OpportunityContact, ContactInfo)
            .outerjoin(ContactInfo, ContactInfo.id == OpportunityContact.contact_id)
            .where(OpportunityContact.opportunity_id == opportunity_id)
            .order_by(desc(OpportunityContact.is_primary), desc(OpportunityContact.id))
        )
        rows = (await db.execute(stmt)).all()
        return [{
            "id": relation.id,
            "contact_id": relation.contact_id,
            "contact_name": contact.name if contact else None,
            "contact_title": contact.title if contact else None,
            "role": relation.role,
            "influence_level": relation.influence_level,
            "is_primary": relation.is_primary,
        } for relation, contact in rows]

    @staticmethod
    async def remove_contact(
        db: AsyncSession,
        opportunity_id: int,
        contact_id: int,
    ) -> bool:
        """移除联系人关联"""

        result = await db.execute(
            delete(OpportunityContact).where(
                OpportunityContact.opportunity_id == opportunity_id,
                OpportunityContact.contact_id == contact_id,
            )
        )

        if result.rowcount > 0:
            opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
            if opportunity:
                opportunity.updated_at = datetime.utcnow()
            await db.commit()
            return True

        return False

    @staticmethod
    async def add_competitor(
        db: AsyncSession,
        opportunity_id: int,
        competitor_name: str,
        strength: Optional[str] = None,
        weakness: Optional[str] = None,
        price_offer: Optional[Decimal] = None,
        threat_level: Optional[int] = None,
    ) -> Competitor:
        """添加竞争对手"""

        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            raise ValueError("商机不存在")

        competitor = Competitor(
            opportunity_id=opportunity_id,
            competitor_name=competitor_name,
            strength=strength,
            weakness=weakness,
            price_offer=price_offer,
            threat_level=threat_level,
        )

        db.add(competitor)
        await db.commit()
        await db.refresh(competitor)

        return competitor

    @staticmethod
    async def get_stage_history(
        db: AsyncSession,
        opportunity_id: int,
    ) -> Optional[List[dict]]:
        """获取商机阶段历史"""
        opportunity = await OpportunityService.get_opportunity_by_id(db, opportunity_id)
        if not opportunity:
            return None

        from_stage = aliased(StageDef)
        to_stage = aliased(StageDef)
        changed_user = aliased(User)

        stmt = (
            select(
                OpportunityStageHistory,
                from_stage.stage_name.label("from_stage_name"),
                to_stage.stage_name.label("to_stage_name"),
                changed_user.real_name.label("changed_real_name"),
                changed_user.username.label("changed_username"),
            )
            .outerjoin(from_stage, from_stage.id == OpportunityStageHistory.from_stage_id)
            .outerjoin(to_stage, to_stage.id == OpportunityStageHistory.to_stage_id)
            .outerjoin(changed_user, changed_user.id == OpportunityStageHistory.changed_by)
            .where(OpportunityStageHistory.opportunity_id == opportunity_id)
            .order_by(desc(OpportunityStageHistory.changed_at), desc(OpportunityStageHistory.id))
        )

        rows = (await db.execute(stmt)).all()
        histories: List[dict] = []
        for history, from_stage_name, to_stage_name, changed_real_name, changed_username in rows:
            histories.append({
                "id": history.id,
                "from_stage_id": history.from_stage_id,
                "from_stage_name": from_stage_name,
                "to_stage_id": history.to_stage_id,
                "to_stage_name": to_stage_name or "",
                "stage_duration": history.stage_duration,
                "changed_at": history.changed_at,
                "changed_by": history.changed_by,
                "changed_by_name": changed_real_name or changed_username,
                "notes": history.notes,
            })
        return histories

    @staticmethod
    async def check_stagnant_opportunities(db: AsyncSession) -> List[OpportunityInfo]:
        """检查停滞商机"""

        # 获取所有进行中的商机
        stmt = select(OpportunityInfo).where(
            OpportunityInfo.status == "open",
            OpportunityInfo.deleted_at.is_(None),
        ).options(selectinload(OpportunityInfo.stage))

        result = await db.execute(stmt)
        opportunities = result.scalars().all()

        stagnant_opportunities = []
        today = date.today()

        for opp in opportunities:
            if not opp.stage or not opp.stage.duration_days:
                continue

            # 计算在当前阶段的停留天数
            days_in_stage = 0
            if opp.updated_at:
                days_in_stage = (today - opp.updated_at.date()).days

            # 更新停留天数
            opp.days_in_stage = days_in_stage

            # 检查是否停滞
            if days_in_stage > opp.stage.duration_days:
                opp.is_stagnant = True
                stagnant_opportunities.append(opp)

        await db.commit()

        return stagnant_opportunities

    @staticmethod
    async def get_opportunity_statistics(
        db: AsyncSession,
        owner_id: Optional[int] = None,
    ) -> dict:
        """获取商机统计"""

        # 构建基础查询
        base_conditions = [OpportunityInfo.deleted_at.is_(None)]
        if owner_id:
            base_conditions.append(OpportunityInfo.owner_id == owner_id)

        # 总商机数
        total_result = await db.execute(
            select(func.count(OpportunityInfo.id)).where(*base_conditions)
        )
        total_count = total_result.scalar() or 0

        # 进行中商机
        open_result = await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                *base_conditions, OpportunityInfo.status == "open"
            )
        )
        open_count = open_result.scalar() or 0

        # 本月赢单
        this_month = date.today().replace(day=1)
        won_result = await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                *base_conditions,
                OpportunityInfo.status == "won",
                OpportunityInfo.actual_close_date >= this_month,
            )
        )
        won_count = won_result.scalar() or 0

        # 本月输单
        lost_result = await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                *base_conditions,
                OpportunityInfo.status == "lost",
                OpportunityInfo.actual_close_date >= this_month,
            )
        )
        lost_count = lost_result.scalar() or 0

        # 停滞商机
        stagnant_result = await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                *base_conditions, OpportunityInfo.is_stagnant == True
            )
        )
        stagnant_count = stagnant_result.scalar() or 0

        # 总金额
        amount_result = await db.execute(
            select(func.sum(OpportunityInfo.estimated_amount)).where(*base_conditions)
        )
        total_amount = amount_result.scalar() or 0

        return {
            "total_count": total_count,
            "open_count": open_count,
            "won_count": won_count,
            "lost_count": lost_count,
            "stagnant_count": stagnant_count,
            "total_amount": float(total_amount),
        }
