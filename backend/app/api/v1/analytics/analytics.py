"""数据分析接口"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.core.utils.response import ApiResponse
from app.schemas.analytics import ReportCreateRequest
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/dashboard/home", response_model=ApiResponse)
async def dashboard_home(
    db: AsyncSession = Depends(get_db),
):
    """首页仪表盘"""
    data = await AnalyticsService.dashboard_home(db)
    return ApiResponse.success(data=data)


@router.get("/dashboard/sales", response_model=ApiResponse)
async def dashboard_sales(
    owner_id: Optional[int] = Query(default=None, description="负责人ID"),
    db: AsyncSession = Depends(get_db),
):
    """销售仪表盘"""
    data = await AnalyticsService.dashboard_sales(db, owner_id=owner_id)
    return ApiResponse.success(data=data)


@router.get("/dashboard/management", response_model=ApiResponse)
async def dashboard_management(
    db: AsyncSession = Depends(get_db),
):
    """管理驾驶舱"""
    data = await AnalyticsService.dashboard_management(db)
    return ApiResponse.success(data=data)


@router.get("/customers", response_model=ApiResponse)
async def customer_analysis(
    db: AsyncSession = Depends(get_db),
):
    """客户分析"""
    data = await AnalyticsService.customer_analysis(db)
    return ApiResponse.success(data=data)


@router.get("/opportunities", response_model=ApiResponse)
async def opportunity_analysis(
    db: AsyncSession = Depends(get_db),
):
    """商机分析"""
    data = await AnalyticsService.opportunity_analysis(db)
    return ApiResponse.success(data=data)


@router.get("/activities", response_model=ApiResponse)
async def activity_analysis(
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
):
    """销售活动分析"""
    data = await AnalyticsService.activity_analysis(db, start_date=start_date, end_date=end_date)
    return ApiResponse.success(data=data)


@router.get("/reports", response_model=ApiResponse)
async def list_reports(
    db: AsyncSession = Depends(get_db),
):
    """自定义报表列表"""
    reports = await AnalyticsService.list_reports(db)
    return ApiResponse.success(data=[{
        "id": r.id,
        "report_name": r.report_name,
        "report_code": r.report_code,
        "report_type": r.report_type,
        "config": r.config,
        "is_active": r.is_active,
        "created_at": r.created_at,
    } for r in reports])


@router.post("/reports", response_model=ApiResponse)
async def create_report(
    payload: ReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """创建自定义报表"""
    report = await AnalyticsService.create_report(
        db,
        payload=payload.model_dump(),
        user_id=user_id,
    )
    return ApiResponse.success(data={"id": report.id}, message="创建成功")


@router.get("/reports/{report_id}/execute", response_model=ApiResponse)
async def execute_report(
    report_id: int,
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
):
    """执行报表"""
    try:
        result = await AnalyticsService.execute_report(
            db,
            report_id=report_id,
            start_date=start_date,
            end_date=end_date,
        )
        return ApiResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/reports/{report_id}/export")
async def export_report(
    report_id: int,
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
):
    """导出报表"""
    try:
        content = await AnalyticsService.export_report_csv(
            db,
            report_id=report_id,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
