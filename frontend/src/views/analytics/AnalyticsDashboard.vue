<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">数据分析看板</h1>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">客户总数</p>
        <p class="text-2xl font-semibold">{{ home?.summary?.total_customers ?? 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Open商机</p>
        <p class="text-2xl font-semibold">{{ home?.summary?.total_open_opportunities ?? 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Open金额（万元）</p>
        <p class="text-2xl font-semibold">{{ formatWanAmount(home?.summary?.total_open_amount) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">高风险商机</p>
        <p class="text-2xl font-semibold text-red-600">{{ home?.summary?.high_risk_opportunities ?? 0 }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <h2 class="text-lg font-semibold mb-3">客户层级分布</h2>
        <div v-for="(count, level) in customer?.level_distribution || {}" :key="String(level)" class="flex justify-between py-1">
          <span>{{ level }}</span><span>{{ count }}</span>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <h2 class="text-lg font-semibold mb-3">商机状态分布</h2>
        <div v-for="(count, status) in opportunity?.status_distribution || {}" :key="String(status)" class="flex justify-between py-1">
          <span>{{ status }}</span><span>{{ count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { analyticsApi } from '@/core/api'

const home = ref<any>(null)
const customer = ref<any>(null)
const opportunity = ref<any>(null)

const formatWanAmount = (amount?: number) => {
  const value = Number(amount || 0)
  return (value / 10000).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

onMounted(async () => {
  const [homeData, customerData, opportunityData] = await Promise.all([
    analyticsApi.dashboardHome(),
    analyticsApi.customerAnalysis(),
    analyticsApi.opportunityAnalysis(),
  ])
  home.value = homeData
  customer.value = customerData
  opportunity.value = opportunityData
})
</script>
