import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getMe } from '@/api'

const defaultPerms = [
  { module: 'rooms', action: 'read' },
  { module: 'items', action: 'read' },
  { module: 'bookings', action: 'read' },
  { module: 'bookings', action: 'create' },
  { module: 'borrowings', action: 'read' },
  { module: 'borrowings', action: 'create' },
]

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.is_admin || false)
  const permissions = computed(() => userInfo.value?.permissions || [])
  const roleName = computed(() => userInfo.value?.role_name || '')

  function getEffectivePerms() {
    if (isAdmin.value) return null
    if (!userInfo.value?.role_id) return defaultPerms
    return permissions.value
  }

  function hasPermission(module, action) {
    const perms = getEffectivePerms()
    if (perms === null) return true
    return perms.some(p => p.module === module && p.action === action)
  }

  function showMenuItem(module) {
    return hasPermission(module, 'read')
  }

  async function login(username, password) {
    const res = await loginApi(username, password)
    token.value = res.access_token
    userInfo.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }

  async function fetchUserInfo() {
    try {
      const res = await getMe()
      userInfo.value = res
      localStorage.setItem('user', JSON.stringify(res))
    } catch (error) {
      logout()
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    permissions,
    roleName,
    hasPermission,
    showMenuItem,
    login,
    logout,
    fetchUserInfo
  }
})