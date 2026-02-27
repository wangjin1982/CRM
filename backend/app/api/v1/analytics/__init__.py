"""分析模块路由"""
from fastapi import APIRouter

from . import analytics

router = APIRouter()
router.include_router(analytics.router)
