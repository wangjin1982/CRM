import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../../views/auth/Login.vue'),
    meta: { requiresAuth: false, layout: 'blank' },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../../views/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/customers',
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'CustomerList',
        component: () => import('../../views/customer/CustomerList.vue'),
      },
      {
        path: ':id',
        name: 'CustomerDetail',
        component: () => import('../../views/customer/CustomerDetail.vue'),
      },
    ],
  },
  {
    path: '/opportunities',
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'OpportunityList',
        component: () => import('../../views/opportunity/OpportunityList.vue'),
      },
      {
        path: ':id',
        name: 'OpportunityDetail',
        component: () => import('../../views/opportunity/OpportunityDetail.vue'),
      },
      {
        path: ':id/edit',
        name: 'OpportunityEdit',
        component: () => import('../../views/opportunity/OpportunityDetail.vue'),
      },
    ],
  },
  {
    path: '/funnel',
    name: 'FunnelView',
    component: () => import('../../views/opportunity/FunnelView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/activity',
    name: 'ActivityDashboard',
    component: () => import('../../views/activity/ActivityDashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analytics',
    name: 'AnalyticsDashboard',
    component: () => import('../../views/analytics/AnalyticsDashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/ai',
    name: 'AIWorkbench',
    component: () => import('../../views/ai/AIWorkbench.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/kanban',
    name: 'KanbanView',
    component: () => import('../../views/opportunity/FunnelView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/system',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'users',
        name: 'Users',
        component: () => import('../../views/system/UserManage.vue'),
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('../../views/system/RoleManage.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 加载用户信息
  if (!authStore.user && authStore.token) {
    authStore.loadUserFromStorage()
  }

  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
