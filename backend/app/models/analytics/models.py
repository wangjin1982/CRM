"""数据分析模块模型"""
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)

from app.models.base import Base, TimestampMixin


class ReportDef(Base, TimestampMixin):
    """报表定义"""
    __tablename__ = "crm_report_def"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_name = Column(String(100), nullable=False)
    report_code = Column(String(100), nullable=False, unique=True, index=True)
    report_type = Column(String(50), nullable=False, index=True)
    config = Column(JSON, comment="报表配置")
    sql_template = Column(Text, comment="SQL模板")
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(BigInteger, ForeignKey("sys_user.id"))


class ReportSubscription(Base, TimestampMixin):
    """报表订阅"""
    __tablename__ = "crm_report_subscription"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(BigInteger, ForeignKey("crm_report_def.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("sys_user.id"), nullable=False, index=True)
    channel = Column(String(20), default="email")
    cron_expr = Column(String(100), comment="调度表达式")
    is_enabled = Column(Boolean, default=True, nullable=False)


class DataSnapshot(Base, TimestampMixin):
    """数据快照"""
    __tablename__ = "crm_data_snapshot"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    snapshot_type = Column(String(50), nullable=False, index=True)
    payload = Column(JSON, nullable=False)


class KPIDef(Base, TimestampMixin):
    """KPI定义"""
    __tablename__ = "crm_kpi_def"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    kpi_code = Column(String(100), nullable=False, unique=True, index=True)
    kpi_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    unit = Column(String(20))
    target_value = Column(Integer)
    calc_rule = Column(Text, comment="计算逻辑")
    is_active = Column(Boolean, default=True, nullable=False)
