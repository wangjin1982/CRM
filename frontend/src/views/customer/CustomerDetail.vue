<template>
  <div class="p-6">
    <!-- 返回按钮 -->
    <div class="mb-6">
      <router-link
        to="/customers"
        class="inline-flex items-center text-gray-600 hover:text-gray-900"
      >
        <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回客户列表
      </router-link>
    </div>

    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else-if="customer">
      <!-- 客户基本信息 -->
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ customer.customer_name }}</h1>
            <p class="text-sm text-gray-500 mt-1">{{ customer.customer_name_en || customer.customer_no }}</p>
          </div>
          <div class="flex gap-2">
            <button
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              @click="handleEdit"
            >
              编辑
            </button>
            <button
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              @click="show360View = true"
            >
              360度视图
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 基本信息 -->
          <div>
            <h3 class="text-sm font-medium text-gray-500 mb-3">基本信息</h3>
            <dl class="space-y-2">
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">省份/城市:</dt>
                <dd class="text-sm text-gray-900">{{ customer.province || '-' }} / {{ customer.city || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">3#客户类型:</dt>
                <dd class="text-sm text-gray-900">{{ customer.customer_type_3 || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">3#客户分级:</dt>
                <dd class="text-sm text-gray-900">{{ customer.customer_level_3 || customer.level || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">5#成交客户:</dt>
                <dd class="text-sm text-gray-900">{{ customer.deal_customer_5 === 1 ? '是' : customer.deal_customer_5 === 0 ? '否' : '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">5#电气工程师人数:</dt>
                <dd class="text-sm text-gray-900">{{ customer.electrical_engineer_count_5 ?? '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">3#负责人:</dt>
                <dd class="text-sm text-gray-900">{{ customer.owner_name_3 || customer.owner?.name || '-' }}</dd>
              </div>
              <div v-if="customer.customer_type === 'enterprise'">
                <div class="flex justify-between">
                  <dt class="text-sm text-gray-500">公司规模:</dt>
                  <dd class="text-sm text-gray-900">{{ customer.company_size || '-' }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-sm text-gray-500">法人代表:</dt>
                  <dd class="text-sm text-gray-900">{{ customer.legal_person || '-' }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-sm text-gray-500">注册资本:</dt>
                  <dd class="text-sm text-gray-900">{{ customer.registered_capital || '-' }}</dd>
                </div>
              </div>
            </dl>
          </div>

          <!-- 联系信息 -->
          <div>
            <h3 class="text-sm font-medium text-gray-500 mb-3">联系信息</h3>
            <dl class="space-y-2">
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">省份:</dt>
                <dd class="text-sm text-gray-900">{{ customer.province || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">城市:</dt>
                <dd class="text-sm text-gray-900">{{ customer.city || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">详细地址:</dt>
                <dd class="text-sm text-gray-900">{{ customer.address || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">官方网站:</dt>
                <dd class="text-sm text-gray-900">
                  <a v-if="customer.website" :href="customer.website" target="_blank" class="text-indigo-600 hover:text-indigo-900">
                    {{ customer.website }}
                  </a>
                  <span v-else>-</span>
                </dd>
              </div>
            </dl>
          </div>

          <!-- 业务信息 -->
          <div>
            <h3 class="text-sm font-medium text-gray-500 mb-3">业务信息</h3>
            <dl class="space-y-2">
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">客户来源:</dt>
                <dd class="text-sm text-gray-900">{{ customer.source || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">负责人:</dt>
                <dd class="text-sm text-gray-900">{{ customer.owner?.name || '-' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">状态:</dt>
                <dd class="text-sm">
                  <span
                    :class="{
                      'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full': true,
                      'bg-green-100 text-green-800': customer.status === 'active',
                      'bg-gray-100 text-gray-800': customer.status === 'inactive',
                      'bg-blue-100 text-blue-800': customer.status === 'pool',
                    }"
                  >
                    {{ statusMap[customer.status] }}
                  </span>
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">创建时间:</dt>
                <dd class="text-sm text-gray-900">{{ formatDate(customer.created_at) }}</dd>
              </div>
            </dl>
            <div v-if="customer.company_info" class="mt-3">
              <p class="text-sm text-gray-500">公司信息:</p>
              <p class="text-sm text-gray-900">{{ customer.company_info }}</p>
            </div>
            <div v-if="customer.product_info" class="mt-3">
              <p class="text-sm text-gray-500">产品信息:</p>
              <p class="text-sm text-gray-900">{{ customer.product_info }}</p>
            </div>
          </div>
        </div>

        <!-- 标签 -->
        <div v-if="customer.tags && customer.tags.length > 0" class="mt-4">
          <h3 class="text-sm font-medium text-gray-500 mb-2">标签</h3>
          <div class="flex gap-2 flex-wrap">
            <span
              v-for="tag in customer.tags"
              :key="tag"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- 备注 -->
        <div v-if="customer.remarks" class="mt-4">
          <h3 class="text-sm font-medium text-gray-500 mb-2">备注</h3>
          <p class="text-sm text-gray-900">{{ customer.remarks }}</p>
        </div>
      </div>

      <!-- 标签页 -->
      <div class="bg-white shadow rounded-lg">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="px-6 py-3 text-sm font-medium"
              :class="activeTab === tab.key ? 'border-indigo-500 text-indigo-600 border-b-2' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- 联系人 -->
          <div v-if="activeTab === 'contacts'">
            <ContactList :customer-id="customerId" />
          </div>

          <!-- 交互记录 -->
          <div v-else-if="activeTab === 'interactions'">
            <div class="mb-4 flex items-center justify-between">
              <h3 class="text-sm font-medium text-gray-700">客户交互记录</h3>
              <button
                class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700"
                @click="showInteractionForm = !showInteractionForm"
              >
                {{ showInteractionForm ? '收起' : '新增交互记录' }}
              </button>
            </div>

            <form
              v-if="showInteractionForm"
              class="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-4"
              @submit.prevent="handleCreateInteraction"
            >
              <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
                <div>
                  <label class="mb-1 block text-xs text-gray-600">交互类型</label>
                  <select
                    v-model="interactionForm.interaction_type"
                    class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    required
                  >
                    <option value="call">电话</option>
                    <option value="email">邮件</option>
                    <option value="visit">拜访</option>
                    <option value="wechat">微信</option>
                    <option value="other">其他</option>
                  </select>
                </div>
                <div>
                  <label class="mb-1 block text-xs text-gray-600">方向</label>
                  <select
                    v-model="interactionForm.direction"
                    class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                  >
                    <option value="">未指定</option>
                    <option value="outbound">外呼</option>
                    <option value="inbound">来电</option>
                  </select>
                </div>
                <div>
                  <label class="mb-1 block text-xs text-gray-600">下次跟进时间</label>
                  <input
                    v-model="interactionForm.next_follow_at"
                    type="datetime-local"
                    class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
                <div class="md:col-span-3">
                  <label class="mb-1 block text-xs text-gray-600">主题</label>
                  <input
                    v-model="interactionForm.subject"
                    type="text"
                    class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    placeholder="如：预算确认、技术交流、方案澄清"
                  />
                </div>
                <div class="md:col-span-3">
                  <label class="mb-1 block text-xs text-gray-600">内容</label>
                  <textarea
                    v-model="interactionForm.content"
                    rows="3"
                    class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                    placeholder="记录本次沟通结论与下一步动作"
                  ></textarea>
                </div>
              </div>
              <div class="mt-3 flex justify-end">
                <button
                  type="submit"
                  class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700 disabled:opacity-60"
                  :disabled="savingInteraction"
                >
                  {{ savingInteraction ? '保存中...' : '保存交互记录' }}
                </button>
              </div>
            </form>

            <div v-if="interactionsLoading" class="flex justify-center items-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
            <div v-else-if="interactions.length === 0" class="text-center py-8 text-gray-500">
              当前客户暂无交互记录
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="item in interactions"
                :key="item.id"
                class="rounded-lg border border-gray-200 bg-white p-4"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ interactionTypeText[item.interaction_type] || item.interaction_type }}
                      <span v-if="item.subject" class="ml-1">- {{ item.subject }}</span>
                    </div>
                    <div class="mt-1 text-xs text-gray-500">
                      {{ item.direction ? directionText[item.direction] || item.direction : '方向未指定' }} |
                      {{ formatDateTime(item.created_at) }}
                    </div>
                  </div>
                  <button
                    class="text-xs text-red-600 hover:text-red-800"
                    @click="handleDeleteInteraction(item.id)"
                  >
                    删除
                  </button>
                </div>
                <p v-if="item.content" class="mt-2 whitespace-pre-line text-sm text-gray-700">{{ item.content }}</p>
                <div v-if="item.next_follow_at" class="mt-2 text-xs text-indigo-700">
                  下次跟进：{{ formatDateTime(item.next_follow_at) }}
                </div>
              </div>
            </div>
          </div>

          <!-- 商机 -->
          <div v-else-if="activeTab === 'opportunities'">
            <div v-if="opportunitiesLoading" class="flex justify-center items-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
            <div v-else-if="opportunities.length === 0" class="text-center py-12 text-gray-500">
              该客户暂无关联商机
            </div>
            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">商机编号</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">商机名称</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">阶段</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">预估金额</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">负责人</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="opp in opportunities" :key="opp.id">
                    <td class="px-4 py-2 text-sm text-gray-700">{{ opp.opportunity_no }}</td>
                    <td class="px-4 py-2 text-sm text-gray-900">{{ opp.opportunity_name }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ opp.stage_name || '-' }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">¥{{ formatAmount(opp.estimated_amount) }}</td>
                    <td class="px-4 py-2 text-sm">
                      <span
                        class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
                        :class="{
                          'bg-blue-100 text-blue-800': opp.status === 'open',
                          'bg-green-100 text-green-800': opp.status === 'won',
                          'bg-red-100 text-red-800': opp.status === 'lost',
                          'bg-gray-100 text-gray-800': opp.status === 'abandoned',
                        }"
                      >
                        {{ opportunityStatusMap[opp.status] || opp.status }}
                      </span>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ opp.owner_name || '-' }}</td>
                    <td class="px-4 py-2 text-sm">
                      <router-link
                        :to="`/opportunities/${opp.id}`"
                        class="text-indigo-600 hover:text-indigo-900"
                      >
                        查看详情
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 拜访记录 -->
          <div v-else-if="activeTab === 'visits'">
            <ActivityTab
              :customer-id="customerId"
              title="客户相关活动（拜访/跟进/任务/日程）"
            />
          </div>

          <!-- 附件 -->
          <div v-else-if="activeTab === 'documents'">
            <div class="text-center py-12 text-gray-500">
              附件功能开发中
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 360度视图弹窗 -->
    <div
      v-if="show360View"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="show360View = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-auto m-4">
        <div class="p-6 border-b border-gray-200 flex justify-between items-center">
          <h2 class="text-xl font-bold text-gray-900">360度视图</h2>
          <button
            class="text-gray-400 hover:text-gray-600"
            @click="show360View = false"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <div v-if="view360Loading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
          <div v-else-if="view360Data">
            <!-- 时间轴 -->
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">时间轴</h3>
              <div class="space-y-4">
                <div
                  v-for="item in view360Data.timeline"
                  :key="item.created_at"
                  class="flex gap-4"
                >
                  <div class="flex flex-col items-center">
                    <div class="w-3 h-3 bg-indigo-600 rounded-full"></div>
                    <div class="w-0.5 flex-1 bg-gray-200"></div>
                  </div>
                  <div class="flex-1 pb-4">
                    <div class="text-sm font-medium text-gray-900">{{ item.title }}</div>
                    <div class="text-sm text-gray-600 mt-1">{{ item.content }}</div>
                    <div class="text-xs text-gray-500 mt-1">{{ formatDateTime(item.created_at) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑客户弹窗 -->
    <CustomerForm
      v-if="showEditModal"
      :customer="customer"
      @close="showEditModal = false"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { customerApi, interactionApi, opportunityApi } from '@/core/api'
import type { CustomerDetail, Customer360View, CustomerInteraction, Opportunity } from '@/core/types'
import ContactList from './components/ContactList.vue'
import CustomerForm from './components/CustomerForm.vue'
import ActivityTab from '../opportunity/tabs/ActivityTab.vue'

const route = useRoute()
const customerId = Number(route.params.id)

// 数据
const customer = ref<CustomerDetail | null>(null)
const loading = ref(true)
const showEditModal = ref(false)
const show360View = ref(false)
const view360Data = ref<Customer360View | null>(null)
const view360Loading = ref(false)
const opportunities = ref<Opportunity[]>([])
const opportunitiesLoading = ref(false)
const interactions = ref<CustomerInteraction[]>([])
const interactionsLoading = ref(false)
const showInteractionForm = ref(false)
const savingInteraction = ref(false)
const interactionForm = ref({
  interaction_type: 'call' as CustomerInteraction['interaction_type'],
  direction: '' as '' | 'inbound' | 'outbound',
  subject: '',
  content: '',
  next_follow_at: '',
})

// 标签页
const activeTab = ref('contacts')
const tabs = [
  { key: 'contacts', label: '联系人' },
  { key: 'interactions', label: '交互记录' },
  { key: 'opportunities', label: '商机' },
  { key: 'visits', label: '活动记录' },
  { key: 'documents', label: '附件' },
]

// 状态映射
const statusMap: Record<string, string> = {
  active: '活跃',
  inactive: '非活跃',
  pool: '公海池',
}

const opportunityStatusMap: Record<string, string> = {
  open: '进行中',
  won: '已赢单',
  lost: '已输单',
  abandoned: '已放弃',
}

const interactionTypeText: Record<string, string> = {
  call: '电话',
  email: '邮件',
  visit: '拜访',
  wechat: '微信',
  other: '其他',
}

const directionText: Record<string, string> = {
  inbound: '来电',
  outbound: '外呼',
}

// 加载客户详情
const loadCustomer = async () => {
  loading.value = true
  try {
    customer.value = await customerApi.getDetail(customerId)
  } catch (error) {
    console.error('Failed to load customer:', error)
  } finally {
    loading.value = false
  }
}

// 加载360度视图
const load360View = async () => {
  view360Loading.value = true
  try {
    view360Data.value = await customerApi.get360View(customerId)
  } catch (error) {
    console.error('Failed to load 360 view:', error)
  } finally {
    view360Loading.value = false
  }
}

const loadCustomerOpportunities = async () => {
  opportunitiesLoading.value = true
  try {
    const response = await opportunityApi.getOpportunities({
      page: 1,
      page_size: 100,
      customer_id: customerId,
    })
    opportunities.value = response.items || []
  } catch (error) {
    console.error('Failed to load customer opportunities:', error)
    opportunities.value = []
  } finally {
    opportunitiesLoading.value = false
  }
}

const loadInteractions = async () => {
  interactionsLoading.value = true
  try {
    const response = await interactionApi.getByCustomer(customerId, {
      page: 1,
      page_size: 100,
    })
    interactions.value = response.items || []
  } catch (error) {
    console.error('Failed to load interactions:', error)
    interactions.value = []
  } finally {
    interactionsLoading.value = false
  }
}

const handleCreateInteraction = async () => {
  savingInteraction.value = true
  try {
    await interactionApi.create(customerId, {
      interaction_type: interactionForm.value.interaction_type,
      direction: interactionForm.value.direction || undefined,
      subject: interactionForm.value.subject || undefined,
      content: interactionForm.value.content || undefined,
      next_follow_at: interactionForm.value.next_follow_at
        ? new Date(interactionForm.value.next_follow_at).toISOString()
        : undefined,
    })
    interactionForm.value = {
      interaction_type: 'call',
      direction: '',
      subject: '',
      content: '',
      next_follow_at: '',
    }
    showInteractionForm.value = false
    await loadInteractions()
  } catch (error) {
    console.error('Failed to create interaction:', error)
    alert('保存交互记录失败，请稍后重试')
  } finally {
    savingInteraction.value = false
  }
}

const handleDeleteInteraction = async (interactionId: number) => {
  if (!confirm('确定删除这条交互记录吗？')) return
  try {
    await interactionApi.delete(interactionId)
    await loadInteractions()
  } catch (error) {
    console.error('Failed to delete interaction:', error)
    alert('删除失败，请稍后重试')
  }
}

// 编辑
const handleEdit = () => {
  showEditModal.value = true
}

// 保存
const handleSave = () => {
  showEditModal.value = false
  loadCustomer()
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatAmount = (amount?: number) => {
  if (!amount) return '0'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

// 监听360度视图弹窗
const handleShow360View = () => {
  if (show360View.value && !view360Data.value) {
    load360View()
  }
}

// 使用watch监听show360View
watch(show360View, handleShow360View)
watch(activeTab, (tab) => {
  if (tab === 'opportunities' && opportunities.value.length === 0 && !opportunitiesLoading.value) {
    loadCustomerOpportunities()
  }
  if (tab === 'interactions' && interactions.value.length === 0 && !interactionsLoading.value) {
    loadInteractions()
  }
})

onMounted(() => {
  loadCustomer()
})
</script>
