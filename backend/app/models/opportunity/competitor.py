"""竞争对手信息模型"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, Numeric, Integer, DateTime
from sqlalchemy.orm import relationship as _relationship

from app.models.base import Base


class Competitor(Base):
    """竞争对手信息表"""

    __tablename__ = "crm_competitor"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="竞争对手ID")
    opportunity_id = Column(BigInteger, ForeignKey("crm_opportunity_info.id"), nullable=False, comment="商机ID")
    competitor_name = Column(String(100), nullable=False, comment="竞争对手名称")
    strength = Column(Text, comment="优势")
    weakness = Column(Text, comment="劣势")
    price_offer = Column(Numeric(20, 2), comment="对手报价")
    threat_level = Column(Integer, comment="威胁等级 1-5")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    opportunity = _relationship("OpportunityInfo", back_populates="competitors_list")
