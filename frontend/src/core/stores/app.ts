import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const isLoading = ref(false)

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  return {
    sidebarCollapsed,
    isLoading,
    toggleSidebar,
    setLoading,
  }
})
