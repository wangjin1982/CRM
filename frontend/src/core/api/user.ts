import request from './request'
import type { UserCreate, UserUpdate, UserResponse, PageParams, PageResponse } from '../types/user'

export const userApi = {
  // 获取用户列表
  getUsers: (params: PageParams) => request.get<any, PageResponse<UserResponse>>('/users', { params }),

  // 获取用户详情
  getUser: (id: number) => request.get<any, UserResponse>(`/users/${id}`),

  // 创建用户
  createUser: (data: UserCreate) => request.post('/users', data),

  // 更新用户
  updateUser: (id: number, data: UserUpdate) => request.put(`/users/${id}`, data),

  // 删除用户
  deleteUser: (id: number) => request.delete(`/users/${id}`),

  // 分配角色
  assignRoles: (id: number, roleIds: number[]) => request.post(`/users/${id}/roles`, roleIds),

  // 修改密码
  changePassword: (data: { old_password: string; new_password: string }) =>
    request.post('/users/change-password', data),
}
