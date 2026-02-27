"""数据分析服务"""
from __future__ import annotations

import csv
import io
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import FollowRecord, TaskInfo, VisitRecord
from app.models.analytics import ReportDef
from app.models.customer import CustomerInfo
from app.models.opportunity import OpportunityInfo, StageDef


class AnalyticsService:
    """数据分析服务类"""

    @staticmethod
    async def dashboard_home(db: AsyncSession) -> Dict[str, Any]:
        """首页仪表盘"""
        total_customers = (await db.execute(
            select(func.count(CustomerInfo.id)).where(CustomerInfo.deleted_at.is_(None))
        )).scalar() or 0
        total_open_opps = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.status == "open",
            )
        )).scalar() or 0
        total_open_amount = (await db.execute(
            select(func.coalesce(func.sum(OpportunityInfo.estimated_amount), 0)).where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.status == "open",
            )
        )).scalar() or 0
        high_risk_count = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.status == "open",
                OpportunityInfo.risk_level == "high",
            )
        )).scalar() or 0

        return {
            "summary": {
                "total_customers": total_customers,
                "total_open_opportunities": total_open_opps,
                "total_open_amount": float(total_open_amount),
                "high_risk_opportunities": high_risk_count,
            },
            "updated_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    async def dashboard_sales(
        db: AsyncSession,
        owner_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """销售仪表盘"""
        conditions = [
            OpportunityInfo.deleted_at.is_(None),
            OpportunityInfo.status == "open",
        ]
        if owner_id:
            conditions.append(OpportunityInfo.owner_id == owner_id)

        stage_stats = (await db.execute(
            select(
                OpportunityInfo.stage_name,
                func.count(OpportunityInfo.id),
                func.coalesce(func.sum(OpportunityInfo.estimated_amount), 0),
            )
            .where(and_(*conditions))
            .group_by(OpportunityInfo.stage_name)
            .order_by(func.count(OpportunityInfo.id).desc())
        )).all()

        stage_distribution = [
            {
                "stage_name": row[0] or "未知",
                "count": row[1],
                "amount": float(row[2] or 0),
            }
            for row in stage_stats
        ]

        this_month = date.today().replace(day=1)
        monthly_new = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                OpportunityInfo.deleted_at.is_(None),
                func.date(OpportunityInfo.created_at) >= this_month,
                *( [OpportunityInfo.owner_id == owner_id] if owner_id else [] ),
            )
        )).scalar() or 0

        won_count = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.status == "won",
                *( [OpportunityInfo.owner_id == owner_id] if owner_id else [] ),
            )
        )).scalar() or 0
        total_closed = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.status.in_(["won", "lost"]),
                *( [OpportunityInfo.owner_id == owner_id] if owner_id else [] ),
            )
        )).scalar() or 0
        win_rate = round((won_count / total_closed * 100), 2) if total_closed else 0

        return {
            "stage_distribution": stage_distribution,
            "monthly_new_opportunities": monthly_new,
            "win_rate": win_rate,
        }

    @staticmethod
    async def dashboard_management(db: AsyncSession) -> Dict[str, Any]:
        """管理驾驶舱"""
        sales = await AnalyticsService.dashboard_sales(db)
        home = await AnalyticsService.dashboard_home(db)

        top_owners = (await db.execute(
            select(
                OpportunityInfo.owner_id,
                OpportunityInfo.owner_name,
                func.count(OpportunityInfo.id),
                func.coalesce(func.sum(OpportunityInfo.estimated_amount), 0),
            )
            .where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.status == "open",
            )
            .group_by(OpportunityInfo.owner_id, OpportunityInfo.owner_name)
            .order_by(func.coalesce(func.sum(OpportunityInfo.estimated_amount), 0).desc())
            .limit(10)
        )).all()

        return {
            "summary": home["summary"],
            "sales": sales,
            "owner_ranking": [
                {
                    "owner_id": row[0],
                    "owner_name": row[1],
                    "opportunity_count": row[2],
                    "amount": float(row[3] or 0),
                }
                for row in top_owners
            ],
        }

    @staticmethod
    async def customer_analysis(db: AsyncSession) -> Dict[str, Any]:
        """客户分析"""
        level_stats = (await db.execute(
            select(CustomerInfo.level, func.count(CustomerInfo.id))
            .where(CustomerInfo.deleted_at.is_(None))
            .group_by(CustomerInfo.level)
        )).all()
        industry_stats = (await db.execute(
            select(CustomerInfo.industry, func.count(CustomerInfo.id))
            .where(CustomerInfo.deleted_at.is_(None))
            .group_by(CustomerInfo.industry)
            .order_by(func.count(CustomerInfo.id).desc())
            .limit(10)
        )).all()

        return {
            "level_distribution": {row[0] or "未知": row[1] for row in level_stats},
            "top_industries": [{"industry": row[0] or "未知", "count": row[1]} for row in industry_stats],
        }

    @staticmethod
    async def opportunity_analysis(db: AsyncSession) -> Dict[str, Any]:
        """商机分析"""
        status_stats = (await db.execute(
            select(OpportunityInfo.status, func.count(OpportunityInfo.id))
            .where(OpportunityInfo.deleted_at.is_(None))
            .group_by(OpportunityInfo.status)
        )).all()
        amount_by_status = (await db.execute(
            select(OpportunityInfo.status, func.coalesce(func.sum(OpportunityInfo.estimated_amount), 0))
            .where(OpportunityInfo.deleted_at.is_(None))
            .group_by(OpportunityInfo.status)
        )).all()
        stagnant_count = (await db.execute(
            select(func.count(OpportunityInfo.id)).where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.is_stagnant.is_(True),
                OpportunityInfo.status == "open",
            )
        )).scalar() or 0

        return {
            "status_distribution": {row[0] or "unknown": row[1] for row in status_stats},
            "amount_by_status": {row[0] or "unknown": float(row[1] or 0) for row in amount_by_status},
            "stagnant_count": stagnant_count,
        }

    @staticmethod
    async def activity_analysis(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """销售行为分析"""
        end_date = end_date or date.today()
        start_date = start_date or (end_date - timedelta(days=29))

        visit_count = (await db.execute(
            select(func.count(VisitRecord.id)).where(
                VisitRecord.visit_date >= start_date,
                VisitRecord.visit_date <= end_date,
            )
        )).scalar() or 0

        follow_count = (await db.execute(
            select(func.count(FollowRecord.id)).where(
                func.date(FollowRecord.created_at) >= start_date,
                func.date(FollowRecord.created_at) <= end_date,
            )
        )).scalar() or 0

        task_total = (await db.execute(
            select(func.count(TaskInfo.id)).where(
                TaskInfo.due_date >= start_date,
                TaskInfo.due_date <= end_date,
            )
        )).scalar() or 0

        task_completed = (await db.execute(
            select(func.count(TaskInfo.id)).where(
                TaskInfo.due_date >= start_date,
                TaskInfo.due_date <= end_date,
                TaskInfo.status == "completed",
            )
        )).scalar() or 0
        completion_rate = round((task_completed / task_total * 100), 2) if task_total else 0

        return {
            "visit_count": visit_count,
            "follow_count": follow_count,
            "task_total": task_total,
            "task_completed": task_completed,
            "task_completion_rate": completion_rate,
            "range": {"start_date": str(start_date), "end_date": str(end_date)},
        }

    @staticmethod
    async def list_reports(db: AsyncSession) -> List[ReportDef]:
        """报表列表"""
        return list((await db.execute(
            select(ReportDef).order_by(ReportDef.created_at.desc())
        )).scalars().all())

    @staticmethod
    async def create_report(
        db: AsyncSession,
        *,
        payload: Dict[str, Any],
        user_id: int,
    ) -> ReportDef:
        """创建报表"""
        report = ReportDef(created_by=user_id, **payload)
        db.add(report)
        await db.flush()
        return report

    @staticmethod
    async def execute_report(
        db: AsyncSession,
        report_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """执行报表（当前支持内置类型）"""
        report = (await db.execute(
            select(ReportDef).where(ReportDef.id == report_id)
        )).scalar_one_or_none()
        if not report:
            raise ValueError("报表不存在")

        report_type = report.report_type
        if report_type == "customer":
            data = await AnalyticsService.customer_analysis(db)
        elif report_type == "opportunity":
            data = await AnalyticsService.opportunity_analysis(db)
        elif report_type == "activity":
            data = await AnalyticsService.activity_analysis(db, start_date, end_date)
        elif report_type == "dashboard_home":
            data = await AnalyticsService.dashboard_home(db)
        else:
            data = {"message": "该报表类型暂未内置执行器", "config": report.config}

        return {
            "report": {
                "id": report.id,
                "name": report.report_name,
                "code": report.report_code,
                "type": report.report_type,
            },
            "data": data,
        }

    @staticmethod
    async def export_report_csv(
        db: AsyncSession,
        report_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> bytes:
        """导出报表CSV"""
        result = await AnalyticsService.execute_report(db, report_id, start_date, end_date)
        report_info = result["report"]
        payload = result["data"]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["report_name", report_info["name"]])
        writer.writerow(["report_code", report_info["code"]])
        writer.writerow(["generated_at", datetime.utcnow().isoformat()])
        writer.writerow([])
        writer.writerow(["key", "value"])

        def write_object(prefix: str, value: Any):
            if isinstance(value, dict):
                for k, v in value.items():
                    write_object(f"{prefix}.{k}" if prefix else str(k), v)
            elif isinstance(value, list):
                for idx, v in enumerate(value):
                    write_object(f"{prefix}[{idx}]", v)
            else:
                writer.writerow([prefix, value])

        write_object("", payload)
        return output.getvalue().encode("utf-8")
