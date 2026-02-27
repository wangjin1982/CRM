"""销售阶段定义模型"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Float, Text

from app.models.base import Base, TimestampMixin


class StageDef(Base, TimestampMixin):
    """销售阶段定义表"""

    __tablename__ = "crm_stage_def"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="阶段ID")
    stage_name = Column(String(50), nullable=False, comment="阶段名称")
    stage_code = Column(String(50), unique=True, nullable=False, comment="阶段代码")
    stage_order = Column(Integer, nullable=False, comment="阶段序号")
    stage_type = Column(String(20), default="normal", comment="阶段类型: normal, won, lost")
    probability = Column(Integer, default=0, comment="默认成交概率(%)")
    weight = Column(Float, comment="漏斗权重(0-1)")
    duration_days = Column(Integer, comment="建议停留天数")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    description = Column(String(200), comment="阶段描述")
    internal_code = Column(String(20), comment="内部简称")
    customer_journey = Column(String(100), comment="客户旅程定义")
    technical_support = Column(Text, comment="技术支持重点工作")
    sales_process = Column(Text, comment="销售侧重点工作")
    stage_criteria = Column(Text, comment="阶段判定标准")

    def __repr__(self):
        return f"<StageDef(id={self.id}, name={self.stage_name}, code={self.stage_code})>"
