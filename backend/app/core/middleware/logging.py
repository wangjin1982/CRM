"""日志中间件"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from loguru import logger

from app.core.config.settings import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件 - 记录请求和响应信息"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """处理请求并记录日志"""
        start_time = time.time()

        # 记录请求信息
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # 处理请求
        try:
            response = await call_next(request)

            # 计算处理时间
            process_time = (time.time() - start_time) * 1000

            # 记录响应信息
            logger.info(
                f"Response: {response.status_code} "
                f"took {process_time:.2f}ms "
                f"for {request.method} {request.url.path}"
            )

            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 记录错误
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Error: {str(e)} "
                f"took {process_time:.2f}ms "
                f"for {request.method} {request.url.path}"
            )
            raise
