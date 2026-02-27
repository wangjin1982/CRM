<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto m-4">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-900">
          {{ contact ? '编辑联系人' : '添加联系人' }}
        </h2>
      </div>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- 基本信息 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
            <input
              v-model="formData.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">性别</label>
            <select
              v-model="formData.gender"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">请选择</option>
              <option value="male">男</option>
              <option value="female">女</option>
              <option value="other">其他</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">职位</label>
            <input
              v-model="formData.title"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">部门</label>
            <input
              v-model="formData.department"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>

        <!-- 联系方式 -->
        <div class="border-t border-gray-200 pt-4">
          <h3 class="text-sm font-medium text-gray-700 mb-3">联系方式</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">手机</label>
              <input
                v-model="formData.mobile"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">固话</label>
              <input
                v-model="formData.phone"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
              <input
                v-model="formData.email"
                type="email"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">微信</label>
              <input
                v-model="formData.wechat"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        <!-- 其他信息 -->
        <div class="border-t border-gray-200 pt-4">
          <h3 class="text-sm font-medium text-gray-700 mb-3">其他信息</h3>
          <div class="grid grid-cols-1 gap-4">
            <div class="flex items-center gap-4">
              <label class="flex items-center">
                <input
                  v-model="formData.is_primary"
                  type="checkbox"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">主要联系人</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="formData.is_decision_maker"
                  type="checkbox"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">决策人</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="formData.is_influencer"
                  type="checkbox"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">影响者</span>
              </label>
            </div>
            <div v-if="formData.is_influencer" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">影响力等级 (1-5)</label>
                <input
                  v-model.number="formData.influence_level"
                  type="number"
                  min="1"
                  max="5"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">关系类型</label>
                <input
                  v-model="formData.relationship"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">沟通偏好</label>
              <input
                v-model="formData.preference"
                type="text"
                placeholder="例如：微信、电话、邮件等"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">兴趣爱好</label>
              <textarea
                v-model="formData.hobbies"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
              <textarea
                v-model="formData.remarks"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              ></textarea>
            </div>
          </div>
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
            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            保存
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { contactApi } from '@/core/api'
import type { Contact, ContactCreate } from '@/core/types'

interface Props {
  contact?: Contact | null
  customerId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  save: []
}>()

// 表单数据
const formData = ref<ContactCreate>({
  name: '',
  gender: undefined,
  title: '',
  department: '',
  mobile: '',
  phone: '',
  email: '',
  wechat: '',
  is_primary: false,
  is_decision_maker: false,
  is_influencer: false,
  influence_level: undefined,
  relationship: '',
  preference: '',
  hobbies: '',
  remarks: '',
})

// 初始化表单数据
if (props.contact) {
  formData.value = {
    name: props.contact.name,
    gender: props.contact.gender,
    title: props.contact.title || '',
    department: props.contact.department || '',
    mobile: props.contact.mobile || '',
    phone: props.contact.phone || '',
    email: props.contact.email || '',
    wechat: props.contact.wechat || '',
    is_primary: props.contact.is_primary,
    is_decision_maker: props.contact.is_decision_maker,
    is_influencer: props.contact.is_influencer,
    influence_level: props.contact.influence_level,
    relationship: props.contact.relationship || '',
    preference: props.contact.preference || '',
    hobbies: props.contact.hobbies || '',
    remarks: props.contact.remarks || '',
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    if (props.contact) {
      await contactApi.update(props.contact.id, formData.value)
    } else {
      await contactApi.create(props.customerId, formData.value)
    }
    emit('save')
  } catch (error) {
    console.error('Failed to save contact:', error)
  }
}
</script>
