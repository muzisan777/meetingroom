<template>
  <div class="rooms-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>会议室列表</span>
          <el-button type="primary" @click="showCreateDialog" v-if="userStore.hasPermission('rooms', 'create')">
            <el-icon><Plus /></el-icon> 新增会议室
          </el-button>
        </div>
      </template>
      
      <el-table :data="rooms" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="capacity" label="容量" width="100" />
        <el-table-column prop="location" label="位置" />
        <el-table-column prop="facilities" label="设施" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '可用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="showEditDialog(row)" v-if="userStore.hasPermission('rooms', 'update')">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)" v-if="userStore.hasPermission('rooms', 'delete')">删除</el-button>
            <el-button size="small" type="primary" @click="showBookingDialog(row)" v-if="userStore.hasPermission('bookings', 'create')">预约</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑会议室' : '新增会议室'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="如：大会议室" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="如：3 楼 301 室" />
        </el-form-item>
        <el-form-item label="设施" prop="facilities">
          <el-input v-model="form.facilities" type="textarea" placeholder="如：投影仪、视频会议系统、白板" />
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
    
    <!-- 预约对话框 -->
    <el-dialog v-model="bookingDialogVisible" title="预约会议室" width="500px">
      <el-form :model="bookingForm" :rules="bookingRules" ref="bookingFormRef" label-width="100px">
        <el-form-item label="会议室">
          <el-input :value="selectedRoom?.name" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="bookingForm.date"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime">
          <el-time-picker
            v-model="bookingForm.startTime"
            placeholder="选择时间"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-time-picker
            v-model="bookingForm.endTime"
            placeholder="选择时间"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预约事由" prop="purpose">
          <el-input v-model="bookingForm.purpose" type="textarea" placeholder="请简要说明预约事由" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBooking" :loading="bookingLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getRooms, createRoom, updateRoom, deleteRoom, createBooking } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const rooms = ref([])
const dialogVisible = ref(false)
const bookingDialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const bookingLoading = ref(false)
const formRef = ref(null)
const bookingFormRef = ref(null)
const selectedRoom = ref(null)

const form = ref({
  id: null,
  name: '',
  capacity: 10,
  location: '',
  facilities: '',
  description: ''
})

const bookingForm = ref({
  room_id: null,
  date: new Date(),
  startTime: '09:00',
  endTime: '10:00',
  purpose: ''
})

const rules = {
  name: [{ required: true, message: '请输入会议室名称', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }]
}

const bookingRules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入预约事由', trigger: 'blur' }]
}

const disabledDate = (time) => time.getTime() < Date.now() - 86400000

onMounted(async () => {
  await fetchRooms()
})

const fetchRooms = async () => {
  try {
    rooms.value = await getRooms()
  } catch (error) {
    console.error(error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', capacity: 10, location: '', facilities: '', description: '' }
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
      const submitData = {
        name: form.value.name,
        capacity: form.value.capacity,
        location: form.value.location || null,
        facilities: form.value.facilities || null,
        description: form.value.description || null
      }
      
      if (isEdit.value) {
        await updateRoom(form.value.id, submitData)
        ElMessage.success('更新成功')
      } else {
        await createRoom(submitData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchRooms()
    } catch (error) {
      console.error('Submit error:', error)
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      loading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该会议室吗？', '提示', { type: 'warning' })
    await deleteRoom(row.id)
    ElMessage.success('删除成功')
    await fetchRooms()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const showBookingDialog = (row) => {
  selectedRoom.value = row
  bookingForm.value = {
    room_id: row.id,
    date: new Date(),
    startTime: '09:00',
    endTime: '10:00',
    purpose: ''
  }
  bookingDialogVisible.value = true
}

const handleBooking = async () => {
  if (!bookingFormRef.value) return
  await bookingFormRef.value.validate(async (valid) => {
    if (!valid) return
    bookingLoading.value = true
    try {
      const start_time = dayjs(bookingForm.value.date).format('YYYY-MM-DD') + 'T' + bookingForm.value.startTime + ':00'
      const end_time = dayjs(bookingForm.value.date).format('YYYY-MM-DD') + 'T' + bookingForm.value.endTime + ':00'
      
      await createBooking({
        room_id: bookingForm.value.room_id,
        start_time,
        end_time,
        purpose: bookingForm.value.purpose
      })
      ElMessage.success('预约成功')
      bookingDialogVisible.value = false
    } catch (error) {
      console.error(error)
    } finally {
      bookingLoading.value = false
    }
  })
}
</script>

<style scoped>
.rooms-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .card-header span {
    font-size: 16px;
  }

  .card-header .el-button {
    width: 100%;
  }

  /* 表格移动端适配 */
  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-table th) {
    padding: 8px 4px;
    font-size: 12px;
  }

  :deep(.el-table td) {
    padding: 8px 4px;
  }

  :deep(.el-table .cell) {
    padding: 0 4px;
  }

  /* 操作按钮适配 */
  :deep(.el-table .el-button) {
    padding: 4px 8px;
    font-size: 12px;
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

  :deep(.el-dialog__title) {
    font-size: 16px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
  }

  :deep(.el-input__inner), :deep(.el-textarea__inner) {
    font-size: 14px;
  }

  :deep(.el-input-number) {
    width: 100%;
  }
}

@media (max-width: 480px) {
  :deep(.el-table) {
    font-size: 11px;
  }

  :deep(.el-table th), :deep(.el-table td) {
    padding: 6px 2px;
  }
}
</style>
