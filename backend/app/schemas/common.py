"""通用Schema"""
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")


class CommonResponse(BaseModel):
    """通用响应Schema"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()), description="时间戳")


class PageParams(BaseModel):
    """分页参数"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """获取限制数量"""
        return self.page_size


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""

    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数量")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PageResponse[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class IdParam(BaseModel):
    """ID参数"""

    id: int = Field(..., gt=0, description="ID")


class IdsParam(BaseModel):
    """ID列表参数"""

    ids: List[int] = Field(..., min_length=1, description="ID列表")
