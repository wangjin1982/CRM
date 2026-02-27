<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-bold">关联联系人</h3>
      <button
        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
        @click="showAddModal = true"
      >
        添加联系人
      </button>
    </div>

    <div v-if="contacts.length === 0" class="text-center py-8 text-gray-500">
      暂无关联联系人
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="contact in contacts"
        :key="contact.id"
        class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
      >
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
            <span class="text-indigo-600 font-medium">
              {{ contact.contact_name?.[0] || '?' }}
            </span>
          </div>
          <div>
            <div class="font-medium">{{ contact.contact_name }}</div>
            <div class="text-sm text-gray-500">{{ contact.contact_title || '-' }}</div>
          </div>
          <div v-if="contact.role" class="px-2 py-1 text-xs rounded bg-gray-200">
            {{ contact.role }}
          </div>
          <div v-if="contact.is_primary" class="px-2 py-1 text-xs rounded bg-indigo-100 text-indigo-800">
            主要
          </div>
        </div>
        <button
          class="text-red-600 hover:text-red-900 text-sm"
          @click="removeContact(contact.contact_id)"
        >
          移除
        </button>
      </div>
    </div>

    <!-- 添加联系人弹窗 -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showAddModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 class="text-lg font-bold mb-4">添加联系人</h2>
        <form @submit.prevent="handleAddContact">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">选择联系人</label>
              <select
                v-model.number="selectedContactId"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option :value="undefined">请选择</option>
                <option v-for="contact in availableContacts" :key="contact.id" :value="contact.id">
                  {{ contact.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">角色</label>
              <input
                v-model="contactRole"
                type="text"
                placeholder="例如：决策人、影响者"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">影响力等级 (1-5)</label>
              <input
                v-model.number="influenceLevel"
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
import { contactApi } from '@/core/api'
import type { OpportunityContact } from '@/core/types'

const props = defineProps<{
  opportunityId: number
}>()

const contacts = ref<OpportunityContact[]>([])
const availableContacts = ref<any[]>([])
const showAddModal = ref(false)
const selectedContactId = ref<number>()
const contactRole = ref('')
const influenceLevel = ref(3)

const loadContacts = async () => {
  try {
    contacts.value = await opportunityApi.getContacts(props.opportunityId)
  } catch (error) {
    console.error('Failed to load contacts:', error)
  }
}

const loadAvailableContacts = async () => {
  try {
    const opportunity = await opportunityApi.getOpportunity(props.opportunityId)
    const response = await contactApi.getByCustomer(opportunity.customer_id)
    const linkedIds = new Set(contacts.value.map(item => item.contact_id))
    availableContacts.value = response.items.filter(item => !linkedIds.has(item.id))
  } catch (error) {
    console.error('Failed to load available contacts:', error)
  }
}

const handleAddContact = async () => {
  if (!selectedContactId.value) return

  try {
    await opportunityApi.addContacts(
      props.opportunityId,
      [selectedContactId.value],
      contactRole.value || undefined,
      influenceLevel.value
    )
    showAddModal.value = false
    selectedContactId.value = undefined
    contactRole.value = ''
    await loadContacts()
    await loadAvailableContacts()
  } catch (error) {
    console.error('Failed to add contact:', error)
  }
}

const removeContact = async (contactId: number) => {
  if (!confirm('确定要移除这个联系人吗？')) return

  try {
    await opportunityApi.removeContact(props.opportunityId, contactId)
    await loadContacts()
    await loadAvailableContacts()
  } catch (error) {
    console.error('Failed to remove contact:', error)
  }
}

onMounted(() => {
  loadContacts()
  loadAvailableContacts()
})
</script>
