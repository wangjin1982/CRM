<template>
  <div class="p-6">
    <h1 class="mb-4 text-2xl font-bold">AI智能工作台</h1>

    <div class="mb-4 rounded-lg bg-white p-4 shadow">
      <h2 class="mb-2 text-lg font-semibold">API 配置（GLM）</h2>
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div>
          <label class="mb-1 block text-sm text-gray-600">Provider</label>
          <input
            v-model="configForm.provider"
            class="w-full rounded border px-3 py-2"
            placeholder="glm"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm text-gray-600">模型名称</label>
          <input
            v-model="configForm.model_name"
            class="w-full rounded border px-3 py-2"
            placeholder="glm-4-flash"
          />
        </div>
        <div class="md:col-span-2">
          <label class="mb-1 block text-sm text-gray-600">API Base</label>
          <input
            v-model="configForm.api_base"
            class="w-full rounded border px-3 py-2"
            placeholder="https://open.bigmodel.cn/api/paas/v4/chat/completions"
          />
        </div>
        <div class="md:col-span-2">
          <label class="mb-1 block text-sm text-gray-600">GLM API Key</label>
          <input
            v-model="configForm.api_key"
            type="password"
            class="w-full rounded border px-3 py-2"
            placeholder="输入后点击保存"
          />
          <p v-if="configMeta.has_api_key" class="mt-1 text-xs text-gray-500">
            已保存Key：{{ configMeta.api_key_masked || '******' }}
          </p>
        </div>
      </div>
      <div class="mt-3 flex gap-2">
        <button class="rounded bg-blue-600 px-4 py-2 text-white" @click="saveConfig">保存配置</button>
        <button class="rounded border px-4 py-2" @click="loadConfig">刷新</button>
      </div>
      <p v-if="configMsg" class="mt-2 text-sm text-green-700">{{ configMsg }}</p>
      <p v-if="configError" class="mt-2 text-sm text-red-700">{{ configError }}</p>
    </div>

    <div class="mb-4 rounded-lg bg-white p-4 shadow">
      <h2 class="mb-2 text-lg font-semibold">客户属性智能补全</h2>
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div>
          <label class="mb-1 block text-sm text-gray-600">搜索客户</label>
          <div class="flex gap-2">
            <input
              v-model="customerKeyword"
              type="text"
              class="w-full rounded border px-3 py-2"
              placeholder="输入客户名称关键词"
              @keyup.enter="searchCustomers"
            />
            <button class="rounded border px-3 py-2 text-sm" @click="searchCustomers">搜索</button>
          </div>
        </div>
        <div class="flex items-end justify-between">
          <label class="inline-flex items-center gap-2 text-sm text-gray-700">
            <input v-model="overwrite" type="checkbox" />
            覆盖已有字段
          </label>
          <span class="text-xs text-gray-500">已加载 {{ customers.length }} 条</span>
        </div>
      </div>

      <div class="mt-3">
        <label class="mb-1 block text-sm text-gray-600">选择客户</label>
        <select v-model.number="selectedCustomerId" class="w-full rounded border px-3 py-2">
          <option :value="0">请选择客户</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">
            {{ c.customer_name }}{{ c.province || c.city ? `（${c.province || '-'} ${c.city || '-'}）` : '' }}
          </option>
        </select>
      </div>

      <div v-if="customerLoading" class="mt-2 text-xs text-gray-500">客户列表加载中...</div>
      <div v-if="customerError" class="mt-2 text-xs text-red-600">{{ customerError }}</div>

      <div class="mt-3">
        <p class="mb-2 text-sm text-gray-600">目标字段</p>
        <div class="flex flex-wrap gap-3">
          <label v-for="field in enrichFields" :key="field.value" class="inline-flex items-center gap-2 text-sm">
            <input v-model="selectedFields" type="checkbox" :value="field.value" />
            {{ field.label }}
          </label>
        </div>
      </div>

      <div class="mt-3">
        <button class="rounded bg-indigo-600 px-4 py-2 text-white" @click="runEnrich">开始补全</button>
      </div>
      <p v-if="enrichError" class="mt-2 text-sm text-red-700">{{ enrichError }}</p>
      <p v-if="enrichMsg" class="mt-2 text-sm text-green-700">{{ enrichMsg }}</p>

      <div v-if="enrichResult" class="mt-3 rounded border bg-gray-50 p-3 text-sm">
        <p><span class="font-medium">客户：</span>{{ enrichResult.customer_name }}</p>
        <p><span class="font-medium">更新字段数：</span>{{ enrichResult.applied_count || 0 }}</p>
        <div v-if="enrichResult.updated_fields && Object.keys(enrichResult.updated_fields).length" class="mt-2">
          <p class="font-medium">已更新字段：</p>
          <ul class="list-inside list-disc">
            <li v-for="(value, key) in enrichResult.updated_fields" :key="String(key)">
              {{ key }}: {{ value }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="mb-4 rounded-lg bg-white p-4 shadow">
      <h2 class="mb-2 text-lg font-semibold">自然语言查询</h2>
      <div class="flex gap-2">
        <input
          v-model="query"
          class="flex-1 rounded border px-3 py-2"
          placeholder="例如：当前高风险商机有哪些？"
          @keyup.enter="runQuery"
        />
        <button class="rounded bg-blue-600 px-4 py-2 text-white" @click="runQuery">查询</button>
      </div>
      <p v-if="answer" class="mt-3 text-gray-700">{{ answer }}</p>
    </div>

    <div class="rounded-lg bg-white p-4 shadow">
      <h2 class="mb-2 text-lg font-semibold">风险预警</h2>
      <div v-if="!alerts.length" class="text-gray-500">暂无预警</div>
      <div v-else class="space-y-2">
        <div v-for="item in alerts" :key="item.id" class="rounded border p-3">
          <div class="flex items-center justify-between">
            <p class="font-medium">{{ item.title }}</p>
            <span class="text-sm text-red-600">{{ item.alert_level }}</span>
          </div>
          <p class="mt-1 text-sm text-gray-600">{{ item.content }}</p>
          <div class="mt-2 flex gap-2">
            <button class="rounded bg-yellow-100 px-3 py-1 text-sm" @click="ack(item.id)">确认</button>
            <button class="rounded bg-green-100 px-3 py-1 text-sm" @click="resolve(item.id)">解决</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { aiApi, customerApi } from '@/core/api'

const query = ref('')
const answer = ref('')
const alerts = ref<any[]>([])

const configForm = ref({
  provider: 'glm',
  model_name: 'glm-4-flash',
  api_base: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
  api_key: '',
})
const configMeta = ref({
  has_api_key: false,
  api_key_masked: '',
})
const configMsg = ref('')
const configError = ref('')

const customers = ref<any[]>([])
const customerKeyword = ref('')
const customerLoading = ref(false)
const customerError = ref('')
const selectedCustomerId = ref(0)
const overwrite = ref(false)
const enrichResult = ref<any>(null)
const enrichMsg = ref('')
const enrichError = ref('')
const selectedFields = ref<string[]>([
  'website',
  'address',
  'product_info',
  'company_info',
  'industry',
])
const enrichFields = [
  { value: 'website', label: '网址' },
  { value: 'address', label: '地址' },
  { value: 'product_info', label: '产品信息' },
  { value: 'company_info', label: '公司信息' },
  { value: 'industry', label: '行业' },
  { value: 'source', label: '客户来源' },
  { value: 'remarks', label: '备注' },
]

const extractError = (error: any) => {
  if (error?.response?.data?.detail) {
    return typeof error.response.data.detail === 'string'
      ? error.response.data.detail
      : JSON.stringify(error.response.data.detail)
  }
  return error?.message || '请求失败'
}

const loadAlerts = async () => {
  try {
    alerts.value = await aiApi.listAlerts({ status: 'new' })
  } catch (error) {
    console.error('Failed to load alerts:', error)
    alerts.value = []
  }
}

const loadCustomers = async (keyword = '') => {
  customerLoading.value = true
  customerError.value = ''
  try {
    const response = await customerApi.getList({
      page: 1,
      page_size: 100,
      keyword: keyword || undefined,
    })
    customers.value = response.items || []
    if (
      selectedCustomerId.value &&
      !customers.value.some((item: any) => item.id === selectedCustomerId.value)
    ) {
      selectedCustomerId.value = 0
    }
  } catch (error) {
    customers.value = []
    customerError.value = extractError(error)
  } finally {
    customerLoading.value = false
  }
}

const searchCustomers = async () => {
  await loadCustomers(customerKeyword.value.trim())
}

const loadConfig = async () => {
  configMsg.value = ''
  configError.value = ''
  try {
    const cfg = await aiApi.getConfig()
    configForm.value.provider = cfg.provider || 'glm'
    configForm.value.model_name = cfg.model_name || 'glm-4-flash'
    configForm.value.api_base = cfg.api_base || 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
    configForm.value.api_key = ''
    configMeta.value = {
      has_api_key: !!cfg.has_api_key,
      api_key_masked: cfg.api_key_masked || '',
    }
  } catch (error) {
    configError.value = extractError(error)
  }
}

const saveConfig = async () => {
  configMsg.value = ''
  configError.value = ''
  try {
    const payload: any = {
      provider: configForm.value.provider,
      model_name: configForm.value.model_name,
      api_base: configForm.value.api_base,
    }
    if (configForm.value.api_key.trim()) {
      payload.api_key = configForm.value.api_key.trim()
    }
    await aiApi.updateConfig(payload)
    configMsg.value = 'AI配置已保存'
    await loadConfig()
  } catch (error) {
    configError.value = extractError(error)
  }
}

const runEnrich = async () => {
  enrichMsg.value = ''
  enrichError.value = ''
  enrichResult.value = null
  if (!selectedCustomerId.value) {
    enrichError.value = '请先选择客户'
    return
  }
  if (!selectedFields.value.length) {
    enrichError.value = '请至少选择一个补全字段'
    return
  }
  try {
    const result = await aiApi.enrichCustomer(selectedCustomerId.value, {
      target_fields: selectedFields.value,
      overwrite: overwrite.value,
    })
    enrichResult.value = result
    enrichMsg.value = result.message || '补全执行完成'
    await loadCustomers()
  } catch (error) {
    enrichError.value = extractError(error)
  }
}

const runQuery = async () => {
  if (!query.value.trim()) return
  const result = await aiApi.nlQuery(query.value)
  answer.value = result.answer || ''
}

const ack = async (id: number) => {
  await aiApi.acknowledgeAlert(id)
  await loadAlerts()
}

const resolve = async (id: number) => {
  await aiApi.resolveAlert(id)
  await loadAlerts()
}

onMounted(async () => {
  await loadConfig()
  await loadCustomers()
  await loadAlerts()
})
</script>
