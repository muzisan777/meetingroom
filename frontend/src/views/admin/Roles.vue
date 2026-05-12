<template>
  <div class="roles-page">
    <div class="page-header">
      <h2>角色管理</h2>
      <el-button type="primary" @click="openCreate" v-if="userStore.hasPermission('roles', 'create')">
        <el-icon><Plus /></el-icon>添加角色
      </el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="roles" v-loading="loading" stripe>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="角色名称" min-width="140">
          <template #default="{ row }">
            <span class="role-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="user_count" label="用户数" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.user_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑权限</el-button>
            <el-popconfirm
              title="确定删除此角色？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button
                  size="small"
                  type="danger"
                  plain
                  :disabled="row.user_count > 0 || row.name === '超级管理员'"
                  v-if="userStore.hasPermission('roles', 'delete')"
                >删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑角色权限' : '添加角色'"
      width="680px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        class="role-form"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input v-model="form.description" placeholder="请输入角色描述" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>

      <el-divider />

      <div class="permission-section">
        <h4 class="permission-title">权限配置</h4>
        <p class="permission-hint">勾选该角色在每个模块中允许的操作</p>
        <el-table :data="moduleList" stripe class="permission-table">
          <el-table-column label="模块" width="120">
            <template #default="{ row }">{{ row.label }}</template>
          </el-table-column>
          <el-table-column label="查看" width="80" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-if="row.actions.includes('read')"
                v-model="permissionMap[row.module].read"
                @change="(v) => onReadChange(row, v)"
              />
            </template>
          </el-table-column>
          <el-table-column label="新增" width="80" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-if="row.actions.includes('create')"
                v-model="permissionMap[row.module].create"
              />
            </template>
          </el-table-column>
          <el-table-column label="修改" width="80" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-if="row.actions.includes('update')"
                v-model="permissionMap[row.module].update"
              />
            </template>
          </el-table-column>
          <el-table-column label="删除" width="80" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-if="row.actions.includes('delete')"
                v-model="permissionMap[row.module].delete"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRoles, createRole, updateRole, deleteRole, getRolePermissions, updateRolePermissions } from '@/api'

const MODULES = [
  { module: 'users', label: '用户管理', actions: ['create', 'read', 'update', 'delete'] },
  { module: 'organizations', label: '组织管理', actions: ['create', 'read', 'update', 'delete'] },
  { module: 'rooms', label: '会议室管理', actions: ['create', 'read', 'update', 'delete'] },
  { module: 'bookings', label: '预约管理', actions: ['create', 'read', 'update', 'delete'] },
  { module: 'items', label: '物品管理', actions: ['create', 'read', 'update', 'delete'] },
  { module: 'borrowings', label: '借用管理', actions: ['create', 'read', 'update', 'delete'] },
  { module: 'logs', label: '系统日志', actions: ['read', 'delete'] },
  { module: 'roles', label: '角色管理', actions: ['read'] },
  { module: 'settings', label: '系统设置', actions: ['read', 'update'] },
]

const userStore = useUserStore()
const moduleList = computed(() => MODULES)

const loading = ref(false)
const roles = ref([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formRef = ref(null)

const form = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

function buildEmptyPermissions() {
  const map = {}
  MODULES.forEach(m => {
    map[m.module] = { read: false, create: false, update: false, delete: false }
  })
  return map
}

const permissionMap = reactive(buildEmptyPermissions())

function formatTime(t) {
  if (!t) return ''
  return t.slice(0, 16).replace('T', ' ')
}

function onReadChange(mod, value) {
  if (!value) {
    mod.actions.forEach(a => {
      if (a !== 'read') permissionMap[mod.module][a] = false
    })
  }
}

async function fetchRoles() {
  loading.value = true
  try {
    roles.value = await getRoles()
  } finally {
    loading.value = false
  }
}

function resetDialog() {
  form.name = ''
  form.description = ''
  Object.assign(permissionMap, buildEmptyPermissions())
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  resetDialog()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

async function openEdit(row) {
  isEditing.value = true
  editingId.value = row.id
  form.name = row.name
  form.description = row.description || ''
  Object.assign(permissionMap, buildEmptyPermissions())

  try {
    const perms = await getRolePermissions(row.id)
    perms.forEach(p => {
      if (permissionMap[p.module]) {
        permissionMap[p.module][p.action] = true
      }
    })
  } catch (e) {
    ElMessage.error('获取权限失败')
  }

  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function getPermissionList() {
  const list = []
  MODULES.forEach(m => {
    const pm = permissionMap[m.module]
    m.actions.forEach(a => {
      if (pm[a]) {
        list.push({ module: m.module, action: a })
      }
    })
  })
  return list
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const roleData = { name: form.name, description: form.description }

    if (isEditing.value) {
      await updateRole(editingId.value, roleData)
    } else {
      const created = await createRole(roleData)
      editingId.value = created.id
    }

    const permList = getPermissionList()
    await updateRolePermissions(editingId.value, permList)

    ElMessage.success(isEditing.value ? '角色已更新' : '角色已创建')
    dialogVisible.value = false
    await fetchRoles()
  } catch (e) {
    // handled by interceptor
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await deleteRole(row.id)
    ElMessage.success('角色已删除')
    await fetchRoles()
  } catch (e) {
    // handled by interceptor
  }
}

onMounted(fetchRoles)
</script>

<style scoped>
.roles-page {
  animation: fadeInUp 0.3s ease;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.role-name {
  font-weight: 500;
  color: var(--text-primary);
}

.permission-section {
  padding: 0 4px;
}

.permission-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.permission-hint {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.permission-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}

:deep(.permission-table .el-checkbox) {
  --el-checkbox-checked-bg-color: var(--primary-color);
  --el-checkbox-checked-border-color: var(--primary-color);
}

.role-form {
  max-width: 460px;
}

.el-divider {
  margin: 20px 0;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  :deep(.el-dialog) {
    width: 92% !important;
    max-width: 680px;
  }
}
</style>