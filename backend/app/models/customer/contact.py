"""联系人信息模型"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship as _relationship
from app.models.base import TimestampMixin, SoftDeleteMixin, Base


class ContactInfo(Base, TimestampMixin, SoftDeleteMixin):
    """联系人信息表"""
    __tablename__ = "crm_contact_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    contact_no = Column(String(50), nullable=False, unique=True, comment="联系人编号")
    customer_id = Column(BigInteger, ForeignKey("crm_customer_info.id"), nullable=False, comment="所属客户ID")

    # 基本信息
    name = Column(String(50), nullable=False, comment="姓名")
    title = Column(String(100), comment="职位")
    department = Column(String(100), comment="部门")
    gender = Column(String(10), comment="性别")

    # 联系方式
    mobile = Column(String(20), comment="手机")
    phone = Column(String(20), comment="固话")
    email = Column(String(100), comment="邮箱")
    wechat = Column(String(50), comment="微信")

    # 决策链信息
    is_decision_maker = Column(Boolean, default=False, comment="是否决策人")
    is_influencer = Column(Boolean, default=False, comment="是否影响者")
    influence_level = Column(Integer, comment="影响力等级 1-5")

    # 关系信息
    relationship = Column(String(50), comment="关系类型")
    preference = Column(Text, comment="沟通偏好")
    birthday = Column(Date, comment="生日")
    hobbies = Column(Text, comment="兴趣爱好")

    # 社交信息
    linkedin = Column(String(200), comment="LinkedIn")
    weibo = Column(String(200), comment="微博")

    # 状态
    status = Column(String(20), default="active", comment="状态: active/inactive")
    is_primary = Column(Boolean, default=False, comment="是否主要联系人")

    # 统计信息
    contact_count = Column(Integer, default=0, comment="联系次数")
    last_contact_at = Column(DateTime, comment="最后联系时间")

    # 元数据
    remarks = Column(Text, comment="备注")
    created_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="创建人ID")
    updated_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="更新人ID")

    # 关系
    customer = _relationship("CustomerInfo", back_populates="contacts")
    follow_records = _relationship("FollowRecord", back_populates="contact")

    def __repr__(self):
        return f"<ContactInfo(id={self.id}, name={self.name}, customer_id={self.customer_id})>"
