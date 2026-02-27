"""角色数据模型"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Role(Base, TimestampMixin):
    """角色表"""

    __tablename__ = "sys_role"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="角色ID")
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色代码")
    description = Column(Text, nullable=True, comment="角色描述")
    status = Column(Integer, default=1, nullable=False, comment="状态：1启用 0禁用")

    # 关系
    users = relationship("User", secondary="sys_user_role", back_populates="roles")
    permissions = relationship("Permission", secondary="sys_role_permission", back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, code={self.code})>"


class UserRole(Base):
    """用户角色关联表"""

    __tablename__ = "sys_user_role"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="关联ID")
    user_id = Column(BigInteger, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    role_id = Column(BigInteger, ForeignKey("sys_role.id", ondelete="CASCADE"), nullable=False, comment="角色ID")
    created_at = Column(DateTime, nullable=False, comment="创建时间")


class RolePermission(Base):
    """角色权限关联表"""

    __tablename__ = "sys_role_permission"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="关联ID")
    role_id = Column(BigInteger, ForeignKey("sys_role.id", ondelete="CASCADE"), nullable=False, comment="角色ID")
    permission_id = Column(BigInteger, ForeignKey("sys_permission.id", ondelete="CASCADE"), nullable=False, comment="权限ID")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
