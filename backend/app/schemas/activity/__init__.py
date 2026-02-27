# 销售行为管理模块Schema
from .visit import *
from .follow import *
from .task import *
from .schedule import *

__all__ = [
    # Visit
    "VisitCreate",
    "VisitUpdate",
    "VisitResponse",
    "VisitListResponse",
    # Follow
    "FollowCreate",
    "FollowUpdate",
    "FollowResponse",
    "FollowListResponse",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskCompleteRequest",
    # Schedule
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "ScheduleListResponse",
    # Statistics
    "ActivityStatistics",
]
