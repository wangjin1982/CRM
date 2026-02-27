"""商机联系人关联模型"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Boolean, String, DateTime
from sqlalchemy.orm import relationship as _relationship

from app.models.base import Base


class OpportunityContact(Base):
    """商机联系人关联表"""

    __tablename__ = "crm_opportunity_contact"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="关联ID")
    opportunity_id = Column(BigInteger, ForeignKey("crm_opportunity_info.id"), nullable=False, index=True, comment="商机ID")
    contact_id = Column(BigInteger, ForeignKey("crm_contact_info.id"), nullable=False, index=True, comment="联系人ID")
    role = Column(String(50), comment="在此商机中的角色")
    influence_level = Column(Integer, comment="影响力等级 1-5")
    is_primary = Column(Boolean, default=False, comment="是否主要联系人")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    opportunity = _relationship("OpportunityInfo", back_populates="contacts")
