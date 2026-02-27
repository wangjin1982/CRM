"""统一响应格式模块"""
from typing import Any, Generic, TypeVar, Optional
from datetime import datetime
from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""

    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()), description="时间戳")

    @classmethod
    def success(cls, data: T = None, message: str = "success") -> "ApiResponse[T]":
        """成功响应"""
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "error", data: T = None) -> "ApiResponse[T]":
        """错误响应"""
        return cls(code=code, message=message, data=data)

    @classmethod
    def list_response(
        cls,
        items: list,
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "success"
    ) -> "ApiResponse[dict]":
        """列表响应"""
        return cls(
            code=200,
            message=message,
            data={
                "items": items,
                "total": total,
                "page": page,
                "pageSize": page_size,
            }
        )


class ValidationError(BaseModel):
    """验证错误详情"""

    field: str = Field(..., description="字段名")
    message: str = Field(..., description="错误消息")


class ErrorResponse(BaseModel):
    """错误响应格式"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    errors: Optional[list[ValidationError]] = Field(default=None, description="验证错误列表")
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))

    @classmethod
    def validation_error(cls, errors: list[ValidationError]) -> "ErrorResponse":
        """验证错误响应"""
        return cls(code=400, message="参数验证失败", errors=errors)

    @classmethod
    def unauthorized(cls, message: str = "未认证") -> "ErrorResponse":
        """未认证响应"""
        return cls(code=401, message=message)

    @classmethod
    def forbidden(cls, message: str = "无权限") -> "ErrorResponse":
        """无权限响应"""
        return cls(code=403, message=message)

    @classmethod
    def not_found(cls, message: str = "资源不存在") -> "ErrorResponse":
        """资源不存在响应"""
        return cls(code=404, message=message)

    @classmethod
    def server_error(cls, message: str = "服务器错误") -> "ErrorResponse":
        """服务器错误响应"""
        return cls(code=500, message=message)


# 兼容性别名
def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应（兼容旧代码）"""
    return {"code": 200, "message": message, "data": data}


def error_response(code: int = 500, message: str = "error", data: Any = None) -> dict:
    """错误响应（兼容旧代码）"""
    return {"code": code, "message": message, "data": data}


# 通用响应Schema
class CommonResponse(BaseModel):
    """通用响应Schema"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()), description="时间戳")
