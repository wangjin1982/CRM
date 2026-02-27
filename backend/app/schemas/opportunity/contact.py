"""商机联系人关联Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class OpportunityContactRequest(BaseModel):
    """商机联系人关联请求"""

    contact_ids: list[int] = Field(..., description="联系人ID列表")
    role: Optional[str] = Field(None, description="角色")
    influence_level: Optional[int] = Field(None, ge=1, le=5, description="影响力等级")


class OpportunityContactResponse(BaseModel):
    """商机联系人关联响应"""

    id: int
    contact_id: int
    contact_name: Optional[str]
    contact_title: Optional[str]
    role: Optional[str]
    influence_level: Optional[int]
    is_primary: bool
