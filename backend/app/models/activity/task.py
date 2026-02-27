# 任务管理数据模型
from sqlalchemy import Column, BigInteger, String, Integer, Text, Boolean, Date, Time, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base, TimestampMixin


class TaskInfo(Base, TimestampMixin):
    """任务管理表"""

    __tablename__ = "crm_task_info"

    # 基本信息
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="任务ID")
    task_no = Column(String(50), unique=True, nullable=False, index=True, comment="任务编号")
    task_title = Column(String(200), nullable=False, comment="任务标题")

    # 关联信息
    customer_id = Column(BigInteger, ForeignKey("crm_customer_info.id", ondelete="SET NULL"), comment="客户ID")
    opportunity_id = Column(BigInteger, ForeignKey("crm_opportunity_info.id", ondelete="SET NULL"), comment="商机ID")
    related_object_type = Column(String(50), comment="关联对象类型: customer/opportunity/contact")
    related_object_id = Column(BigInteger, comment="关联对象ID")

    # 任务类型
    task_type = Column(String(50), nullable=False, comment="任务类型: call/visit/meeting/followup/other")
    task_category = Column(String(50), comment="任务分类")

    # 时间信息
    due_date = Column(Date, nullable=False, index=True, comment="截止日期")
    due_time = Column(Time, comment="截止时间")
    reminder_time = Column(DateTime, comment="提醒时间")
    duration = Column(Integer, comment="预计时长(分钟)")

    # 优先级与状态
    priority = Column(String(20), default="medium", index=True, comment="优先级: high/medium/low")
    status = Column(String(20), default="pending", index=True, comment="状态: pending/in_progress/completed/cancelled")

    # 任务详情
    description = Column(Text, comment="任务描述")
    location = Column(String(200), comment="地点")
    notes = Column(Text, comment="备注")

    # 完成信息
    completed_at = Column(DateTime, comment="完成时间")
    completion_note = Column(Text, comment="完成备注")

    # 重复设置
    is_recurring = Column(Boolean, default=False, comment="是否重复任务")
    recurrence_rule = Column(Text, comment="重复规则(JSON字符串)")
    parent_task_id = Column(BigInteger, ForeignKey("crm_task_info.id"), comment="父任务ID")

    # 参与人
    assigned_to = Column(BigInteger, ForeignKey("sys_user.id"), index=True, comment="分配给")
    created_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="创建人ID")

    # 附件
    attachments = Column(JSON, comment="附件URL")

    # 关系
    customer = relationship("CustomerInfo", back_populates="tasks", foreign_keys=[customer_id])
    opportunity = relationship("OpportunityInfo", back_populates="tasks", foreign_keys=[opportunity_id])
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by])
    parent_task = relationship("TaskInfo", remote_side=[id], backref="sub_tasks")
    reminder_logs = relationship("TaskReminderLog", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TaskInfo(id={self.id}, task_no={self.task_no}, title={self.task_title})>"


class TaskReminderLog(Base):
    """任务提醒日志表"""

    __tablename__ = "crm_task_reminder_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")
    task_id = Column(BigInteger, ForeignKey("crm_task_info.id", ondelete="CASCADE"), nullable=False, index=True, comment="任务ID")
    user_id = Column(BigInteger, ForeignKey("sys_user.id"), nullable=False, comment="用户ID")
    reminder_time = Column(DateTime, nullable=False, comment="提醒时间")
    reminder_type = Column(String(50), comment="提醒类型: email/sms/push")
    status = Column(String(20), comment="状态: sent/failed")
    sent_at = Column(DateTime, comment="发送时间")
    error_msg = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    task = relationship("TaskInfo", back_populates="reminder_logs")
    user = relationship("User")

    def __repr__(self):
        return f"<TaskReminderLog(id={self.id}, task_id={self.task_id}, status={self.status})>"
