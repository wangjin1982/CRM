"""客户交互记录相关Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class InteractionBase(BaseModel):
    """交互记录基础Schema"""
    contact_id: Optional[int] = Field(None, description="联系人ID")
    interaction_type: str = Field(..., pattern="^(call|email|visit|wechat|other)$", description="交互类型")
    direction: Optional[str] = Field(None, pattern="^(inbound|outbound)$", description="方向")
    subject: Optional[str] = Field(None, max_length=200, description="主题")
    content: Optional[str] = Field(None, description="内容")
    duration: Optional[int] = Field(None, ge=0, description="时长(秒)")
    attachments: Optional[List[str]] = Field(default_factory=list, description="附件URL列表")
    next_follow_at: Optional[datetime] = Field(None, description="下次跟进时间")
    next_follow_note: Optional[str] = Field(None, description="下次跟进备注")


class InteractionCreate(InteractionBase):
    """创建交互记录Schema"""
    pass


class InteractionResponse(InteractionBase):
    """交互记录响应Schema"""
    id: int
    customer_id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionListResponse(BaseModel):
    """交互记录列表响应"""
    items: List[InteractionResponse]
    total: int
    page: int
    page_size: int
