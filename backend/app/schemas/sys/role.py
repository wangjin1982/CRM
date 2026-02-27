"""角色Schema"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """角色基础模型"""

    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    code: str = Field(..., min_length=1, max_length=50, description="角色代码")
    description: Optional[str] = Field(None, description="角色描述")


class RoleCreate(RoleBase):
    """角色创建模型"""

    permission_ids: Optional[List[int]] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseModel):
    """角色更新模型"""

    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1, description="状态：1启用 0禁用")
    permission_ids: Optional[List[int]] = None


class RoleResponse(BaseModel):
    """角色响应模型"""

    id: int
    name: str
    code: str
    description: Optional[str]
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleListResponse(RoleResponse):
    """角色列表响应模型"""

    permissions: List[str] = Field(default_factory=list, description="权限列表")
    user_count: int = Field(default=0, description="用户数量")
