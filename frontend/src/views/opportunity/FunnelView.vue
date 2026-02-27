<template>
  <div class="p-6">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">销售漏斗</h1>
        <p class="text-sm text-gray-500 mt-1">可视化销售机会和转化率</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="selectedUserId"
          class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          @change="handleOwnerChange"
        >
          <option value="">全部销售</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.real_name || user.username }}
          </option>
        </select>
        <button
          class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-2"
          @click="showKanban = !showKanban"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
          {{ showKanban ? '漏斗视图' : '看板视图' }}
        </button>
      </div>
    </div>

    <!-- 漏斗视图 -->
    <div v-if="!showKanban">
      <!-- 汇总卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-gray-500">总商机数</div>
          <div class="text-2xl font-bold mt-1 text-blue-600">{{ funnelData.summary?.total_count || 0 }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-gray-500">总金额</div>
          <div class="text-2xl font-bold mt-1 text-green-600">
            ¥{{ formatAmount(funnelData.summary?.total_amount) }}
          </div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-gray-500">加权金额</div>
          <div class="text-2xl font-bold mt-1 text-indigo-600">
            ¥{{ formatAmount(funnelData.summary?.weighted_amount) }}
          </div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-gray-500">平均商机额</div>
          <div class="text-2xl font-bold mt-1 text-purple-600">
            ¥{{ formatAmount(funnelData.summary?.avg_amount) }}
          </div>
        </div>
      </div>

      <!-- 漏斗图 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-bold mb-4">销售漏斗</h2>
        <div class="space-y-3">
          <div
            v-for="(stage, index) in reversedFunnel"
            :key="stage.stage_id"
            class="relative"
          >
            <div class="flex justify-between items-center mb-1">
              <span class="text-sm font-medium">{{ stage.stage_name }}</span>
              <span class="text-sm text-gray-500">
                {{ stage.count }}个 | ¥{{ formatAmount(stage.amount) }} | {{ stage.probability }}%
              </span>
            </div>
            <div class="relative">
              <div
                class="h-8 rounded"
                :class="getFunnelColor(index)"
                :style="{ width: getFunnelWidth(stage.amount) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 转化率 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-bold mb-4">转化率分析</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="item in conversionRows"
            :key="item.key"
            class="p-4 bg-gray-50 rounded-lg"
          >
            <div class="text-sm text-gray-500 mb-1">{{ item.label }}</div>
            <div class="flex items-end justify-between">
              <div class="text-xl font-bold" :class="getRateColor(item.rate)">
                {{ item.rate.toFixed(1) }}%
              </div>
              <div v-if="item.from_count !== undefined" class="text-xs text-gray-500">
                {{ item.to_count }}/{{ item.from_count }}
              </div>
            </div>
          </div>
        </div>
        <div class="mt-3 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3">
          <div class="text-sm text-blue-700">整体漏斗转化率</div>
          <div class="text-2xl font-bold text-blue-900">
            {{ (conversionRates.overall || 0).toFixed(1) }}%
          </div>
        </div>
      </div>

      <!-- 阶段健康度 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-bold mb-4">阶段健康度</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="health in stageHealthRows"
            :key="health.stage_id"
            class="rounded-lg border p-4"
          >
            <div class="text-sm font-medium text-gray-800">{{ health.stage_name }}</div>
            <div class="mt-2 text-xs text-gray-500">平均停留</div>
            <div class="text-lg font-semibold text-indigo-700">{{ health.avg_days_in_stage.toFixed(1) }} 天</div>
            <div class="mt-2 text-xs text-gray-500">停滞率</div>
            <div class="text-base font-semibold" :class="getRateColor(100 - health.stagnant_rate)">
              {{ health.stagnant_rate.toFixed(1) }}%
            </div>
            <div class="mt-1 text-xs text-gray-500">
              停滞 {{ health.stagnant_count }} / {{ health.count }}
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6 mt-6">
        <h2 class="text-lg font-bold mb-4">下一步建议</h2>
        <div class="space-y-3">
          <div
            v-for="item in recommendations"
            :key="`${item.type}-${item.title}`"
            class="rounded-lg border p-4"
          >
            <div class="flex items-center justify-between">
              <div class="font-medium text-gray-900">{{ item.title }}</div>
              <span
                class="rounded-full px-2 py-0.5 text-xs"
                :class="{
                  'bg-red-100 text-red-700': item.priority === 'high',
                  'bg-yellow-100 text-yellow-700': item.priority === 'medium',
                  'bg-slate-100 text-slate-700': item.priority === 'low',
                }"
              >
                {{ item.priority }}
              </span>
            </div>
            <p class="mt-2 text-sm text-gray-700">{{ item.action }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 看板视图 -->
    <div v-else class="flex gap-4 overflow-x-auto pb-4">
      <div
        v-for="column in kanbanData"
        :key="column.stage_id"
        class="flex-shrink-0 w-80 bg-gray-100 rounded-lg p-4"
      >
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-bold text-gray-900">{{ column.stage_name }}</h3>
          <span class="text-sm text-gray-500">{{ column.probability }}%</span>
        </div>
        <div class="text-sm text-gray-500 mb-3">{{ column.opportunities.length }}个商机</div>

        <div class="space-y-2">
          <div
            v-for="opp in column.opportunities"
            :key="opp.id"
            class="bg-white rounded-lg p-3 shadow-sm cursor-pointer hover:shadow-md transition-shadow"
            @click="viewDetail(opp.id)"
          >
            <div class="font-medium text-sm mb-1">{{ opp.opportunity_name }}</div>
            <div class="text-xs text-gray-500 mb-2">{{ opp.customer_name }}</div>
            <div class="flex justify-between items-center">
              <span class="text-sm font-medium text-indigo-600">
                ¥{{ formatAmount(opp.estimated_amount) }}
              </span>
              <span class="text-xs text-gray-400">{{ opp.days_in_stage }}天</span>
            </div>
            <div v-if="opp.is_stagnant" class="mt-2">
              <span class="px-2 py-0.5 text-xs rounded bg-yellow-100 text-yellow-800">
                停滞
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { funnelApi } from '@/core/api'
import { userApi } from '@/core/api'
import type { FunnelData, KanbanData } from '@/core/types'

const router = useRouter()

// 数据
const funnelData = ref<FunnelData>({ funnel: [], summary: null, conversion_rates: {} })
const kanbanData = ref<KanbanData[]>([])
const users = ref<any[]>([])

const selectedUserId = ref<string | number>('')
const showKanban = ref(false)

const currentOwnerId = computed<number | undefined>(() => {
  if (selectedUserId.value === '' || selectedUserId.value === null || selectedUserId.value === undefined) {
    return undefined
  }
  const parsed = Number(selectedUserId.value)
  return Number.isFinite(parsed) ? parsed : undefined
})

// 反转的漏斗数据（用于从上到下显示）
const reversedFunnel = computed(() => {
  return [...funnelData.value.funnel].reverse()
})

// 转化率
const conversionRates = computed(() => funnelData.value.conversion_rates)
const conversionRows = computed(() => {
  const explicit = funnelData.value.conversion_stages || []
  if (explicit.length > 0) {
    return explicit.map(item => ({
      key: item.key,
      label: `${item.from_stage_name} → ${item.to_stage_name}`,
      rate: item.rate || 0,
      from_count: item.from_count,
      to_count: item.to_count,
    }))
  }

  const entries = Object.entries(conversionRates.value || {})
    .filter(([key]) => key !== 'overall')
  return entries.map(([key, rate]) => ({
    key,
    label: getConversionLabel(key),
    rate: Number(rate) || 0,
  }))
})
const stageHealthRows = computed(() => funnelData.value.stage_health || [])
const recommendations = computed(() => funnelData.value.recommendations || [])

// 加载数据
const loadFunnelData = async () => {
  try {
    funnelData.value = await funnelApi.getFunnel(currentOwnerId.value)
  } catch (error) {
    console.error('Failed to load funnel data:', error)
  }
}

const loadKanbanData = async () => {
  try {
    kanbanData.value = await funnelApi.getKanbanBoard(currentOwnerId.value)
  } catch (error) {
    console.error('Failed to load kanban data:', error)
  }
}

const loadUsers = async () => {
  try {
    const response = await userApi.getUsers({ page: 1, page_size: 100 })
    users.value = response.items
  } catch (error) {
    console.error('Failed to load users:', error)
  }
}

const handleOwnerChange = () => {
  loadFunnelData()
  loadKanbanData()
}

// 格式化金额
const formatAmount = (amount?: number) => {
  if (!amount) return '0'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

// 漏斗宽度（相对于最大金额）
const getFunnelWidth = (amount: number) => {
  const maxAmount = Math.max(...funnelData.value.funnel.map(s => s.amount), 1)
  return (amount / maxAmount) * 100
}

// 漏斗颜色
const getFunnelColor = (index: number) => {
  const colors = [
    'bg-green-500',
    'bg-indigo-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-orange-500',
    'bg-yellow-500',
  ]
  return colors[index % colors.length]
}

// 转化率标签
const getConversionLabel = (key: string) => {
  const customLabels: Record<string, string> = {
    overall: '整体转化率',
  }
  if (customLabels[key]) return customLabels[key]
  if (key.includes('_to_')) {
    const [fromStage, toStage] = key.split('_to_')
    return `${fromStage} → ${toStage}`
  }
  return key
}

// 转化率颜色
const getRateColor = (rate?: number) => {
  if (!rate) return 'text-gray-400'
  if (rate >= 50) return 'text-green-600'
  if (rate >= 30) return 'text-yellow-600'
  return 'text-red-600'
}

// 查看详情
const viewDetail = (id: number) => {
  router.push(`/opportunities/${id}`)
}

onMounted(() => {
  loadFunnelData()
  loadKanbanData()
  loadUsers()
})
</script>
