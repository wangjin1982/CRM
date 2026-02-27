"""客户相关Schema"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
import json


# ==================== 基础Schema ====================
class CustomerBase(BaseModel):
    """客户基础Schema"""
    customer_name: str = Field(..., min_length=1, max_length=200, description="1#客户名称（中）")
    customer_name_en: Optional[str] = Field(None, max_length=200, description="1#客户名称（EN）")
    region: Optional[str] = Field(None, max_length=50, description="区域")
    customer_type_3: Optional[str] = Field(None, max_length=50, description="3#客户类型")
    customer_level_3: Optional[str] = Field(None, max_length=50, description="3#客户分级")
    deal_customer_5: Optional[int] = Field(None, ge=0, le=1, description="5#成交客户(0/1)")
    electrical_engineer_count_5: Optional[int] = Field(None, ge=0, description="5#电气工程师人数")
    owner_name_3: Optional[str] = Field(None, max_length=50, description="3#负责人")
    customer_type: str = Field(..., pattern="^(enterprise|individual)$", description="客户类型")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    company_size: Optional[str] = Field(None, max_length=50, description="公司规模")
    legal_person: Optional[str] = Field(None, max_length=50, description="法人代表")
    registered_capital: Optional[Decimal] = Field(None, ge=0, description="注册资本")
    establish_date: Optional[date] = Field(None, description="成立日期")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    district: Optional[str] = Field(None, max_length=50, description="区县")
    address: Optional[str] = Field(None, max_length=500, description="详细地址")
    website: Optional[str] = Field(None, max_length=200, description="官方网站")
    company_info: Optional[str] = Field(None, description="公司信息")
    product_info: Optional[str] = Field(None, description="产品信息")
    source: Optional[str] = Field(None, max_length=50, description="客户来源")
    level: Optional[str] = Field("C", pattern="^(A|B|C|D)$", description="客户级别")
    owner_id: Optional[int] = Field(None, description="负责人ID")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    remarks: Optional[str] = Field(None, description="备注")


class CustomerCreate(CustomerBase):
    """创建客户Schema"""
    pass


class CustomerUpdate(CustomerBase):
    """更新客户Schema"""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=200)
    customer_name_en: Optional[str] = Field(None, max_length=200)
    region: Optional[str] = Field(None, max_length=50)
    customer_type_3: Optional[str] = Field(None, max_length=50)
    customer_level_3: Optional[str] = Field(None, max_length=50)
    deal_customer_5: Optional[int] = Field(None, ge=0, le=1)
    electrical_engineer_count_5: Optional[int] = Field(None, ge=0)
    owner_name_3: Optional[str] = Field(None, max_length=50)
    customer_type: Optional[str] = Field(None, pattern="^(enterprise|individual)$")
    level: Optional[str] = Field(None, pattern="^(A|B|C|D)$")


# ==================== 响应Schema ====================
class OwnerInfo(BaseModel):
    """负责人信息"""
    id: int
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class ContactSummary(BaseModel):
    """联系人摘要"""
    id: int
    name: str
    title: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    is_primary: bool = False

    class Config:
        from_attributes = True


class CustomerStatistics(BaseModel):
    """客户统计信息"""
    opportunity_count: int = 0
    visit_count: int = 0
    last_visit_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None


class CustomerResponse(CustomerBase):
    """客户响应Schema"""
    id: int
    customer_no: str
    status: str
    owner: Optional[OwnerInfo] = None
    statistics: CustomerStatistics = Field(default_factory=CustomerStatistics)
    ai_summary: Optional[str] = None
    ai_insights: Optional[Dict[str, Any]] = None
    data_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _fill_statistics(cls, data):
        """兼容ORM对象：自动从扁平统计字段组装statistics

        注意：不要在这里直接修改 ORM 对象属性，避免把仅用于响应的临时转换值
        （例如 tags:list）回写到数据库会话，导致读接口提交时报类型错误。
        """
        def _parse_tags(value: Any) -> List[str]:
            if value is None:
                return []
            if isinstance(value, list):
                return [str(v).strip() for v in value if str(v).strip()]
            if isinstance(value, str):
                text = value.strip()
                if not text:
                    return []
                if text.startswith("[") and text.endswith("]"):
                    try:
                        parsed = json.loads(text)
                        if isinstance(parsed, list):
                            return [str(v).strip() for v in parsed if str(v).strip()]
                    except json.JSONDecodeError:
                        pass
                return [segment.strip() for segment in text.split(",") if segment.strip()]
            return []

        def _parse_ai_insights(value: Any) -> Optional[Dict[str, Any]]:
            if value is None or value == "":
                return None
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                text = value.strip()
                if not text:
                    return None
                try:
                    parsed = json.loads(text)
                    return parsed if isinstance(parsed, dict) else None
                except json.JSONDecodeError:
                    return None
            return None

        if isinstance(data, dict):
            data = dict(data)
            data["tags"] = _parse_tags(data.get("tags"))
            data["ai_insights"] = _parse_ai_insights(data.get("ai_insights"))
            if not data.get("statistics"):
                data["statistics"] = {
                    "opportunity_count": data.get("opportunity_count") or 0,
                    "visit_count": data.get("visit_count") or 0,
                    "last_visit_at": data.get("last_visit_at"),
                    "last_activity_at": data.get("last_activity_at"),
                }
            return data

        # ORM对象转dict，避免污染session中的对象状态
        data_dict = {}
        for field_name in cls.model_fields.keys():
            if field_name == "statistics":
                continue
            if hasattr(data, field_name):
                data_dict[field_name] = getattr(data, field_name)

        data_dict["tags"] = _parse_tags(data_dict.get("tags"))
        data_dict["ai_insights"] = _parse_ai_insights(data_dict.get("ai_insights"))
        if not data_dict.get("statistics"):
            data_dict["statistics"] = {
                "opportunity_count": getattr(data, "opportunity_count", 0) or 0,
                "visit_count": getattr(data, "visit_count", 0) or 0,
                "last_visit_at": getattr(data, "last_visit_at", None),
                "last_activity_at": getattr(data, "last_activity_at", None),
            }
        return data_dict

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerResponse):
    """客户详情响应Schema"""
    contacts: List[ContactSummary] = []

    class Config:
        from_attributes = True


# ==================== 列表查询Schema ====================
class CustomerQueryParams(BaseModel):
    """客户查询参数"""
    keyword: Optional[str] = Field(None, description="客户名称搜索")
    customer_type: Optional[str] = Field(None, pattern="^(enterprise|individual)$")
    level: Optional[str] = Field(None, pattern="^(A|B|C|D)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive|pool)$")
    owner_id: Optional[int] = None
    tags: Optional[List[str]] = None
    region: Optional[str] = None
    industry: Optional[str] = None
    source: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at", description="排序字段")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class CustomerListResponse(BaseModel):
    """客户列表响应"""
    items: List[CustomerResponse]
    total: int
    page: int
    page_size: int


# ==================== 转移Schema ====================
class CustomerTransfer(BaseModel):
    """客户转移Schema"""
    to_user_id: int = Field(..., description="目标用户ID")
    remark: Optional[str] = Field(None, description="转移备注")


# ==================== 360视图Schema ====================
class TimelineItem(BaseModel):
    """时间轴条目"""
    type: str
    title: str
    content: str
    created_at: datetime
    created_by: Optional[str] = None


class Customer360ViewResponse(BaseModel):
    """客户360度视图响应"""
    customer: CustomerDetailResponse
    contacts: List[ContactSummary]
    opportunities: List[Dict[str, Any]] = []
    visits: List[Dict[str, Any]] = []
    interactions: List[Dict[str, Any]] = []
    tasks: List[Dict[str, Any]] = []
    documents: List[Dict[str, Any]] = []
    timeline: List[TimelineItem] = []


# ==================== 批量操作Schema ====================
class CustomerBatchOperation(BaseModel):
    """客户批量操作Schema"""
    action: str = Field(..., pattern="^(transfer|assignTags|changeLevel|changeStatus)$")
    customer_ids: List[int] = Field(..., min_items=1, description="客户ID列表")
    params: Dict[str, Any] = Field(default_factory=dict, description="操作参数")
