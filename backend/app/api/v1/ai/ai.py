"""AI增强接口"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.core.utils.response import ApiResponse
from app.schemas.ai import (
    AIConfigUpdate,
    AlertActionRequest,
    CustomerEnrichApplyRequest,
    CustomerEnrichRequest,
    NLQueryRequest,
    PromptTemplateCreate,
    PromptTemplateUpdate,
    RiskBatchScanRequest,
    SmartCompleteRequest,
)
from app.services.ai import AIService

router = APIRouter()


@router.post("/complete", response_model=ApiResponse)
async def smart_complete(
    payload: SmartCompleteRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """信息智能补全"""
    try:
        data = await AIService.smart_complete(
            db,
            entity_type=payload.entity_type,
            entity_id=payload.entity_id,
            missing_fields=payload.missing_fields,
            context=payload.context,
            user_id=user_id,
        )
        return ApiResponse.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/complete/{task_id}", response_model=ApiResponse)
async def get_complete_status(task_id: str):
    """补全状态查询（当前为同步，固定返回完成）"""
    return ApiResponse.success(data={"task_id": task_id, "status": "completed"})


@router.post("/risk/opportunity/{opportunity_id}", response_model=ApiResponse)
async def analyze_opportunity_risk(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """商机风险分析"""
    try:
        data = await AIService.analyze_opportunity_risk(
            db,
            opportunity_id=opportunity_id,
            user_id=user_id,
        )
        return ApiResponse.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/risk/batch-scan", response_model=ApiResponse)
async def batch_risk_scan(
    payload: RiskBatchScanRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """批量风险扫描"""
    data = await AIService.batch_risk_scan(
        db,
        opportunity_ids=payload.opportunity_ids,
        threshold_days=payload.threshold_days,
        user_id=user_id,
    )
    return ApiResponse.success(data=data)


@router.post("/analyze/visit/{visit_id}", response_model=ApiResponse)
async def summarize_visit(
    visit_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """拜访记录AI总结"""
    try:
        data = await AIService.summarize_visit(db, visit_id=visit_id, user_id=user_id)
        return ApiResponse.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/analyze/funnel", response_model=ApiResponse)
async def analyze_funnel(
    owner_id: Optional[int] = Query(default=None, description="负责人ID"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """销售漏斗智能分析"""
    data = await AIService.analyze_funnel(db, owner_id=owner_id, user_id=user_id)
    return ApiResponse.success(data=data)


@router.post("/query", response_model=ApiResponse)
async def natural_language_query(
    payload: NLQueryRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """自然语言查询"""
    data = await AIService.natural_language_query(db, query=payload.query, user_id=user_id)
    return ApiResponse.success(data=data)


@router.get("/alerts", response_model=ApiResponse)
async def list_alerts(
    alert_status: Optional[str] = Query(default=None, alias="status"),
    level: Optional[str] = None,
    related_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """预警列表"""
    alerts = await AIService.list_alerts(
        db,
        status=alert_status,
        level=level,
        related_type=related_type,
    )
    return ApiResponse.success(data=[{
        "id": a.id,
        "alert_type": a.alert_type,
        "alert_level": a.alert_level,
        "related_type": a.related_type,
        "related_id": a.related_id,
        "title": a.title,
        "content": a.content,
        "suggestion": a.suggestion,
        "status": a.status,
        "created_at": a.created_at,
    } for a in alerts])


@router.post("/alerts/{alert_id}/ack", response_model=ApiResponse)
async def acknowledge_alert(
    alert_id: int,
    payload: AlertActionRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """确认预警"""
    alert = await AIService.acknowledge_alert(db, alert_id=alert_id, user_id=user_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预警不存在")
    return ApiResponse.success(message="预警已确认")


@router.post("/alerts/{alert_id}/resolve", response_model=ApiResponse)
async def resolve_alert(
    alert_id: int,
    payload: AlertActionRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """解决预警"""
    alert = await AIService.resolve_alert(db, alert_id=alert_id, user_id=user_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预警不存在")
    return ApiResponse.success(message="预警已解决")


@router.get("/config", response_model=ApiResponse)
async def get_ai_config(
    db: AsyncSession = Depends(get_db),
):
    """获取AI配置"""
    config = await AIService.get_config(db)
    api_key_masked = AIService._mask_api_key(config.api_key)
    return ApiResponse.success(data={
        "id": config.id,
        "provider": config.provider,
        "model_name": config.model_name,
        "api_base": config.api_base,
        "has_api_key": bool(config.api_key),
        "api_key_masked": api_key_masked,
        "temperature": float(config.temperature) if config.temperature is not None else None,
        "max_tokens": config.max_tokens,
        "timeout_seconds": config.timeout_seconds,
        "is_enabled": config.is_enabled,
        "remark": config.remark,
    })


@router.put("/config", response_model=ApiResponse)
async def update_ai_config(
    payload: AIConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新AI配置"""
    config = await AIService.update_config(db, payload.model_dump(exclude_unset=True))
    return ApiResponse.success(data={"id": config.id}, message="更新成功")


@router.post("/customers/{customer_id}/enrich", response_model=ApiResponse)
async def enrich_customer_profile(
    customer_id: int,
    payload: CustomerEnrichRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """按客户名称补全客户空缺属性"""
    try:
        data = await AIService.enrich_customer_profile(
            db,
            customer_id=customer_id,
            target_fields=payload.target_fields,
            overwrite=payload.overwrite,
            user_id=user_id,
        )
        return ApiResponse.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/customers/{customer_id}/enrich/preview", response_model=ApiResponse)
async def preview_customer_enrich_profile(
    customer_id: int,
    payload: CustomerEnrichRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """客户属性补全预览（不写入）"""
    try:
        data = await AIService.preview_customer_enrich_profile(
            db,
            customer_id=customer_id,
            target_fields=payload.target_fields,
            overwrite=payload.overwrite,
            user_id=user_id,
        )
        return ApiResponse.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/customers/{customer_id}/enrich/apply", response_model=ApiResponse)
async def apply_customer_enrich_profile(
    customer_id: int,
    payload: CustomerEnrichApplyRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """客户属性补全确认写入"""
    try:
        data = await AIService.apply_customer_enrich_profile(
            db,
            customer_id=customer_id,
            updates=payload.updates,
            request_id=payload.request_id,
            user_id=user_id,
        )
        return ApiResponse.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/prompts", response_model=ApiResponse)
async def list_prompt_templates(
    scene: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """提示词模板列表"""
    templates = await AIService.list_prompt_templates(db, scene=scene)
    return ApiResponse.success(data=[{
        "id": t.id,
        "template_code": t.template_code,
        "template_name": t.template_name,
        "scene": t.scene,
        "content": t.content,
        "input_schema": t.input_schema,
        "is_active": t.is_active,
    } for t in templates])


@router.post("/prompts", response_model=ApiResponse)
async def create_prompt_template(
    payload: PromptTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建提示词模板"""
    template = await AIService.create_prompt_template(db, payload.model_dump())
    return ApiResponse.success(data={"id": template.id}, message="创建成功")


@router.put("/prompts/{template_id}", response_model=ApiResponse)
async def update_prompt_template(
    template_id: int,
    payload: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新提示词模板"""
    template = await AIService.update_prompt_template(
        db, template_id, payload.model_dump(exclude_unset=True)
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")
    return ApiResponse.success(message="更新成功")
