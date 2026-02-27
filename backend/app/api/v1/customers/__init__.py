"""客户模块API路由"""
from fastapi import APIRouter

from app.api.v1.customers import customers, contacts, tags, interactions

# 创建客户模块路由器
customer_router = APIRouter()

# 注册子路由 - customers路由不需要前缀，因为它的路由已经定义了完整路径
# 直接将customers路由的方法添加到customer_router中
for route in customers.router.routes:
    customer_router.routes.append(route)

# 联系人和标签路由需要前缀
customer_router.include_router(contacts.router, prefix="/contacts", tags=["联系人管理"])
customer_router.include_router(tags.router, prefix="/tags", tags=["标签管理"])
customer_router.include_router(interactions.router, prefix="/interactions", tags=["交互记录"])
