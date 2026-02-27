<template>
  <div>
    <!-- 头部 -->
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-medium text-gray-900">联系人</h3>
      <button
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
        @click="handleCreate"
      >
        添加联系人
      </button>
    </div>

    <!-- 联系人列表 -->
    <div v-if="contacts.length > 0" class="space-y-4">
      <div
        v-for="contact in contacts"
        :key="contact.id"
        class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <h4 class="text-sm font-medium text-gray-900">{{ contact.name }}</h4>
              <span
                v-if="contact.is_primary"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800"
              >
                主要
              </span>
              <span
                v-if="contact.is_decision_maker"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
              >
                决策人
              </span>
            </div>
            <div class="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              <div v-if="contact.title" class="text-gray-600">
                <span class="text-gray-500">职位:</span> {{ contact.title }}
              </div>
              <div v-if="contact.department" class="text-gray-600">
                <span class="text-gray-500">部门:</span> {{ contact.department }}
              </div>
              <div v-if="contact.mobile" class="text-gray-600">
                <span class="text-gray-500">手机:</span> {{ contact.mobile }}
              </div>
              <div v-if="contact.email" class="text-gray-600">
                <span class="text-gray-500">邮箱:</span> {{ contact.email }}
              </div>
              <div v-if="contact.wechat" class="text-gray-600">
                <span class="text-gray-500">微信:</span> {{ contact.wechat }}
              </div>
              <div v-if="contact.phone" class="text-gray-600">
                <span class="text-gray-500">固话:</span> {{ contact.phone }}
              </div>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              v-if="!contact.is_primary"
              class="text-sm text-indigo-600 hover:text-indigo-900"
              @click="handleSetPrimary(contact)"
            >
              设为主要
            </button>
            <button
              class="text-sm text-indigo-600 hover:text-indigo-900"
              @click="handleEdit(contact)"
            >
              编辑
            </button>
            <button
              class="text-sm text-red-600 hover:text-red-900"
              @click="handleDelete(contact)"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center py-12 text-gray-500">
      暂无联系人
    </div>

    <!-- 联系人表单弹窗 -->
    <ContactForm
      v-if="showFormModal"
      :contact="editingContact"
      :customer-id="customerId"
      @close="showFormModal = false"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { contactApi } from '@/core/api'
import type { Contact } from '@/core/types'
import ContactForm from './ContactForm.vue'

interface Props {
  customerId: number
}

const props = defineProps<Props>()

// 数据
const contacts = ref<Contact[]>([])
const showFormModal = ref(false)
const editingContact = ref<Contact | null>(null)

// 加载联系人列表
const loadContacts = async () => {
  try {
    const response = await contactApi.getByCustomer(props.customerId)
    contacts.value = response.items
  } catch (error) {
    console.error('Failed to load contacts:', error)
  }
}

// 创建
const handleCreate = () => {
  editingContact.value = null
  showFormModal.value = true
}

// 编辑
const handleEdit = (contact: Contact) => {
  editingContact.value = contact
  showFormModal.value = true
}

// 保存
const handleSave = () => {
  showFormModal.value = false
  loadContacts()
}

// 删除
const handleDelete = async (contact: Contact) => {
  if (!confirm(`确定要删除联系人"${contact.name}"吗？`)) {
    return
  }

  try {
    await contactApi.delete(contact.id)
    loadContacts()
  } catch (error) {
    console.error('Failed to delete contact:', error)
  }
}

// 设置主要联系人
const handleSetPrimary = async (contact: Contact) => {
  try {
    await contactApi.setPrimary(contact.id)
    loadContacts()
  } catch (error) {
    console.error('Failed to set primary contact:', error)
  }
}

onMounted(() => {
  loadContacts()
})
</script>
