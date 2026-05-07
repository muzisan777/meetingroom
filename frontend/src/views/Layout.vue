<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <span>📋</span>
        <span class="text">会议室系统</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        background-color="#0f172a"
        text-color="#94a3b8"
        active-text-color="#4f6ef7"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-menu-item index="/rooms">
          <el-icon><OfficeBuilding /></el-icon>
          <span>{{ userStore.isAdmin ? '会议室管理' : '会议室' }}</span>
        </el-menu-item>
        
        <el-menu-item index="/bookings">
          <el-icon><Calendar /></el-icon>
          <span>{{ userStore.isAdmin ? '预约管理' : '我的预约' }}</span>
        </el-menu-item>
        
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          <span>{{ userStore.isAdmin ? '物品管理' : '可借物品' }}</span>
        </el-menu-item>
        
        <el-menu-item index="/borrowings">
          <el-icon><Document /></el-icon>
          <span>{{ userStore.isAdmin ? '借用管理' : '我的借用' }}</span>
        </el-menu-item>
        
        <el-menu-item v-if="userStore.isAdmin" index="/organizations">
          <el-icon><OfficeBuilding /></el-icon>
          <span>组织管理</span>
        </el-menu-item>
        
        <el-menu-item v-if="userStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item v-if="userStore.isAdmin" index="/logs">
          <el-icon><Document /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
      </el-menu>
      
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon><Fold /></el-icon>
      </div>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="breadcrumb">{{ currentTitle }}</span>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main">
        <transition name="fade-slide" mode="out-in">
          <slot />
        </transition>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { UserFilled, Fold } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapsed = ref(false)
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '首页')

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.aside {
  background: #0f172a;
  box-shadow: 1px 0 0 rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

.header {
  background: #fff;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
}

.header-left .breadcrumb {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.header-right .user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  transition: background 0.2s;
}

.header-right .user-info:hover {
  background: var(--bg-color);
}

.username {
  color: var(--text-secondary);
  font-size: 14px;
}

.main {
  background: var(--bg-color);
  padding: 24px;
}

.collapse-btn {
  margin-top: auto;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  border-top: 1px solid rgba(255,255,255,0.06);
  transition: all var(--transition-fast);
}
.collapse-btn:hover {
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
}

:deep(.el-menu) {
  border-right: none;
}
:deep(.el-menu-item) {
  border-left: 3px solid transparent;
  transition: all var(--transition-fast);
  margin: 2px 8px;
  border-radius: var(--radius-sm);
}
:deep(.el-menu-item:hover) {
  background: rgba(255,255,255,0.06) !important;
  color: #e2e8f0 !important;
}
:deep(.el-menu-item.is-active) {
  background: rgba(79,110,247,0.15) !important;
  border-left-color: #4f6ef7;
  color: #4f6ef7 !important;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  .aside {
    width: 100% !important;
    height: auto;
    box-shadow: 0 1px 0 rgba(255,255,255,0.06);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .logo {
    height: 48px;
    font-size: 14px;
    border-bottom: none;
  }

  .logo span {
    font-size: 14px;
  }

  /* 菜单改为横向滚动 */
  :deep(.el-menu) {
    display: flex;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    white-space: nowrap;
    border-bottom: 1px solid var(--border-color);
    height: 48px;
  }

  :deep(.el-menu-item) {
    height: 48px;
    line-height: 48px;
    padding: 0 16px;
    border-right: none;
    flex-shrink: 0;
  }

  :deep(.el-menu-item .el-icon) {
    margin-right: 4px;
  }

  :deep(.el-menu-item span) {
    font-size: 13px;
  }

  /* 隐藏滚动条但保留滚动功能 */
  :deep(.el-menu)::-webkit-scrollbar {
    display: none;
  }

  .header {
    height: 48px;
    padding: 0 12px;
  }

  .header-left .breadcrumb {
    font-size: 14px;
  }

  .header-right .user-info {
    padding: 4px 8px;
  }

  .header-right .username {
    display: none; /* 隐藏用户名，保留头像 */
  }

  .header-right .el-avatar {
    width: 28px;
    height: 28px;
  }

  .main {
    padding: 12px;
  }

  /* 对话框移动端适配 */
  :deep(.el-dialog) {
    width: 90% !important;
    max-width: 500px;
    margin: 20px auto;
  }

  :deep(.el-dialog__body) {
    padding: 16px;
  }

  :deep(.el-dialog__footer) {
    padding: 12px 16px;
  }
}

/* 手机端进一步优化 */
@media (max-width: 480px) {
  .logo {
    height: 44px;
  }

  :deep(.el-menu) {
    height: 44px;
  }

  :deep(.el-menu-item) {
    height: 44px;
    line-height: 44px;
    padding: 0 12px;
    font-size: 12px;
  }

  .header {
    height: 44px;
  }

  .header-left .breadcrumb {
    font-size: 13px;
  }

  .main {
    padding: 8px;
  }
}
</style>
