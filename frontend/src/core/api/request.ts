import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '../stores/auth'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 文件流直接返回，避免按JSON业务结构解析
    if (
      response.request?.responseType === 'blob' ||
      response.data instanceof Blob ||
      response.data instanceof ArrayBuffer
    ) {
      return response.data
    }

    const payload = response.data

    // 兼容后端统一响应结构: { code, message, data }
    if (
      payload &&
      typeof payload === 'object' &&
      Object.prototype.hasOwnProperty.call(payload, 'code') &&
      Object.prototype.hasOwnProperty.call(payload, 'data')
    ) {
      const { code, message, data } = payload
      if (code === 200) {
        return data
      }
      return Promise.reject(new Error(message || '请求失败'))
    }

    // 兼容后端裸JSON响应（如部分customers接口）
    return payload
  },
  (error) => {
    const authStore = useAuthStore()

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Token过期或无效
          authStore.logout()
          window.location.href = '/login'
          break
        case 403:
          console.error('无权限访问')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器错误')
          break
        default:
          console.error(data.message || '请求失败')
      }
    }

    return Promise.reject(error)
  }
)

export default request
