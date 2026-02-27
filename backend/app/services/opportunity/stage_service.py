"""销售阶段服务"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import StageDef
from app.schemas.opportunity.stage import StageDefCreate, StageDefUpdate
from .stage_templates import DEFAULT_STAGE_TEMPLATES


class StageService:
    """销售阶段服务类"""

    @staticmethod
    async def ensure_default_stages(db: AsyncSession) -> None:
        """确保默认阶段模板存在（按EPLAN销售阶段定义）"""
        existing = (await db.execute(select(StageDef))).scalars().all()
        by_code = {stage.stage_code: stage for stage in existing}
        changed = False

        for template in DEFAULT_STAGE_TEMPLATES:
            stage = by_code.get(template["stage_code"])
            if stage:
                for field, value in template.items():
                    if getattr(stage, field) != value:
                        setattr(stage, field, value)
                        changed = True
                if not stage.is_active:
                    stage.is_active = True
                    changed = True
            else:
                db.add(StageDef(**template, is_active=True))
                changed = True

        if changed:
            await db.commit()

    @staticmethod
    async def get_all_stages(
        db: AsyncSession,
        is_active: Optional[bool] = None,
    ) -> List[StageDef]:
        """获取所有阶段"""
        await StageService.ensure_default_stages(db)
        stmt = select(StageDef).order_by(StageDef.stage_order)

        if is_active is not None:
            stmt = stmt.where(StageDef.is_active == is_active)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_stage_by_id(
        db: AsyncSession,
        stage_id: int,
    ) -> Optional[StageDef]:
        """获取阶段详情"""
        stmt = select(StageDef).where(StageDef.id == stage_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_stage(
        db: AsyncSession,
        data: StageDefCreate,
    ) -> StageDef:
        """创建阶段"""
        stage = StageDef(**data.model_dump())
        db.add(stage)
        await db.commit()
        await db.refresh(stage)
        return stage

    @staticmethod
    async def update_stage(
        db: AsyncSession,
        stage_id: int,
        data: StageDefUpdate,
    ) -> Optional[StageDef]:
        """更新阶段"""
        stage = await StageService.get_stage_by_id(db, stage_id)
        if not stage:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stage, field, value)

        await db.commit()
        await db.refresh(stage)
        return stage

    @staticmethod
    async def delete_stage(
        db: AsyncSession,
        stage_id: int,
    ) -> bool:
        """删除阶段"""
        stage = await StageService.get_stage_by_id(db, stage_id)
        if not stage:
            return False

        await db.delete(stage)
        await db.commit()
        return True
