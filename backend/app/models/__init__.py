"""数据模型模块"""
from .base import Base, TimestampMixin
from .customer.info import CustomerInfo
from .customer.contact import ContactInfo
from .customer.interaction import CustomerInteraction
from .customer.tag import CustomerTag
from .opportunity.info import OpportunityInfo
from .opportunity.stage import StageDef
from .opportunity.contact import OpportunityContact
from .opportunity.stage_history import OpportunityStageHistory
from .opportunity.competitor import Competitor
from .activity.visit import VisitRecord
from .activity.follow import FollowRecord
from .activity.task import TaskInfo, TaskReminderLog
from .activity.schedule import Schedule
from .ai import (
    AIConfig,
    AIPromptTemplate,
    AIRequestLog,
    AIAnalysisResult,
    AIRiskAlert,
    AISearchHistory,
)
from .analytics import ReportDef, ReportSubscription, DataSnapshot, KPIDef

__all__ = [
    "Base",
    "TimestampMixin",
    "CustomerInfo",
    "ContactInfo",
    "CustomerInteraction",
    "CustomerTag",
    "OpportunityInfo",
    "StageDef",
    "OpportunityContact",
    "OpportunityStageHistory",
    "Competitor",
    "VisitRecord",
    "FollowRecord",
    "TaskInfo",
    "TaskReminderLog",
    "Schedule",
    "AIConfig",
    "AIPromptTemplate",
    "AIRequestLog",
    "AIAnalysisResult",
    "AIRiskAlert",
    "AISearchHistory",
    "ReportDef",
    "ReportSubscription",
    "DataSnapshot",
    "KPIDef",
]
