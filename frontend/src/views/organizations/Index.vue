<template>
  <div class="organizations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>组织管理</span>
          <el-button type="primary" @click="showCreateDialog" v-if="userStore.hasPermission('organizations', 'create')">
            <el-icon><Plus /></el-icon> 新增组织
          </el-button>
        </div>
      </template>
      
      <el-table :data="organizations" style="width: 100%">
        <el-table-column prop="name" label="组织名称" min-width="200" />
        <el-table-column prop="parent_name" label="上级组织" width="150" />
        <el-table-column prop="user_count" label="用户数" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.user_count }}人</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="showEditDialog(row)" v-if="userStore.hasPermission('organizations', 'update')">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)" v-if="userStore.hasPermission('organizations', 'delete')" :disabled="row.user_count > 0">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑组织' : '新增组织'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="form.name" placeholder="如：技术部" />
        </el-form-item>
        <el-form-item label="上级组织" prop="parent_id">
          <el-select v-model="form.parent_id" placeholder="选择上级组织（可选）" clearable style="width: 100%">
            <el-option v-for="org in organizations" :key="org.id" :label="org.name" :value="org.id" :disabled="org.id === form.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="可选" />
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
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const API_BASE = '/api'

const organizations = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const formRef = ref(null)

const form = ref({
  id: null,
  name: '',
  parent_id: null,
  description: '',
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入组织名称', trigger: 'blur' }]
}

onMounted(() => {
  fetchOrganizations()
})

const fetchOrganizations = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/organizations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    if (!res.ok) throw new Error('Failed to fetch')
    organizations.value = await res.json()
  } catch (error) {
    console.error('Fetch organizations error:', error)
    ElMessage.error('加载组织列表失败')
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', parent_id: null, description: '', is_active: true }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const token = localStorage.getItem('token')
      const url = isEdit.value ? `${API_BASE}/organizations/${form.value.id}` : `${API_BASE}/organizations`
      const method = isEdit.value ? 'PUT' : 'POST'
      
      const res = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: form.value.name,
          parent_id: form.value.parent_id || null,
          description: form.value.description,
          is_active: form.value.is_active
        })
      })
      
      if (!res.ok) throw new Error('Failed to save')
      
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      await fetchOrganizations()
    } catch (error) {
      console.error('Save organization error:', error)
      ElMessage.error('操作失败')
    } finally {
      loading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除组织"${row.name}"吗？`, '警告', { type: 'warning' })
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/organizations/${row.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!res.ok) throw new Error('Failed to delete')
    
    ElMessage.success('删除成功')
    await fetchOrganizations()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete organization error:', error)
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.organizations-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
