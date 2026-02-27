"""AI模块模型"""
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text, BigInteger, ForeignKey, JSON

from app.models.base import Base, TimestampMixin


class AIConfig(Base, TimestampMixin):
    """AI配置表"""
    __tablename__ = "ai_config"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False, default="mock", comment="服务提供商")
    model_name = Column(String(100), nullable=False, default="mock-model", comment="模型名称")
    api_base = Column(String(255), comment="API地址")
    api_key = Column(String(255), comment="API密钥")
    temperature = Column(Numeric(3, 2), default=0.3, comment="温度")
    max_tokens = Column(Integer, default=1500, comment="最大token")
    timeout_seconds = Column(Integer, default=30, comment="超时秒数")
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    remark = Column(String(255), comment="备注")


class AIPromptTemplate(Base, TimestampMixin):
    """提示词模板表"""
    __tablename__ = "ai_prompt_template"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    template_code = Column(String(100), unique=True, nullable=False, index=True)
    template_name = Column(String(100), nullable=False)
    scene = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    input_schema = Column(JSON, comment="输入参数定义")
    is_active = Column(Boolean, default=True, nullable=False)


class AIRequestLog(Base, TimestampMixin):
    """AI请求日志"""
    __tablename__ = "ai_request_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    scene = Column(String(100), nullable=False, index=True)
    request_id = Column(String(64), unique=True, nullable=False, index=True)
    input_payload = Column(JSON)
    output_payload = Column(JSON)
    prompt = Column(Text)
    model_name = Column(String(100))
    status = Column(String(20), default="success", index=True)
    latency_ms = Column(Integer)
    tokens = Column(Integer)
    error_message = Column(Text)
    created_by = Column(BigInteger, ForeignKey("sys_user.id"))


class AIAnalysisResult(Base, TimestampMixin):
    """AI分析结果"""
    __tablename__ = "ai_analysis_result"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    scene = Column(String(100), nullable=False, index=True)
    related_type = Column(String(50), nullable=False, index=True)
    related_id = Column(BigInteger, nullable=False, index=True)
    score = Column(Numeric(5, 2), comment="评分")
    level = Column(String(20), comment="等级")
    summary = Column(Text)
    result_data = Column(JSON)
    request_log_id = Column(BigInteger, ForeignKey("ai_request_log.id"))


class AIRiskAlert(Base, TimestampMixin):
    """AI风险预警"""
    __tablename__ = "ai_risk_alert"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False, index=True)
    alert_level = Column(String(20), nullable=False, index=True)
    related_type = Column(String(50), nullable=False, index=True)
    related_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    suggestion = Column(Text)
    status = Column(String(20), default="new", index=True, comment="new/acknowledged/resolved")
    acknowledged_by = Column(BigInteger, ForeignKey("sys_user.id"))
    acknowledged_at = Column(DateTime)
    resolved_by = Column(BigInteger, ForeignKey("sys_user.id"))
    resolved_at = Column(DateTime)


class AISearchHistory(Base, TimestampMixin):
    """AI自然语言查询历史"""
    __tablename__ = "ai_search_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    intent = Column(String(50), index=True)
    sql_text = Column(Text)
    answer = Column(Text)
    result_count = Column(Integer, default=0)
    created_by = Column(BigInteger, ForeignKey("sys_user.id"))
