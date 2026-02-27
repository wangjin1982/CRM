# 拜访记录数据模型
from sqlalchemy import Column, BigInteger, String, Integer, Text, Boolean, DateTime, Date, Time, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base, TimestampMixin


class VisitRecord(Base, TimestampMixin):
    """拜访记录表"""

    __tablename__ = "crm_visit_record"

    # 基本信息
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="拜访ID")
    visit_no = Column(String(50), unique=True, nullable=False, index=True, comment="拜访编号")
    visit_type = Column(String(50), nullable=False, comment="拜访类型: onsite/online")

    # 关联信息
    customer_id = Column(BigInteger, ForeignKey("crm_customer_info.id", ondelete="CASCADE"), nullable=False, index=True, comment="客户ID")
    customer_name = Column(String(200), comment="客户名称（冗余）")
    opportunity_id = Column(BigInteger, ForeignKey("crm_opportunity_info.id", ondelete="SET NULL"), comment="商机ID")

    # 拜访对象
    contact_ids = Column(JSON, comment="参与联系人ID列表")
    participant_names = Column(String(500), comment="参与人姓名（冗余）")

    # 时间地点
    visit_date = Column(Date, nullable=False, index=True, comment="拜访日期")
    start_time = Column(Time, comment="开始时间")
    end_time = Column(Time, comment="结束时间")
    duration = Column(Integer, comment="时长(分钟)")

    # 地址信息（外勤拜访）
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    address = Column(String(500), comment="详细地址")
    latitude = Column(Numeric(10, 7), comment="纬度")
    longitude = Column(Numeric(10, 7), comment="经度")

    # 拜访内容
    purpose = Column(String(200), comment="拜访目的")
    content = Column(Text, comment="拜访内容/纪要")
    customer_feedback = Column(Text, comment="客户反馈")
    next_plan = Column(Text, comment="下一步计划")

    # 结果评估
    result_type = Column(String(50), comment="结果类型: positive/neutral/negative")
    interest_level = Column(Integer, comment="兴趣等级 1-5")
    purchase_intent = Column(Integer, comment="采购意向 1-5")

    # 附件
    photos = Column(JSON, comment="照片URL")
    attachments = Column(JSON, comment="附件URL")

    # 费用
    expense_amount = Column(Numeric(10, 2), comment="拜访费用")
    expense_desc = Column(String(200), comment="费用说明")

    # AI增强
    ai_summary = Column(Text, comment="AI生成的总结")
    ai_action_items = Column(Text, comment="AI提取的行动项(JSON字符串)")

    # 元数据
    created_by = Column(BigInteger, ForeignKey("sys_user.id"), index=True, comment="创建人ID")

    # 关系
    customer = relationship("CustomerInfo", back_populates="visits", foreign_keys=[customer_id])
    opportunity = relationship("OpportunityInfo", back_populates="visits", foreign_keys=[opportunity_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<VisitRecord(id={self.id}, visit_no={self.visit_no}, customer_id={self.customer_id})>"
