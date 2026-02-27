"""分析模块请求Schema"""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ReportCreateRequest(BaseModel):
    """创建报表"""
    report_name: str = Field(..., min_length=2, max_length=100)
    report_code: str = Field(..., min_length=2, max_length=100)
    report_type: str = Field(..., min_length=2, max_length=50)
    config: Dict[str, Any] = Field(default_factory=dict)
    sql_template: Optional[str] = None
    is_active: bool = True


class ReportExecuteParams(BaseModel):
    """报表执行参数"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
