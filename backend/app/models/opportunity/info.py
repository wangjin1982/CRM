"""商机信息模型"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Numeric, Text, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class OpportunityInfo(Base, TimestampMixin, SoftDeleteMixin):
    """商机信息表"""

    __tablename__ = "crm_opportunity_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="商机ID")
    opportunity_no = Column(String(50), unique=True, nullable=False, index=True, comment="商机编号")
    opportunity_name = Column(String(200), nullable=False, comment="商机名称")

    # 关联信息
    customer_id = Column(BigInteger, ForeignKey("crm_customer_info.id"), nullable=False, index=True, comment="客户ID")
    customer_name = Column(String(200), comment="客户名称(冗余)")
    primary_contact_id = Column(BigInteger, ForeignKey("crm_contact_info.id"), comment="主要联系人ID")

    # 金额信息
    estimated_amount = Column(Numeric(20, 2), comment="预估金额")
    actual_amount = Column(Numeric(20, 2), comment="实际成交金额")
    currency = Column(String(10), default="CNY", comment="币种")

    # 阶段信息
    stage_id = Column(BigInteger, ForeignKey("crm_stage_def.id"), nullable=False, index=True, comment="当前阶段")
    stage_name = Column(String(50), comment="阶段名称(冗余)")
    stage_order = Column(Integer, comment="阶段序号")

    # 时间信息
    expected_close_date = Column(Date, comment="预计成交日期")
    actual_close_date = Column(Date, comment="实际成交日期")

    # 概率与优先级
    win_probability = Column(Integer, default=50, comment="成交概率(%)")
    priority = Column(String(20), default="medium", comment="优先级: high/medium/low")

    # 负责人信息
    owner_id = Column(BigInteger, ForeignKey("sys_user.id"), index=True, comment="负责人ID")
    owner_name = Column(String(50), comment="负责人姓名")

    # 竞争信息
    competitors = Column(Text, comment="竞争对手")
    competitive_status = Column(String(50), comment="竞争状态")

    # 产品信息 (JSON格式)
    products = Column(JSON, comment="产品信息")

    # 来源信息
    lead_source = Column(String(50), comment="商机来源")

    # 状态
    status = Column(String(20), default="open", index=True, comment="状态: open/won/lost/abandoned")

    # AI分析字段
    risk_level = Column(String(20), comment="风险等级: low/medium/high")
    risk_factors = Column(JSON, comment="风险因素")
    ai_suggestions = Column(Text, comment="AI建议")
    last_ai_analysis = Column(DateTime, comment="最后AI分析时间")

    # 停滞预警
    days_in_stage = Column(Integer, default=0, comment="当前阶段停留天数")
    is_stagnant = Column(Boolean, default=False, index=True, comment="是否停滞")
    stagnant_alert_sent = Column(Boolean, default=False, comment="是否已发送预警")

    # 统计信息
    activity_count = Column(Integer, default=0, comment="活动次数")
    last_activity_at = Column(DateTime, comment="最后活动时间")

    # 元数据
    description = Column(Text, comment="商机描述")
    lost_reason = Column(String(200), comment="流失原因")
    tags = Column(JSON, comment="标签")

    created_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="创建人")
    updated_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="更新人")

    # 关系
    customer = relationship("CustomerInfo", back_populates="opportunities", foreign_keys=[customer_id])
    stage = relationship("StageDef", backref="opportunities")
    contacts = relationship("OpportunityContact", back_populates="opportunity", cascade="all, delete-orphan")
    stage_history = relationship("OpportunityStageHistory", back_populates="opportunity", cascade="all, delete-orphan")
    competitors_list = relationship("Competitor", back_populates="opportunity", cascade="all, delete-orphan")
    visits = relationship("VisitRecord", back_populates="opportunity")
    follow_records = relationship("FollowRecord", back_populates="opportunity")
    tasks = relationship("TaskInfo", back_populates="opportunity")
    schedules = relationship("Schedule", back_populates="opportunity")

    def __repr__(self):
        return f"<OpportunityInfo(id={self.id}, no={self.opportunity_no}, name={self.opportunity_name})>"
