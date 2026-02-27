import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<any>(null)

  const setCurrentUser = (user: any) => {
    currentUser.value = user
  }

  const clearCurrentUser = () => {
    currentUser.value = null
  }

  return {
    currentUser,
    setCurrentUser,
    clearCurrentUser,
  }
})
