"""销售阶段Schema"""
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


class StageDefBase(BaseModel):
    """销售阶段基础模型"""

    stage_name: str = Field(..., description="阶段名称")
    stage_code: str = Field(..., description="阶段代码")
    stage_order: int = Field(..., description="阶段序号")
    stage_type: str = Field(default="normal", description="阶段类型")
    probability: int = Field(default=0, description="成交概率")
    weight: Optional[float] = Field(None, description="漏斗权重(0-1)")
    duration_days: Optional[int] = Field(None, description="建议停留天数")
    description: Optional[str] = Field(None, description="阶段描述")
    internal_code: Optional[str] = Field(None, description="内部简称")
    customer_journey: Optional[str] = Field(None, description="客户旅程")
    technical_support: Optional[str] = Field(None, description="技术支持重点工作")
    sales_process: Optional[str] = Field(None, description="销售重点工作")
    stage_criteria: Optional[str] = Field(None, description="阶段判定标准")


class StageDefCreate(StageDefBase):
    """销售阶段创建模型"""
    pass


class StageDefUpdate(BaseModel):
    """销售阶段更新模型"""

    stage_name: Optional[str] = None
    stage_code: Optional[str] = None
    stage_order: Optional[int] = None
    probability: Optional[int] = None
    weight: Optional[float] = None
    duration_days: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    internal_code: Optional[str] = None
    customer_journey: Optional[str] = None
    technical_support: Optional[str] = None
    sales_process: Optional[str] = None
    stage_criteria: Optional[str] = None


class StageDefResponse(StageDefBase):
    """销售阶段响应模型"""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StageChangeRequest(BaseModel):
    """阶段变更请求"""

    to_stage_id: int = Field(..., description="目标阶段ID")
    notes: Optional[str] = Field(None, description="变更说明")


class OpportunityWonRequest(BaseModel):
    """赢单请求"""

    actual_amount: float = Field(..., description="实际成交金额")
    actual_close_date: date = Field(..., description="实际成交日期")
    notes: Optional[str] = Field(None, description="备注")


class OpportunityLostRequest(BaseModel):
    """输单请求"""

    lost_reason: str = Field(..., description="流失原因")
    competitor: Optional[str] = Field(None, description="竞争对手")
    notes: Optional[str] = Field(None, description="备注")


class StageHistoryResponse(BaseModel):
    """阶段历史响应"""

    id: int
    from_stage_id: Optional[int] = None
    from_stage_name: Optional[str] = None
    to_stage_id: int
    to_stage_name: str
    stage_duration: Optional[int] = None
    changed_at: datetime
    changed_by: Optional[int] = None
    changed_by_name: Optional[str] = None
    notes: Optional[str] = None
