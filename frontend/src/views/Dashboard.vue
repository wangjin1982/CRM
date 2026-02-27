<template>
  <div class="min-h-screen bg-slate-50">
    <header class="border-b bg-white">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div>
          <h1 class="text-lg font-semibold text-slate-900">CRM 控制台</h1>
          <p class="text-xs text-slate-500">客户与商机运营总览</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="rounded-md bg-slate-100 px-3 py-1 text-sm text-slate-700">
            {{ authStore.user?.username || '未命名用户' }}
          </span>
          <button
            class="rounded-md bg-rose-600 px-3 py-2 text-sm font-medium text-white hover:bg-rose-700"
            @click="handleLogout"
          >
            退出登录
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <section class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div v-for="metric in metrics" :key="metric.label" class="rounded-xl border bg-white p-4 shadow-sm">
          <p class="text-sm text-slate-500">{{ metric.label }}</p>
          <p class="mt-2 text-2xl font-semibold text-slate-900">{{ metric.value }}</p>
        </div>
      </section>

      <section class="mb-6 rounded-xl border bg-white p-4 shadow-sm">
        <h2 class="mb-3 text-base font-semibold text-slate-900">模块入口</h2>
        <div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          <button
            v-for="item in modules"
            :key="item.path"
            class="rounded-lg border p-4 text-left transition hover:border-indigo-300 hover:bg-indigo-50"
            @click="go(item.path)"
          >
            <p class="text-sm font-semibold text-slate-900">{{ item.title }}</p>
            <p class="mt-1 text-sm text-slate-600">{{ item.desc }}</p>
          </button>
        </div>
      </section>

      <section class="rounded-xl border bg-white p-4 shadow-sm">
        <h2 class="mb-3 text-base font-semibold text-slate-900">快捷操作</h2>
        <div class="flex flex-wrap gap-3">
          <button
            class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            @click="go('/customers')"
          >
            查看客户列表
          </button>
          <button
            class="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
            @click="go('/opportunities')"
          >
            查看商机列表
          </button>
          <button
            class="rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
            @click="go('/analytics')"
          >
            查看分析看板
          </button>
        </div>
        <p v-if="loadError" class="mt-3 text-sm text-amber-700">
          指标加载失败，仍可直接进入各业务模块。({{ loadError }})
        </p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/core/stores'
import { analyticsApi, activityApi } from '@/core/api'

const router = useRouter()
const authStore = useAuthStore()
const loadError = ref('')
const home = ref<any>(null)
const activityStats = ref<any>(null)

const modules = [
  { path: '/customers', title: '客户管理', desc: '客户档案、联系人、标签、导入导出' },
  { path: '/opportunities', title: '商机管理', desc: '商机推进、阶段管理、赢单输单跟踪' },
  { path: '/funnel', title: '销售漏斗', desc: '阶段分布、转化率、看板视图' },
  { path: '/activity', title: '销售行为', desc: '拜访、跟进、任务与日程管理' },
  { path: '/analytics', title: '数据分析', desc: '业务指标、统计分析、报表视图' },
  { path: '/ai', title: 'AI 工作台', desc: 'AI洞察、建议生成、策略辅助' },
]

const formatWanAmount = (amount?: number) => {
  const value = Number(amount || 0)
  return (value / 10000).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

const metrics = computed(() => [
  { label: '客户总数', value: home.value?.summary?.total_customers ?? 0 },
  { label: 'Open 商机数', value: home.value?.summary?.total_open_opportunities ?? 0 },
  { label: 'Open 金额（万元）', value: formatWanAmount(home.value?.summary?.total_open_amount) },
  { label: '待办任务', value: activityStats.value?.summary?.total_tasks ?? 0 },
])

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const go = (path: string) => {
  router.push(path)
}

const loadMetrics = async () => {
  loadError.value = ''
  try {
    const [homeData, activityData] = await Promise.all([
      analyticsApi.dashboardHome(),
      activityApi.getStatistics(),
    ])
    home.value = homeData
    activityStats.value = activityData
  } catch (error: any) {
    loadError.value = error?.message || '请求失败'
  }
}

onMounted(() => {
  loadMetrics()
})
</script>
