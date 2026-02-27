# 任务管理Schema
from typing import Optional, List
from datetime import date, time, datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """任务基础模型"""
    task_title: str = Field(..., description="任务标题")
    customer_id: Optional[int] = Field(None, description="客户ID")
    opportunity_id: Optional[int] = Field(None, description="商机ID")
    related_object_type: Optional[str] = Field(None, description="关联对象类型")
    related_object_id: Optional[int] = Field(None, description="关联对象ID")
    task_type: str = Field(..., description="任务类型")
    task_category: Optional[str] = Field(None, description="任务分类")
    due_date: date = Field(..., description="截止日期")
    due_time: Optional[time] = Field(None, description="截止时间")
    reminder_time: Optional[datetime] = Field(None, description="提醒时间")
    duration: Optional[int] = Field(None, description="预计时长(分钟)")
    priority: str = Field("medium", description="优先级: high/medium/low")
    description: Optional[str] = Field(None, description="任务描述")
    location: Optional[str] = Field(None, description="地点")
    notes: Optional[str] = Field(None, description="备注")
    is_recurring: bool = Field(False, description="是否重复任务")
    recurrence_rule: Optional[str] = Field(None, description="重复规则")
    parent_task_id: Optional[int] = Field(None, description="父任务ID")
    assigned_to: int = Field(..., description="分配给")
    attachments: Optional[List[str]] = Field(default=[], description="附件URL")


class TaskCreate(TaskBase):
    """创建任务"""
    pass


class TaskUpdate(BaseModel):
    """更新任务"""
    task_title: Optional[str] = None
    customer_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    task_type: Optional[str] = None
    task_category: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    reminder_time: Optional[datetime] = None
    duration: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[List[str]] = None


class TaskCompleteRequest(BaseModel):
    """完成任务请求"""
    completion_note: Optional[str] = Field(None, description="完成备注")


class TaskCancelRequest(BaseModel):
    """取消任务请求"""
    cancel_reason: Optional[str] = Field(None, description="取消原因")


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    task_no: str
    task_title: str
    customer_id: Optional[int]
    opportunity_id: Optional[int]
    related_object_type: Optional[str]
    related_object_id: Optional[int]
    task_type: str
    task_category: Optional[str]
    due_date: date
    due_time: Optional[time]
    reminder_time: Optional[datetime]
    duration: Optional[int]
    priority: str
    status: str
    description: Optional[str]
    location: Optional[str]
    notes: Optional[str]
    completed_at: Optional[datetime]
    completion_note: Optional[str]
    is_recurring: bool
    recurrence_rule: Optional[str]
    parent_task_id: Optional[int]
    assigned_to: Optional[int]
    created_by: Optional[int]
    attachments: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""
    id: int
    task_no: str
    task_title: str
    task_type: str
    priority: str
    status: str
    due_date: date
    due_time: Optional[time]
    is_overdue: bool = False
    assigned_to: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
