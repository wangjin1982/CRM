<template>
  <div class="space-y-4">
    <h3 class="text-lg font-bold">阶段历史</h3>

    <div v-if="histories.length === 0" class="text-center py-8 text-gray-500">
      暂无阶段变更记录
    </div>

    <div v-else class="relative">
      <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
      <div class="space-y-4">
        <div
          v-for="(history, index) in histories"
          :key="history.id"
          class="relative pl-10"
        >
          <div
            class="absolute left-2.5 w-3 h-3 bg-indigo-600 rounded-full border-2 border-white"
          ></div>
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex justify-between items-start">
              <div>
                <div class="font-medium">
                  {{ history.from_stage_name || '初始' }} → {{ history.to_stage_name }}
                </div>
                <div class="text-sm text-gray-500 mt-1">
                  {{ formatDateTime(history.changed_at) }}
                </div>
              </div>
              <div v-if="history.stage_duration" class="text-sm text-gray-500">
                停留 {{ history.stage_duration }}天
              </div>
            </div>
            <div v-if="history.notes" class="mt-2 text-sm text-gray-600">
              {{ history.notes }}
            </div>
            <div class="text-xs text-gray-400 mt-2">
              操作人: {{ history.changed_by_name || '-' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { opportunityApi } from '@/core/api'
import type { StageHistory } from '@/core/types'

const props = defineProps<{
  opportunityId: number
}>()

const histories = ref<StageHistory[]>([])

const loadHistories = async () => {
  try {
    histories.value = await opportunityApi.getStageHistory(props.opportunityId)
  } catch (error) {
    console.error('Failed to load stage history:', error)
  }
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadHistories()
})
</script>
