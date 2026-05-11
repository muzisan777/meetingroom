<template>
  <div class="dashboard">
    <!-- 统计卡片区 - 可点击 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover" @click.native="$router.push('/bookings/today')" style="cursor: pointer;">
          <div class="stat-content">
            <div class="stat-icon" style="background: var(--success-light); color: var(--success-color);">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.todayBookings }}</div>
              <div class="stat-label">今日预约</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8" v-if="userStore.hasPermission('bookings', 'read')">
        <el-card class="stat-card" shadow="hover" @click.native="$router.push('/bookings')" style="cursor: pointer;">
          <div class="stat-content">
            <div class="stat-icon" style="background: #fff7e6; color: var(--warning-color);">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.myBookings }}</div>
              <div class="stat-label">我的预约</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover" @click.native="$router.push('/borrowings')" style="cursor: pointer;">
          <div class="stat-content">
            <div class="stat-icon" style="background: var(--danger-light); color: var(--danger-color);">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.borrowingItems }}</div>
              <div class="stat-label">借用中物品</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 会议室卡片区 -->
    <div class="section-title">
      <span>会议室</span>
      <el-button text type="primary" @click="$router.push('/rooms')">查看全部</el-button>
    </div>
    
    <el-row :gutter="16" class="rooms-grid">
      <el-col :span="8" v-for="room in rooms" :key="room.id">
        <el-card class="room-card" shadow="hover">
          <div class="room-header">
            <div class="room-icon">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <div class="room-info">
              <div class="room-name">{{ room.name }}</div>
              <div class="room-meta">👥 {{ room.capacity }}人</div>
            </div>
            <div class="room-status">
              <el-tag :type="room.status === '使用中' ? 'danger' : 'success'" size="small">
                {{ room.status }}
              </el-tag>
            </div>
          </div>
          
          <div class="room-bookings">
            <div class="bookings-title">今日预约</div>
            <div v-if="getRoomTodayBookings(room.id).length > 0" class="bookings-list">
              <div v-for="booking in getRoomTodayBookings(room.id)" :key="booking.id" class="booking-item">
                <div class="booking-time">
                  <span class="time-range">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</span>
                  <div class="booking-user">
                    <span class="user-name">{{ booking.userName || '未知用户' }}</span>
                    <span class="user-org" v-if="booking.userOrgName && booking.userOrgName !== '-'">（{{ booking.userOrgName }}）</span>
                  </div>
                  <el-tag :type="getBookingStatusType(booking)" size="small">
                    {{ getBookingStatus(booking) }}
                  </el-tag>
                </div>
                <div class="booking-purpose">{{ booking.purpose }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无预约" :image-size="60" />
          </div>
          
          <div class="room-footer" v-if="userStore.hasPermission('bookings', 'create')">
            <el-button type="primary" @click="showBookingDialog(room)">
              <el-icon><Plus /></el-icon> 预约
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8" v-if="rooms.length === 0">
        <el-card class="empty-card">
          <el-empty description="暂无会议室" />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 物品卡片区 -->
    <div class="section-title">
      <span>可借用物品</span>
      <el-button text type="primary" @click="$router.push('/items')">查看全部</el-button>
    </div>
    
    <el-row :gutter="16" class="items-grid">
      <el-col :span="8" v-for="item in items" :key="item.id">
        <el-card class="item-card" shadow="hover">
          <div class="item-header">
            <div class="item-icon">
              <el-icon><Box /></el-icon>
            </div>
            <div class="item-info">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-category" v-if="item.category">{{ item.category }}</div>
            </div>
            <div class="item-stock">
              <el-tag :type="item.available_quantity > 0 ? 'success' : 'danger'" size="small">
                剩余 {{ item.available_quantity }}/{{ item.quantity }}
              </el-tag>
            </div>
          </div>
          
          <div class="item-description" v-if="item.description">
            {{ item.description }}
          </div>
          
          <div class="item-footer" v-if="userStore.hasPermission('borrowings', 'create')">
            <el-button 
              type="primary" 
              @click="showBorrowDialog(item)"
              :disabled="item.available_quantity <= 0"
            >
              <el-icon><Download /></el-icon> {{ item.available_quantity > 0 ? '借用' : '暂不可用' }}
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8" v-if="items.length === 0">
        <el-card class="empty-card">
          <el-empty description="暂无物品" />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 今日预约列表模块 -->
    <div class="section-title">
      <span>今日预约</span>
      <el-button text type="primary" @click="$router.push('/bookings/today')">查看全部</el-button>
    </div>
    
    <el-card class="today-bookings-card" shadow="hover">
      <div v-if="todayBookingsList.length > 0" class="bookings-table">
        <el-table :data="todayBookingsList" style="width: 100%" :header-cell-style="{background: '#f5f7fa', color: '#606266'}">
          <el-table-column prop="roomName" label="会议室" width="150" />
          <el-table-column label="时间" width="180">
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
              <el-tag :type="getBookingStatusType(row)" size="small">
                {{ getBookingStatus(row) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="暂无今日预约" />
    </el-card>
    
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
          <el-select v-model="bookingForm.startTime" placeholder="请选择开始时间" style="width: 100%">
            <el-option
              v-for="slot in availableTimeSlots"
              :key="slot.value"
              :label="slot.label"
              :value="slot.value"
              :disabled="slot.disabled"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-select v-model="bookingForm.endTime" placeholder="请选择结束时间" style="width: 100%">
            <el-option
              v-for="slot in availableTimeSlots"
              :key="slot.value"
              :label="slot.label"
              :value="slot.value"
              :disabled="slot.disabled || slot.value <= bookingForm.startTime"
            />
          </el-select>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getRooms, getBookings, getItems, getBorrowings, getTodayBookings, createBooking, createBorrowing } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import isBetween from 'dayjs/plugin/isBetween'
import 'dayjs/locale/zh-cn'

dayjs.extend(isBetween)
dayjs.locale('zh-cn')

const router = useRouter()
const userStore = useUserStore()

const stats = ref({
  rooms: 0,
  todayBookings: 0,
  myBookings: 0,
  borrowingItems: 0
})

const rooms = ref([])
const items = ref([])
const allBookings = ref([])
const todayBookingsData = ref([])  // 今日预约原始数据（所有用户）
const bookingDialogVisible = ref(false)
const borrowDialogVisible = ref(false)
const bookingLoading = ref(false)
const borrowLoading = ref(false)
const bookingFormRef = ref(null)
const borrowFormRef = ref(null)
const selectedRoom = ref(null)
const selectedItem = ref(null)

const bookingForm = ref({
  room_id: null,
  date: new Date(),
  startTime: '09:00',
  endTime: '10:00',
  purpose: ''
})

const borrowForm = ref({
  item_id: null,
  quantity: 1,
  return_date: new Date(Date.now() + 7 * 86400000),
  notes: ''
})

const bookingRules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入预约事由', trigger: 'blur' }]
}

const borrowRules = {
  quantity: [{ required: true, message: '请输入借用数量', trigger: 'change' }],
  return_date: [{ required: true, message: '请选择归还日期', trigger: 'change' }]
}

const disabledDate = (time) => time.getTime() < Date.now() - 86400000
const formatTime = (time) => dayjs(time).format('HH:mm')

// 生成所有可用时间段（8:00-19:00，15 分钟间隔）
const availableTimeSlots = computed(() => {
  const slots = []
  const now = new Date()
  const today = now.toDateString()
  const selectedDate = bookingForm.value.date ? new Date(bookingForm.value.date).toDateString() : today
  
  for (let hour = 8; hour <= 19; hour++) {
    const minutes = hour === 8 ? [30, 45] : (hour === 19 ? [0] : [0, 15, 30, 45])
    
    for (const minute of minutes) {
      const value = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      const label = `${value}`
      
      // 如果选择的是今天，检查是否小于当前时间
      let disabled = false
      if (selectedDate === today) {
        const slotTime = new Date()
        slotTime.setHours(hour, minute, 0, 0)
        if (slotTime < now) {
          disabled = true
        }
      }
      
      slots.push({ value, label, disabled })
    }
  }
  
  return slots
})

// 监听开始时间变化，自动更新结束时间为 +1 小时
watch(() => bookingForm.value.startTime, (newStart) => {
  if (newStart) {
    const [hours, minutes] = newStart.split(':').map(Number)
    const endHour = hours + 1
    bookingForm.value.endTime = `${String(Math.min(endHour, 20)).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
  }
})

// 今日预约列表（使用今日预约原始数据，显示所有用户）
const todayBookingsList = computed(() => {
  if (!todayBookingsData.value || !Array.isArray(todayBookingsData.value)) {
    return []
  }
  
  return todayBookingsData.value
    .filter(b => b.status !== 'cancelled')
    .map(b => {
      const room = rooms.value.find(r => r.id === b.room_id)
      return {
        ...b,
        roomName: room ? room.name : '未知会议室',
        userName: b.user_name || '未知用户',
        userOrgName: b.user_org_name || '-'
      }
    })
    .sort((a, b) => dayjs(a.start_time).valueOf() - dayjs(b.start_time).valueOf())
})

// 会议室今日预约（过滤已取消的，显示所有用户的预约）
const getRoomTodayBookings = (roomId) => {
  return todayBookingsList.value
    .filter(b => b.room_id === roomId)
    .sort((a, b) => dayjs(a.start_time).valueOf() - dayjs(b.start_time).valueOf())
}

const getBookingStatus = (booking) => {
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

const getBookingStatusType = (booking) => {
  const status = getBookingStatus(booking)
  return {
    '已取消': 'info',
    '已完成': 'success',
    '使用中': 'danger',
    '待开始': 'warning'
  }[status] || 'info'
}

onMounted(async () => {
  await fetchDashboardData()
})

const fetchDashboardData = async () => {
  try {
    // 获取会议室
    const roomsRes = await getRooms()
    rooms.value = roomsRes
    stats.value.rooms = roomsRes.length
    
    // 获取今日预约（所有用户，不限制权限）- 使用新接口
    const todayBookingsRes = await getTodayBookings()
    // 保存今日预约原始数据（所有用户）
    todayBookingsData.value = todayBookingsRes
    // 今日预约显示所有用户的预约（不限制权限）
    stats.value.todayBookings = todayBookingsRes.filter(b => b.status !== 'cancelled').length
    
    // 获取所有预约（用于我的预约统计和其他功能）
    const allBookingsRes = await getBookings({ limit: 100 })
    allBookings.value = allBookingsRes
    // 我的预约统计：管理员统计所有，普通用户统计自己的
    stats.value.myBookings = userStore.isAdmin
      ? allBookingsRes.filter(b => b.status !== 'cancelled').length
      : allBookingsRes.filter(b => b.user_id === userStore.userInfo?.id && b.status !== 'cancelled').length
    
    console.log('[Dashboard] 今日预约总数:', stats.value.todayBookings)
    console.log('[Dashboard] 今日预约原始数据:', todayBookingsData.value.length)
    console.log('[Dashboard] 今日预约列表:', todayBookingsList.value.length)
    console.log('[Dashboard] 我的预约数:', stats.value.myBookings)
    
    // 将预约分配到对应会议室，并计算状态（使用今日预约数据，显示所有用户）
    const roomsWithBookings = roomsRes.map(room => {
      const roomBookings = todayBookingsData.value
        .filter(b => b.room_id === room.id && b.status !== 'cancelled')
        .sort((a, b) => dayjs(a.start_time).valueOf() - dayjs(b.start_time).valueOf())
      
      // 计算会议室当前状态
      const now = dayjs()
      const currentBooking = roomBookings.find(b => {
        const start = dayjs(b.start_time)
        const end = dayjs(b.end_time)
        return now.isBetween(start, end) && b.status !== 'cancelled'
      })
      
      return {
        ...room,
        todayBookings: roomBookings,
        status: currentBooking ? '使用中' : '空闲'
      }
    })
    
    rooms.value = roomsWithBookings
    
    // 获取物品
    const itemsRes = await getItems()
    items.value = itemsRes
    
    // 获取借用中的物品
    const borrowingsRes = await getBorrowings({ status: 'borrowed' })
    stats.value.borrowingItems = borrowingsRes.length
  } catch (error) {
    console.error('Fetch dashboard data error:', error)
    ElMessage.error('加载数据失败')
  }
}

// 获取默认开始时间（当前时间之后第一个可用时间）
const getDefaultStartTime = () => {
  const now = new Date()
  const currentHour = now.getHours()
  const currentMinute = now.getMinutes()
  
  // 找到下一个 15 分钟间隔
  let nextMinute = Math.ceil(currentMinute / 15) * 15
  let nextHour = currentHour
  
  if (nextMinute >= 60) {
    nextMinute = 0
    nextHour++
  }
  
  // 如果超过 19 点，返回 8:00
  if (nextHour > 19 || (nextHour === 19 && nextMinute > 0)) {
    return '08:00'
  }
  
  // 如果早于 8 点，返回 8:30
  if (nextHour < 8) {
    return '08:30'
  }
  
  return `${String(nextHour).padStart(2, '0')}:${String(nextMinute).padStart(2, '0')}`
}

const showBookingDialog = (room) => {
  selectedRoom.value = room
  const defaultStartTime = getDefaultStartTime()
  // 计算默认结束时间（开始时间 +1 小时）
  const [hours, minutes] = defaultStartTime.split(':').map(Number)
  const endHour = hours + 1
  const defaultEndTime = `${String(Math.min(endHour, 20)).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
  
  bookingForm.value = {
    room_id: room.id,
    date: new Date(),
    startTime: defaultStartTime,
    endTime: defaultEndTime,
    purpose: ''
  }
  bookingDialogVisible.value = true
}

const handleBooking = async () => {
  if (!bookingFormRef.value) return
  
  // 先验证表单
  await bookingFormRef.value.validate(async (valid, fields) => {
    if (!valid) {
      // 显示第一个验证错误
      const firstError = Object.values(fields)[0]
      if (firstError && firstError[0]) {
        ElMessage.warning(firstError[0].message)
      }
      return
    }
    
    // 验证预约时间是否有效
    const now = dayjs()
    const start_time = dayjs(bookingForm.value.date).format('YYYY-MM-DD') + 'T' + bookingForm.value.startTime + ':00'
    const end_time = dayjs(bookingForm.value.date).format('YYYY-MM-DD') + 'T' + bookingForm.value.endTime + ':00'
    const startTimeObj = dayjs(start_time)
    const endTimeObj = dayjs(end_time)
    
    // 检查开始时间是否在当前时间之后
    if (startTimeObj.isBefore(now)) {
      ElMessage.warning('预约开始时间必须晚于当前时间')
      return
    }
    
    // 检查结束时间是否晚于开始时间
    if (endTimeObj.isBefore(startTimeObj)) {
      ElMessage.error('结束时间不能早于开始时间')
      return
    }
    
    bookingLoading.value = true
    try {
      const payload = {
        room_id: bookingForm.value.room_id,
        start_time,
        end_time,
        purpose: bookingForm.value.purpose
      }
      console.log('提交预约数据:', payload)
      
      await createBooking(payload)
      ElMessage.success('预约成功')
      bookingDialogVisible.value = false
      await fetchDashboardData()
    } catch (error) {
      console.error('预约失败:', error)
      console.error('错误响应:', error.response)
      // 显示具体的错误信息
      const errorMsg = error.response?.data?.detail || error.message || '预约失败'
      ElMessage.error(errorMsg)
    } finally {
      bookingLoading.value = false
    }
  })
}

const showBorrowDialog = (item) => {
  selectedItem.value = item
  borrowForm.value = {
    item_id: item.id,
    quantity: 1,
    return_date: new Date(Date.now() + 7 * 86400000),
    notes: ''
  }
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
      await fetchDashboardData()
    } catch (error) {
      console.error(error)
      ElMessage.error(error.response?.data?.detail || '借用失败')
    } finally {
      borrowLoading.value = false
    }
  })
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 6px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 4px;
}

.section-title span {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.today-bookings-card {
  margin-bottom: 24px;
  border-radius: var(--radius-lg);
}

.bookings-table {
  padding: 8px 0;
}

.time-tag {
  background: var(--bg-color);
  padding: 4px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.rooms-grid, .items-grid {
  margin-bottom: 24px;
}

.room-card, .item-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.room-card:hover, .item-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.room-card :deep(.el-card__body), .item-card :deep(.el-card__body) {
  padding: 16px;
}

.room-header, .item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.room-icon, .item-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--primary-light);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.room-info, .item-info {
  flex: 1;
  min-width: 0;
}

.room-name, .item-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.room-meta, .item-category {
  font-size: 13px;
  color: var(--text-secondary);
}

.room-status {
  flex-shrink: 0;
}

.room-bookings {
  background: var(--bg-color);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 16px;
  min-height: 120px;
}

.bookings-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.booking-item {
  background: var(--card-bg);
  border-radius: var(--radius-sm);
  padding: 12px;
  border: 1px solid var(--border-color);
}

.booking-time {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  gap: 8px;
}

.time-range {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  background: var(--bg-color);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.booking-user {
  font-size: 12px;
  color: var(--text-secondary);
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
}

.user-org {
  color: var(--text-secondary);
}

.booking-purpose {
  font-size: 13px;
  color: var(--text-secondary);
}

.room-footer, .item-footer {
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
}

.item-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  background: var(--card-bg);
}

.empty-card :deep(.el-card__body) {
  padding: 40px 20px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .dashboard {
    padding: 0;
  }

  .stats-row {
    margin-bottom: 16px;
  }

  .stat-card {
    margin-bottom: 12px;
  }

  .stat-card :deep(.el-card__body) {
    padding: 16px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }

  .stat-value {
    font-size: 28px;
  }

  .stat-label {
    font-size: 13px;
  }

  .section-title {
    padding: 0 12px;
    margin-bottom: 12px;
  }

  .section-title span {
    font-size: 16px;
  }

  .section-title .el-button {
    font-size: 13px;
    padding: 4px 8px;
  }

  .rooms-grid, .items-grid {
    margin-bottom: 16px;
  }

  .room-card, .item-card {
    margin-bottom: 12px;
  }

  .room-card :deep(.el-card__body), .item-card :deep(.el-card__body) {
    padding: 12px;
  }

  .room-header, .item-header {
    gap: 8px;
    margin-bottom: 12px;
  }

  .room-icon, .item-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .room-name, .item-name {
    font-size: 14px;
  }

  .room-meta, .item-category {
    font-size: 12px;
  }

  .room-bookings {
    padding: 12px;
    min-height: 100px;
  }

  .bookings-title {
    font-size: 12px;
    margin-bottom: 8px;
  }

  .booking-item {
    padding: 10px;
  }

  .booking-time {
    flex-wrap: wrap;
  }

  .time-range {
    font-size: 12px;
    padding: 2px 6px;
  }

  .booking-user {
    font-size: 11px;
  }

  .booking-purpose {
    font-size: 12px;
  }

  .room-footer, .item-footer {
    padding-top: 8px;
  }

  .room-footer .el-button, .item-footer .el-button {
    width: 100%;
  }

  .item-description {
    font-size: 12px;
    margin-bottom: 8px;
  }

  .today-bookings-card {
    margin-bottom: 16px;
  }

  .bookings-table {
    padding: 4px 0;
    overflow-x: auto;
  }

  .time-tag {
    font-size: 11px;
    padding: 2px 8px;
  }

  /* 表格移动端适配 */
  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-table th) {
    padding: 8px 4px;
  }

  :deep(.el-table td) {
    padding: 8px 4px;
  }

  :deep(.el-table .cell) {
    padding: 0 4px;
  }

  /* 对话框移动端适配 */
  :deep(.el-dialog) {
    width: 90% !important;
    max-width: 500px;
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

  :deep(.el-button) {
    padding: 8px 16px;
    font-size: 14px;
  }

  /* 空状态适配 */
  .empty-card :deep(.el-card__body) {
    padding: 24px 16px;
  }

  :deep(.el-empty__description) {
    font-size: 12px;
  }
}

/* 手机端进一步优化 */
@media (max-width: 480px) {
  .stat-value {
    font-size: 24px;
  }

  .room-name, .item-name {
    font-size: 13px;
  }

  .booking-time {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .time-range {
    width: 100%;
    text-align: center;
  }

  .booking-user {
    width: 100%;
    text-align: center;
  }

  :deep(.el-table) {
    font-size: 11px;
  }
}
</style>
