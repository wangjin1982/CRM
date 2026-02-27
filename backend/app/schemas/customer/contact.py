"""联系人相关Schema"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator


# ==================== 基础Schema ====================
class ContactBase(BaseModel):
    """联系人基础Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    title: Optional[str] = Field(None, max_length=100, description="职位")
    department: Optional[str] = Field(None, max_length=100, description="部门")
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$", description="性别")
    mobile: Optional[str] = Field(None, max_length=20, description="手机")
    phone: Optional[str] = Field(None, max_length=20, description="固话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    wechat: Optional[str] = Field(None, max_length=50, description="微信")
    is_decision_maker: bool = Field(False, description="是否决策人")
    is_influencer: bool = Field(False, description="是否影响者")
    influence_level: Optional[int] = Field(None, ge=1, le=5, description="影响力等级")
    relationship: Optional[str] = Field(None, max_length=50, description="关系类型")
    preference: Optional[str] = Field(None, description="沟通偏好")
    birthday: Optional[date] = Field(None, description="生日")
    hobbies: Optional[str] = Field(None, description="兴趣爱好")
    linkedin: Optional[str] = Field(None, max_length=200, description="LinkedIn")
    weibo: Optional[str] = Field(None, max_length=200, description="微博")
    is_primary: bool = Field(False, description="是否主要联系人")
    remarks: Optional[str] = Field(None, description="备注")


class ContactCreate(ContactBase):
    """创建联系人Schema"""
    pass


class ContactUpdate(ContactBase):
    """更新联系人Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)


# ==================== 响应Schema ====================
class ContactResponse(ContactBase):
    """联系人响应Schema"""
    id: int
    contact_no: str
    customer_id: int
    status: str
    contact_count: int = 0
    last_contact_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """联系人列表响应"""
    items: List[ContactResponse]
    total: int
