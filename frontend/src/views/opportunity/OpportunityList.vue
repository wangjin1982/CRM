<template>
  <div class="p-6">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">商机管理</h1>
        <p class="text-sm text-gray-500 mt-1">管理销售机会和销售漏斗</p>
      </div>
      <button
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 flex items-center gap-2"
        @click="showCreateModal = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新建商机
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div
        v-for="stat in statistics"
        :key="stat.label"
        class="bg-white rounded-lg shadow p-4 border-l-4"
        :class="stat.borderColor"
      >
        <div class="text-sm text-gray-500">{{ stat.label }}</div>
        <div class="text-2xl font-bold mt-1" :class="stat.textColor">{{ stat.value }}</div>
        <div v-if="stat.amount" class="text-sm text-gray-400 mt-1">
          ¥{{ formatAmount(stat.amount) }}
        </div>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <input
          v-model="filters.keyword"
          type="text"
          placeholder="搜索商机名称、编号..."
          class="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          @keyup.enter="loadOpportunities"
        />
        <select
          v-model="filters.stage_id"
          class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option :value="undefined">所有阶段</option>
          <option v-for="stage in stages" :key="stage.id" :value="stage.id">
            {{ stage.stage_name }}
          </option>
        </select>
        <select
          v-model="filters.status"
          class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option :value="undefined">所有状态</option>
          <option value="open">进行中</option>
          <option value="won">已赢单</option>
          <option value="lost">已输单</option>
        </select>
        <select
          v-model="filters.priority"
          class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option :value="undefined">所有优先级</option>
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
        <button
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          @click="loadOpportunities"
        >
          查询
        </button>
        <button
          class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          @click="resetFilters"
        >
          重置
        </button>
      </div>
    </div>

    <!-- 商机表格 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              商机编号
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              商机名称
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              客户名称
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              阶段
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              预估金额
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              负责人
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              停留天数
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              状态
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="opp in opportunities" :key="opp.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ opp.opportunity_no }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ opp.opportunity_name }}</div>
              <div class="flex items-center gap-2 mt-1">
                <span
                  v-if="opp.priority === 'high'"
                  class="px-2 py-0.5 text-xs rounded bg-red-100 text-red-800"
                >
                  高优先级
                </span>
                <span v-if="opp.is_stagnant" class="px-2 py-0.5 text-xs rounded bg-yellow-100 text-yellow-800">
                  停滞
                </span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ opp.customer_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 py-1 text-xs rounded-full"
                :class="getStageColor(opp.stage_order)"
              >
                {{ opp.stage_name }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              ¥{{ formatAmount(opp.estimated_amount) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ opp.owner_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span :class="{ 'text-red-600 font-medium': opp.days_in_stage > 30 }">
                {{ opp.days_in_stage }}天
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 py-1 text-xs rounded"
                :class="getStatusClass(opp.status)"
              >
                {{ getStatusText(opp.status) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button
                class="text-indigo-600 hover:text-indigo-900 mr-3"
                @click="viewDetail(opp.id)"
              >
                查看
              </button>
              <button
                class="text-gray-600 hover:text-gray-900 mr-3"
                @click="editOpportunity(opp.id)"
              >
                编辑
              </button>
              <button
                class="text-red-600 hover:text-red-900"
                @click="deleteOpportunity(opp.id)"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          共 {{ total }} 条记录
        </div>
        <div class="flex gap-2">
          <button
            :disabled="currentPage === 1"
            class="px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="changePage(currentPage - 1)"
          >
            上一页
          </button>
          <span class="px-3 py-1">{{ currentPage }}</span>
          <button
            :disabled="currentPage * pageSize >= total"
            class="px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="changePage(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 创建商机弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-bold">新建商机</h2>
        </div>
        <div class="p-6">
          <OpportunityForm @submit="handleCreate" @cancel="showCreateModal = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { opportunityApi, stageApi } from '@/core/api'
import type { Opportunity, Stage, OpportunityStatistics } from '@/core/types'

const router = useRouter()

// 数据
const opportunities = ref<Opportunity[]>([])
const stages = ref<Stage[]>([])
const statistics = ref<Statistics[]>([])

const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = ref<{
  keyword?: string
  stage_id?: number
  status?: string
  priority?: string
}>({})

const showCreateModal = ref(false)

// 统计数据
interface Statistics {
  label: string
  value: number
  amount?: number
  borderColor: string
  textColor: string
}

// 加载数据
const loadOpportunities = async () => {
  try {
    const response = await opportunityApi.getOpportunities({
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters.value,
    })
    opportunities.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('Failed to load opportunities:', error)
  }
}

const loadStages = async () => {
  try {
    stages.value = await stageApi.getStages()
  } catch (error) {
    console.error('Failed to load stages:', error)
  }
}

const loadStatistics = async () => {
  try {
    const stats = await opportunityApi.getStatistics()
    statistics.value = [
      {
        label: '全部商机',
        value: stats.total_count,
        amount: stats.total_amount,
        borderColor: 'border-blue-500',
        textColor: 'text-blue-600',
      },
      {
        label: '进行中',
        value: stats.open_count,
        borderColor: 'border-green-500',
        textColor: 'text-green-600',
      },
      {
        label: '本月赢单',
        value: stats.won_count,
        borderColor: 'border-indigo-500',
        textColor: 'text-indigo-600',
      },
      {
        label: '本月输单',
        value: stats.lost_count,
        borderColor: 'border-red-500',
        textColor: 'text-red-600',
      },
      {
        label: '停滞商机',
        value: stats.stagnant_count,
        borderColor: 'border-yellow-500',
        textColor: 'text-yellow-600',
      },
    ]
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

// 格式化金额
const formatAmount = (amount?: number) => {
  if (!amount) return '0'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

// 阶段颜色
const getStageColor = (order?: number) => {
  const colors = [
    'bg-gray-100 text-gray-800',
    'bg-blue-100 text-blue-800',
    'bg-indigo-100 text-indigo-800',
    'bg-purple-100 text-purple-800',
    'bg-pink-100 text-pink-800',
    'bg-green-100 text-green-800',
  ]
  return colors[(order || 1) - 1] || colors[0]
}

// 状态样式
const getStatusClass = (status: string) => {
  const classes = {
    open: 'bg-blue-100 text-blue-800',
    won: 'bg-green-100 text-green-800',
    lost: 'bg-red-100 text-red-800',
    abandoned: 'bg-gray-100 text-gray-800',
  }
  return classes[status as keyof typeof classes] || classes.open
}

const getStatusText = (status: string) => {
  const texts = {
    open: '进行中',
    won: '已赢单',
    lost: '已输单',
    abandoned: '已放弃',
  }
  return texts[status as keyof typeof texts] || status
}

// 操作
const viewDetail = (id: number) => {
  router.push(`/opportunities/${id}`)
}

const editOpportunity = (id: number) => {
  router.push(`/opportunities/${id}/edit`)
}

const deleteOpportunity = async (id: number) => {
  if (!confirm('确定要删除这个商机吗？')) return

  try {
    await opportunityApi.deleteOpportunity(id)
    loadOpportunities()
    loadStatistics()
  } catch (error) {
    console.error('Failed to delete opportunity:', error)
  }
}

const handleCreate = async (data: any) => {
  try {
    await opportunityApi.createOpportunity(data)
    showCreateModal.value = false
    loadOpportunities()
    loadStatistics()
  } catch (error) {
    console.error('Failed to create opportunity:', error)
    const detail = (error as any)?.response?.data?.detail
    alert(typeof detail === 'string' ? detail : '创建商机失败，请检查输入项')
  }
}

const resetFilters = () => {
  filters.value = {}
  currentPage.value = 1
  loadOpportunities()
}

const changePage = (page: number) => {
  currentPage.value = page
  loadOpportunities()
}

onMounted(() => {
  loadOpportunities()
  loadStages()
  loadStatistics()
})
</script>
