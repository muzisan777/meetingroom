<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">系统设置</span>
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="userStore.hasPermission('settings', 'update')">
            保存设置
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本设置" name="basic">
          <el-form label-width="160px" label-position="left">
            <el-form-item label="前端标题">
              <el-input v-model="settings.app_title" placeholder="会议室系统" />
              <div class="form-tip">浏览器标签栏显示的名称</div>
            </el-form-item>
            <el-form-item label="开放注册">
              <el-switch v-model="settings.enable_registration" :active-value="'true'" :inactive-value="'false'" />
            </el-form-item>
            <el-form-item label="每页默认条数">
              <el-input-number v-model="settings.items_per_page" :min="5" :max="200" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="日志配置" name="log">
          <el-form label-width="160px" label-position="left">
            <el-form-item label="日志级别">
              <el-select v-model="settings.log_level">
                <el-option label="DEBUG" value="DEBUG" />
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
              </el-select>
            </el-form-item>
            <el-form-item label="单文件最大字节数">
              <el-input v-model="settings.log_max_bytes" placeholder="10485760" />
              <div class="form-tip">默认 10485760 (10MB)</div>
            </el-form-item>
            <el-form-item label="备份文件个数">
              <el-input-number v-model="settings.log_backup_count" :min="0" :max="100" />
            </el-form-item>
            <el-form-item label="时间戳格式">
              <el-input v-model="settings.log_date_format" placeholder="%Y-%m-%d %H:%M:%S" />
            </el-form-item>
            <el-form-item label="自动清理天数">
              <el-input-number v-model="settings.log_retention_days" :min="0" :max="3650" />
              <div class="form-tip">0 表示不自动清理</div>
            </el-form-item>
            <el-form-item label="记录操作类型">
              <div class="action-checklist">
                <el-checkbox
                  :checked="isAllActionsEnabled"
                  :indeterminate="isActionIndeterminate"
                  @change="toggleAllActions"
                >全选</el-checkbox>
                <el-divider />
                <div v-for="group in actionGroups" :key="group.label" class="action-group">
                  <div class="action-group-label">{{ group.label }}</div>
                  <el-checkbox-group v-model="enabledActions">
                    <el-checkbox v-for="item in group.actions" :key="item.value" :label="item.value" :value="item.value">
                      {{ item.label }}
                    </el-checkbox>
                  </el-checkbox-group>
                </div>
              </div>
              <div class="form-tip">选择需要记录到操作日志的操作类型，不勾选则不记录</div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '@/api'

const userStore = useUserStore()
const appStore = useAppStore()

const activeTab = ref('basic')
const saving = ref(false)
const loading = ref(false)

const settings = reactive({
  app_title: '',
  enable_registration: 'true',
  items_per_page: 20,
  log_max_bytes: '10485760',
  log_backup_count: 10,
  log_level: 'INFO',
  log_date_format: '%Y-%m-%d %H:%M:%S',
  log_retention_days: 0,
})

const enabledActions = ref([])

const allActionTypes = [
  { label: '用户登录', value: 'login', group: 'auth' },
  { label: '用户注册', value: 'register', group: 'auth' },
  { label: '修改密码', value: 'change_password', group: 'auth' },
  { label: '创建组织', value: 'create_organization', group: 'organization' },
  { label: '更新组织', value: 'update_organization', group: 'organization' },
  { label: '删除组织', value: 'delete_organization', group: 'organization' },
  { label: '创建用户', value: 'create_user', group: 'user' },
  { label: '更新用户', value: 'update_user', group: 'user' },
  { label: '删除用户', value: 'delete_user', group: 'user' },
  { label: '创建会议室', value: 'create_room', group: 'room' },
  { label: '更新会议室', value: 'update_room', group: 'room' },
  { label: '删除会议室', value: 'delete_room', group: 'room' },
  { label: '创建预约', value: 'create_booking', group: 'booking' },
  { label: '更新预约', value: 'update_booking', group: 'booking' },
  { label: '取消预约', value: 'cancel_booking', group: 'booking' },
  { label: '创建物品', value: 'create_item', group: 'item' },
  { label: '更新物品', value: 'update_item', group: 'item' },
  { label: '删除物品', value: 'delete_item', group: 'item' },
  { label: '创建借用', value: 'create_borrowing', group: 'borrowing' },
  { label: '归还物品', value: 'return_item', group: 'borrowing' },
  { label: '创建角色', value: 'create_role', group: 'role' },
  { label: '更新角色', value: 'update_role', group: 'role' },
  { label: '删除角色', value: 'delete_role', group: 'role' },
  { label: '更新角色权限', value: 'update_role_permissions', group: 'role' },
]

const actionGroups = [
  { label: '认证相关', actions: allActionTypes.filter(a => a.group === 'auth') },
  { label: '组织管理', actions: allActionTypes.filter(a => a.group === 'organization') },
  { label: '用户管理', actions: allActionTypes.filter(a => a.group === 'user') },
  { label: '会议室管理', actions: allActionTypes.filter(a => a.group === 'room') },
  { label: '预约管理', actions: allActionTypes.filter(a => a.group === 'booking') },
  { label: '物品管理', actions: allActionTypes.filter(a => a.group === 'item') },
  { label: '借用管理', actions: allActionTypes.filter(a => a.group === 'borrowing') },
  { label: '角色管理', actions: allActionTypes.filter(a => a.group === 'role') },
]

const isAllActionsEnabled = computed(() => {
  return enabledActions.value.length === allActionTypes.length
})

const isActionIndeterminate = computed(() => {
  return enabledActions.value.length > 0 && enabledActions.value.length < allActionTypes.length
})

function toggleAllActions(checked) {
  if (checked) {
    enabledActions.value = allActionTypes.map(a => a.value)
  } else {
    enabledActions.value = []
  }
}

async function fetchSettings() {
  loading.value = true
  try {
    const data = await getSettings()
    for (const item of data) {
      if (item.key === 'items_per_page' || item.key === 'log_backup_count' || item.key === 'log_retention_days') {
        settings[item.key] = parseInt(item.value) || 0
      } else {
        settings[item.key] = item.value
      }
    }
    // 初始化 enabled_log_actions
    const actionsVal = settings.enabled_log_actions || '*'
    if (actionsVal === '*') {
      enabledActions.value = allActionTypes.map(a => a.value)
    } else {
      enabledActions.value = actionsVal.split(',').map(s => s.trim()).filter(Boolean)
    }
  } catch (error) {
    console.error('获取设置失败:', error)
    ElMessage.error('获取系统设置失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const payload = {
      ...settings,
      enabled_log_actions: isAllActionsEnabled.value ? '*' : enabledActions.value.join(','),
    }
    const stringPayload = {}
    for (const [key, value] of Object.entries(payload)) {
      stringPayload[key] = String(value)
    }
    await updateSettings({ settings: stringPayload })
    // 实时更新前端标题
    if (stringPayload.app_title) {
      appStore.setTitle(stringPayload.app_title)
    }
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchSettings()
  // 确保标题同步
  if (settings.app_title) {
    appStore.setTitle(settings.app_title)
  }
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.action-checklist {
  max-width: 600px;
}

.action-group {
  margin-bottom: 16px;
}

.action-group-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  padding-left: 4px;
}

.action-group .el-checkbox {
  margin-right: 16px;
  margin-bottom: 6px;
}
</style>
