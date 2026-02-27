"""客户信息模型"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, Integer, DECIMAL, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship as _relationship
from app.models.base import TimestampMixin, SoftDeleteMixin, Base


class CustomerInfo(Base, TimestampMixin, SoftDeleteMixin):
    """客户信息表"""
    __tablename__ = "crm_customer_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    customer_no = Column(String(50), nullable=False, unique=True, comment="客户编号")
    customer_name = Column(String(200), nullable=False, comment="1#客户名称（中）")
    customer_name_en = Column(String(200), comment="1#客户名称（EN）")
    region = Column(String(50), comment="区域")
    customer_type_3 = Column(String(50), comment="3#客户类型")
    customer_level_3 = Column(String(50), comment="3#客户分级")
    deal_customer_5 = Column(Integer, comment="5#成交客户")
    electrical_engineer_count_5 = Column(Integer, comment="5#电气工程师人数")
    owner_name_3 = Column(String(50), comment="3#负责人")
    customer_type = Column(String(20), nullable=False, comment="客户类型: enterprise/individual")

    # 企业客户信息
    industry = Column(String(100), comment="所属行业")
    company_size = Column(String(50), comment="公司规模")
    legal_person = Column(String(50), comment="法人代表")
    registered_capital = Column(DECIMAL(20, 2), comment="注册资本")
    establish_date = Column(Date, comment="成立日期")

    # 联系信息
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    address = Column(String(500), comment="详细地址")
    website = Column(String(200), comment="官方网站")
    company_info = Column(Text, comment="公司信息")
    product_info = Column(Text, comment="产品信息")

    # 业务信息
    source = Column(String(50), comment="客户来源")
    level = Column(String(20), comment="客户级别: A/B/C/D")
    status = Column(String(20), default="active", comment="状态: active/inactive/pool")

    # 负责人信息
    owner_id = Column(BigInteger, ForeignKey("sys_user.id"), comment="负责人ID")
    owner_name = Column(String(50), comment="负责人姓名")

    # 统计信息
    opportunity_count = Column(Integer, default=0, comment="商机数量")
    visit_count = Column(Integer, default=0, comment="拜访次数")
    last_visit_at = Column(DateTime, comment="最后拜访时间")
    last_activity_at = Column(DateTime, comment="最后活动时间")

    # AI增强字段
    ai_summary = Column(Text, comment="AI生成的客户画像摘要")
    ai_insights = Column(Text, comment="AI分析洞察(JSON格式)")
    data_completed_at = Column(DateTime, comment="AI数据补全时间")

    # 元数据
    tags = Column(Text, comment="标签数组(逗号分隔)")
    remarks = Column(Text, comment="备注")
    created_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="创建人ID")
    updated_by = Column(BigInteger, ForeignKey("sys_user.id"), comment="更新人ID")

    # 关系
    contacts = _relationship("ContactInfo", back_populates="customer", cascade="all, delete-orphan")
    interactions = _relationship("CustomerInteraction", back_populates="customer", cascade="all, delete-orphan")
    opportunities = _relationship("OpportunityInfo", back_populates="customer")
    visits = _relationship("VisitRecord", back_populates="customer")
    follow_records = _relationship("FollowRecord", back_populates="customer")
    tasks = _relationship("TaskInfo", back_populates="customer")
    schedules = _relationship("Schedule", back_populates="customer")

    def __repr__(self):
        return f"<CustomerInfo(id={self.id}, name={self.customer_name}, no={self.customer_no})>"
