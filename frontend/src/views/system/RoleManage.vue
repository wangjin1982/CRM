<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">角色管理</h1>
      <button
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        @click="showCreateModal = true"
      >
        新增角色
      </button>
    </div>

    <div class="bg-white shadow rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色代码</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">描述</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="role in roles" :key="role.id">
            <td class="px-6 py-4 whitespace-nowrap">{{ role.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ role.code }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ role.description || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="role.status === 1 ? 'text-green-600' : 'text-red-600'">
                {{ role.status === 1 ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button class="text-indigo-600 hover:text-indigo-900 mr-3">编辑</button>
              <button class="text-red-600 hover:text-red-900">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Role {
  id: number
  name: string
  code: string
  description?: string
  status: number
}

const roles = ref<Role[]>([
  { id: 1, name: '管理员', code: 'admin', description: '系统管理员', status: 1 },
  { id: 2, name: '普通用户', code: 'user', description: '普通用户', status: 1 },
])

const showCreateModal = ref(false)
</script>
