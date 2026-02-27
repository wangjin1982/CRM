"""商机信息Schema"""
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field


class OpportunityBase(BaseModel):
    """商机基础模型"""

    opportunity_name: str = Field(..., min_length=1, max_length=200, description="商机名称")
    customer_id: int = Field(..., description="客户ID")
    primary_contact_id: Optional[int] = Field(None, description="主要联系人ID")
    estimated_amount: Optional[Decimal] = Field(None, description="预估金额")
    currency: str = Field(default="CNY", description="币种")
    stage_id: int = Field(..., description="阶段ID")
    expected_close_date: Optional[date] = Field(None, description="预计成交日期")
    win_probability: int = Field(default=50, ge=0, le=100, description="成交概率")
    priority: str = Field(default="medium", description="优先级")
    owner_id: Optional[int] = Field(None, description="负责人ID")
    lead_source: Optional[str] = Field(None, description="商机来源")
    description: Optional[str] = Field(None, description="商机描述")
    tags: Optional[List[str]] = Field(default=[], description="标签")


class OpportunityCreate(OpportunityBase):
    """商机创建模型"""

    products: Optional[List[dict]] = Field(default=[], description="产品信息")


class OpportunityUpdate(BaseModel):
    """商机更新模型"""

    opportunity_name: Optional[str] = None
    primary_contact_id: Optional[int] = None
    estimated_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    expected_close_date: Optional[date] = None
    win_probability: Optional[int] = None
    priority: Optional[str] = None
    owner_id: Optional[int] = None
    lead_source: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    products: Optional[List[dict]] = None


class OpportunityResponse(BaseModel):
    """商机响应模型"""

    id: int
    opportunity_no: str
    opportunity_name: str
    customer_id: int
    customer_name: Optional[str]
    primary_contact_id: Optional[int]
    estimated_amount: Optional[Decimal]
    actual_amount: Optional[Decimal]
    currency: str
    stage_id: int
    stage_name: Optional[str]
    stage_order: Optional[int]
    expected_close_date: Optional[date]
    actual_close_date: Optional[date]
    win_probability: int
    priority: str
    owner_id: Optional[int]
    owner_name: Optional[str]
    status: str
    risk_level: Optional[str]
    days_in_stage: int
    is_stagnant: bool
    activity_count: int
    last_activity_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OpportunityListResponse(OpportunityResponse):
    """商机列表响应模型"""

    stage_probability: Optional[int] = None
    customer_name: Optional[str] = None


class OpportunityTransferRequest(BaseModel):
    """商机转移请求"""

    to_user_id: int = Field(..., description="目标用户ID")
    remark: Optional[str] = Field(None, description="转移备注")


class OpportunityPageParams(BaseModel):
    """商机分页参数"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="关键词")
    customer_id: Optional[int] = Field(None, description="客户ID")
    stage_id: Optional[int] = Field(None, description="阶段ID")
    status: Optional[str] = Field(None, description="状态")
    owner_id: Optional[int] = Field(None, description="负责人ID")
    priority: Optional[str] = Field(None, description="优先级")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    min_amount: Optional[Decimal] = Field(None, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, description="最大金额")
    is_stagnant: Optional[bool] = Field(None, description="是否停滞")
