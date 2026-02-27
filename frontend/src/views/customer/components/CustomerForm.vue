<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto m-4">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-900">
          {{ customer ? '编辑客户' : '新增客户' }}
        </h2>
      </div>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
        <!-- 基本信息 -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">基本信息</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">1#客户名称（中）*</label>
              <input
                v-model="formData.customer_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">1#客户名称（EN）</label>
              <input
                v-model="formData.customer_name_en"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">3#客户类型</label>
              <input
                v-model="formData.customer_type_3"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">3#客户分级</label>
              <input
                v-model="formData.customer_level_3"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">5#成交客户</label>
              <select
                v-model.number="formData.deal_customer_5"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option :value="0">否(0)</option>
                <option :value="1">是(1)</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">5#电气工程师人数</label>
              <input
                v-model.number="formData.electrical_engineer_count_5"
                type="number"
                min="0"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">3#负责人（销售）</label>
              <input
                v-model="salesKeyword"
                type="text"
                placeholder="搜索销售姓名"
                class="mb-2 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
              <select
                v-model="formData.owner_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option :value="undefined">请选择销售负责人</option>
                <option
                  v-for="user in filteredSalesUsers"
                  :key="user.id"
                  :value="user.id"
                >
                  {{ user.real_name || user.username }}{{ user.position ? `（${user.position}）` : '' }}
                </option>
              </select>
              <p class="mt-1 text-xs text-gray-500">
                当前负责人：{{ formData.owner_name_3 || '未选择' }}
              </p>
            </div>
          </div>
        </div>

        <!-- 企业信息 -->
        <div v-if="formData.customer_type === 'enterprise'">
          <h3 class="text-lg font-medium text-gray-900 mb-4">企业信息</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">公司规模</label>
              <select
                v-model="formData.company_size"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">请选择</option>
                <option value="1-10人">1-10人</option>
                <option value="10-50人">10-50人</option>
                <option value="50-100人">50-100人</option>
                <option value="100-500人">100-500人</option>
                <option value="500-1000人">500-1000人</option>
                <option value="1000人以上">1000人以上</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">法人代表</label>
              <input
                v-model="formData.legal_person"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">注册资本（万元）</label>
              <input
                v-model.number="formData.registered_capital"
                type="number"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">成立日期</label>
              <input
                v-model="formData.establish_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        <!-- 联系信息 -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">联系信息</h3>
          <RegionSelector v-model="regionModel" />
          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">详细地址</label>
            <textarea
              v-model="formData.address"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            ></textarea>
          </div>
          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">官方网站</label>
            <input
              v-model="formData.website"
              type="url"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>

        <!-- 标签 -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">标签</h3>
          <div class="flex flex-wrap gap-2 mb-2">
            <span
              v-for="(tag, index) in formData.tags"
              :key="index"
              class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800"
            >
              {{ tag }}
              <button
                type="button"
                class="hover:text-indigo-600"
                @click="removeTag(index)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          </div>
          <div class="flex gap-2">
            <input
              v-model="newTag"
              type="text"
              placeholder="输入标签后按回车添加"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              @keyup.enter="addTag"
            />
            <button
              type="button"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              @click="addTag"
            >
              添加
            </button>
          </div>
        </div>

        <!-- 备注 -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">备注</h3>
          <textarea
            v-model="formData.remarks"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          ></textarea>
        </div>

        <!-- 按钮 -->
        <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            @click="$emit('close')"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { customerApi, userApi } from '@/core/api'
import type { Customer, CustomerCreate, UserResponse } from '@/core/types'
import RegionSelector from '@/core/components/RegionSelector.vue'

interface Props {
  customer?: Customer | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  save: []
}>()

// 状态
const submitting = ref(false)
const newTag = ref('')
const salesKeyword = ref('')
const allUsers = ref<UserResponse[]>([])

// 表单数据
const formData = ref<CustomerCreate>({
  customer_name: '',
  customer_name_en: '',
  region: '',
  customer_type_3: '',
  customer_level_3: '',
  deal_customer_5: 0,
  electrical_engineer_count_5: undefined,
  owner_name_3: '',
  customer_type: 'enterprise',
  industry: '',
  company_size: '',
  legal_person: '',
  registered_capital: undefined,
  establish_date: '',
  province: '',
  city: '',
  district: '',
  address: '',
  website: '',
  source: '',
  level: 'C',
  owner_id: undefined,
  tags: [],
  remarks: '',
})

// 初始化表单数据
if (props.customer) {
  formData.value = {
    customer_name: props.customer.customer_name,
    customer_name_en: props.customer.customer_name_en || '',
    region: props.customer.region || '',
    customer_type_3: props.customer.customer_type_3 || '',
    customer_level_3: props.customer.customer_level_3 || '',
    deal_customer_5: props.customer.deal_customer_5 ?? 0,
    electrical_engineer_count_5: props.customer.electrical_engineer_count_5,
    owner_name_3: props.customer.owner_name_3 || '',
    customer_type: props.customer.customer_type,
    industry: props.customer.industry || '',
    company_size: props.customer.company_size || '',
    legal_person: props.customer.legal_person || '',
    registered_capital: props.customer.registered_capital,
    establish_date: props.customer.establish_date || '',
    province: props.customer.province || '',
    city: props.customer.city || '',
    district: props.customer.district || '',
    address: props.customer.address || '',
    website: props.customer.website || '',
    source: props.customer.source || '',
    level: props.customer.level,
    owner_id: props.customer.owner_id || props.customer.owner?.id,
    tags: props.customer.tags || [],
    remarks: props.customer.remarks || '',
  }
}

const regionModel = computed({
  get: () => ({
    province: formData.value.province || '',
    city: formData.value.city || '',
    district: formData.value.district || '',
  }),
  set: (value: { province: string; city: string; district: string }) => {
    formData.value.province = value.province
    formData.value.city = value.city
    formData.value.district = value.district
  },
})

const isSalesPosition = (position?: string) => {
  const text = (position || '').toLowerCase()
  return text.includes('销售') || text.includes('ism')
}

const isTechnicalPosition = (position?: string) => {
  const text = (position || '').toLowerCase()
  return text.includes('技术') || text.includes('to') || text.includes('tbm') || text.includes('rtm')
}

const salesUsers = computed(() => {
  const activeUsers = allUsers.value.filter(user => user.status === 1)
  const filtered = activeUsers.filter((user) => {
    if (isSalesPosition(user.position)) return true
    if (isTechnicalPosition(user.position)) return false
    return false
  })
  return filtered.length > 0 ? filtered : activeUsers
})

const filteredSalesUsers = computed(() => {
  const keyword = salesKeyword.value.trim().toLowerCase()
  if (!keyword) return salesUsers.value
  return salesUsers.value.filter((user) => {
    const name = (user.real_name || user.username || '').toLowerCase()
    return name.includes(keyword) || user.username.toLowerCase().includes(keyword)
  })
})

const syncOwnerNameFromId = () => {
  if (!formData.value.owner_id) return
  const matched = salesUsers.value.find(user => user.id === formData.value.owner_id)
  if (matched) {
    formData.value.owner_name_3 = matched.real_name || matched.username
  }
}

const syncOwnerIdFromName = () => {
  if (formData.value.owner_id || !formData.value.owner_name_3) return
  const target = formData.value.owner_name_3.trim().toLowerCase()
  const matched = salesUsers.value.find((user) => {
    const candidate = (user.real_name || user.username || '').trim().toLowerCase()
    return candidate === target
  })
  if (matched) {
    formData.value.owner_id = matched.id
  }
}

const loadUsers = async () => {
  try {
    const response = await userApi.getUsers({ page: 1, page_size: 100 })
    allUsers.value = response.items || []
    syncOwnerIdFromName()
    syncOwnerNameFromId()
  } catch (error) {
    console.error('Failed to load users for owner select:', error)
    allUsers.value = []
  }
}

watch(
  () => formData.value.owner_id,
  () => {
    syncOwnerNameFromId()
  }
)

// 添加标签
const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !formData.value.tags?.includes(tag)) {
    if (!formData.value.tags) {
      formData.value.tags = []
    }
    formData.value.tags.push(tag)
    newTag.value = ''
  }
}

// 删除标签
const removeTag = (index: number) => {
  formData.value.tags?.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  submitting.value = true
  try {
    formData.value.region = formData.value.city || formData.value.province || formData.value.region || ''
    syncOwnerNameFromId()
    if (props.customer) {
      await customerApi.update(props.customer.id, formData.value)
    } else {
      await customerApi.create(formData.value)
    }
    emit('save')
  } catch (error) {
    console.error('Failed to save customer:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>
