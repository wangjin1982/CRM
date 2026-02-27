"""验证器模块"""
import re
from typing import Optional
from pydantic import field_validator, EmailStr
from pydantic import BaseModel


class PasswordValidator(BaseModel):
    """密码验证器"""
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度
        - 至少8位
        - 包含大小写字母、数字或特殊字符中的至少两种
        """
        if len(v) < 8:
            raise ValueError("密码长度至少8位")

        # 检查字符类型
        has_upper = bool(re.search(r"[A-Z]", v))
        has_lower = bool(re.search(r"[a-z]", v))
        has_digit = bool(re.search(r"\d", v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', v))

        char_types = sum([has_upper, has_lower, has_digit, has_special])
        if char_types < 2:
            raise ValueError("密码必须包含大小写字母、数字或特殊字符中的至少两种")

        return v


class PhoneNumberValidator(BaseModel):
    """手机号验证器"""
    phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """验证手机号格式"""
        if v is None:
            return v

        # 中国大陆手机号正则
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, v):
            raise ValueError("手机号格式不正确")

        return v
