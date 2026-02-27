"""API v1 路由模块"""
from fastapi import APIRouter

from app.api.v1 import auth, users, roles, activity, health
from app.api.v1.ai import router as ai_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.customers import customer_router
from app.api.v1.opportunity import opportunities, stages, funnel

# 创建API路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(health.router, tags=["健康检查"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(customer_router, prefix="/customers", tags=["客户资源管理"])
api_router.include_router(activity.router, prefix="/activity", tags=["销售行为管理"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["商机管理"])
api_router.include_router(stages.router, prefix="/stages", tags=["销售阶段"])
api_router.include_router(funnel.router, prefix="/funnel", tags=["销售漏斗"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI智能增强"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["数据分析"])
