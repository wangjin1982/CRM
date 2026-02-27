"""商机模块初始化数据"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.config.database import async_session_maker
from app.models.opportunity import StageDef


async def init_stages():
    """初始化销售阶段"""
    async with async_session_maker() as session:
        # 检查是否已有数据
        result = await session.execute(select(StageDef))
        if result.scalar_one_or_none():
            print("销售阶段数据已存在，跳过初始化")
            return

        # 创建默认销售阶段
        stages = [
            StageDef(
                stage_name="线索",
                stage_code="lead",
                stage_order=1,
                stage_type="normal",
                probability=10,
                duration_days=7,
                is_active=True,
            ),
            StageDef(
                stage_name="需求确认",
                stage_code="qualified",
                stage_order=2,
                stage_type="normal",
                probability=20,
                duration_days=14,
                is_active=True,
            ),
            StageDef(
                stage_name="方案报价",
                stage_code="proposal",
                stage_order=3,
                stage_type="normal",
                probability=40,
                duration_days=21,
                is_active=True,
            ),
            StageDef(
                stage_name="谈判协商",
                stage_code="negotiation",
                stage_order=4,
                stage_type="normal",
                probability=60,
                duration_days=30,
                is_active=True,
            ),
            StageDef(
                stage_name="合同审核",
                stage_code="contract",
                stage_order=5,
                stage_type="normal",
                probability=80,
                duration_days=14,
                is_active=True,
            ),
            StageDef(
                stage_name="赢单",
                stage_code="won",
                stage_order=6,
                stage_type="won",
                probability=100,
                duration_days=None,
                is_active=True,
            ),
            StageDef(
                stage_name="输单",
                stage_code="lost",
                stage_order=7,
                stage_type="lost",
                probability=0,
                duration_days=None,
                is_active=True,
            ),
        ]

        for stage in stages:
            session.add(stage)

        await session.commit()
        print(f"已创建 {len(stages)} 个销售阶段")


async def main():
    """主函数"""
    print("开始初始化商机模块数据...")
    await init_stages()
    print("商机模块数据初始化完成!")


if __name__ == "__main__":
    asyncio.run(main())
