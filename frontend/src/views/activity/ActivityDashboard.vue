<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">销售行为看板</h1>
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">拜访总数</p>
        <p class="text-2xl font-semibold">{{ stats?.summary?.total_visits ?? 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">跟进总数</p>
        <p class="text-2xl font-semibold">{{ stats?.summary?.total_follows ?? 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">任务总数</p>
        <p class="text-2xl font-semibold">{{ stats?.summary?.total_tasks ?? 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">任务完成率</p>
        <p class="text-2xl font-semibold">{{ stats?.task_completion_rate ?? 0 }}%</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">逾期任务</p>
        <p class="text-2xl font-semibold text-red-600">{{ stats?.overdue_tasks ?? 0 }}</p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <h2 class="text-lg font-semibold mb-3">拜访趋势</h2>
      <div v-if="!stats?.visit_trend?.length" class="text-gray-500">暂无数据</div>
      <div v-else class="space-y-2">
        <div
          v-for="item in stats.visit_trend"
          :key="item.date"
          class="flex items-center justify-between border-b pb-2"
        >
          <span>{{ item.date }}</span>
          <span class="font-medium">{{ item.count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { activityApi } from '@/core/api'

const stats = ref<any>(null)

onMounted(async () => {
  stats.value = await activityApi.getStatistics()
})
</script>
