<template>
  <div class="bookings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预约记录</span>
          <el-button type="primary" @click="showCreateDialog" v-if="userStore.hasPermission('bookings', 'create')">
            <el-icon><Plus /></el-icon> 新建预约
          </el-button>
        </div>
      </template>
      
      <el-table :data="bookings" style="width: 100%">
        <el-table-column prop="roomName" label="会议室" />
        <el-table-column label="预约时间">
          <template #default="{ row }">
            {{ formatDate(row.start_time) }} {{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="事由" show-overflow-tooltip />
        <el-table-column prop="userName" label="预约人" width="100" />
        <el-table-column prop="userOrgName" label="部门" width="120">
          <template #default="{ row }">
            {{ row.userOrgName || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row)">{{ getStatusText(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button 
              v-if="canCancelBooking(row) && (userStore.hasPermission('bookings', 'update') || row.user_id === userStore.userInfo?.id)"
              size="small" 
              type="danger" 
              @click="handleCancel(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新建预约对话框 -->
    <el-dialog v-model="dialogVisible" title="新建预约" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="会议室" prop="room_id">
          <el-select v-model="form.room_id" placeholder="选择会议室" style="width: 100%">
            <el-option v-for="room in rooms" :key="room.id" :label="room.name" :value="room.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime">
          <el-time-picker v-model="form.startTime" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-time-picker v-model="form.endTime" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预约事由" prop="purpose">
          <el-input v-model="form.purpose" type="textarea" placeholder="请简要说明预约事由" />
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
import { getBookings, createBooking, deleteBooking, getRooms, getUsers } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const bookings = ref([])
const rooms = ref([])
const users = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref(null)

const form = ref({
  room_id: null,
  date: new Date(),
  startTime: '09:00',
  endTime: '10:00',
  purpose: ''
})

const rules = {
  room_id: [{ required: true, message: '请选择会议室', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入预约事由', trigger: 'blur' }]
}

const disabledDate = (time) => time.getTime() < Date.now() - 86400000

const formatDate = (time) => dayjs(time).format('YYYY-MM-DD')
const formatTime = (time) => dayjs(time).format('HH:mm')

// 获取预约状态文本
const getStatusText = (booking) => {
  if (booking.status === 'cancelled') return '已取消'
  const now = dayjs()
  const startTime = dayjs(booking.start_time)
  const endTime = dayjs(booking.end_time)
  
  if (now.isAfter(endTime)) return '已完成'
  if (now.isBetween(startTime, endTime)) return '使用中'
  return '待开始'
}

// 获取状态标签类型
const getStatusType = (booking) => {
  const status = getStatusText(booking)
  return {
    '已取消': 'info',
    '已完成': 'success',
    '使用中': 'danger',
    '待开始': 'warning'
  }[status] || 'info'
}

// 判断是否显示取消按钮（待开始和使用中可以取消）
const canCancelBooking = (booking) => {
  if (booking.status === 'cancelled') return false
  const now = dayjs()
  const endTime = dayjs(booking.end_time)
  // 未结束前都可以取消（待开始 + 使用中）
  return now.isBefore(endTime)
}

onMounted(async () => {
  await fetchBookings()
})

const fetchBookings = async () => {
  try {
    console.log('[Bookings] Fetching, isAdmin:', userStore.isAdmin)
    
    // 先加载会议室和用户数据
    await Promise.all([fetchRooms(), fetchUsers()])
    console.log('[Bookings] Rooms:', rooms.value.length, 'Users:', users.value.length)
    
    // 普通用户只获取自己的预约
    const params = userStore.isAdmin ? { limit: 100 } : {}
    console.log('[Bookings] Request params:', params)
    const bookingsRes = await getBookings(params)
    console.log('[Bookings] Response:', bookingsRes)
    
    // 关联会议室名称和用户名
    bookings.value = bookingsRes.map(b => {
      const room = rooms.value.find(r => r.id === b.room_id)
      const user = users.value.find(u => u.id === b.user_id)
      return {
        ...b,
        roomName: room?.name || '未知会议室',
        userName: b.user_name || user?.username || '未知用户',
        userOrgName: b.user_org_name || '-'
      }
    })
    console.log('[Bookings] Final bookings:', bookings.value)
  } catch (error) {
    console.error('[Bookings] Error:', error)
    ElMessage.error('加载预约记录失败：' + (error.message || '未知错误'))
  }
}

const fetchRooms = async () => {
  rooms.value = await getRooms()
}

const fetchUsers = async () => {
  if (userStore.isAdmin) {
    users.value = await getUsers()
  }
}

const showCreateDialog = () => {
  form.value = { room_id: null, date: new Date(), startTime: '09:00', endTime: '10:00', purpose: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const start_time = dayjs(form.value.date).format('YYYY-MM-DD') + 'T' + form.value.startTime + ':00'
      const end_time = dayjs(form.value.date).format('YYYY-MM-DD') + 'T' + form.value.endTime + ':00'
      
      await createBooking({
        room_id: form.value.room_id,
        start_time,
        end_time,
        purpose: form.value.purpose
      })
      ElMessage.success('预约成功')
      dialogVisible.value = false
      await fetchBookings()
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  })
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消该预约吗？', '提示', { type: 'warning' })
    await deleteBooking(row.id)
    ElMessage.success('取消成功')
    await fetchBookings()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error(error.response?.data?.detail || '取消失败')
    }
  }
}
</script>

<style scoped>
.bookings-page { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
