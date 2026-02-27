import request from './request'
import type { LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse } from '../types/auth'

export const authApi = {
  // 登录
  login: (data: LoginRequest) => request.post<any, LoginResponse>('/auth/login', data),

  // 登出
  logout: () => request.post('/auth/logout'),

  // 刷新Token
  refreshToken: (data: RefreshTokenRequest) => request.post<any, RefreshTokenResponse>('/auth/refresh', data),

  // 获取当前用户
  getCurrentUser: () => request.get('/auth/me'),
}
