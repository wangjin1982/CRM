"""权限数据模型"""
from sqlalchemy import Column, BigInteger, String, Text, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Permission(Base, TimestampMixin):
    """权限表"""

    __tablename__ = "sys_permission"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="权限ID")
    parent_id = Column(BigInteger, default=0, nullable=False, comment="父权限ID")
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, nullable=False, comment="权限代码")
    type = Column(String(20), nullable=False, comment="权限类型：menu菜单 button按钮 api接口")
    path = Column(String(200), nullable=True, comment="路由路径")
    method = Column(String(10), nullable=True, comment="请求方法：GET POST PUT DELETE")
    icon = Column(String(50), nullable=True, comment="图标")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    status = Column(Integer, default=1, nullable=False, comment="状态：1启用 0禁用")

    # 关系
    roles = relationship("Role", secondary="sys_role_permission", back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, code={self.code})>"
