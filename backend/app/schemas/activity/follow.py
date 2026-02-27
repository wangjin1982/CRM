# 跟进记录Schema
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class FollowBase(BaseModel):
    """跟进记录基础模型"""
    customer_id: int = Field(..., description="客户ID")
    opportunity_id: Optional[int] = Field(None, description="商机ID")
    contact_id: Optional[int] = Field(None, description="联系人ID")
    follow_type: str = Field(..., description="跟进类型: call/email/wechat/message/other")
    follow_direction: Optional[str] = Field(None, description="方向: inbound/outbound")
    subject: Optional[str] = Field(None, description="主题")
    content: Optional[str] = Field(None, description="内容")
    call_duration: Optional[int] = Field(None, description="通话时长(秒)")
    call_recording_url: Optional[str] = Field(None, description="录音URL")
    email_from: Optional[str] = Field(None, description="发件人")
    email_to: Optional[List[str]] = Field(None, description="收件人")
    email_cc: Optional[List[str]] = Field(None, description="抄送")
    email_subject: Optional[str] = Field(None, description="邮件主题")
    email_body: Optional[str] = Field(None, description="邮件正文")
    response: Optional[str] = Field(None, description="对方回应")
    result: Optional[str] = Field(None, description="结果评估")
    next_follow_date: Optional[date] = Field(None, description="下次跟进日期")
    next_follow_note: Optional[str] = Field(None, description="下次跟进备注")
    attachments: Optional[List[str]] = Field(default=[], description="附件URL")


class FollowCreate(FollowBase):
    """创建跟进记录"""
    pass


class FollowUpdate(BaseModel):
    """更新跟进记录"""
    follow_type: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    call_duration: Optional[int] = None
    response: Optional[str] = None
    result: Optional[str] = None
    next_follow_date: Optional[date] = None
    next_follow_note: Optional[str] = None
    attachments: Optional[List[str]] = None


class FollowResponse(BaseModel):
    """跟进记录响应"""
    id: int
    follow_no: str
    customer_id: int
    customer_name: Optional[str]
    opportunity_id: Optional[int]
    contact_id: Optional[int]
    follow_type: str
    follow_direction: Optional[str]
    subject: Optional[str]
    content: Optional[str]
    call_duration: Optional[int]
    call_recording_url: Optional[str]
    email_from: Optional[str]
    email_to: Optional[List[str]]
    email_cc: Optional[List[str]]
    email_subject: Optional[str]
    email_body: Optional[str]
    response: Optional[str]
    result: Optional[str]
    next_follow_date: Optional[date]
    next_follow_note: Optional[str]
    attachments: Optional[List[str]]
    ai_summary: Optional[str]
    ai_sentiment: Optional[str]
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class FollowListResponse(BaseModel):
    """跟进记录列表响应"""
    id: int
    follow_no: str
    customer_id: int
    customer_name: Optional[str]
    contact_id: Optional[int]
    follow_type: str
    subject: Optional[str]
    result: Optional[str]
    next_follow_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True
