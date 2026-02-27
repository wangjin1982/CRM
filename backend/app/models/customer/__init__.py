"""客户模块数据模型"""
from .info import CustomerInfo
from .contact import ContactInfo
from .interaction import CustomerInteraction
from .tag import CustomerTag

__all__ = [
    "CustomerInfo",
    "ContactInfo",
    "CustomerInteraction",
    "CustomerTag",
]
