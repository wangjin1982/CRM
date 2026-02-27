<template>
  <div class="p-6">
    <!-- 返回按钮 -->
    <button
      class="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
      @click="$router.back()"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      返回
    </button>

    <!-- 商机不存在 -->
    <div v-if="!opportunity" class="text-center py-12">
      <div class="text-gray-400 mb-2">商机不存在</div>
      <button
        class="text-indigo-600 hover:text-indigo-900"
        @click="$router.push('/opportunities')"
      >
        返回商机列表
      </button>
    </div>

    <!-- 商机详情 -->
    <div v-else>
      <!-- 头部信息 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex justify-between items-start">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold text-gray-900">{{ opportunity.opportunity_name }}</h1>
              <span
                class="px-3 py-1 text-sm rounded-full"
                :class="getStatusClass(opportunity.status)"
              >
                {{ getStatusText(opportunity.status) }}
              </span>
              <span
                v-if="opportunity.priority === 'high'"
                class="px-3 py-1 text-sm rounded bg-red-100 text-red-800"
              >
                高优先级
              </span>
              <span
                v-if="opportunity.is_stagnant"
                class="px-3 py-1 text-sm rounded bg-yellow-100 text-yellow-800"
              >
                停滞预警
              </span>
            </div>
            <div class="text-gray-500 mt-1">
              商机编号: {{ opportunity.opportunity_no }}
            </div>
          </div>
          <div class="flex gap-2">
            <button
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              @click="showEditModal = true"
            >
              编辑
            </button>
            <button
              v-if="opportunity.status === 'open'"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              @click="showWonModal = true"
            >
              标记赢单
            </button>
            <button
              v-if="opportunity.status === 'open'"
              class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              @click="showLostModal = true"
            >
              标记输单
            </button>
          </div>
        </div>
      </div>

      <!-- Tab导航 -->
      <div class="border-b border-gray-200 mb-6">
        <nav class="flex gap-6">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="py-2 px-1 border-b-2 transition-colors"
            :class="activeTab === tab.key ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab内容 -->
      <div class="bg-white rounded-lg shadow p-6">
        <!-- 概览 -->
        <div v-if="activeTab === 'overview'">
          <OverviewTab :opportunity="opportunity" @stage-change="handleStageChange" />
        </div>

        <!-- 活动记录 -->
        <div v-if="activeTab === 'activities'">
          <ActivityTab :opportunity-id="opportunity.id" />
        </div>

        <!-- 联系人 -->
        <div v-if="activeTab === 'contacts'">
          <ContactsTab :opportunity-id="opportunity.id" />
        </div>

        <!-- 阶段历史 -->
        <div v-if="activeTab === 'history'">
          <HistoryTab :opportunity-id="opportunity.id" />
        </div>

        <!-- 竞争对手 -->
        <div v-if="activeTab === 'competitors'">
          <CompetitorsTab :opportunity-id="opportunity.id" />
        </div>

        <!-- AI分析 -->
        <div v-if="activeTab === 'ai'">
          <AITab :opportunity="opportunity" />
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showEditModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-bold">编辑商机</h2>
        </div>
        <div class="p-6">
          <OpportunityForm
            :initial-data="opportunity"
            @submit="handleUpdate"
            @cancel="showEditModal = false"
          />
        </div>
      </div>
    </div>

    <!-- 赢单弹窗 -->
    <div
      v-if="showWonModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showWonModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 class="text-lg font-bold mb-4">标记赢单</h2>
        <form @submit.prevent="handleWon">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">实际成交金额</label>
              <input
                v-model.number="wonForm.actual_amount"
                type="number"
                step="0.01"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">实际成交日期</label>
              <input
                v-model="wonForm.actual_close_date"
                type="date"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
              <textarea
                v-model="wonForm.notes"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              ></textarea>
            </div>
          </div>
          <div class="flex justify-end gap-3 mt-6">
            <button
              type="button"
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              @click="showWonModal = false"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              确认赢单
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 输单弹窗 -->
    <div
      v-if="showLostModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showLostModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 class="text-lg font-bold mb-4">标记输单</h2>
        <form @submit.prevent="handleLost">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">流失原因</label>
              <input
                v-model="lostForm.lost_reason"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">竞争对手</label>
              <input
                v-model="lostForm.competitor"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
              <textarea
                v-model="lostForm.notes"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              ></textarea>
            </div>
          </div>
          <div class="flex justify-end gap-3 mt-6">
            <button
              type="button"
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              @click="showLostModal = false"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              确认输单
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { opportunityApi, stageApi } from '@/core/api'
import type { Opportunity, Stage } from '@/core/types'
import OverviewTab from './tabs/OverviewTab.vue'
import ContactsTab from './tabs/ContactsTab.vue'
import HistoryTab from './tabs/HistoryTab.vue'
import CompetitorsTab from './tabs/CompetitorsTab.vue'
import ActivityTab from './tabs/ActivityTab.vue'
import AITab from './tabs/AITab.vue'
import OpportunityForm from './OpportunityForm.vue'

const route = useRoute()
const router = useRouter()

// 数据
const opportunity = ref<Opportunity | null>(null)
const stages = ref<Stage[]>([])

// Tab
const tabs = [
  { key: 'overview', label: '概览' },
  { key: 'activities', label: '活动记录' },
  { key: 'contacts', label: '联系人' },
  { key: 'history', label: '阶段历史' },
  { key: 'competitors', label: '竞争对手' },
  { key: 'ai', label: 'AI分析' },
]
const activeTab = ref('overview')

// 弹窗
const showEditModal = ref(false)
const showWonModal = ref(false)
const showLostModal = ref(false)

// 表单
const wonForm = ref({
  actual_amount: 0,
  actual_close_date: new Date().toISOString().split('T')[0],
  notes: '',
})

const lostForm = ref({
  lost_reason: '',
  competitor: '',
  notes: '',
})

// 加载商机
const loadOpportunity = async () => {
  try {
    const id = Number(route.params.id)
    opportunity.value = await opportunityApi.getOpportunity(id)
  } catch (error) {
    console.error('Failed to load opportunity:', error)
  }
}

const loadStages = async () => {
  try {
    stages.value = await stageApi.getStages()
  } catch (error) {
    console.error('Failed to load stages:', error)
  }
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

// 处理函数
const handleUpdate = async (data: any) => {
  try {
    await opportunityApi.updateOpportunity(opportunity.value!.id, data)
    showEditModal.value = false
    loadOpportunity()
  } catch (error) {
    console.error('Failed to update opportunity:', error)
  }
}

const handleStageChange = async (toStageId: number) => {
  try {
    await opportunityApi.changeStage(opportunity.value!.id, { to_stage_id: toStageId })
    loadOpportunity()
  } catch (error) {
    console.error('Failed to change stage:', error)
    const detail = (error as any)?.response?.data?.detail
    alert(typeof detail === 'string' ? detail : '阶段推进失败')
  }
}

const handleWon = async () => {
  try {
    await opportunityApi.markAsWon(opportunity.value!.id, wonForm.value)
    showWonModal.value = false
    loadOpportunity()
  } catch (error) {
    console.error('Failed to mark as won:', error)
  }
}

const handleLost = async () => {
  try {
    await opportunityApi.markAsLost(opportunity.value!.id, lostForm.value)
    showLostModal.value = false
    loadOpportunity()
  } catch (error) {
    console.error('Failed to mark as lost:', error)
  }
}

onMounted(() => {
  loadOpportunity()
  loadStages()
})
</script>
