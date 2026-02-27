# 拜访记录Schema
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class VisitBase(BaseModel):
    """拜访记录基础模型"""
    visit_type: str = Field(..., description="拜访类型: onsite/online")
    customer_id: int = Field(..., description="客户ID")
    opportunity_id: Optional[int] = Field(None, description="商机ID")
    contact_ids: Optional[List[int]] = Field(default=[], description="参与联系人ID列表")
    visit_date: date = Field(..., description="拜访日期")
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    duration: Optional[int] = Field(None, description="时长(分钟)")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    address: Optional[str] = Field(None, description="详细地址")
    latitude: Optional[Decimal] = Field(None, description="纬度")
    longitude: Optional[Decimal] = Field(None, description="经度")
    purpose: Optional[str] = Field(None, description="拜访目的")
    content: Optional[str] = Field(None, description="拜访内容")
    customer_feedback: Optional[str] = Field(None, description="客户反馈")
    next_plan: Optional[str] = Field(None, description="下一步计划")
    result_type: Optional[str] = Field(None, description="结果类型")
    interest_level: Optional[int] = Field(None, ge=1, le=5, description="兴趣等级")
    purchase_intent: Optional[int] = Field(None, ge=1, le=5, description="采购意向")
    photos: Optional[List[str]] = Field(default=[], description="照片URL")
    attachments: Optional[List[str]] = Field(default=[], description="附件URL")
    expense_amount: Optional[Decimal] = Field(None, description="拜访费用")
    expense_desc: Optional[str] = Field(None, description="费用说明")


class VisitCreate(VisitBase):
    """创建拜访记录"""
    pass


class VisitUpdate(BaseModel):
    """更新拜访记录"""
    visit_type: Optional[str] = None
    customer_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    contact_ids: Optional[List[int]] = None
    visit_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: Optional[int] = None
    province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    purpose: Optional[str] = None
    content: Optional[str] = None
    customer_feedback: Optional[str] = None
    next_plan: Optional[str] = None
    result_type: Optional[str] = None
    interest_level: Optional[int] = None
    purchase_intent: Optional[int] = None
    photos: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    expense_amount: Optional[Decimal] = None
    expense_desc: Optional[str] = None


class VisitResponse(BaseModel):
    """拜访记录响应"""
    id: int
    visit_no: str
    visit_type: str
    customer_id: int
    customer_name: Optional[str]
    opportunity_id: Optional[int]
    contact_ids: Optional[List[int]]
    participant_names: Optional[str]
    visit_date: date
    start_time: Optional[time]
    end_time: Optional[time]
    duration: Optional[int]
    province: Optional[str]
    city: Optional[str]
    address: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    purpose: Optional[str]
    content: Optional[str]
    customer_feedback: Optional[str]
    next_plan: Optional[str]
    result_type: Optional[str]
    interest_level: Optional[int]
    purchase_intent: Optional[int]
    photos: Optional[List[str]]
    attachments: Optional[List[str]]
    expense_amount: Optional[Decimal]
    expense_desc: Optional[str]
    ai_summary: Optional[str]
    ai_action_items: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VisitListResponse(BaseModel):
    """拜访记录列表响应"""
    id: int
    visit_no: str
    visit_type: str
    customer_id: int
    customer_name: Optional[str]
    visit_date: date
    result_type: Optional[str]
    interest_level: Optional[int]
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
