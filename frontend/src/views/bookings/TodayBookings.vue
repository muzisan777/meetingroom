<template>
  <div class="today-bookings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>今日预约</span>
          <el-button type="primary" @click="handleBack">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
        </div>
      </template>
      
      <el-table :data="todayBookings" style="width: 100%" :header-cell-style="{background: '#f5f7fa', color: '#606266'}">
        <el-table-column prop="roomName" label="会议室" width="150" />
        <el-table-column label="预约时间" width="200">
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
      </el-table>
      
      <el-empty v-if="todayBookings.length === 0" description="暂无今日预约" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getBookings, getRooms, getUsers } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const allBookings = ref([])
const rooms = ref([])
const users = ref([])

const todayBookings = computed(() => {
  const today = dayjs().format('YYYY-MM-DD')
  
  return allBookings.value
    .filter(b => {
      const bookingDate = dayjs(b.start_time).format('YYYY-MM-DD')
      return bookingDate === today && b.status !== 'cancelled'
    })
    .map(b => {
      const room = rooms.value.find(r => r.id === b.room_id)
      const user = users.value.find(u => u.id === b.user_id)
      return {
        ...b,
        roomName: room ? room.name : '未知会议室',
        userName: b.user_name || (user ? user.username : '未知用户'),
        userOrgName: b.user_org_name || null
      }
    })
    .sort((a, b) => dayjs(a.start_time).valueOf() - dayjs(b.start_time).valueOf())
})

const formatDate = (time) => dayjs(time).format('YYYY-MM-DD')
const formatTime = (time) => dayjs(time).format('HH:mm')

const getStatusType = (booking) => {
  const now = dayjs()
  const start = dayjs(booking.start_time)
  const end = dayjs(booking.end_time)
  
  if (now.isBefore(start)) return 'info'
  if (now.isBetween(start, end)) return 'warning'
  return 'success'
}

const getStatusText = (booking) => {
  const now = dayjs()
  const start = dayjs(booking.start_time)
  const end = dayjs(booking.end_time)
  
  if (now.isBefore(start)) return '待开始'
  if (now.isBetween(start, end)) return '使用中'
  return '已完成'
}

const handleBack = () => {
  router.push('/dashboard')
}

onMounted(async () => {
  await fetchTodayBookings()
})

const fetchTodayBookings = async () => {
  try {
    // 加载会议室和用户数据
    await Promise.all([
      getRooms().then(data => rooms.value = data),
      userStore.isAdmin ? getUsers().then(data => users.value = data) : Promise.resolve()
    ])
    
    // 获取所有预约（不限制权限，显示今天所有预约）
    const today = dayjs().format('YYYY-MM-DD')
    const bookingsRes = await getBookings({
      start_date: `${today}T00:00:00`,
      end_date: `${today}T23:59:59`,
      limit: 100
    })
    allBookings.value = bookingsRes
    
    console.log('Today bookings:', todayBookings.value.length)
  } catch (error) {
    console.error('Fetch today bookings error:', error)
    ElMessage.error('加载今日预约失败')
  }
}
</script>

<style scoped>
.today-bookings-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
