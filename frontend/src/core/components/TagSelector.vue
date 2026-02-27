<template>
  <div class="tag-selector">
    <div class="flex flex-wrap gap-2 mb-2">
      <span
        v-for="(tag, index) in selectedTags"
        :key="index"
        class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium"
        :class="getTagClass(tag)"
      >
        {{ tag }}
        <button
          type="button"
          class="hover:opacity-70"
          @click="removeTag(index)"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>
    </div>
    <div class="flex gap-2">
      <select
        v-if="availableTags.length > 0"
        v-model="selectedAvailableTag"
        class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        @change="selectAvailableTag"
      >
        <option value="">从已有标签选择...</option>
        <option v-for="tag in availableTags" :key="tag" :value="tag">
          {{ tag }}
        </option>
      </select>
      <input
        v-model="newTag"
        type="text"
        placeholder="或输入新标签"
        class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        @keyup.enter="addNewTag"
      />
      <button
        type="button"
        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
        @click="addNewTag"
      >
        添加
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue: string[]
  availableTags?: string[]
  tagColors?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  availableTags: () => [],
  tagColors: () => ({}),
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const selectedTags = ref<string[]>([...props.modelValue])
const newTag = ref('')
const selectedAvailableTag = ref('')

// 可用但未选中的标签
const availableTags = computed(() => {
  return props.availableTags.filter(tag => !selectedTags.value.includes(tag))
})

// 获取标签样式类
const getTagClass = (tag: string) => {
  const colorClass = props.tagColors[tag]
  if (colorClass) {
    return colorClass
  }
  // 默认颜色
  return 'bg-indigo-100 text-indigo-800'
}

// 从已有标签中选择
const selectAvailableTag = () => {
  if (selectedAvailableTag.value) {
    selectedTags.value.push(selectedAvailableTag.value)
    selectedAvailableTag.value = ''
    emitUpdate()
  }
}

// 添加新标签
const addNewTag = () => {
  const tag = newTag.value.trim()
  if (tag && !selectedTags.value.includes(tag)) {
    selectedTags.value.push(tag)
    newTag.value = ''
    emitUpdate()
  }
}

// 删除标签
const removeTag = (index: number) => {
  selectedTags.value.splice(index, 1)
  emitUpdate()
}

// 触发更新
const emitUpdate = () => {
  emit('update:modelValue', selectedTags.value)
}

// 监听外部值变化
import { watch } from 'vue'
watch(() => props.modelValue, (newValue) => {
  selectedTags.value = [...newValue]
}, { deep: true })
</script>
