import { router } from './index'
import { useAuthStore } from '../stores'
import type { Router } from 'vue-router'

// 设置路由守卫
export function setupRouterGuards(router: Router) {
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // 检查是否需要认证
    const requiresAuth = to.meta.requiresAuth !== false

    if (requiresAuth && !authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({
        name: 'Login',
        query: { redirect: to.fullPath },
      })
    } else if (to.name === 'Login' && authStore.isAuthenticated) {
      // 已登录，跳转到首页
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  })

  // 路由后置守卫
  router.afterEach((to) => {
    // 设置页面标题
    document.title = `${to.meta.title || 'CRM系统'}`
  })
}
