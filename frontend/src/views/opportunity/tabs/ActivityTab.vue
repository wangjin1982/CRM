<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-bold">{{ panelTitle }}</h3>
      <button
        class="rounded border border-gray-300 px-3 py-1 text-sm text-gray-700 hover:bg-gray-50"
        @click="loadData"
      >
        刷新
      </button>
    </div>

    <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
      <div class="rounded-lg border bg-white p-3">
        <div class="text-xs text-gray-500">拜访记录</div>
        <div class="mt-1 text-xl font-semibold text-indigo-700">{{ visits.length }}</div>
      </div>
      <div class="rounded-lg border bg-white p-3">
        <div class="text-xs text-gray-500">跟进记录</div>
        <div class="mt-1 text-xl font-semibold text-indigo-700">{{ follows.length }}</div>
      </div>
      <div class="rounded-lg border bg-white p-3">
        <div class="text-xs text-gray-500">任务</div>
        <div class="mt-1 text-xl font-semibold text-indigo-700">{{ tasks.length }}</div>
      </div>
      <div class="rounded-lg border bg-white p-3">
        <div class="text-xs text-gray-500">日程</div>
        <div class="mt-1 text-xl font-semibold text-indigo-700">{{ schedules.length }}</div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <div class="h-8 w-8 animate-spin rounded-full border-b-2 border-indigo-600"></div>
    </div>

    <div v-else class="space-y-6">
      <section class="rounded-lg border bg-white">
        <div class="border-b px-4 py-3 text-sm font-semibold text-gray-800">拜访记录</div>
        <div v-if="!visits.length" class="px-4 py-6 text-sm text-gray-500">暂无拜访记录</div>
        <div v-else class="divide-y">
          <div v-for="item in visits" :key="item.id" class="px-4 py-3 text-sm">
            <div class="font-medium text-gray-900">{{ item.visit_no }}</div>
            <div class="mt-1 text-gray-600">
              {{ item.visit_type || '-' }} | {{ formatDate(item.visit_date) }} | 结果: {{ item.result_type || '-' }}
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-lg border bg-white">
        <div class="border-b px-4 py-3 text-sm font-semibold text-gray-800">跟进记录</div>
        <div v-if="!follows.length" class="px-4 py-6 text-sm text-gray-500">暂无跟进记录</div>
        <div v-else class="divide-y">
          <div v-for="item in follows" :key="item.id" class="px-4 py-3 text-sm">
            <div class="font-medium text-gray-900">{{ item.follow_no }} {{ item.subject ? `- ${item.subject}` : '' }}</div>
            <div class="mt-1 text-gray-600">
              {{ item.follow_type || '-' }} | {{ formatDateTime(item.created_at) }} | 下次: {{ item.next_follow_date ? formatDate(item.next_follow_date) : '-' }}
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-lg border bg-white">
        <div class="border-b px-4 py-3 text-sm font-semibold text-gray-800">任务</div>
        <div v-if="!tasks.length" class="px-4 py-6 text-sm text-gray-500">暂无任务</div>
        <div v-else class="divide-y">
          <div v-for="item in tasks" :key="item.id" class="px-4 py-3 text-sm">
            <div class="flex items-center justify-between">
              <div class="font-medium text-gray-900">{{ item.task_no }} - {{ item.task_title }}</div>
              <span class="rounded px-2 py-0.5 text-xs" :class="taskStatusClass(item.status)">
                {{ taskStatusText[item.status] || item.status }}
              </span>
            </div>
            <div class="mt-1 text-gray-600">
              截止: {{ formatDate(item.due_date) }} {{ item.due_time || '' }} | 优先级: {{ item.priority || '-' }}
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-lg border bg-white">
        <div class="border-b px-4 py-3 text-sm font-semibold text-gray-800">日程</div>
        <div v-if="!schedules.length" class="px-4 py-6 text-sm text-gray-500">暂无日程</div>
        <div v-else class="divide-y">
          <div v-for="item in schedules" :key="item.id" class="px-4 py-3 text-sm">
            <div class="font-medium text-gray-900">{{ item.schedule_title }}</div>
            <div class="mt-1 text-gray-600">
              {{ formatDateTime(item.start_time) }} - {{ formatDateTime(item.end_time) }} | {{ item.schedule_type || '-' }}
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { activityApi } from '@/core/api'

const props = defineProps<{
  opportunityId?: number
  customerId?: number
  title?: string
}>()

const loading = ref(false)
const visits = ref<any[]>([])
const follows = ref<any[]>([])
const tasks = ref<any[]>([])
const schedules = ref<any[]>([])

const panelTitle = computed(() => {
  if (props.title) return props.title
  if (props.customerId) return '客户销售行为记录'
  return '销售行为活动记录'
})

const taskStatusText: Record<string, string> = {
  pending: '待处理',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消',
}

const taskStatusClass = (status: string) => {
  const map: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-700',
    in_progress: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    cancelled: 'bg-red-100 text-red-700',
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

const loadData = async () => {
  loading.value = true
  try {
    const commonParams: Record<string, any> = {
      page: 1,
      pageSize: 50,
    }
    if (props.opportunityId) commonParams.opportunityId = props.opportunityId
    if (props.customerId) commonParams.customerId = props.customerId

    const [visitResp, followResp, taskResp, scheduleResp] = await Promise.all([
      activityApi.getVisits(commonParams),
      activityApi.getFollows(commonParams),
      activityApi.getTasks(commonParams),
      activityApi.getSchedules({
        opportunityId: props.opportunityId,
        customerId: props.customerId,
      }),
    ])
    visits.value = visitResp?.items || []
    follows.value = followResp?.items || []
    tasks.value = taskResp?.items || []
    schedules.value = Array.isArray(scheduleResp) ? scheduleResp : []
  } catch (error) {
    console.error('Failed to load activity records for opportunity:', error)
    visits.value = []
    follows.value = []
    tasks.value = []
    schedules.value = []
  } finally {
    loading.value = false
  }
}

const formatDate = (value?: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('zh-CN')
}

const formatDateTime = (value?: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

watch(
  () => [props.opportunityId, props.customerId],
  () => {
    loadData()
  },
  { immediate: true }
)
</script>
