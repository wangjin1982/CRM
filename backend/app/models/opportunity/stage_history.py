"""阶段变更历史模型"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import relationship as _relationship

from app.models.base import Base


class OpportunityStageHistory(Base):
    """阶段变更历史表"""

    __tablename__ = "crm_opportunity_stage_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="历史ID")
    opportunity_id = Column(BigInteger, ForeignKey("crm_opportunity_info.id"), nullable=False, index=True, comment="商机ID")
    from_stage_id = Column(BigInteger, ForeignKey("crm_stage_def.id"), comment="原阶段ID")
    to_stage_id = Column(BigInteger, ForeignKey("crm_stage_def.id"), nullable=False, comment="新阶段ID")
    stage_duration = Column(Integer, comment="在上一阶段停留天数")
    changed_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="变更人")
    changed_at = Column(DateTime, default=datetime.utcnow, comment="变更时间")
    notes = Column(Text, comment="变更说明")

    # 关系
    opportunity = _relationship("OpportunityInfo", back_populates="stage_history")
