"""客户交互记录模型"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship as _relationship
from app.models.base import TimestampMixin, Base


class CustomerInteraction(Base, TimestampMixin):
    """客户交互记录表"""
    __tablename__ = "crm_customer_interaction"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    customer_id = Column(BigInteger, ForeignKey("crm_customer_info.id"), nullable=False, comment="客户ID")
    contact_id = Column(BigInteger, ForeignKey("crm_contact_info.id"), comment="联系人ID")

    interaction_type = Column(String(50), nullable=False, comment="交互类型: call/email/visit/wechat/other")
    direction = Column(String(20), comment="方向: inbound/outbound")

    subject = Column(String(200), comment="主题")
    content = Column(Text, comment="内容")
    duration = Column(Integer, comment="时长(秒)")

    attachments = Column(Text, comment="附件URL列表(JSON格式)")

    next_follow_at = Column(DateTime, comment="下次跟进时间")
    next_follow_note = Column(Text, comment="下次跟进备注")

    created_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="创建人ID")

    # 关系
    customer = _relationship("CustomerInfo", back_populates="interactions")

    def __repr__(self):
        return f"<CustomerInteraction(id={self.id}, type={self.interaction_type}, customer_id={self.customer_id})>"
