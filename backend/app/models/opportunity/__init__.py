"""商机模块数据模型"""
from .info import OpportunityInfo
from .stage import StageDef
from .contact import OpportunityContact
from .stage_history import OpportunityStageHistory
from .competitor import Competitor

__all__ = [
    "OpportunityInfo",
    "StageDef",
    "OpportunityContact",
    "OpportunityStageHistory",
    "Competitor",
]
