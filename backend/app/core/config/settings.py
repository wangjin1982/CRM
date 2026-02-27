"""应用配置模块"""
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # 应用配置
    APP_NAME: str = "CRM系统"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]

    # 数据库配置
    DATABASE_URL: str = f"sqlite+aiosqlite:///{(BASE_DIR / 'data' / 'crm.db').as_posix()}"
    DATABASE_ECHO: bool = False

    # Redis配置 (可选)
    REDIS_URL: str = "redis://:redis_password@localhost:6379/0"

    # GLM API配置
    ZHIPUAI_API_KEY: str = ""

    # OpenAI配置 (备用)
    OPENAI_API_KEY: str = ""

    # JWT配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 文件上传
    UPLOAD_DIR: str = "/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # 时区
    TZ: str = "Asia/Shanghai"


# 全局配置实例
settings = Settings()
