<template>
  <Layout v-if="needsLayout">
    <router-view />
  </Layout>
  <router-view v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/views/Layout.vue'

const route = useRoute()
const needsLayout = computed(() => route.meta?.requiresAuth)
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f7f8fa;
  color: #1a1a2e;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app { min-height: 100vh; }

:root {
  --primary-color: #4f6ef7;
  --primary-hover: #6c8cff;
  --primary-light: #eef1ff;
  --primary-gradient: linear-gradient(135deg, #4f6ef7, #6c8cff);
  --success-color: #34d399;
  --success-light: #ecfdf5;
  --warning-color: #fb923c;
  --warning-light: #fff7ed;
  --danger-color: #f87171;
  --danger-light: #fef2f2;
  --bg-color: #f7f8fa;
  --bg-secondary: #f0f1f5;
  --card-bg: #ffffff;
  --sidebar-bg: #0f172a;
  --sidebar-hover: rgba(255, 255, 255, 0.06);
  --sidebar-active: rgba(79, 110, 247, 0.15);
  --text-primary: #1a1a2e;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --text-inverse: #e2e8f0;
  --text-sidebar: #94a3b8;
  --border-color: #e5e7eb;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.08);
  --shadow-xl: 0 12px 40px rgba(0, 0, 0, 0.1);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

:deep(.el-button--primary) {
  --el-button-bg-color: var(--primary-color);
  --el-button-border-color: var(--primary-color);
  --el-button-hover-bg-color: var(--primary-hover);
  --el-button-hover-border-color: var(--primary-hover);
}
:deep(.el-card) {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  transition: all var(--transition-base);
}
:deep(.el-card:hover) { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
:deep(.el-table) { --el-table-border-color: var(--border-color); }
:deep(.el-table th.el-table__cell) {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13px;
}
:deep(.el-dialog) { border-radius: var(--radius-xl); overflow: hidden; }
:deep(.el-dialog__header) { padding: 20px 24px 0; }
:deep(.el-dialog__title) { font-size: 18px; font-weight: 600; color: var(--text-primary); }
:deep(.el-dialog__body) { padding: 20px 24px; }
:deep(.el-dialog__footer) { padding: 0 24px 20px; }
:deep(.el-overlay) { backdrop-filter: blur(4px); background-color: rgba(0, 0, 0, 0.3) !important; }
:deep(.el-tag) { border-radius: var(--radius-sm); font-weight: 500; }
:deep(.el-input__wrapper) { border-radius: var(--radius-md); box-shadow: 0 0 0 1px var(--border-color); transition: all var(--transition-fast); }
:deep(.el-input__wrapper:hover) { box-shadow: 0 0 0 1px var(--primary-color); }
:deep(.el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px var(--primary-color); }
:deep(.el-select .el-input__wrapper) { border-radius: var(--radius-md); }
</style>
