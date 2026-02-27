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
      <h2 class="mb-2 text-lg font-semibold">客户属性智能补全（先预览后确认）</h2>
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
      <div v-if="selectedCustomerLoading" class="mt-2 text-xs text-gray-500">客户详情加载中...</div>

      <div class="mt-3">
        <p class="mb-2 text-sm text-gray-600">目标字段</p>
        <div class="flex flex-wrap gap-3">
          <label v-for="field in enrichFields" :key="field.value" class="inline-flex items-center gap-2 text-sm">
            <input v-model="selectedFields" type="checkbox" :value="field.value" />
            {{ field.label }}
          </label>
        </div>
      </div>

      <div v-if="selectedCustomerDetail && selectedFieldRows.length" class="mt-4 rounded border border-slate-200 bg-slate-50 p-3">
        <p class="mb-2 text-sm font-medium text-slate-800">
          当前客户信息：{{ selectedCustomerDetail.customer_name }}
        </p>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-100">
              <tr>
                <th class="px-3 py-2 text-left">字段</th>
                <th class="px-3 py-2 text-left">当前值</th>
                <th class="px-3 py-2 text-left">状态</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="row in selectedFieldRows" :key="row.field">
                <td class="px-3 py-2">{{ row.label }}</td>
                <td class="px-3 py-2">
                  <span class="line-clamp-2 break-all">{{ row.current_value || '-' }}</span>
                </td>
                <td class="px-3 py-2">
                  <span
                    class="rounded px-2 py-0.5 text-xs"
                    :class="row.is_empty ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'"
                  >
                    {{ row.is_empty ? '空缺' : '已填写' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="mt-3 flex flex-wrap gap-2">
        <button
          class="rounded bg-indigo-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="previewLoading"
          @click="runEnrichPreview"
        >
          {{ previewLoading ? '生成建议中...' : '开始补全（生成建议）' }}
        </button>
        <button
          v-if="enrichPreview"
          class="rounded border px-4 py-2"
          @click="clearPreview"
        >
          清空建议
        </button>
      </div>
      <p v-if="enrichError" class="mt-2 text-sm text-red-700">{{ enrichError }}</p>
      <p v-if="enrichMsg" class="mt-2 text-sm text-green-700">{{ enrichMsg }}</p>

      <div v-if="enrichPreview" class="mt-4 rounded border border-indigo-100 bg-indigo-50 p-3 text-sm">
        <p>
          <span class="font-medium">预览请求ID：</span>{{ enrichPreview.request_id }}
        </p>
        <p>
          <span class="font-medium">候选字段数：</span>{{ enrichPreview.preview_count || 0 }}
        </p>
        <div class="mt-1 text-xs text-slate-600">
          <span class="font-medium">数据来源：</span>
          百度百科
          <template v-if="enrichPreview.data_sources?.baidu_baike?.matched">
            （已命中：
            <a
              class="text-indigo-700 underline"
              :href="enrichPreview.data_sources.baidu_baike.url"
              target="_blank"
              rel="noreferrer"
            >
              {{ enrichPreview.data_sources.baidu_baike.url }}
            </a>
            ）
          </template>
          <template v-else>（未命中，已使用GLM补全）</template>
        </div>

        <div
          v-if="baikeInfoRows.length || enrichPreview.external_profile?.summary"
          class="mt-3 rounded border border-slate-200 bg-white p-3"
        >
          <p class="text-sm font-medium text-slate-800">百度百科提取信息</p>
          <p v-if="enrichPreview.external_profile?.summary" class="mt-1 text-xs text-slate-700">
            {{ enrichPreview.external_profile.summary }}
          </p>
          <div v-if="baikeInfoRows.length" class="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
            <div
              v-for="item in baikeInfoRows"
              :key="item.key"
              class="rounded border border-slate-200 px-2 py-1"
            >
              <p class="text-[11px] text-slate-500">{{ item.key }}</p>
              <p class="text-xs text-slate-800 break-all">{{ item.value }}</p>
            </div>
          </div>
        </div>

        <div class="mt-3 overflow-x-auto">
          <table class="min-w-full divide-y divide-indigo-100 text-sm">
            <thead class="bg-indigo-100/60">
              <tr>
                <th class="px-3 py-2 text-left">确认</th>
                <th class="px-3 py-2 text-left">字段</th>
                <th class="px-3 py-2 text-left">当前值</th>
                <th class="px-3 py-2 text-left">建议值（可修改）</th>
                <th class="px-3 py-2 text-left">说明</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-indigo-100 bg-white">
              <tr v-for="row in previewRows" :key="row.field">
                <td class="px-3 py-2">
                  <input
                    v-model="acceptedMap[row.field]"
                    type="checkbox"
                    :disabled="!pendingUpdates[row.field]"
                  />
                </td>
                <td class="px-3 py-2">{{ row.label }}</td>
                <td class="px-3 py-2">
                  <span class="line-clamp-2 break-all">{{ row.current_value || '-' }}</span>
                </td>
                <td class="px-3 py-2">
                  <textarea
                    v-if="isLongTextField(row.field)"
                    v-model="pendingUpdates[row.field]"
                    rows="3"
                    class="w-full rounded border px-2 py-1"
                  ></textarea>
                  <input
                    v-else
                    v-model="pendingUpdates[row.field]"
                    type="text"
                    class="w-full rounded border px-2 py-1"
                  />
                </td>
                <td class="px-3 py-2 text-xs text-slate-600">{{ row.reason }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-3 flex flex-wrap gap-2">
          <button
            class="rounded bg-emerald-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="applyLoading || confirmedCount === 0"
            @click="applyEnrich"
          >
            {{ applyLoading ? '写入中...' : '确认写入客户信息' }}
          </button>
          <button class="rounded border px-4 py-2" @click="selectAllSuggested">全选有建议字段</button>
          <button class="rounded border px-4 py-2" @click="unselectAllSuggested">取消全选</button>
        </div>
        <p class="mt-2 text-xs text-slate-600">
          当前已选可写入字段：{{ confirmedCount }} 个
        </p>
      </div>

      <div v-if="applyResult" class="mt-3 rounded border bg-emerald-50 p-3 text-sm">
        <p><span class="font-medium">写入完成：</span>{{ applyResult.customer_name }}</p>
        <p><span class="font-medium">更新字段数：</span>{{ applyResult.applied_count || 0 }}</p>
        <div v-if="applyResult.change_details?.length" class="mt-2">
          <p class="font-medium">已更新字段：</p>
          <ul class="list-inside list-disc">
            <li v-for="item in applyResult.change_details" :key="`${item.field}-${item.new_value}`">
              {{ item.label || item.field }}：`{{ item.old_value || '-' }}` -> `{{ item.new_value }}`
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
import { computed, onMounted, ref, watch } from 'vue'
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
const selectedCustomerDetail = ref<any>(null)
const selectedCustomerLoading = ref(false)

const overwrite = ref(false)
const enrichMsg = ref('')
const enrichError = ref('')
const previewLoading = ref(false)
const applyLoading = ref(false)
const enrichPreview = ref<any>(null)
const applyResult = ref<any>(null)
const pendingUpdates = ref<Record<string, string>>({})
const acceptedMap = ref<Record<string, boolean>>({})
const selectedFields = ref<string[]>([
  'website',
  'address',
  'product_info',
  'company_info',
  'industry',
  'legal_person',
  'registered_capital',
  'establish_date',
])
const enrichFields = [
  { value: 'website', label: '网址' },
  { value: 'address', label: '地址' },
  { value: 'product_info', label: '产品信息' },
  { value: 'company_info', label: '公司信息' },
  { value: 'industry', label: '行业' },
  { value: 'legal_person', label: '法人代表' },
  { value: 'registered_capital', label: '注册资本' },
  { value: 'establish_date', label: '成立日期' },
  { value: 'company_size', label: '公司规模' },
  { value: 'source', label: '客户来源' },
  { value: 'remarks', label: '备注' },
]
const enrichFieldLabelMap = Object.fromEntries(enrichFields.map(item => [item.value, item.label]))

const extractError = (error: any) => {
  if (error?.response?.data?.detail) {
    return typeof error.response.data.detail === 'string'
      ? error.response.data.detail
      : JSON.stringify(error.response.data.detail)
  }
  return error?.message || '请求失败'
}

const normalizeValue = (value: any) => {
  if (value === null || value === undefined) return ''
  return typeof value === 'string' ? value.trim() : String(value).trim()
}

const selectedFieldRows = computed(() =>
  selectedFields.value.map((field) => {
    const current = normalizeValue(selectedCustomerDetail.value?.[field])
    return {
      field,
      label: enrichFieldLabelMap[field] || field,
      current_value: current,
      is_empty: !current,
    }
  })
)

const previewRows = computed(() => {
  if (!enrichPreview.value?.field_status) return []
  return selectedFields.value.map((field) => {
    const status = enrichPreview.value.field_status[field] || {}
    return {
      field,
      label: status.label || enrichFieldLabelMap[field] || field,
      current_value: status.current_value || '',
      reason: status.reason || '',
    }
  })
})

const baikeInfoRows = computed(() => {
  const info = enrichPreview.value?.external_profile?.basic_info || {}
  return Object.keys(info)
    .slice(0, 16)
    .map((key) => ({
      key,
      value: info[key],
    }))
})

const confirmedCount = computed(() => Object.keys(collectConfirmedUpdates()).length)

const isLongTextField = (field: string) => ['address', 'product_info', 'company_info', 'remarks'].includes(field)

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

const loadSelectedCustomerDetail = async () => {
  if (!selectedCustomerId.value) {
    selectedCustomerDetail.value = null
    return
  }
  selectedCustomerLoading.value = true
  try {
    selectedCustomerDetail.value = await customerApi.getDetail(selectedCustomerId.value)
  } catch (error) {
    selectedCustomerDetail.value = null
    enrichError.value = extractError(error)
  } finally {
    selectedCustomerLoading.value = false
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

const initPreviewSelection = (preview: any) => {
  const nextPending: Record<string, string> = {}
  const nextAccepted: Record<string, boolean> = {}
  const fieldStatus = preview?.field_status || {}
  for (const field of selectedFields.value) {
    const status = fieldStatus[field] || {}
    const candidate = normalizeValue(status.candidate_value || preview?.proposed_updates?.[field])
    nextPending[field] = candidate
    nextAccepted[field] = Boolean(candidate && status.will_update)
  }
  pendingUpdates.value = nextPending
  acceptedMap.value = nextAccepted
}

const clearPreview = () => {
  enrichPreview.value = null
  pendingUpdates.value = {}
  acceptedMap.value = {}
}

const runEnrichPreview = async () => {
  enrichMsg.value = ''
  enrichError.value = ''
  applyResult.value = null
  if (!selectedCustomerId.value) {
    enrichError.value = '请先选择客户'
    return
  }
  if (!selectedFields.value.length) {
    enrichError.value = '请至少选择一个补全字段'
    return
  }
  previewLoading.value = true
  try {
    const result = await aiApi.previewCustomerEnrich(selectedCustomerId.value, {
      target_fields: selectedFields.value,
      overwrite: overwrite.value,
    })
    enrichPreview.value = result
    initPreviewSelection(result)
    enrichMsg.value = result.preview_count
      ? `已生成 ${result.preview_count} 项建议，请核对后确认写入。`
      : '本次没有生成可写入建议（可能字段已有值或模型未返回有效内容）。'
  } catch (error) {
    clearPreview()
    enrichError.value = extractError(error)
  } finally {
    previewLoading.value = false
  }
}

const collectConfirmedUpdates = () => {
  const updates: Record<string, string> = {}
  for (const field of selectedFields.value) {
    const accepted = !!acceptedMap.value[field]
    const value = normalizeValue(pendingUpdates.value[field])
    if (accepted && value) {
      updates[field] = value
    }
  }
  return updates
}

const applyEnrich = async () => {
  enrichMsg.value = ''
  enrichError.value = ''
  applyResult.value = null
  if (!selectedCustomerId.value) {
    enrichError.value = '请先选择客户'
    return
  }
  if (!enrichPreview.value?.request_id) {
    enrichError.value = '请先生成补全建议'
    return
  }
  const updates = collectConfirmedUpdates()
  if (!Object.keys(updates).length) {
    enrichError.value = '请至少勾选一项有效建议后再确认写入'
    return
  }
  applyLoading.value = true
  try {
    const result = await aiApi.applyCustomerEnrich(selectedCustomerId.value, {
      request_id: enrichPreview.value.request_id,
      updates,
    })
    applyResult.value = result
    enrichMsg.value = `已确认写入 ${result.applied_count || 0} 个字段。`
    await Promise.all([
      loadSelectedCustomerDetail(),
      loadCustomers(customerKeyword.value.trim()),
    ])
    clearPreview()
  } catch (error) {
    enrichError.value = extractError(error)
  } finally {
    applyLoading.value = false
  }
}

const selectAllSuggested = () => {
  const nextMap = { ...acceptedMap.value }
  for (const field of selectedFields.value) {
    const value = normalizeValue(pendingUpdates.value[field])
    nextMap[field] = !!value
  }
  acceptedMap.value = nextMap
}

const unselectAllSuggested = () => {
  const nextMap = { ...acceptedMap.value }
  for (const field of selectedFields.value) {
    nextMap[field] = false
  }
  acceptedMap.value = nextMap
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

watch(selectedCustomerId, async () => {
  enrichError.value = ''
  enrichMsg.value = ''
  applyResult.value = null
  clearPreview()
  await loadSelectedCustomerDetail()
})

watch(selectedFields, () => {
  applyResult.value = null
  clearPreview()
})

onMounted(async () => {
  await loadConfig()
  await loadCustomers()
  await loadAlerts()
})
</script>
