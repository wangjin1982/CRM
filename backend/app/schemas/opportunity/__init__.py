"""商机Schema模块"""
from .info import *
from .stage import *
from .contact import *
from .competitor import *
from .funnel import *

__all__ = [
    # Info
    "OpportunityBase",
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityResponse",
    "OpportunityListResponse",
    "OpportunityTransferRequest",
    # Stage
    "StageDefBase",
    "StageDefCreate",
    "StageDefUpdate",
    "StageDefResponse",
    "StageChangeRequest",
    "OpportunityWonRequest",
    "OpportunityLostRequest",
    "StageHistoryResponse",
    # Contact
    "OpportunityContactRequest",
    "OpportunityContactResponse",
    # Competitor
    "CompetitorCreate",
    "CompetitorResponse",
    # Funnel
    "FunnelResponse",
    "FunnelStageData",
    "FunnelSummary",
    "ConversionRates",
]
