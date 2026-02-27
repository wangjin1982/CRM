<template>
  <div class="p-6">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">客户管理</h1>
      <div class="flex gap-3">
        <button
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 flex items-center gap-2"
          @click="handleImport"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          导入
        </button>
        <button
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 flex items-center gap-2"
          @click="handleExport"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          导出
        </button>
        <button
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 flex items-center gap-2"
          @click="handleCreate"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新增客户
        </button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="bg-white shadow rounded-lg p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">关键词</label>
          <input
            v-model="filters.keyword"
            type="text"
            placeholder="客户名称"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            @keyup.enter="handleSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">客户类型</label>
          <select
            v-model="filters.customer_type"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">全部</option>
            <option value="enterprise">企业</option>
            <option value="individual">个人</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">客户级别</label>
          <select
            v-model="filters.level"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">全部</option>
            <option value="A">A级</option>
            <option value="B">B级</option>
            <option value="C">C级</option>
            <option value="D">D级</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
          <select
            v-model="filters.status"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">全部</option>
            <option value="active">活跃</option>
            <option value="inactive">非活跃</option>
            <option value="pool">公海池</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">所属行业</label>
          <input
            v-model="filters.industry"
            type="text"
            placeholder="行业"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="flex items-end gap-2">
          <button
            class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            @click="handleSearch"
          >
            搜索
          </button>
          <button
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            @click="handleReset"
          >
            重置
          </button>
        </div>
      </div>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="selectedIds.length > 0" class="bg-indigo-50 border border-indigo-200 rounded-lg p-3 mb-4 flex items-center justify-between">
      <span class="text-sm text-indigo-700">已选择 {{ selectedIds.length }} 条记录</span>
      <div class="flex gap-2">
        <button
          class="px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50"
          @click="handleBatchTransfer"
        >
          批量转移
        </button>
        <button
          class="px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50"
          @click="handleBatchAssignTags"
        >
          分配标签
        </button>
        <button
          class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
          @click="selectedIds = []"
        >
          取消选择
        </button>
      </div>
    </div>

    <!-- 客户列表 -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  :checked="selectedIds.length === customers.length && customers.length > 0"
                  @change="handleSelectAll"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">1#客户名称（中）</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">省份/城市</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">3#客户类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">3#客户分级</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">5#成交客户</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">5#电气工程师人数</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">3#负责人</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="customer in customers" :key="customer.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  :checked="selectedIds.includes(customer.id)"
                  @change="toggleSelect(customer.id)"
                />
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ customer.customer_name }}</div>
                    <div class="text-sm text-gray-500">{{ customer.customer_name_en || customer.customer_no }}</div>
                  </div>
                </div>
                <div v-if="customer.tags && customer.tags.length > 0" class="mt-1 flex gap-1 flex-wrap">
                  <span
                    v-for="tag in customer.tags"
                    :key="tag"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800"
                  >
                    {{ tag }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ customer.province || '-' }} / {{ customer.city || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ customer.customer_type_3 || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ customer.customer_level_3 || customer.level || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ customer.deal_customer_5 === 1 ? '是' : customer.deal_customer_5 === 0 ? '否' : '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ customer.electrical_engineer_count_5 ?? '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ customer.owner_name_3 || customer.owner?.name || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
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
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(customer.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <router-link
                  :to="`/customers/${customer.id}`"
                  class="text-indigo-600 hover:text-indigo-900 mr-3"
                >
                  查看
                </router-link>
                <button
                  class="text-indigo-600 hover:text-indigo-900 mr-3"
                  @click="handleEdit(customer)"
                >
                  编辑
                </button>
                <button
                  class="text-red-600 hover:text-red-900"
                  @click="handleDelete(customer)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          共 {{ total }} 条记录，第 {{ page }} / {{ totalPages }} 页
        </div>
        <div class="flex gap-2">
          <button
            class="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 disabled:opacity-50"
            :disabled="page <= 1"
            @click="handlePageChange(page - 1)"
          >
            上一页
          </button>
          <button
            class="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 disabled:opacity-50"
            :disabled="page >= totalPages"
            @click="handlePageChange(page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 创建/编辑客户弹窗 -->
    <CustomerForm
      v-if="showFormModal"
      :customer="editingCustomer"
      @close="showFormModal = false"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { customerApi } from '@/core/api'
import type { Customer, CustomerQueryParams } from '@/core/types'
import CustomerForm from './components/CustomerForm.vue'

const router = useRouter()

// 数据
const customers = ref<Customer[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedIds = ref<number[]>([])

// 筛选条件
const filters = ref<Partial<CustomerQueryParams>>({
  keyword: '',
  customer_type: undefined,
  level: undefined,
  status: undefined,
  industry: '',
})

// 弹窗
const showFormModal = ref(false)
const editingCustomer = ref<Customer | null>(null)

// 状态映射
const statusMap: Record<string, string> = {
  active: '活跃',
  inactive: '非活跃',
  pool: '公海池',
}

// 计算总页数
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 加载数据
const loadData = async () => {
  try {
    const response = await customerApi.getList({
      ...filters.value,
      page: page.value,
      page_size: pageSize.value,
    })
    customers.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('Failed to load customers:', error)
  }
}

// 搜索
const handleSearch = () => {
  page.value = 1
  loadData()
}

// 重置
const handleReset = () => {
  filters.value = {
    keyword: '',
    customer_type: undefined,
    level: undefined,
    status: undefined,
    industry: '',
  }
  handleSearch()
}

// 分页
const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadData()
}

// 选择
const toggleSelect = (id: number) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const handleSelectAll = () => {
  if (selectedIds.value.length === customers.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = customers.value.map(c => c.id)
  }
}

// 创建
const handleCreate = () => {
  editingCustomer.value = null
  showFormModal.value = true
}

// 编辑
const handleEdit = (customer: Customer) => {
  editingCustomer.value = customer
  showFormModal.value = true
}

// 保存
const handleSave = () => {
  showFormModal.value = false
  loadData()
}

// 删除
const handleDelete = async (customer: Customer) => {
  if (!confirm(`确定要删除客户"${customer.customer_name}"吗？`)) {
    return
  }

  try {
    await customerApi.delete(customer.id)
    loadData()
  } catch (error) {
    console.error('Failed to delete customer:', error)
  }
}

// 批量转移
const handleBatchTransfer = () => {
  // TODO: 实现批量转移弹窗
  alert('批量转移功能开发中')
}

// 批量分配标签
const handleBatchAssignTags = () => {
  // TODO: 实现批量分配标签弹窗
  alert('批量分配标签功能开发中')
}

// 导出
const handleExport = async () => {
  try {
    const blob = await customerApi.export(filters.value)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `customers_${new Date().getTime()}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export customers:', error)
  }
}

// 导入
const handleImport = () => {
  // TODO: 实现导入弹窗
  alert('导入功能开发中')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>
