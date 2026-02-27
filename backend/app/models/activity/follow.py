# 跟进记录数据模型
from sqlalchemy import Column, BigInteger, String, Integer, Text, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base, TimestampMixin


class FollowRecord(Base, TimestampMixin):
    """跟进记录表"""

    __tablename__ = "crm_follow_record"

    # 基本信息
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="跟进ID")
    follow_no = Column(String(50), unique=True, nullable=False, index=True, comment="跟进编号")

    # 关联信息
    customer_id = Column(BigInteger, ForeignKey("crm_customer_info.id", ondelete="CASCADE"), nullable=False, index=True, comment="客户ID")
    customer_name = Column(String(200), comment="客户名称（冗余）")
    opportunity_id = Column(BigInteger, ForeignKey("crm_opportunity_info.id", ondelete="SET NULL"), comment="商机ID")
    contact_id = Column(BigInteger, ForeignKey("crm_contact_info.id", ondelete="SET NULL"), comment="联系人ID")

    # 跟进类型
    follow_type = Column(String(50), nullable=False, index=True, comment="跟进类型: call/email/wechat/message/other")
    follow_direction = Column(String(20), comment="方向: inbound/outbound")

    # 跟进内容
    subject = Column(String(200), comment="主题")
    content = Column(Text, comment="内容")

    # 通话信息（电话类型）
    call_duration = Column(Integer, comment="通话时长(秒)")
    call_recording_url = Column(String(500), comment="录音URL")

    # 邮件信息（邮件类型）
    email_from = Column(String(200), comment="发件人")
    email_to = Column(JSON, comment="收件人")
    email_cc = Column(JSON, comment="抄送")
    email_subject = Column(String(500), comment="邮件主题")
    email_body = Column(Text, comment="邮件正文")

    # 结果
    response = Column(Text, comment="对方回应")
    result = Column(String(50), comment="结果评估")

    # 下次跟进
    next_follow_date = Column(Date, comment="下次跟进日期")
    next_follow_note = Column(Text, comment="下次跟进备注")

    # 附件
    attachments = Column(JSON, comment="附件URL")

    # AI增强
    ai_summary = Column(Text, comment="AI总结")
    ai_sentiment = Column(String(20), comment="情感分析: positive/neutral/negative")

    # 元数据
    created_by = Column(BigInteger, ForeignKey("sys_user.id"), index=True, comment="创建人ID")

    # 关系
    customer = relationship("CustomerInfo", back_populates="follow_records", foreign_keys=[customer_id])
    opportunity = relationship("OpportunityInfo", back_populates="follow_records", foreign_keys=[opportunity_id])
    contact = relationship("ContactInfo", back_populates="follow_records", foreign_keys=[contact_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<FollowRecord(id={self.id}, follow_no={self.follow_no}, customer_id={self.customer_id})>"
