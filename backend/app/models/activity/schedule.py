# 日程安排数据模型
from sqlalchemy import Column, BigInteger, String, Integer, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base, TimestampMixin


class Schedule(Base, TimestampMixin):
    """日程安排表"""

    __tablename__ = "crm_schedule"

    # 基本信息
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日程ID")
    schedule_title = Column(String(200), nullable=False, comment="日程标题")

    # 时间信息
    start_time = Column(DateTime, nullable=False, index=True, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    is_all_day = Column(Boolean, default=False, comment="是否全天")

    # 关联信息
    customer_id = Column(BigInteger, ForeignKey("crm_customer_info.id", ondelete="SET NULL"), comment="客户ID")
    opportunity_id = Column(BigInteger, ForeignKey("crm_opportunity_info.id", ondelete="SET NULL"), comment="商机ID")
    task_id = Column(BigInteger, ForeignKey("crm_task_info.id", ondelete="SET NULL"), comment="任务ID")

    # 类型
    schedule_type = Column(String(50), comment="日程类型: meeting/call/training/other")
    location = Column(String(200), comment="地点")

    # 详情
    description = Column(Text, comment="描述")
    attendees = Column(Text, comment="参与人(JSON字符串)")

    # 提醒
    reminder_minutes = Column(JSON, comment="提醒时间点(分钟)")

    # 重复
    is_recurring = Column(Boolean, default=False, comment="是否重复")
    recurrence_rule = Column(Text, comment="重复规则(JSON字符串)")

    # 状态
    status = Column(String(20), default="scheduled", comment="状态: scheduled/completed/cancelled")

    # 元数据
    created_by = Column(BigInteger, ForeignKey("sys_user.id"), index=True, comment="创建人ID")

    # 关系
    customer = relationship("CustomerInfo", back_populates="schedules", foreign_keys=[customer_id])
    opportunity = relationship("OpportunityInfo", back_populates="schedules", foreign_keys=[opportunity_id])
    task = relationship("TaskInfo", foreign_keys=[task_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Schedule(id={self.id}, title={self.schedule_title}, start_time={self.start_time})>"
