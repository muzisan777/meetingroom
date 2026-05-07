<template>
  <div class="items-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>物品列表</span>
          <el-button type="primary" @click="showCreateDialog" v-if="userStore.isAdmin">
            <el-icon><Plus /></el-icon> 新增物品
          </el-button>
        </div>
      </template>
      
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="quantity" label="总量" width="80" />
        <el-table-column prop="available_quantity" label="可用" width="80">
          <template #default="{ row }">
            <el-tag :type="row.available_quantity > 0 ? 'success' : 'danger'">
              {{ row.available_quantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '可用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" v-if="userStore.isAdmin">
          <template #default="{ row }">
            <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" v-else>
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="showBorrowDialog(row)" :disabled="row.available_quantity <= 0">
              借用
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑物品' : '新增物品'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="如：投影仪" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="form.category" placeholder="如：电子设备" />
        </el-form-item>
        <el-form-item label="总量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 借用对话框 -->
    <el-dialog v-model="borrowDialogVisible" title="借用物品" width="500px">
      <el-form :model="borrowForm" :rules="borrowRules" ref="borrowFormRef" label-width="100px">
        <el-form-item label="物品">
          <el-input :value="selectedItem?.name" disabled />
        </el-form-item>
        <el-form-item label="可用数量">
          <el-input :value="selectedItem?.available_quantity" disabled />
        </el-form-item>
        <el-form-item label="借用数量" prop="quantity">
          <el-input-number v-model="borrowForm.quantity" :min="1" :max="selectedItem?.available_quantity || 1" />
        </el-form-item>
        <el-form-item label="预计归还" prop="return_date">
          <el-date-picker
            v-model="borrowForm.return_date"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="borrowForm.notes" type="textarea" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBorrow" :loading="borrowLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getItems, createItem, updateItem, deleteItem, createBorrowing } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const items = ref([])
const dialogVisible = ref(false)
const borrowDialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const borrowLoading = ref(false)
const formRef = ref(null)
const borrowFormRef = ref(null)
const selectedItem = ref(null)

const form = ref({ id: null, name: '', category: '', quantity: 1, description: '' })
const borrowForm = ref({ item_id: null, quantity: 1, return_date: new Date(), notes: '' })

const rules = {
  name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const borrowRules = {
  quantity: [{ required: true, message: '请输入借用数量', trigger: 'change' }],
  return_date: [{ required: true, message: '请选择归还日期', trigger: 'change' }]
}

const disabledDate = (time) => time.getTime() < Date.now() - 86400000

onMounted(async () => {
  await fetchItems()
})

const fetchItems = async () => {
  try {
    items.value = await getItems()
  } catch (error) {
    console.error(error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', category: '', quantity: 1, description: '' }
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
      if (isEdit.value) {
        await updateItem(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await createItem(form.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchItems()
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该物品吗？', '提示', { type: 'warning' })
    await deleteItem(row.id)
    ElMessage.success('删除成功')
    await fetchItems()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const showBorrowDialog = (row) => {
  selectedItem.value = row
  borrowForm.value = { item_id: row.id, quantity: 1, return_date: new Date(Date.now() + 7 * 86400000), notes: '' }
  borrowDialogVisible.value = true
}

const handleBorrow = async () => {
  if (!borrowFormRef.value) return
  await borrowFormRef.value.validate(async (valid) => {
    if (!valid) return
    borrowLoading.value = true
    try {
      await createBorrowing({
        item_id: borrowForm.value.item_id,
        quantity: borrowForm.value.quantity,
        return_date: dayjs(borrowForm.value.return_date).format('YYYY-MM-DDTHH:mm:ss'),
        notes: borrowForm.value.notes
      })
      ElMessage.success('借用成功')
      borrowDialogVisible.value = false
      await fetchItems()
    } catch (error) {
      console.error(error)
    } finally {
      borrowLoading.value = false
    }
  })
}
</script>

<style scoped>
.items-page { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
