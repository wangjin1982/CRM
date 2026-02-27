import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api'
import type { LoginRequest, LoginResponse, User } from '../types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)

  // Actions
  const login = async (credentials: LoginRequest) => {
    const response = await authApi.login(credentials)
    token.value = response.access_token
    refreshToken.value = response.refresh_token
    user.value = response.user as any

    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    localStorage.setItem('user', JSON.stringify(response.user))

    return response
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      token.value = null
      refreshToken.value = null
      user.value = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  const refreshTokens = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    const response = await authApi.refreshToken({ refresh_token: refreshToken.value })
    token.value = response.access_token

    localStorage.setItem('access_token', response.access_token)

    return response
  }

  const loadUserFromStorage = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('Failed to parse user from localStorage', e)
      }
    }
  }

  return {
    // State
    token,
    refreshToken,
    user,
    // Getters
    isAuthenticated,
    isAdmin,
    // Actions
    login,
    logout,
    refreshTokens,
    loadUserFromStorage,
  }
})
