/**
 * 客户资源管理相关API
 */
import request from './request'
import type {
  Customer,
  CustomerCreate,
  CustomerUpdate,
  CustomerDetail,
  CustomerListResponse,
  CustomerQueryParams,
  CustomerTransfer,
  CustomerBatchOperation,
  Customer360View,
  CustomerInteraction,
  CustomerInteractionCreate,
  CustomerInteractionListResponse,
  Contact,
  ContactCreate,
  ContactUpdate,
  ContactListResponse,
  CustomerTag,
  TagCreate,
  TagUpdate,
  TagListResponse,
  ImportResult,
} from '../types'

// ==================== 客户管理API ====================

export const customerApi = {
  /**
   * 获取客户列表
   */
  getList(params: CustomerQueryParams): Promise<CustomerListResponse> {
    return request.get('/customers', { params })
  },

  /**
   * 获取客户详情
   */
  getDetail(id: number): Promise<CustomerDetail> {
    return request.get(`/customers/${id}`)
  },

  /**
   * 获取客户360度视图
   */
  get360View(id: number): Promise<Customer360View> {
    return request.get(`/customers/${id}/360view`)
  },

  /**
   * 创建客户
   */
  create(data: CustomerCreate): Promise<Customer> {
    return request.post('/customers', data)
  },

  /**
   * 更新客户
   */
  update(id: number, data: CustomerUpdate): Promise<Customer> {
    return request.put(`/customers/${id}`, data)
  },

  /**
   * 删除客户（软删除）
   */
  delete(id: number): Promise<{ code: number; message: string }> {
    return request.delete(`/customers/${id}`)
  },

  /**
   * 转移客户
   */
  transfer(id: number, data: CustomerTransfer): Promise<{ code: number; message: string }> {
    return request.post(`/customers/${id}/transfer`, data)
  },

  /**
   * 批量操作客户
   */
  batchOperation(data: CustomerBatchOperation): Promise<{ code: number; message: string }> {
    return request.post('/customers/batch', data)
  },

  /**
   * 导出客户数据
   */
  export(params?: {
    customer_ids?: string
    keyword?: string
    customer_type?: string
    level?: string
    status?: string
    owner_id?: number
    tags?: string
    region?: string
    industry?: string
    source?: string
  }): Promise<Blob> {
    return request.get('/customers/export', {
      params,
      responseType: 'blob',
    })
  },

  /**
   * 导入客户数据
   */
  import(file: File): Promise<ImportResult> {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/customers/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  /**
   * 下载导入模板
   */
  downloadTemplate(): Promise<Blob> {
    return request.get('/customers/import-template', {
      responseType: 'blob',
    })
  },
}

// ==================== 客户交互记录API ====================

export const interactionApi = {
  /**
   * 获取客户交互记录
   */
  getByCustomer(
    customerId: number,
    params?: { page?: number; page_size?: number }
  ): Promise<CustomerInteractionListResponse> {
    return request.get(`/customers/interactions/customer/${customerId}`, { params })
  },

  /**
   * 创建交互记录
   */
  create(customerId: number, data: CustomerInteractionCreate): Promise<CustomerInteraction> {
    return request.post(`/customers/interactions/customer/${customerId}`, data)
  },

  /**
   * 删除交互记录
   */
  delete(interactionId: number): Promise<{ code: number; message: string }> {
    return request.delete(`/customers/interactions/${interactionId}`)
  },
}

// ==================== 联系人管理API ====================

export const contactApi = {
  /**
   * 获取客户的联系人列表
   */
  getByCustomer(customerId: number): Promise<ContactListResponse> {
    return request.get(`/customers/contacts/customer/${customerId}`)
  },

  /**
   * 获取联系人详情
   */
  getDetail(id: number): Promise<Contact> {
    return request.get(`/customers/contacts/${id}`)
  },

  /**
   * 创建联系人
   */
  create(customerId: number, data: ContactCreate): Promise<Contact> {
    return request.post(`/customers/contacts/customer/${customerId}`, data)
  },

  /**
   * 更新联系人
   */
  update(id: number, data: ContactUpdate): Promise<Contact> {
    return request.put(`/customers/contacts/${id}`, data)
  },

  /**
   * 删除联系人
   */
  delete(id: number): Promise<{ code: number; message: string }> {
    return request.delete(`/customers/contacts/${id}`)
  },

  /**
   * 设置主要联系人
   */
  setPrimary(id: number): Promise<Contact> {
    return request.post(`/customers/contacts/${id}/set-primary`)
  },
}

// ==================== 标签管理API ====================

export const tagApi = {
  /**
   * 获取标签列表
   */
  getList(tagType?: string): Promise<TagListResponse> {
    return request.get('/customers/tags', {
      params: { tag_type: tagType },
    })
  },

  /**
   * 创建标签
   */
  create(data: TagCreate): Promise<CustomerTag> {
    return request.post('/customers/tags', data)
  },

  /**
   * 更新标签
   */
  update(id: number, data: TagUpdate): Promise<CustomerTag> {
    return request.put(`/customers/tags/${id}`, data)
  },

  /**
   * 删除标签
   */
  delete(id: number): Promise<{ code: number; message: string }> {
    return request.delete(`/customers/tags/${id}`)
  },
}
