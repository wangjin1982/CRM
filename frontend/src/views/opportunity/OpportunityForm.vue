<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-2 gap-6">
      <!-- 商机名称 -->
      <div class="col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">商机名称 *</label>
        <input
          v-model="formData.opportunity_name"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- 客户 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">客户 *</label>
        <select
          v-model.number="formData.customer_id"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option :value="0">请选择客户</option>
          <option v-for="customer in customers" :key="customer.id" :value="customer.id">
            {{ customer.customer_name }}
          </option>
        </select>
      </div>

      <!-- 联系人 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">主要联系人</label>
        <select
          v-model.number="formData.primary_contact_id"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option :value="undefined">请选择联系人</option>
          <option v-for="contact in contacts" :key="contact.id" :value="contact.id">
            {{ contact.name }}
          </option>
        </select>
      </div>

      <!-- 预估金额 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">预估金额</label>
        <input
          v-model.number="formData.estimated_amount"
          type="number"
          step="0.01"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- 币种 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">币种</label>
        <select
          v-model="formData.currency"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="CNY">人民币</option>
          <option value="USD">美元</option>
          <option value="EUR">欧元</option>
        </select>
      </div>

      <!-- 阶段 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">销售阶段 *</label>
        <select
          v-model.number="formData.stage_id"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option :value="0">请选择阶段</option>
          <option v-for="stage in stages" :key="stage.id" :value="stage.id">
            {{ stage.stage_name }} ({{ stage.probability }}%)
          </option>
        </select>
      </div>

      <!-- 预计成交日期 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">预计成交日期</label>
        <input
          v-model="formData.expected_close_date"
          type="date"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- 成交概率 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">成交概率 (%)</label>
        <input
          v-model.number="formData.win_probability"
          type="number"
          min="0"
          max="100"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- 优先级 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">优先级</label>
        <select
          v-model="formData.priority"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
        </select>
      </div>

      <!-- 商机来源 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">商机来源</label>
        <select
          v-model="formData.lead_source"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">请选择</option>
          <option value="website">官网</option>
          <option value="referral">推荐</option>
          <option value="exhibition">展会</option>
          <option value="cold_call">电话营销</option>
          <option value="other">其他</option>
        </select>
      </div>

      <!-- 负责人 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">负责人</label>
        <select
          v-model.number="formData.owner_id"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option :value="undefined">请选择</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.real_name || user.username }}
          </option>
        </select>
      </div>
    </div>

    <!-- 描述 -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">商机描述</label>
      <textarea
        v-model="formData.description"
        rows="3"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
      ></textarea>
    </div>

    <!-- 按钮 -->
    <div class="flex justify-end gap-3 pt-4 border-t">
      <p v-if="errorMessage" class="mr-auto text-sm text-red-600">{{ errorMessage }}</p>
      <button
        type="button"
        class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        @click="$emit('cancel')"
      >
        取消
      </button>
      <button
        type="submit"
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
      >
        {{ isEdit ? '保存' : '创建' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { customerApi, contactApi } from '@/core/api'
import { stageApi } from '@/core/api/opportunity'
import { userApi } from '@/core/api'
import type { Opportunity, OpportunityCreate } from '@/core/types'

const props = defineProps<{
  customerId?: number
  initialData?: Partial<Opportunity>
}>()

const emit = defineEmits<{
  submit: [data: OpportunityCreate]
  cancel: []
}>()

// 表单数据
const getDefaultFormData = (): OpportunityCreate => ({
  opportunity_name: '',
  customer_id: props.customerId || 0,
  primary_contact_id: undefined,
  estimated_amount: undefined,
  stage_id: 0,
  currency: 'CNY',
  expected_close_date: undefined,
  win_probability: 50,
  priority: 'medium',
  owner_id: undefined,
  lead_source: '',
  description: '',
})

const formData = ref<OpportunityCreate>({
  ...getDefaultFormData(),
})

const isEdit = computed(() => Boolean(props.initialData?.id))
const errorMessage = ref('')

// 选项数据
const customers = ref<any[]>([])
const contacts = ref<any[]>([])
const stages = ref<any[]>([])
const users = ref<any[]>([])

// 加载选项数据
const loadCustomers = async () => {
  try {
    const response = await customerApi.getList({ page: 1, page_size: 100 })
    customers.value = response.items
  } catch (error) {
    console.error('Failed to load customers:', error)
  }
}

const loadContacts = async () => {
  if (!formData.value.customer_id) {
    contacts.value = []
    formData.value.primary_contact_id = undefined
    return
  }
  try {
    const response = await contactApi.getByCustomer(formData.value.customer_id)
    contacts.value = response.items
  } catch (error) {
    console.error('Failed to load contacts:', error)
  }
}

const loadStages = async () => {
  try {
    const allStages = await stageApi.getStages()
    const workbookStages = allStages.filter(
      stage => stage.stage_type === 'normal' && Boolean(stage.internal_code)
    )
    const normalStages = allStages.filter(stage => stage.stage_type === 'normal')
    stages.value = workbookStages.length > 0
      ? workbookStages
      : (normalStages.length > 0 ? normalStages : allStages)
    if (!formData.value.stage_id && stages.value.length > 0) {
      formData.value.stage_id = stages.value[0].id
      formData.value.win_probability = stages.value[0].probability
    }
  } catch (error) {
    console.error('Failed to load stages:', error)
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

// 提交表单
const handleSubmit = () => {
  errorMessage.value = ''
  if (!formData.value.opportunity_name?.trim()) {
    errorMessage.value = '请填写商机名称'
    return
  }
  if (!formData.value.customer_id) {
    errorMessage.value = '请选择客户'
    return
  }
  if (!formData.value.stage_id) {
    errorMessage.value = '请选择销售阶段'
    return
  }
  emit('submit', formData.value)
}

const initializeForm = () => {
  if (!props.initialData) return
  formData.value = {
    ...getDefaultFormData(),
    opportunity_name: props.initialData.opportunity_name || '',
    customer_id: props.initialData.customer_id || props.customerId || 0,
    primary_contact_id: props.initialData.primary_contact_id,
    estimated_amount: props.initialData.estimated_amount,
    stage_id: props.initialData.stage_id || 0,
    currency: props.initialData.currency || 'CNY',
    expected_close_date: props.initialData.expected_close_date,
    win_probability: props.initialData.win_probability ?? 50,
    priority: props.initialData.priority || 'medium',
    owner_id: props.initialData.owner_id,
    lead_source: props.initialData.lead_source || '',
    description: props.initialData.description || '',
    tags: props.initialData.tags || [],
    products: props.initialData.products || [],
  }
}

// 监听客户变化，加载联系人
watch(() => formData.value.customer_id, () => {
  loadContacts()
})

watch(() => formData.value.stage_id, (stageId) => {
  const stage = stages.value.find(item => item.id === stageId)
  if (stage) {
    formData.value.win_probability = stage.probability
  }
})

onMounted(() => {
  initializeForm()
  loadCustomers()
  loadStages()
  loadUsers()
  if (formData.value.customer_id) {
    loadContacts()
  }
})
</script>
