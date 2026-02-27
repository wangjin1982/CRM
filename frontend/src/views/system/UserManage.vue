<template>
  <div class="p-6">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">内部人员管理</h1>
        <p class="mt-1 text-sm text-gray-500">录入并管理销售、技术人员档案信息</p>
      </div>
      <button
        class="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
        @click="openCreateModal"
      >
        新增员工
      </button>
    </div>

    <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-lg border bg-white p-4 shadow-sm">
        <p class="text-sm text-gray-500">总人数</p>
        <p class="mt-1 text-2xl font-semibold text-gray-900">{{ users.length }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4 shadow-sm">
        <p class="text-sm text-gray-500">销售人数</p>
        <p class="mt-1 text-2xl font-semibold text-blue-700">{{ salesCount }}</p>
      </div>
      <div class="rounded-lg border bg-white p-4 shadow-sm">
        <p class="text-sm text-gray-500">技术人数</p>
        <p class="mt-1 text-2xl font-semibold text-emerald-700">{{ technicalCount }}</p>
      </div>
    </div>

    <div class="mb-4 rounded-lg border bg-white p-4 shadow-sm">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-4">
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索姓名/用户名/邮箱"
          class="rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
          @keyup.enter="loadUsers"
        />
        <select
          v-model="staffTypeFilter"
          class="rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
        >
          <option value="all">全部类型</option>
          <option value="sales">销售</option>
          <option value="technical">技术</option>
          <option value="other">其他</option>
        </select>
        <button
          class="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
          @click="loadUsers"
        >
          查询
        </button>
        <button
          class="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
          @click="resetFilters"
        >
          重置
        </button>
      </div>
    </div>

    <div class="overflow-hidden rounded-lg border bg-white shadow">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">姓名</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">用户名</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">邮箱</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">手机</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">员工类型</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">岗位</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">状态</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-for="user in filteredUsers" :key="user.id">
            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900">{{ user.real_name || '-' }}</td>
            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900">{{ user.username }}</td>
            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{{ user.email }}</td>
            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{{ user.phone || '-' }}</td>
            <td class="whitespace-nowrap px-4 py-3 text-sm">
              <span
                class="rounded-full px-2 py-1 text-xs font-medium"
                :class="staffTypeClass(getStaffType(user.position))"
              >
                {{ staffTypeLabel(getStaffType(user.position)) }}
              </span>
            </td>
            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{{ user.position || '-' }}</td>
            <td class="whitespace-nowrap px-4 py-3 text-sm">
              <span :class="user.status === 1 ? 'text-green-600' : 'text-red-600'">
                {{ user.status === 1 ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="whitespace-nowrap px-4 py-3 text-sm">
              <button class="mr-3 text-indigo-600 hover:text-indigo-900" @click="openEditModal(user)">编辑</button>
              <button class="text-red-600 hover:text-red-900" @click="handleDelete(user)">删除</button>
            </td>
          </tr>
          <tr v-if="!filteredUsers.length">
            <td colspan="8" class="px-4 py-8 text-center text-sm text-gray-500">暂无人员数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="showFormModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 p-4"
      @click.self="showFormModal = false"
    >
      <div class="max-h-[90vh] w-full max-w-2xl overflow-auto rounded-lg bg-white shadow-xl">
        <div class="border-b px-6 py-4">
          <h2 class="text-lg font-semibold text-gray-900">{{ editingUser ? '编辑员工' : '新增员工' }}</h2>
        </div>
        <form class="space-y-4 px-6 py-5" @submit.prevent="handleSubmit">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm text-gray-700">姓名 *</label>
              <input
                v-model="form.real_name"
                type="text"
                required
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm text-gray-700">用户名 *</label>
              <input
                v-model="form.username"
                type="text"
                required
                :disabled="!!editingUser"
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 disabled:bg-gray-100"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm text-gray-700">邮箱 *</label>
              <input
                v-model="form.email"
                type="email"
                required
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm text-gray-700">手机号</label>
              <input
                v-model="form.phone"
                type="text"
                placeholder="11位手机号"
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              />
            </div>
            <div v-if="!editingUser">
              <label class="mb-1 block text-sm text-gray-700">初始密码 *</label>
              <input
                v-model="form.password"
                type="password"
                required
                minlength="8"
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm text-gray-700">员工类型 *</label>
              <select
                v-model="form.staff_group"
                required
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              >
                <option value="sales">销售</option>
                <option value="technical">技术</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div>
              <label class="mb-1 block text-sm text-gray-700">岗位 *</label>
              <select
                v-model="form.position"
                required
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              >
                <option value="">请选择</option>
                <option v-for="option in positionOptionsByGroup" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </div>
            <div>
              <label class="mb-1 block text-sm text-gray-700">部门ID</label>
              <input
                v-model.number="form.department_id"
                type="number"
                min="1"
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm text-gray-700">状态 *</label>
              <select
                v-model.number="form.status"
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
              >
                <option :value="1">启用</option>
                <option :value="0">禁用</option>
              </select>
            </div>
          </div>

          <p v-if="formError" class="text-sm text-red-600">{{ formError }}</p>

          <div class="flex justify-end gap-3 border-t pt-4">
            <button
              type="button"
              class="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
              @click="showFormModal = false"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {{ submitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { userApi } from '@/core/api'
import type { UserCreate, UserResponse, UserUpdate } from '@/core/types'

type StaffGroup = 'sales' | 'technical' | 'other'

const users = ref<UserResponse[]>([])
const keyword = ref('')
const staffTypeFilter = ref<'all' | StaffGroup>('all')

const showFormModal = ref(false)
const editingUser = ref<UserResponse | null>(null)
const submitting = ref(false)
const formError = ref('')

const salesPositions = ['销售经理', '区域销售经理 (ISM)', '大客户销售']
const technicalPositions = [
  '技术支持工程师 (TO)',
  'Technical Business Manager (TBM)',
  'Regional Technical Manager (RTM)',
  '解决方案工程师',
]
const otherPositions = ['运营', '财务', '管理']

const form = ref({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  password: '',
  department_id: undefined as number | undefined,
  position: '',
  staff_group: 'sales' as StaffGroup,
  status: 1,
})

const getStaffType = (position?: string | null): StaffGroup => {
  const value = (position || '').toLowerCase()
  if (value.includes('销售') || value.includes('ism')) return 'sales'
  if (value.includes('技术') || value.includes('to') || value.includes('tbm') || value.includes('rtm')) return 'technical'
  return 'other'
}

const staffTypeLabel = (staffType: StaffGroup) =>
  staffType === 'sales' ? '销售' : staffType === 'technical' ? '技术' : '其他'

const staffTypeClass = (staffType: StaffGroup) => {
  if (staffType === 'sales') return 'bg-blue-100 text-blue-700'
  if (staffType === 'technical') return 'bg-emerald-100 text-emerald-700'
  return 'bg-gray-100 text-gray-700'
}

const positionOptionsByGroup = computed(() => {
  if (form.value.staff_group === 'sales') return salesPositions
  if (form.value.staff_group === 'technical') return technicalPositions
  return otherPositions
})

const filteredUsers = computed(() => {
  return users.value.filter((user) => {
    if (staffTypeFilter.value === 'all') return true
    return getStaffType(user.position) === staffTypeFilter.value
  })
})

const salesCount = computed(() => users.value.filter((u) => getStaffType(u.position) === 'sales').length)
const technicalCount = computed(() => users.value.filter((u) => getStaffType(u.position) === 'technical').length)

const resetForm = () => {
  form.value = {
    username: '',
    real_name: '',
    email: '',
    phone: '',
    password: '',
    department_id: undefined,
    position: salesPositions[0],
    staff_group: 'sales',
    status: 1,
  }
  formError.value = ''
}

const extractError = (error: any): string => {
  if (error?.response?.data?.detail) {
    if (typeof error.response.data.detail === 'string') return error.response.data.detail
    return JSON.stringify(error.response.data.detail)
  }
  return error?.message || '请求失败'
}

const loadUsers = async () => {
  try {
    const response = await userApi.getUsers({
      page: 1,
      page_size: 100,
      keyword: keyword.value || undefined,
    })
    users.value = response.items
  } catch (error) {
    console.error('Failed to load users:', error)
  }
}

const resetFilters = () => {
  keyword.value = ''
  staffTypeFilter.value = 'all'
  loadUsers()
}

const openCreateModal = () => {
  editingUser.value = null
  resetForm()
  showFormModal.value = true
}

const openEditModal = (user: UserResponse) => {
  editingUser.value = user
  form.value = {
    username: user.username,
    real_name: user.real_name || '',
    email: user.email,
    phone: user.phone || '',
    password: '',
    department_id: user.department_id,
    position: user.position || '',
    staff_group: getStaffType(user.position),
    status: user.status,
  }
  formError.value = ''
  showFormModal.value = true
}

const handleSubmit = async () => {
  submitting.value = true
  formError.value = ''

  try {
    if (editingUser.value) {
      const payload: UserUpdate = {
        email: form.value.email,
        real_name: form.value.real_name,
        phone: form.value.phone || undefined,
        department_id: form.value.department_id,
        position: form.value.position,
        status: form.value.status,
      }
      await userApi.updateUser(editingUser.value.id, payload)
    } else {
      const payload: UserCreate = {
        username: form.value.username,
        email: form.value.email,
        real_name: form.value.real_name,
        phone: form.value.phone || undefined,
        password: form.value.password,
        department_id: form.value.department_id,
        position: form.value.position,
      }
      const created: any = await userApi.createUser(payload)
      if (form.value.status === 0 && created?.id) {
        await userApi.updateUser(created.id, { status: 0 })
      }
    }

    showFormModal.value = false
    await loadUsers()
  } catch (error: any) {
    formError.value = extractError(error)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (user: UserResponse) => {
  const ok = window.confirm(`确认删除员工 "${user.real_name || user.username}" 吗？`)
  if (!ok) return

  try {
    await userApi.deleteUser(user.id)
    await loadUsers()
  } catch (error) {
    window.alert(`删除失败: ${extractError(error)}`)
  }
}

onMounted(async () => {
  resetForm()
  await loadUsers()
})
</script>
