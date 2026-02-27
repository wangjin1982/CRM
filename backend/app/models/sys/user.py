"""用户数据模型"""
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    """用户表"""

    __tablename__ = "sys_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    status = Column(Integer, default=1, nullable=False, index=True, comment="状态：1启用 0禁用")
    department_id = Column(BigInteger, nullable=True, comment="部门ID")
    position = Column(String(50), nullable=True, comment="职位")
    is_admin = Column(Boolean, default=False, nullable=False, comment="是否管理员")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")

    # 关系
    roles = relationship("Role", secondary="sys_user_role", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
