"""客户标签模型"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from app.models.base import TimestampMixin, Base


class CustomerTag(Base, TimestampMixin):
    """客户标签表"""
    __tablename__ = "crm_customer_tag"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tag_name = Column(String(50), nullable=False, unique=True, comment="标签名称")
    tag_color = Column(String(20), comment="标签颜色")
    tag_type = Column(String(20), comment="标签类型: system/custom")
    sort_order = Column(Integer, default=0, comment="排序")

    def __repr__(self):
        return f"<CustomerTag(id={self.id}, name={self.tag_name}, type={self.tag_type})>"
