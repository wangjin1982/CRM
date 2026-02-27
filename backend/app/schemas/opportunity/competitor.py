"""竞争对手Schema"""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class CompetitorCreate(BaseModel):
    """竞争对手创建请求"""

    competitor_name: str = Field(..., description="竞争对手名称")
    strength: Optional[str] = Field(None, description="优势")
    weakness: Optional[str] = Field(None, description="劣势")
    price_offer: Optional[Decimal] = Field(None, description="对手报价")
    threat_level: Optional[int] = Field(None, ge=1, le=5, description="威胁等级")


class CompetitorResponse(CompetitorCreate):
    """竞争对手响应"""

    id: int
    opportunity_id: int

    class Config:
        from_attributes = True
