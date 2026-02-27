"""系统配置数据模型"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, Integer, DateTime

from app.models.base import Base, TimestampMixin


class SysConfig(Base, TimestampMixin):
    """系统配置表"""

    __tablename__ = "sys_config"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="配置ID")
    config_key = Column(String(100), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, nullable=True, comment="配置值")
    config_type = Column(String(20), nullable=True, comment="配置类型：string number boolean json")
    description = Column(String(200), nullable=True, comment="配置描述")
    is_public = Column(Boolean, default=False, nullable=False, comment="是否可向前端暴露")


class SysOperationLog(Base):
    """操作日志表"""

    __tablename__ = "sys_operation_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(BigInteger, nullable=True, comment="用户ID")
    username = Column(String(50), nullable=True, comment="用户名")
    module = Column(String(50), nullable=True, comment="模块名称")
    operation = Column(String(50), nullable=True, comment="操作名称")
    method = Column(String(10), nullable=True, comment="请求方法")
    path = Column(String(200), nullable=True, comment="请求路径")
    params = Column(Text, nullable=True, comment="请求参数")
    ip = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    status = Column(Boolean, nullable=True, comment="状态：1成功 0失败")
    error_msg = Column(Text, nullable=True, comment="错误信息")
    duration = Column(Integer, nullable=True, comment="请求耗时(ms)")
    created_at = Column(DateTime, nullable=False, comment="创建时间")


class SysDict(Base):
    """字典表"""

    __tablename__ = "sys_dict"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="字典ID")
    dict_type = Column(String(50), nullable=False, index=True, comment="字典类型")
    dict_label = Column(String(100), nullable=False, comment="字典标签")
    dict_value = Column(String(100), nullable=False, comment="字典值")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    status = Column(Boolean, default=True, nullable=False, comment="状态")
    remark = Column(String(200), nullable=True, comment="备注")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
