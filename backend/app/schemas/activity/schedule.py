# 日程管理Schema
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class ScheduleBase(BaseModel):
    """日程基础模型"""
    schedule_title: str = Field(..., description="日程标题")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    is_all_day: bool = Field(False, description="是否全天")
    customer_id: Optional[int] = Field(None, description="客户ID")
    opportunity_id: Optional[int] = Field(None, description="商机ID")
    task_id: Optional[int] = Field(None, description="任务ID")
    schedule_type: Optional[str] = Field(None, description="日程类型")
    location: Optional[str] = Field(None, description="地点")
    description: Optional[str] = Field(None, description="描述")
    attendees: Optional[List[Dict[str, Any]]] = Field(default=[], description="参与人")
    reminder_minutes: Optional[List[int]] = Field(default=[], description="提醒时间点")
    is_recurring: bool = Field(False, description="是否重复")
    recurrence_rule: Optional[str] = Field(None, description="重复规则")


class ScheduleCreate(ScheduleBase):
    """创建日程"""
    pass


class ScheduleUpdate(BaseModel):
    """更新日程"""
    schedule_title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_all_day: Optional[bool] = None
    customer_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    task_id: Optional[int] = None
    schedule_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    attendees: Optional[List[Dict[str, Any]]] = None
    reminder_minutes: Optional[List[int]] = None
    status: Optional[str] = None


class ScheduleResponse(BaseModel):
    """日程响应"""
    id: int
    schedule_title: str
    start_time: datetime
    end_time: datetime
    is_all_day: bool
    customer_id: Optional[int]
    opportunity_id: Optional[int]
    task_id: Optional[int]
    schedule_type: Optional[str]
    location: Optional[str]
    description: Optional[str]
    attendees: Optional[List[Dict[str, Any]]]
    reminder_minutes: Optional[List[int]]
    is_recurring: bool
    recurrence_rule: Optional[str]
    status: str
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduleListResponse(BaseModel):
    """日程列表响应"""
    id: int
    schedule_title: str
    start_time: datetime
    end_time: datetime
    is_all_day: bool
    schedule_type: Optional[str]
    location: Optional[str]
    status: str

    class Config:
        from_attributes = True


class ActivityStatistics(BaseModel):
    """销售行为统计响应"""
    summary: Dict[str, Any]
    visit_trend: List[Dict[str, Any]]
    follow_type_distribution: Dict[str, int]
    task_completion_rate: float
    overdue_tasks: int
