/**
 * 权限检查工具
 */
import { useAuthStore } from '@/core/stores'

export type Permission = string

export function hasPermission(permission: Permission): boolean {
  const authStore = useAuthStore()
  // 管理员拥有所有权限
  if (authStore.user?.is_admin) return true
  // TODO: 实现完整的权限检查逻辑
  return true
}

export function hasAnyPermission(permissions: Permission[]): boolean {
  return permissions.some((p) => hasPermission(p))
}

export function hasAllPermissions(permissions: Permission[]): boolean {
  return permissions.every((p) => hasPermission(p))
}
