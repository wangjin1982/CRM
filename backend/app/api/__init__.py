"""API路由模块"""
from fastapi import APIRouter

from app.api.v1 import api_router as api_v1_router

# 创建API路由器
api_router = APIRouter()

# 注册v1路由
api_router.include_router(api_v1_router)
