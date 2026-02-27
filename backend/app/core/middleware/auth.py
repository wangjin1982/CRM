"""认证中间件"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.utils.response import ErrorResponse


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件 - 检查请求是否包含有效的认证令牌"""

    def __init__(self, app: ASGIApp, exclude_paths: list[str] = None):
        super().__init__(app)
        # 不需要认证的路径
        self.exclude_paths = exclude_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
        ]

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        path = request.url.path

        # 检查是否在排除列表中
        if any(path.startswith(exclude_path) for exclude_path in self.exclude_paths):
            return await call_next(request)

        # 检查Authorization头
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponse.unauthorized("缺少认证令牌").model_dump(),
            )

        # 验证Bearer Token格式
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponse.unauthorized("认证令牌格式错误").model_dump(),
            )

        # 将token传递给请求状态，供后续使用
        token = authorization.replace("Bearer ", "")
        request.state.token = token

        return await call_next(request)
