"""客户标签相关Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签基础Schema"""
    tag_name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    tag_color: Optional[str] = Field(None, max_length=20, description="标签颜色")
    tag_type: str = Field("custom", pattern="^(system|custom)$", description="标签类型")
    sort_order: int = Field(0, description="排序")


class TagCreate(TagBase):
    """创建标签Schema"""
    pass


class TagUpdate(TagBase):
    """更新标签Schema"""
    tag_name: Optional[str] = Field(None, min_length=1, max_length=50)


class TagResponse(TagBase):
    """标签响应Schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """标签列表响应"""
    items: List[TagResponse]
    total: int
