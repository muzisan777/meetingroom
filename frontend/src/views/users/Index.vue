<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showCreateDialog" v-if="userStore.hasPermission('users', 'create')">
            <el-icon><Plus /></el-icon> 新增用户
          </el-button>
        </div>
      </template>
      
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="full_name" label="姓名" />
        <el-table-column prop="org_name" label="部门" width="150">
          <template #default="{ row }">
            {{ row.org_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机" />
        <el-table-column label="角色" width="130">
          <template #default="{ row }">
            <el-tag v-if="row.is_admin" type="danger">管理员</el-tag>
            <el-tag v-else-if="row.role_name" type="primary">{{ row.role_name }}</el-tag>
            <span v-else class="no-role">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="showEditDialog(row)" v-if="userStore.hasPermission('users', 'update')">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)" v-if="userStore.hasPermission('users', 'delete')" :disabled="row.username === 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="用户名" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input v-model="form.password" type="password" :placeholder="isEdit ? '留空则不修改' : '请输入密码'" show-password />
        </el-form-item>
        <el-form-item label="部门" prop="org_id">
          <el-select v-model="form.org_id" placeholder="选择部门（可选）" clearable style="width: 100%">
            <el-option v-for="org in organizations" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="选择角色（可选）" clearable style="width: 100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="可选" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" placeholder="可选" />
        </el-form-item>
        <el-form-item label="手机" prop="phone">
          <el-input v-model="form.phone" placeholder="可选" />
        </el-form-item>
        <el-form-item label="管理员" prop="is_admin">
          <el-switch v-model="form.is_admin" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getUsers, createUser, updateUser, deleteUser, getRoles } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const users = ref([])
const organizations = ref([])
const roles = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const formRef = ref(null)

const form = ref({
  id: null,
  username: '',
  password: '',
  email: '',
  full_name: '',
  phone: '',
  org_id: null,
  role_id: null,
  is_admin: false,
  is_active: true
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }]
}

onMounted(async () => {
  await Promise.all([fetchUsers(), fetchOrganizations(), fetchRoles()])
})

const fetchUsers = async () => {
  try {
    users.value = await getUsers()
  } catch (error) {
    console.error(error)
  }
}

const fetchOrganizations = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/organizations', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    if (!res.ok) throw new Error('Failed to fetch')
    organizations.value = await res.json()
  } catch (error) {
    console.error('Fetch organizations error:', error)
  }
}

const fetchRoles = async () => {
  if (!userStore.hasPermission('roles', 'read')) return
  try {
    roles.value = await getRoles()
  } catch (error) {
    console.error('Fetch roles error:', error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  form.value = { id: null, username: '', password: '', email: '', full_name: '', phone: '', org_id: null, role_id: null, is_admin: false, is_active: true }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  form.value = { ...row, password: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const data = { ...form.value }
      if (isEdit.value && !data.password) delete data.password
      
      if (isEdit.value) {
        await updateUser(data.id, data)
        ElMessage.success('更新成功')
      } else {
        await createUser(data)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchUsers()
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${row.username} 吗？`, '警告', { type: 'warning' })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    await fetchUsers()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}
</script>

<style scoped>
.users-page { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
