<template>
  <div class="space-y-6">
    <h3 class="text-lg font-bold">AI智能分析</h3>

    <!-- 风险等级 -->
    <div class="bg-gray-50 rounded-lg p-4">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm font-medium">风险等级</span>
        <span
          class="px-3 py-1 text-sm rounded-full"
          :class="getRiskClass(opportunity.risk_level)"
        >
          {{ getRiskLabel(opportunity.risk_level) }}
        </span>
      </div>
      <div v-if="opportunity.risk_factors && opportunity.risk_factors.length > 0" class="mt-3">
        <div class="text-sm text-gray-500 mb-2">风险因素:</div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(factor, index) in opportunity.risk_factors"
            :key="index"
            class="px-2 py-1 text-xs rounded bg-red-100 text-red-800"
          >
            {{ factor }}
          </span>
        </div>
      </div>
    </div>

    <!-- AI建议 -->
    <div v-if="opportunity.ai_suggestions" class="bg-blue-50 rounded-lg p-4">
      <div class="flex items-start gap-3">
        <svg class="w-6 h-6 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <div class="font-medium text-blue-900 mb-1">AI建议</div>
          <div class="text-sm text-blue-800">{{ opportunity.ai_suggestions }}</div>
        </div>
      </div>
    </div>

    <!-- 停滞预警 -->
    <div v-if="opportunity.is_stagnant" class="bg-yellow-50 rounded-lg p-4">
      <div class="flex items-start gap-3">
        <svg class="w-6 h-6 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <div class="font-medium text-yellow-900 mb-1">停滞预警</div>
          <div class="text-sm text-yellow-800">
            该商机已在当前阶段停留 {{ opportunity.days_in_stage }} 天，建议跟进推进
          </div>
        </div>
      </div>
    </div>

    <!-- 刷新分析 -->
    <div class="text-center">
      <button
        class="px-4 py-2 border border-indigo-600 text-indigo-600 rounded-md hover:bg-indigo-50"
        @click="refreshAnalysis"
      >
        刷新AI分析
      </button>
    </div>

    <!-- 数据指标 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-gray-900">{{ opportunity.days_in_stage }}</div>
        <div class="text-xs text-gray-500">停留天数</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-gray-900">{{ opportunity.activity_count }}</div>
        <div class="text-xs text-gray-500">活动次数</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-gray-900">{{ opportunity.win_probability }}%</div>
        <div class="text-xs text-gray-500">成交概率</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold" :class="opportunity.is_stagnant ? 'text-red-600' : 'text-green-600'">
          {{ opportunity.is_stagnant ? '是' : '否' }}
        </div>
        <div class="text-xs text-gray-500">是否停滞</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Opportunity } from '@/core/types'

const props = defineProps<{
  opportunity: Opportunity
}>()

const getRiskClass = (level?: string) => {
  const classes = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
  }
  return classes[level as keyof typeof classes] || classes.medium
}

const getRiskLabel = (level?: string) => {
  const labels = {
    low: '低风险',
    medium: '中风险',
    high: '高风险',
  }
  return labels[level as keyof typeof labels] || '未知'
}

const refreshAnalysis = () => {
  // TODO: 调用AI分析接口
  console.log('Refreshing AI analysis...')
}
</script>
