"""销售漏斗Schema"""
from typing import List, Dict
from pydantic import BaseModel, Field


class FunnelStageData(BaseModel):
    """漏斗阶段数据"""

    stage_id: int
    stage_name: str
    stage_order: int
    count: int
    amount: float
    probability: int
    weighted_amount: float


class FunnelSummary(BaseModel):
    """漏斗汇总"""

    total_count: int
    total_amount: float
    weighted_amount: float
    avg_amount: float


class ConversionRates(BaseModel):
    """转化率"""

    rates: Dict[str, float] = Field(default_factory=dict)


class FunnelResponse(BaseModel):
    """销售漏斗响应"""

    funnel: List[FunnelStageData]
    summary: FunnelSummary
    conversion_rates: Dict[str, float]
    conversion_stages: List[Dict]
    stage_health: List[Dict]
    win_loss: Dict[str, int]
