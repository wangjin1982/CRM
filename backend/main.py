#!/usr/bin/env python3
"""
CRM系统主应用程序入口
"""
import uvicorn
from app.core.config.settings import settings


def main():
    """运行应用"""
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
