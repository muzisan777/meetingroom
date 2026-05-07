<template>
  <div class="today-bookings-container">
    <el-card class="bookings-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>今日预约</span>
          <el-tag type="success">{{ bookings.length }} 条</el-tag>
        </div>
      </template>

      <div v-if="bookings.length > 0" class="bookings-table">
        <el-table :data="bookings" style="width: 100%" :header-cell-style="{background: '#f5f7fa', color: '#606266'}">
          <el-table-column prop="roomName" label="会议室" width="120" />
          <el-table-column label="时间" width="160">
            <template #default="{ row }">
              <span class="time-tag">{{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}</span>
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
              <el-tag :type="getStatusType(row)" size="small">
                {{ getStatus(row) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="暂无今日预约" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTodayBookings } from '@/api'
import dayjs from 'dayjs'

const bookings = ref([])

const formatTime = (time) => dayjs(time).format('HH:mm')

const getStatus = (booking) => {
  if (booking.status === 'cancelled') return '已取消'
  const now = dayjs()
  const start = dayjs(booking.start_time)
  const end = dayjs(booking.end_time)
  
  if (now.isAfter(end)) {
    return '已完成'
  } else if (now.isBetween(start, end)) {
    return '使用中'
  } else {
    return '待开始'
  }
}

const getStatusType = (booking) => {
  const status = getStatus(booking)
  return {
    '已取消': 'info',
    '已完成': 'success',
    '使用中': 'danger',
    '待开始': 'warning'
  }[status] || 'info'
}

const fetchTodayBookings = async () => {
  try {
    const data = await getTodayBookings()
    bookings.value = data
  } catch (error) {
    console.error('获取今日预约失败:', error)
  }
}

onMounted(() => {
  fetchTodayBookings()
})
</script>

<style scoped>
.today-bookings-container {
  padding: 20px;
}

.bookings-card {
  overflow-x: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bookings-table {
  overflow-x: auto;
}

.time-tag {
  font-weight: 500;
  color: #409EFF;
}

@media (max-width: 768px) {
  .today-bookings-container {
    padding: 12px;
  }
  
  .bookings-card {
    padding: 12px !important;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .el-table {
    font-size: 12px;
  }
  
  .el-table .cell {
    padding: 8px 4px !important;
  }
  
  .el-table--small th {
    padding: 8px 0 !important;
  }
  
  .el-tag {
    font-size: 11px !important;
    padding: 2px 6px !important;
  }
  
  .time-tag {
    font-size: 11px !important;
  }
}

@media (max-width: 480px) {
  .today-bookings-container {
    padding: 8px;
  }
  
  .bookings-card {
    padding: 8px !important;
  }
  
  .card-header span {
    font-size: 14px !important;
  }
}
</style>
