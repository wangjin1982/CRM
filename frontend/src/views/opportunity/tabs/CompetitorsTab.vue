<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-bold">竞争对手</h3>
      <button
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
        @click="showAddModal = true"
      >
        添加对手
      </button>
    </div>

    <div v-if="competitors.length === 0" class="text-center py-8 text-gray-500">
      暂无竞争对手信息
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="competitor in competitors"
        :key="competitor.id"
        class="border border-gray-200 rounded-lg p-4"
      >
        <div class="flex justify-between items-start mb-3">
          <div>
            <div class="font-bold text-lg">{{ competitor.competitor_name }}</div>
            <div v-if="competitor.price_offer" class="text-sm text-gray-500">
              报价: ¥{{ formatAmount(competitor.price_offer) }}
            </div>
          </div>
          <div v-if="competitor.threat_level" class="flex gap-1">
            <span
              v-for="i in 5"
              :key="i"
              class="w-3 h-3 rounded-full"
              :class="i <= competitor.threat_level! ? 'bg-red-500' : 'bg-gray-300'"
            ></span>
          </div>
        </div>
        <div v-if="competitor.strength" class="text-sm">
          <span class="text-gray-500">优势:</span> {{ competitor.strength }}
        </div>
        <div v-if="competitor.weakness" class="text-sm">
          <span class="text-gray-500">劣势:</span> {{ competitor.weakness }}
        </div>
      </div>
    </div>

    <!-- 添加对手弹窗 -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showAddModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 class="text-lg font-bold mb-4">添加竞争对手</h2>
        <form @submit.prevent="handleAddCompetitor">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">对手名称 *</label>
              <input
                v-model="competitorForm.competitor_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">优势</label>
              <textarea
                v-model="competitorForm.strength"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">劣势</label>
              <textarea
                v-model="competitorForm.weakness"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">报价</label>
              <input
                v-model.number="competitorForm.price_offer"
                type="number"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">威胁等级 (1-5)</label>
              <input
                v-model.number="competitorForm.threat_level"
                type="number"
                min="1"
                max="5"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
          <div class="flex justify-end gap-3 mt-6">
            <button
              type="button"
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              @click="showAddModal = false"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              添加
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { opportunityApi } from '@/core/api'
import type { Competitor, CompetitorCreate } from '@/core/types'

const props = defineProps<{
  opportunityId: number
}>()

const competitors = ref<Competitor[]>([])
const showAddModal = ref(false)

const competitorForm = ref<CompetitorCreate>({
  competitor_name: '',
  strength: '',
  weakness: '',
  price_offer: undefined,
  threat_level: 3,
})

const loadCompetitors = async () => {
  try {
    // TODO: 加载竞争对手列表
    competitors.value = []
  } catch (error) {
    console.error('Failed to load competitors:', error)
  }
}

const handleAddCompetitor = async () => {
  try {
    await opportunityApi.addCompetitor(props.opportunityId, competitorForm.value)
    showAddModal.value = false
    competitorForm.value = {
      competitor_name: '',
      strength: '',
      weakness: '',
      price_offer: undefined,
      threat_level: 3,
    }
    loadCompetitors()
  } catch (error) {
    console.error('Failed to add competitor:', error)
  }
}

const formatAmount = (amount?: number) => {
  if (!amount) return '0'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

onMounted(() => {
  loadCompetitors()
})
</script>
