"""用户Schema"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模型"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    avatar: Optional[str] = Field(None, description="头像URL")
    department_id: Optional[int] = Field(None, description="部门ID")
    position: Optional[str] = Field(None, max_length=50, description="职位")


class UserCreate(UserBase):
    """用户创建模型"""

    password: str = Field(..., min_length=8, max_length=100, description="密码")
    role_ids: Optional[list[int]] = Field(default=[], description="角色ID列表")


class UserUpdate(BaseModel):
    """用户更新模型"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    department_id: Optional[int] = None
    position: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1, description="状态：1启用 0禁用")
    role_ids: Optional[list[int]] = None


class UserResponse(BaseModel):
    """用户响应模型"""

    id: int
    username: str
    email: str
    phone: Optional[str]
    real_name: Optional[str]
    avatar: Optional[str]
    status: int
    department_id: Optional[int]
    position: Optional[str]
    is_admin: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(UserResponse):
    """用户列表响应模型"""

    roles: list[str] = Field(default_factory=list, description="角色列表")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")
