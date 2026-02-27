"""辅助函数模块"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    return secrets.token_hex(length)


def hash_string(text: str) -> str:
    """字符串哈希"""
    return hashlib.sha256(text.encode()).hexdigest()


def timestamp_to_datetime(timestamp: int) -> datetime:
    """时间戳转datetime"""
    return datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(dt: datetime) -> int:
    """datetime转时间戳"""
    return int(dt.timestamp())


def calculate_age(birth_date: datetime) -> Optional[int]:
    """计算年龄"""
    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def format_phone_number(phone: str) -> str:
    """格式化手机号：13812345678 -> 138****5678"""
    if len(phone) == 11:
        return f"{phone[:3]}****{phone[7:]}"
    return phone


def mask_email(email: str) -> str:
    """掩码邮箱：user@example.com -> u***@example.com"""
    if "@" not in email:
        return email

    username, domain = email.split("@", 1)
    if len(username) > 1:
        masked_username = f"{username[0]}***{username[-1]}" if len(username) > 3 else f"{username[0]}***"
    else:
        masked_username = "***"

    return f"{masked_username}@{domain}"


def get_current_timestamp() -> int:
    """获取当前时间戳"""
    return int(datetime.now().timestamp())


def get_future_timestamp(days: int = 0, hours: int = 0, minutes: int = 0) -> int:
    """获取未来时间戳"""
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    return int((datetime.now() + delta).timestamp())


def generate_future_timestamp(days: int = 0, hours: int = 0, minutes: int = 0) -> int:
    """兼容旧调用：生成未来时间戳"""
    return get_future_timestamp(days=days, hours=hours, minutes=minutes)


async def generate_customer_no(db: AsyncSession) -> str:
    """生成客户编号 CUSYYYYMMDDXXXX"""
    from app.models.customer.info import CustomerInfo

    today = datetime.now().strftime("%Y%m%d")
    prefix = f"CUS{today}"

    # 查询今天已有的最大编号
    result = await db.execute(
        select(func.max(CustomerInfo.customer_no))
        .where(CustomerInfo.customer_no.like(f"{prefix}%"))
    )
    max_no = result.scalar()

    if max_no:
        # 提取序号并递增
        serial = int(max_no[-4:]) + 1
    else:
        serial = 1

    return f"{prefix}{serial:04d}"


async def generate_contact_no(db: AsyncSession) -> str:
    """生成联系人编号 CONYYYYMMDDXXXX"""
    from app.models.customer.contact import ContactInfo

    today = datetime.now().strftime("%Y%m%d")
    prefix = f"CON{today}"

    # 查询今天已有的最大编号
    result = await db.execute(
        select(func.max(ContactInfo.contact_no))
        .where(ContactInfo.contact_no.like(f"{prefix}%"))
    )
    max_no = result.scalar()

    if max_no:
        # 提取序号并递增
        serial = int(max_no[-4:]) + 1
    else:
        serial = 1

    return f"{prefix}{serial:04d}"


def tags_to_string(tags: List[str]) -> Optional[str]:
    """将标签列表转换为逗号分隔的字符串"""
    if not tags:
        return None
    return ",".join(str(tag) for tag in tags)


def string_to_tags(tags_string: Optional[str]) -> List[str]:
    """将逗号分隔的字符串转换为标签列表"""
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(",") if tag.strip()]


def json_to_string(data: Any) -> Optional[str]:
    """将对象转换为JSON字符串"""
    if data is None:
        return None
    import json
    return json.dumps(data, ensure_ascii=False)


def string_to_json(json_string: Optional[str]) -> Any:
    """将JSON字符串转换为对象"""
    if not json_string:
        return None
    import json
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return None
