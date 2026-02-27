"""AI模块请求Schema"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SmartCompleteRequest(BaseModel):
    """信息补全请求"""
    entity_type: str = Field(..., description="实体类型 customer/contact/opportunity")
    entity_id: int = Field(..., gt=0, description="实体ID")
    missing_fields: List[str] = Field(default_factory=list, description="缺失字段列表")
    context: Dict[str, Any] = Field(default_factory=dict, description="补充上下文")


class RiskBatchScanRequest(BaseModel):
    """批量风险扫描请求"""
    opportunity_ids: Optional[List[int]] = Field(default=None, description="商机ID列表，不传则扫描所有open商机")
    threshold_days: int = Field(default=30, ge=1, le=365, description="停滞阈值天数")


class NLQueryRequest(BaseModel):
    """自然语言查询请求"""
    query: str = Field(..., min_length=2, max_length=500, description="自然语言问题")


class AlertActionRequest(BaseModel):
    """预警状态变更请求"""
    note: Optional[str] = Field(default=None, max_length=500, description="备注")


class AIConfigUpdate(BaseModel):
    """AI配置更新"""
    model_config = ConfigDict(protected_namespaces=())

    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=32000)
    timeout_seconds: Optional[int] = Field(default=None, ge=1, le=180)
    is_enabled: Optional[bool] = None
    remark: Optional[str] = None


class PromptTemplateCreate(BaseModel):
    """提示词模板创建"""
    template_code: str = Field(..., min_length=2, max_length=100)
    template_name: str = Field(..., min_length=2, max_length=100)
    scene: str = Field(..., min_length=2, max_length=100)
    content: str = Field(..., min_length=5)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class PromptTemplateUpdate(BaseModel):
    """提示词模板更新"""
    template_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    scene: Optional[str] = Field(default=None, min_length=2, max_length=100)
    content: Optional[str] = Field(default=None, min_length=5)
    input_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CustomerEnrichRequest(BaseModel):
    """客户属性补全请求"""

    target_fields: Optional[List[str]] = Field(
        default=None,
        description="目标字段列表，不传则自动识别缺失字段",
    )
    overwrite: bool = Field(default=False, description="是否覆盖已有字段")


class CustomerEnrichApplyRequest(BaseModel):
    """客户属性补全确认写入请求"""

    request_id: Optional[str] = Field(default=None, description="补全预览请求ID")
    updates: Dict[str, Any] = Field(default_factory=dict, description="确认写入的字段和值")
