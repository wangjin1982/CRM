"""数据库模型基类"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    """时间戳混入类"""

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")


class SoftDeleteMixin:
    """软删除混入类"""

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True, comment="删除时间")


# 导入Base
from app.core.config.database import Base
