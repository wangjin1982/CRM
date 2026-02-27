"""数据库初始化脚本"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.config.database import engine, async_session_maker, Base
from app.core.security import jwt_manager
from app.models.sys import User, Role, Permission, UserRole, RolePermission
from app.models.sys.config import SysConfig, SysDict


async def init_database():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建成功")


async def create_default_data():
    """创建默认数据"""
    async with async_session_maker() as session:
        # 创建默认权限
        permissions_data = [
            # 用户管理权限
            {"name": "用户查看", "code": "user:view", "type": "api", "method": "GET", "path": "/api/v1/users"},
            {"name": "用户创建", "code": "user:create", "type": "api", "method": "POST", "path": "/api/v1/users"},
            {"name": "用户编辑", "code": "user:update", "type": "api", "method": "PUT", "path": "/api/v1/users"},
            {"name": "用户删除", "code": "user:delete", "type": "api", "method": "DELETE", "path": "/api/v1/users"},
            # 角色管理权限
            {"name": "角色查看", "code": "role:view", "type": "api", "method": "GET", "path": "/api/v1/roles"},
            {"name": "角色创建", "code": "role:create", "type": "api", "method": "POST", "path": "/api/v1/roles"},
            {"name": "角色编辑", "code": "role:update", "type": "api", "method": "PUT", "path": "/api/v1/roles"},
            {"name": "角色删除", "code": "role:delete", "type": "api", "method": "DELETE", "path": "/api/v1/roles"},
        ]

        for perm_data in permissions_data:
            existing = await session.execute(
                select(Permission).where(Permission.code == perm_data["code"])
            )
            if not existing.scalar_one_or_none():
                permission = Permission(**perm_data)
                session.add(permission)

        await session.commit()
        print("默认权限创建成功")

        # 创建默认角色
        roles_data = [
            {"name": "超级管理员", "code": "admin", "description": "系统超级管理员，拥有所有权限"},
            {"name": "普通用户", "code": "user", "description": "普通用户，拥有基本权限"},
        ]

        for role_data in roles_data:
            existing = await session.execute(
                select(Role).where(Role.code == role_data["code"])
            )
            if not existing.scalar_one_or_none():
                role = Role(**role_data)
                session.add(role)

        await session.commit()
        print("默认角色创建成功")

        # 获取所有权限
        all_permissions = await session.execute(select(Permission))
        all_permissions = all_permissions.scalars().all()

        # 为管理员角色分配所有权限
        admin_role = await session.execute(
            select(Role).where(Role.code == "admin")
        )
        admin_role = admin_role.scalar_one_or_none()

        if admin_role:
            for perm in all_permissions:
                existing = await session.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == admin_role.id,
                        RolePermission.permission_id == perm.id
                    )
                )
                if not existing.scalar_one_or_none():
                    role_perm = RolePermission(role_id=admin_role.id, permission_id=perm.id, created_at=datetime.utcnow())
                    session.add(role_perm)

        await session.commit()
        print("角色权限分配成功")

        # 创建默认管理员用户
        admin_user = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = admin_user.scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@crm.com",
                password_hash=jwt_manager.hash_password("admin123456"),
                real_name="系统管理员",
                is_admin=True,
                status=1,
            )
            session.add(admin_user)
            await session.flush()

            # 分配管理员角色
            user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id, created_at=datetime.utcnow())
            session.add(user_role)

        await session.commit()
        print("默认管理员用户创建成功")
        print("用户名: admin")
        print("密码: admin123456")

        # 创建系统配置
        configs_data = [
            {
                "config_key": "system.title",
                "config_value": "CRM系统",
                "config_type": "string",
                "description": "系统标题",
                "is_public": True,
            },
            {
                "config_key": "system.logo",
                "config_value": "/logo.png",
                "config_type": "string",
                "description": "系统Logo",
                "is_public": True,
            },
        ]

        for config_data in configs_data:
            existing = await session.execute(
                select(SysConfig).where(SysConfig.config_key == config_data["config_key"])
            )
            if not existing.scalar_one_or_none():
                config = SysConfig(**config_data)
                session.add(config)

        await session.commit()
        print("系统配置创建成功")

        # 创建字典数据
        dicts_data = [
            {"dict_type": "user_status", "dict_label": "启用", "dict_value": "1", "sort_order": 1},
            {"dict_type": "user_status", "dict_label": "禁用", "dict_value": "0", "sort_order": 2},
            {"dict_type": "role_status", "dict_label": "启用", "dict_value": "1", "sort_order": 1},
            {"dict_type": "role_status", "dict_label": "禁用", "dict_value": "0", "sort_order": 2},
        ]

        for dict_data in dicts_data:
            existing = await session.execute(
                select(SysDict).where(
                    SysDict.dict_type == dict_data["dict_type"],
                    SysDict.dict_value == dict_data["dict_value"]
                )
            )
            if not existing.scalar_one_or_none():
                sys_dict = SysDict(**dict_data, created_at=datetime.utcnow())
                session.add(sys_dict)

        await session.commit()
        print("字典数据创建成功")


async def main():
    """主函数"""
    print("开始初始化数据库...")
    await init_database()
    await create_default_data()
    print("数据库初始化完成!")


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())
