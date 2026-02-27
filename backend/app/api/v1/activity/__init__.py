# 销售行为管理模块API
from fastapi import APIRouter
from app.api.v1.activity import visit, follow, task, schedule, statistics

router = APIRouter()

# 注册子路由
router.include_router(visit.router, prefix="/visits", tags=["拜访记录"])
router.include_router(follow.router, prefix="/follows", tags=["跟进记录"])
router.include_router(task.router, prefix="/tasks", tags=["任务管理"])
router.include_router(schedule.router, prefix="/schedules", tags=["日程管理"])
router.include_router(statistics.router, prefix="/statistics", tags=["行为统计"])
