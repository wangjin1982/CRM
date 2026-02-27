<template>
  <div class="space-y-6">
    <!-- 基本信息 -->
    <div class="grid grid-cols-2 gap-6">
      <div>
        <label class="text-sm text-gray-500">客户名称</label>
        <div class="mt-1">{{ opportunity.customer_name || '-' }}</div>
      </div>
      <div>
        <label class="text-sm text-gray-500">负责人</label>
        <div class="mt-1">{{ opportunity.owner_name || '-' }}</div>
      </div>
      <div>
        <label class="text-sm text-gray-500">预估金额</label>
        <div class="mt-1 text-lg font-bold text-indigo-600">
          ¥{{ formatAmount(opportunity.estimated_amount) }}
        </div>
      </div>
      <div>
        <label class="text-sm text-gray-500">成交概率</label>
        <div class="mt-1">{{ opportunity.win_probability }}%</div>
      </div>
      <div>
        <label class="text-sm text-gray-500">预计成交日期</label>
        <div class="mt-1">{{ formatDate(opportunity.expected_close_date) }}</div>
      </div>
      <div>
        <label class="text-sm text-gray-500">当前阶段</label>
        <div class="mt-1">
          <span
            class="px-3 py-1 text-sm rounded-full"
            :class="getStageColor(opportunity.stage_order)"
          >
            {{ opportunity.stage_name }}
          </span>
        </div>
      </div>
      <div>
        <label class="text-sm text-gray-500">停留天数</label>
        <div class="mt-1" :class="{ 'text-red-600 font-medium': opportunity.days_in_stage > 30 }">
          {{ opportunity.days_in_stage }}天
        </div>
      </div>
      <div>
        <label class="text-sm text-gray-500">活动次数</label>
        <div class="mt-1">{{ opportunity.activity_count }}次</div>
      </div>
    </div>

    <!-- 描述 -->
    <div v-if="opportunity.description">
      <label class="text-sm text-gray-500">商机描述</label>
      <div class="mt-1 text-gray-900">{{ opportunity.description }}</div>
    </div>

    <!-- 产品信息 -->
    <div v-if="opportunity.products && opportunity.products.length > 0">
      <label class="text-sm text-gray-500">产品信息</label>
      <table class="mt-2 min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">产品名称</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">数量</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">单价</th>
            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">小计</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="(product, index) in opportunity.products" :key="index">
            <td class="px-4 py-2 text-sm">{{ product.name }}</td>
            <td class="px-4 py-2 text-sm">{{ product.quantity }}</td>
            <td class="px-4 py-2 text-sm">¥{{ formatAmount(product.price) }}</td>
            <td class="px-4 py-2 text-sm">¥{{ formatAmount(product.amount) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 阶段推进 -->
    <div>
      <label class="text-sm text-gray-500">阶段推进（按顺序点击）</label>
      <div class="mt-2 flex flex-wrap gap-2">
        <button
          v-for="stage in normalStages"
          :key="stage.id"
          type="button"
          class="rounded-full border px-3 py-1 text-sm transition"
          :class="getStageStepClass(stage)"
          :disabled="!canMoveToStage(stage)"
          @click="handleStageClick(stage.id)"
        >
          <span class="font-medium">{{ stage.stage_order }}. {{ stage.stage_name }}</span>
          <span class="ml-1 text-xs opacity-80">{{ stage.probability }}%</span>
        </button>
      </div>
      <p class="mt-2 text-xs text-gray-500">
        规则：只能推进到下一阶段；赢单/输单请使用页面右上角按钮。
      </p>
    </div>

    <!-- 阶段定义透传 -->
    <div v-if="currentStage" class="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <h4 class="mb-3 text-sm font-semibold text-slate-800">
        阶段定义透传：{{ currentStage.stage_name }}
        <span v-if="currentStage.internal_code" class="ml-1 text-xs text-slate-500">
          ({{ currentStage.internal_code }})
        </span>
      </h4>
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div v-if="currentStage.description">
          <p class="text-xs text-slate-500">定义</p>
          <p class="mt-1 whitespace-pre-line text-sm text-slate-800">{{ currentStage.description }}</p>
        </div>
        <div v-if="currentStage.customer_journey">
          <p class="text-xs text-slate-500">Customer Journey</p>
          <p class="mt-1 text-sm text-slate-800">{{ currentStage.customer_journey }}</p>
        </div>
        <div v-if="currentStage.technical_support">
          <p class="text-xs text-slate-500">技术支持动作</p>
          <p class="mt-1 whitespace-pre-line text-sm text-slate-800">{{ currentStage.technical_support }}</p>
        </div>
        <div v-if="currentStage.sales_process">
          <p class="text-xs text-slate-500">销售动作</p>
          <p class="mt-1 whitespace-pre-line text-sm text-slate-800">{{ currentStage.sales_process }}</p>
        </div>
      </div>
      <div v-if="currentStage.stage_criteria" class="mt-3">
        <p class="text-xs text-slate-500">阶段判定标准</p>
        <p class="mt-1 whitespace-pre-line text-sm text-slate-800">{{ currentStage.stage_criteria }}</p>
      </div>
    </div>

    <!-- 下一步建议 -->
    <div class="rounded-lg border border-indigo-100 bg-indigo-50 p-4">
      <h4 class="mb-2 text-sm font-semibold text-indigo-900">下一步建议</h4>
      <ul class="space-y-1 text-sm text-indigo-900">
        <li v-for="(item, index) in nextActionSuggestions" :key="`${index}-${item}`">
          {{ index + 1 }}. {{ item }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { stageApi } from '@/core/api'
import type { Opportunity, Stage } from '@/core/types'

const props = defineProps<{
  opportunity: Opportunity
}>()

const emit = defineEmits<{
  stageChange: [stageId: number]
}>()

const stages = ref<Stage[]>([])

const loadStages = async () => {
  try {
    stages.value = await stageApi.getStages()
  } catch (error) {
    console.error('Failed to load stages:', error)
  }
}

const normalStages = computed(() =>
  {
    const workbook = stages.value.filter(
      stage => stage.stage_type === 'normal' && Boolean(stage.internal_code)
    )
    const explicit = stages.value.filter(stage => stage.stage_type === 'normal')
    const fallback = workbook.length > 0 ? workbook : (explicit.length > 0 ? explicit : stages.value)
    return [...fallback].sort((a, b) => a.stage_order - b.stage_order)
  }
)

const currentStage = computed(() => stages.value.find(stage => stage.id === props.opportunity.stage_id))
const currentOrder = computed(() => currentStage.value?.stage_order || 0)

const nextActionSuggestions = computed(() => {
  const opp = props.opportunity
  const suggestions: string[] = []

  if (opp.status === 'won') {
    return ['商机已赢单，建议在3天内补齐复盘、交付计划和二次销售机会识别。']
  }
  if (opp.status === 'lost') {
    return ['商机已输单，建议在48小时内完成输单原因复盘并沉淀竞争对手信息。']
  }

  if (opp.is_stagnant || (opp.days_in_stage || 0) > 30) {
    suggestions.push('当前商机出现阶段停滞，建议48小时内安排一次关键人沟通并更新推进计划。')
  }

  if ((opp.activity_count || 0) === 0) {
    suggestions.push('当前阶段尚无活动记录，建议至少补充1条拜访或跟进记录。')
  } else if ((opp.activity_count || 0) < 3) {
    suggestions.push('活动触达频次偏低，建议增加跟进节奏并补充任务/日程。')
  }

  if (opp.expected_close_date) {
    const daysToClose = Math.ceil(
      (new Date(opp.expected_close_date).getTime() - Date.now()) / (24 * 60 * 60 * 1000)
    )
    if (daysToClose < 0) {
      suggestions.push('预计成交日期已过期，建议立即重新评估close plan并更新预计成交日期。')
    } else if (daysToClose <= 14 && (opp.win_probability || 0) < 50) {
      suggestions.push('预计成交窗口临近但概率偏低，建议优先确认预算、审批链与技术方案可行性。')
    }
  }

  if ((opp.stage_order || 0) <= 2) {
    suggestions.push('处于早期阶段，建议尽快完成客户需求澄清与项目角色识别（TO/TBM/ISM）。')
  }

  if (currentStage.value?.stage_criteria) {
    const firstCriteria = currentStage.value.stage_criteria
      .split('\n')
      .map(item => item.trim())
      .find(Boolean)
    if (firstCriteria) {
      suggestions.push(`推进前请先满足当前阶段判定标准：${firstCriteria}`)
    }
  }

  if (!suggestions.length) {
    suggestions.push('商机节奏正常，建议保持周节奏复盘并持续更新活动记录。')
  }

  return suggestions.slice(0, 5)
})

const canMoveToStage = (stage: Stage) => {
  if (props.opportunity.status !== 'open') return false
  if (stage.id === props.opportunity.stage_id) return false
  return stage.stage_order === currentOrder.value + 1
}

const handleStageClick = (stageId: number) => {
  emit('stageChange', stageId)
}

const getStageStepClass = (stage: Stage) => {
  if (stage.id === props.opportunity.stage_id) {
    return 'border-indigo-600 bg-indigo-600 text-white'
  }
  if (stage.stage_order < currentOrder.value) {
    return 'border-emerald-300 bg-emerald-50 text-emerald-700'
  }
  if (canMoveToStage(stage)) {
    return 'border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-50'
  }
  return 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
}

const formatAmount = (amount?: number) => {
  if (!amount) return '0'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const formatDate = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

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

onMounted(() => {
  loadStages()
})
</script>
