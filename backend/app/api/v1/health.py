# 健康检查路由
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "CRM系统运行正常"
    }


@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用智能CRM系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }
