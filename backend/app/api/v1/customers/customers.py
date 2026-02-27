"""客户管理API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.sys.user import User
from app.schemas.customer.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerDetailResponse,
    CustomerListResponse,
    CustomerQueryParams,
    CustomerTransfer,
    CustomerBatchOperation,
    Customer360ViewResponse,
)
from app.schemas.common import CommonResponse
from app.services.customer.customer_service import CustomerService
from app.core.utils.response import success_response

router = APIRouter()


@router.get("", response_model=CustomerListResponse, summary="获取客户列表")
async def get_customers(
    keyword: str = Query(None, description="客户名称搜索"),
    customer_type: str = Query(None, regex="^(enterprise|individual)$", description="客户类型"),
    level: str = Query(None, regex="^(A|B|C|D)$", description="客户级别"),
    status: str = Query(None, regex="^(active|inactive|pool)$", description="客户状态"),
    owner_id: int = Query(None, description="负责人ID"),
    tags: str = Query(None, description="标签(逗号分隔)"),
    region: str = Query(None, description="区域"),
    industry: str = Query(None, description="所属行业"),
    source: str = Query(None, description="客户来源"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="排序方向"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取客户列表

    支持多条件筛选和分页查询
    """
    # 构建查询参数
    tag_list = tags.split(",") if tags else None

    params = CustomerQueryParams(
        keyword=keyword,
        customer_type=customer_type,
        level=level,
        status=status,
        owner_id=owner_id,
        tags=tag_list,
        region=region,
        industry=industry,
        source=source,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    customers, total = await CustomerService.get_customers_paginated(db, params)

    return CustomerListResponse(
        items=customers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse, summary="获取客户详情")
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取客户详情

    包含客户基本信息和联系人列表
    """
    customer = await CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )

    return customer


@router.get("/{customer_id}/360view", response_model=Customer360ViewResponse, summary="客户360度视图")
async def get_customer_360_view(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取客户360度视图

    整合客户的所有关联信息：基本信息、联系人、商机、拜访记录、交互记录、时间轴等
    """
    view_data = await CustomerService.get_customer_360_view(db, customer_id)
    if not view_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )

    return view_data


@router.post("", response_model=CustomerResponse, summary="创建客户", status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建新客户

    - **customer_name**: 客户名称（必填）
    - **customer_type**: 客户类型（enterprise/individual）
    - **level**: 客户级别（A/B/C/D）
    - **owner_id**: 负责人ID（不填则默认为当前用户）
    """
    # 如果没有指定负责人，使用当前用户
    if not customer_data.owner_id:
        customer_data.owner_id = current_user.id

    customer = await CustomerService.create_customer(
        db,
        customer_data,
        creator_id=current_user.id,
        owner_name=current_user.real_name,
    )

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse, summary="更新客户")
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新客户信息

    只更新提供的字段，未提供的字段保持不变
    """
    customer = await CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )

    updated_customer = await CustomerService.update_customer(
        db,
        customer,
        customer_data,
        updater_id=current_user.id,
        owner_name=None,
    )

    return updated_customer


@router.delete("/{customer_id}", response_model=CommonResponse, summary="删除客户")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除客户（软删除）

    客户数据不会被物理删除，只是标记为已删除
    """
    customer = await CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )

    await CustomerService.delete_customer(db, customer)

    return success_response(message="客户删除成功")


@router.post("/{customer_id}/transfer", response_model=CommonResponse, summary="转移客户")
async def transfer_customer(
    customer_id: int,
    transfer_data: CustomerTransfer,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    转移客户负责人

    将客户转移给其他用户负责
    """
    customer = await CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在",
        )

    await CustomerService.transfer_customer(db, customer, transfer_data)

    return success_response(message="客户转移成功")


@router.post("/batch", response_model=CommonResponse, summary="批量操作客户")
async def batch_operation(
    operation_data: CustomerBatchOperation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量操作客户

    支持的操作类型：
    - **transfer**: 批量转移客户
    - **assignTags**: 批量分配标签
    - **changeLevel**: 批量修改级别
    - **changeStatus**: 批量修改状态
    """
    if operation_data.action == "transfer":
        to_user_id = operation_data.params.get("to_user_id")
        if not to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少to_user_id参数",
            )

        count = await CustomerService.batch_transfer(
            db,
            operation_data.customer_ids,
            to_user_id,
        )

        return success_response(message=f"成功转移{count}个客户")

    elif operation_data.action == "assignTags":
        tags = operation_data.params.get("tags") or []
        count = await CustomerService.batch_assign_tags(
            db,
            operation_data.customer_ids,
            tags,
        )
        return success_response(message=f"成功更新{count}个客户标签")

    elif operation_data.action == "changeLevel":
        level = operation_data.params.get("level")
        if not level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少level参数",
            )
        count = await CustomerService.batch_change_level(
            db,
            operation_data.customer_ids,
            level,
        )
        return success_response(message=f"成功更新{count}个客户级别")

    elif operation_data.action == "changeStatus":
        customer_status = operation_data.params.get("status")
        if not customer_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少status参数",
            )
        count = await CustomerService.batch_change_status(
            db,
            operation_data.customer_ids,
            customer_status,
        )
        return success_response(message=f"成功更新{count}个客户状态")

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的操作类型: {operation_data.action}",
        )


@router.get("/export", summary="导出客户数据")
async def export_customers(
    customer_ids: str = Query(None, description="客户ID列表(逗号分隔)"),
    keyword: str = Query(None, description="客户名称搜索"),
    customer_type: str = Query(None, regex="^(enterprise|individual)$", description="客户类型"),
    level: str = Query(None, regex="^(A|B|C|D)$", description="客户级别"),
    status: str = Query(None, regex="^(active|inactive|pool)$", description="客户状态"),
    owner_id: int = Query(None, description="负责人ID"),
    tags: str = Query(None, description="标签(逗号分隔)"),
    region: str = Query(None, description="区域"),
    industry: str = Query(None, description="所属行业"),
    source: str = Query(None, description="客户来源"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    导出客户数据为Excel

    支持按ID列表导出或按查询条件导出
    """
    from fastapi.responses import Response
    from app.services.customer.import_export_service import ImportExportService

    # 解析客户ID列表
    id_list = None
    if customer_ids:
        id_list = [int(id.strip()) for id in customer_ids.split(",") if id.strip()]

    # 构建查询参数
    tag_list = tags.split(",") if tags else None
    params = CustomerQueryParams(
        keyword=keyword,
        customer_type=customer_type,
        level=level,
        status=status,
        owner_id=owner_id,
        tags=tag_list,
        region=region,
        industry=industry,
        source=source,
        page=1,
        page_size=10000,  # 导出时使用较大的页面大小
    )

    # 生成Excel文件
    excel_data = await ImportExportService.export_customers(
        db,
        customer_ids=id_list,
        params=params if not id_list else None,
    )

    # 返回文件
    filename = f"customers_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/import", summary="导入客户数据")
async def import_customers(
    file: UploadFile = File(..., description="Excel文件"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    从Excel导入客户数据

    请使用导出功能获取模板文件
    """
    from app.services.customer.import_export_service import ImportExportService

    file_data = await file.read()
    result = await ImportExportService.import_customers(
        db,
        file_data=file_data,
        creator_id=current_user.id,
        owner_name=current_user.real_name,
    )

    return {
        "code": 200,
        "message": "导入完成",
        "data": result,
    }


@router.get("/import-template", summary="下载导入模板")
async def get_import_template(
    current_user: User = Depends(get_current_user),
):
    """
    下载客户导入模板

    返回Excel格式的模板文件
    """
    from fastapi.responses import Response
    from app.services.customer.import_export_service import ImportExportService

    template_data = ImportExportService.get_import_template()

    return Response(
        content=template_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=customer_import_template.xlsx"
        }
    )
