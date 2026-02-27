"""销售漏斗服务"""
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import OpportunityInfo, StageDef


class FunnelService:
    """销售漏斗服务类"""

    @staticmethod
    async def get_funnel_data(
        db: AsyncSession,
        owner_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """获取销售漏斗数据"""

        # 构建基础查询条件
        base_conditions = [OpportunityInfo.deleted_at.is_(None)]
        if owner_id:
            base_conditions.append(OpportunityInfo.owner_id == owner_id)
        if start_date:
            base_conditions.append(OpportunityInfo.created_at >= start_date)
        if end_date:
            base_conditions.append(OpportunityInfo.created_at <= end_date)

        # 获取所有活跃阶段
        stages_stmt = select(StageDef).where(
            StageDef.is_active == True,
            StageDef.stage_type == "normal",
        ).order_by(StageDef.stage_order)
        stages_result = await db.execute(stages_stmt)
        stages = stages_result.scalars().all()

        # 构建漏斗数据
        funnel_data = []
        total_count = 0
        total_amount = 0
        weighted_amount = 0

        for stage in stages:
            # 统计该阶段的商机
            conditions = base_conditions + [
                OpportunityInfo.stage_id == stage.id,
                OpportunityInfo.status == "open",
            ]
            count_stmt = select(func.count(OpportunityInfo.id)).where(*conditions)
            count_result = await db.execute(count_stmt)
            count = count_result.scalar() or 0

            # 统计该阶段的金额
            amount_stmt = select(
                func.coalesce(func.sum(OpportunityInfo.estimated_amount), 0)
            ).where(*conditions)
            amount_result = await db.execute(amount_stmt)
            amount = float(amount_result.scalar())

            # 计算加权金额
            stage_weighted = amount * (stage.probability / 100)

            funnel_data.append({
                "stage_id": stage.id,
                "stage_name": stage.stage_name,
                "stage_order": stage.stage_order,
                "count": count,
                "amount": amount,
                "probability": stage.probability,
                "weighted_amount": stage_weighted,
            })

            total_count += count
            total_amount += amount
            weighted_amount += stage_weighted

        # 计算平均值
        avg_amount = total_amount / total_count if total_count > 0 else 0

        # 计算转化率
        conversion_rates, conversion_stages = await FunnelService._calculate_conversion_rates(
            db, base_conditions, stages
        )

        # 阶段健康度（用于漏斗优化）
        stage_health = await FunnelService._calculate_stage_health(
            db,
            owner_id=owner_id,
            stages=stages,
        )

        won_conditions = list(base_conditions)
        won_conditions.append(OpportunityInfo.status == "won")
        won_count = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(*won_conditions)
        )).scalar() or 0

        lost_conditions = list(base_conditions)
        lost_conditions.append(OpportunityInfo.status == "lost")
        lost_count = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(*lost_conditions)
        )).scalar() or 0

        return {
            "funnel": funnel_data,
            "summary": {
                "total_count": total_count,
                "total_amount": total_amount,
                "weighted_amount": weighted_amount,
                "avg_amount": avg_amount,
            },
            "conversion_rates": conversion_rates,
            "conversion_stages": conversion_stages,
            "stage_health": stage_health,
            "win_loss": {
                "won_count": won_count,
                "lost_count": lost_count,
            },
            "recommendations": FunnelService._build_recommendations(
                stages=stages,
                conversion_stages=conversion_stages,
                stage_health=stage_health,
            ),
        }

    @staticmethod
    async def _calculate_conversion_rates(
        db: AsyncSession,
        base_conditions: List,
        stages: List[StageDef],
    ) -> Tuple[Dict[str, float], List[dict]]:
        """计算转化率"""

        if len(stages) < 2:
            return {"overall": 0.0}, []

        conversion_rates: Dict[str, float] = {}
        conversion_items: List[dict] = []

        # 获取各阶段商机数
        stage_counts = {}
        for stage in stages:
            conditions = base_conditions + [
                OpportunityInfo.stage_id == stage.id,
                OpportunityInfo.status == "open",
            ]
            count_stmt = select(func.count(OpportunityInfo.id)).where(*conditions)
            count_result = await db.execute(count_stmt)
            stage_counts[stage.stage_order] = count_result.scalar() or 0

        # 计算相邻阶段转化率
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]

            current_count = stage_counts.get(current_stage.stage_order, 0)
            next_count = stage_counts.get(next_stage.stage_order, 0)

            if current_count > 0:
                rate = (next_count / current_count) * 100
            else:
                rate = 0

            key = f"{current_stage.stage_code}_to_{next_stage.stage_code}"
            rounded_rate = round(rate, 2)
            conversion_rates[key] = rounded_rate
            conversion_items.append({
                "key": key,
                "from_stage_code": current_stage.stage_code,
                "from_stage_name": current_stage.stage_name,
                "to_stage_code": next_stage.stage_code,
                "to_stage_name": next_stage.stage_name,
                "rate": rounded_rate,
                "from_count": current_count,
                "to_count": next_count,
            })

        # 计算整体转化率（从第一个阶段到最后一个阶段的转化率）
        first_stage_count = stage_counts.get(stages[0].stage_order, 0)
        last_stage_count = stage_counts.get(stages[-1].stage_order, 0)

        if first_stage_count > 0:
            conversion_rates["overall"] = round(
                (last_stage_count / first_stage_count) * 100, 2
            )
        else:
            conversion_rates["overall"] = 0

        return conversion_rates, conversion_items

    @staticmethod
    async def _calculate_stage_health(
        db: AsyncSession,
        owner_id: Optional[int],
        stages: List[StageDef],
    ) -> List[dict]:
        """计算阶段健康度：平均停留天数、停滞率"""
        result: List[dict] = []

        for stage in stages:
            conditions = [
                OpportunityInfo.stage_id == stage.id,
                OpportunityInfo.status == "open",
                OpportunityInfo.deleted_at.is_(None),
            ]
            if owner_id:
                conditions.append(OpportunityInfo.owner_id == owner_id)

            count = (await db.execute(
                select(func.count(OpportunityInfo.id)).where(*conditions)
            )).scalar() or 0

            avg_days = (await db.execute(
                select(func.coalesce(func.avg(OpportunityInfo.days_in_stage), 0)).where(*conditions)
            )).scalar() or 0

            stagnant_count = (await db.execute(
                select(func.count(OpportunityInfo.id)).where(
                    *conditions,
                    OpportunityInfo.is_stagnant.is_(True),
                )
            )).scalar() or 0

            stagnant_rate = round((stagnant_count / count) * 100, 2) if count else 0.0
            result.append({
                "stage_id": stage.id,
                "stage_name": stage.stage_name,
                "stage_code": stage.stage_code,
                "count": count,
                "avg_days_in_stage": round(float(avg_days), 2),
                "stagnant_count": stagnant_count,
                "stagnant_rate": stagnant_rate,
            })

        return result

    @staticmethod
    def _build_recommendations(
        stages: List[StageDef],
        conversion_stages: List[dict],
        stage_health: List[dict],
    ) -> List[dict]:
        """根据漏斗数据生成可执行建议（轻量规则版）"""
        recommendations: List[dict] = []
        stage_by_code = {stage.stage_code: stage for stage in stages}

        for item in conversion_stages:
            to_stage_code = item.get("to_stage_code")
            to_stage = stage_by_code.get(to_stage_code)
            target_rate = float(to_stage.probability) if to_stage else None
            actual_rate = float(item.get("rate") or 0.0)

            if target_rate is None:
                continue

            # 实际推进率比下一阶段概率低较多，提示补齐动作
            if actual_rate + 15 < target_rate:
                recommendations.append({
                    "type": "conversion_gap",
                    "priority": "high",
                    "title": f"{item.get('from_stage_name')} → {item.get('to_stage_name')} 转化偏低",
                    "action": (
                        f"当前转化率 {actual_rate:.1f}% 低于阶段目标 {target_rate:.1f}%。"
                        "建议补齐阶段判定标准、增加联合拜访，并在 7 天内完成重点商机复盘。"
                    ),
                })

        for health in stage_health:
            stage_code = health.get("stage_code")
            stage = stage_by_code.get(stage_code)
            if not stage:
                continue

            avg_days = float(health.get("avg_days_in_stage") or 0.0)
            stagnant_rate = float(health.get("stagnant_rate") or 0.0)
            duration_days = float(stage.duration_days or 0)

            if duration_days > 0 and avg_days > duration_days and stagnant_rate >= 15:
                recommendations.append({
                    "type": "stage_stagnation",
                    "priority": "high",
                    "title": f"{stage.stage_name} 阶段停滞风险",
                    "action": (
                        f"平均停留 {avg_days:.1f} 天，超出建议 {duration_days:.0f} 天，"
                        f"停滞率 {stagnant_rate:.1f}%。建议拆分周任务并设置阶段退出条件。"
                    ),
                })

        if not recommendations:
            recommendations.append({
                "type": "baseline",
                "priority": "medium",
                "title": "漏斗运行稳定",
                "action": "建议继续按阶段定义执行，并每周复核一次阶段停留和转化变化。",
            })

        return recommendations[:6]

    @staticmethod
    async def get_stage_distribution(
        db: AsyncSession,
        owner_id: Optional[int] = None,
    ) -> List[dict]:
        """获取阶段分布（用于看板视图）"""

        # 获取所有活跃阶段
        stages_stmt = select(StageDef).where(
            StageDef.is_active == True,
        ).order_by(StageDef.stage_order)
        stages_result = await db.execute(stages_stmt)
        stages = stages_result.scalars().all()

        result = []
        for stage in stages:
            conditions = [
                OpportunityInfo.stage_id == stage.id,
                OpportunityInfo.status == "open",
                OpportunityInfo.deleted_at.is_(None),
            ]
            if owner_id:
                conditions.append(OpportunityInfo.owner_id == owner_id)

            # 获取该阶段的商机
            opp_stmt = select(OpportunityInfo).where(*conditions).order_by(
                OpportunityInfo.priority.desc(),
                OpportunityInfo.updated_at.desc()
            )
            opp_result = await db.execute(opp_stmt)
            opportunities = opp_result.scalars().all()

            result.append({
                "stage_id": stage.id,
                "stage_name": stage.stage_name,
                "stage_order": stage.stage_order,
                "probability": stage.probability,
                "opportunities": [
                    {
                        "id": opp.id,
                        "opportunity_no": opp.opportunity_no,
                        "opportunity_name": opp.opportunity_name,
                        "customer_name": opp.customer_name,
                        "estimated_amount": float(opp.estimated_amount) if opp.estimated_amount else 0,
                        "priority": opp.priority,
                        "owner_name": opp.owner_name,
                        "days_in_stage": opp.days_in_stage,
                        "is_stagnant": opp.is_stagnant,
                    }
                    for opp in opportunities
                ],
            })

        return result
