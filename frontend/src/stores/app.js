import { defineStore } from 'pinia'
import { getAppConfig } from '@/api'

export const useAppStore = defineStore('app', {
  state: () => ({
    appTitle: '会议室系统',
  }),
  actions: {
    async fetchConfig() {
      try {
        const data = await getAppConfig()
        this.appTitle = data.app_title || '会议室系统'
        document.title = this.appTitle
      } catch {
        document.title = this.appTitle
      }
    },
    setTitle(title) {
      this.appTitle = title
      document.title = title
    },
  },
})
