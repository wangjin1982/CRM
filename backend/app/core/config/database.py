"""数据库配置模块"""
from sqlalchemy import BigInteger, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase

from app.core.config.settings import settings


# SQLite 对 BIGINT PRIMARY KEY 不会自动生成自增值，统一映射为 INTEGER 以保证本地开发可用
@compiles(BigInteger, "sqlite")
def _compile_big_integer_for_sqlite(_type, _compiler, **_kw):
    return "INTEGER"


# 创建异步引擎
# SQLite 不支持连接池，需要特殊处理
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """数据库模型基类"""

    pass


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 导入所有模型以确保表被创建
        from app.models import sys  # noqa: F401
        from app.models import customer  # noqa: F401
        from app.models import opportunity  # noqa: F401
        from app.models import activity  # noqa: F401
        from app.models import ai  # noqa: F401
        from app.models import analytics  # noqa: F401

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

        # 兼容已存在的 SQLite 库：补齐客户表新增字段
        if settings.DATABASE_URL.startswith("sqlite"):
            result = await conn.execute(text("PRAGMA table_info(crm_customer_info)"))
            existing_columns = {row[1] for row in result.fetchall()}
            required_columns = {
                "customer_name_en": "VARCHAR(200)",
                "region": "VARCHAR(50)",
                "customer_type_3": "VARCHAR(50)",
                "customer_level_3": "VARCHAR(50)",
                "deal_customer_5": "INTEGER",
                "electrical_engineer_count_5": "INTEGER",
                "owner_name_3": "VARCHAR(50)",
                "company_info": "TEXT",
                "product_info": "TEXT",
            }
            for column_name, column_type in required_columns.items():
                if column_name not in existing_columns:
                    await conn.execute(
                        text(
                            f"ALTER TABLE crm_customer_info "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )

            ai_config_result = await conn.execute(text("PRAGMA table_info(ai_config)"))
            ai_config_columns = {row[1] for row in ai_config_result.fetchall()}
            if "api_key" not in ai_config_columns:
                await conn.execute(text("ALTER TABLE ai_config ADD COLUMN api_key VARCHAR(255)"))

            # 兼容已存在的阶段定义表：补齐阶段增强字段
            stage_result = await conn.execute(text("PRAGMA table_info(crm_stage_def)"))
            stage_columns = {row[1] for row in stage_result.fetchall()}
            stage_required_columns = {
                "weight": "FLOAT",
                "internal_code": "VARCHAR(20)",
                "customer_journey": "VARCHAR(100)",
                "technical_support": "TEXT",
                "sales_process": "TEXT",
                "stage_criteria": "TEXT",
            }
            for column_name, column_type in stage_required_columns.items():
                if column_name not in stage_columns:
                    await conn.execute(
                        text(
                            f"ALTER TABLE crm_stage_def "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )
