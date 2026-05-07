<template>
  <div class="home-page">
    <header class="top-bar">
      <div class="top-bar-inner">
        <div class="logo-area">
          <span class="logo-emoji">📋</span>
          <span class="logo-title">会议室预约系统</span>
        </div>
        <div class="top-bar-right">
          <el-button v-if="!userStore.isLoggedIn" type="primary" round @click="showLoginDialog = true">登录</el-button>
          <el-dropdown v-else @command="handleCommand">
            <span class="user-badge">
              <el-avatar :size="28" :icon="UserFilled" class="avatar" />
              <span class="uname">{{ userStore.userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="dashboard">进入后台</el-dropdown-item>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="page-header">
        <h1 class="page-title">今日会议室预约情况</h1>
        <p class="page-date">{{ todayStr }}</p>
      </div>

      <div class="stats-bar">
        <div class="stat-item" style="--stat-color: var(--primary-color);">
          <span class="stat-value">{{ stats.todayBookings }}</span>
          <span class="stat-label">今日预约</span>
        </div>
        <div class="stat-item" style="--stat-color: var(--success-color);">
          <span class="stat-value">{{ stats.availableRooms }}</span>
          <span class="stat-label">空闲会议室</span>
        </div>
        <div class="stat-item" style="--stat-color: var(--warning-color);">
          <span class="stat-value">{{ stats.inUseRooms }}</span>
          <span class="stat-label">使用中</span>
        </div>
        <div class="stat-item" style="--stat-color: var(--text-secondary);">
          <span class="stat-value">{{ stats.totalItems || 0 }}</span>
          <span class="stat-label">可借物品</span>
        </div>
      </div>

      <!-- 会议室 + 时间线 -->
      <div class="two-col">
        <div class="col-left">
          <div class="section-label">会议室</div>
          <div class="room-grid">
            <div v-for="(room, idx) in rooms" :key="room.id" class="room-card" :style="{ '--delay': idx * 50 + 'ms' }">
              <div class="room-top" :class="room.statusClass">
                <div class="room-icon-area"><el-icon class="room-icon"><OfficeBuilding /></el-icon></div>
                <div class="room-meta">
                  <div class="room-name">{{ room.name }}</div>
                  <div class="room-sub">
                    <span>👥 {{ room.capacity }}人</span>
                    <span v-if="room.location" class="room-loc">📍 {{ room.location }}</span>
                  </div>
                </div>
                <el-tag :type="room.isInUse ? 'danger' : 'success'" effect="dark" size="small" class="status-tag">
                  {{ room.isInUse ? '使用中' : '空闲' }}
                </el-tag>
              </div>
              <div class="room-bookings-area">
                <div class="bookings-header">
                  <span>今日预约</span>
                  <span class="count">{{ room.todayBookings.length }} 项</span>
                </div>
                <div v-if="room.todayBookings.length > 0" class="bookings-timeline">
                  <div v-for="b in room.todayBookings" :key="b.id" class="timeline-item">
                    <div class="tl-dot" :class="{ active: b.isActive }"></div>
                    <div class="tl-content">
                      <div class="tl-time">{{ formatTime(b.start_time) }} - {{ formatTime(b.end_time) }}</div>
                      <div class="tl-user">
                        <span class="tl-name">{{ b.user_name }}</span>
                        <span v-if="b.user_org_name" class="tl-org">{{ b.user_org_name }}</span>
                      </div>
                      <div v-if="b.purpose" class="tl-purpose">{{ b.purpose }}</div>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无预约" :image-size="40" />
              </div>
              <div class="room-actions">
                <el-button type="primary" :icon="Plus" round @click="handleBookRoom(room)">预约</el-button>
              </div>
            </div>
          </div>
          <el-empty v-if="rooms.length === 0" description="暂无可用会议室" />
        </div>

        <div class="col-right">
          <div class="section-label">今日预约时间线</div>
          <div class="timeline-card">
            <div v-if="sortedBookings.length > 0" class="global-timeline">
              <div v-for="b in sortedBookings" :key="b.id" class="global-tl-item">
                <div class="tl-time-col">
                  <span class="tl-start">{{ formatTime(b.start_time) }}</span>
                  <span class="tl-end">{{ formatTime(b.end_time) }}</span>
                </div>
                <div class="tl-line-col">
                  <div class="tl-line"></div>
                  <div class="tl-dot" :class="{ active: b.isActive }"></div>
                </div>
                <div class="tl-info-col">
                  <div class="tl-room">{{ b.room_name }}</div>
                  <div class="tl-person">
                    <span>{{ b.user_name }}</span>
                    <span v-if="b.user_org_name" class="tl-org">({{ b.user_org_name }})</span>
                  </div>
                  <div v-if="b.purpose" class="tl-purpose">{{ b.purpose }}</div>
                </div>
              </div>
            </div>
            <el-empty v-else description="今日暂无预约" :image-size="60" />
          </div>
        </div>
      </div>

      <!-- 可借物品 -->
      <div class="section-label" style="margin-top: 28px;">可借物品</div>
      <div class="items-grid">
        <div v-for="(item, idx) in items" :key="item.id" class="item-card" :style="{ '--delay': idx * 50 + 'ms' }">
          <div class="item-card-top">
            <div class="item-icon-area"><el-icon class="item-icon"><Box /></el-icon></div>
            <div class="item-avail" :class="{ empty: item.available_quantity <= 0 }">
              <span class="avail-num">{{ item.available_quantity }}</span>
              <span class="avail-total">/ {{ item.quantity }}</span>
            </div>
          </div>
          <div class="item-name">{{ item.name }}</div>
          <div v-if="item.category" class="item-category">{{ item.category }}</div>
          <div v-if="item.description" class="item-desc">{{ item.description }}</div>
          <div class="item-footer">
            <el-button type="primary" size="small" round
              :disabled="item.available_quantity <= 0"
              @click="handleBorrowItem(item)">
              {{ item.available_quantity > 0 ? '借用' : '暂不可用' }}
            </el-button>
          </div>
        </div>
      </div>
      <el-empty v-if="items.length === 0" description="暂无可用物品" />
    </main>

    <!-- 登录弹窗 -->
    <el-dialog v-model="showLoginDialog" title="登录" width="400px" :close-on-click-modal="false" destroy-on-close>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="0" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" :prefix-icon="UserFilled" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" :prefix-icon="Lock" size="large"
            show-password @keyup.enter="handleLogin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLoginDialog = false">取消</el-button>
        <el-button type="primary" :loading="loginLoading" @click="handleLogin">登录</el-button>
      </template>
    </el-dialog>

    <!-- 预约弹窗 -->
    <el-dialog v-model="bookingDialogVisible" title="预约会议室" width="500px">
      <el-form :model="bookingForm" :rules="bookingRules" ref="bookingFormRef" label-width="100px">
        <el-form-item label="会议室">
          <el-input :value="selectedRoom?.name" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker v-model="bookingForm.date" type="date" placeholder="选择日期"
            :disabled-date="d => d.getTime() < Date.now() - 86400000" style="width:100%" />
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime">
          <el-select v-model="bookingForm.startTime" placeholder="选择开始时间" style="width:100%">
            <el-option v-for="s in timeSlots" :key="s.value" :label="s.label" :value="s.value" :disabled="s.disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-select v-model="bookingForm.endTime" placeholder="选择结束时间" style="width:100%">
            <el-option v-for="s in timeSlots" :key="s.value" :label="s.label" :value="s.value"
              :disabled="s.disabled || s.value <= bookingForm.startTime" />
          </el-select>
        </el-form-item>
        <el-form-item label="预约事由" prop="purpose">
          <el-input v-model="bookingForm.purpose" type="textarea" placeholder="请简要说明预约事由" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookingDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bookingLoading" @click="handleCreateBooking">确定</el-button>
      </template>
    </el-dialog>

    <!-- 借用弹窗 -->
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
          <el-date-picker v-model="borrowForm.return_date" type="date" placeholder="选择日期"
            :disabled-date="d => d.getTime() < Date.now() - 86400000" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="borrowForm.notes" type="textarea" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="borrowLoading" @click="handleCreateBorrowing">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getPublicTodayBookings, getPublicRooms, getPublicStats, getPublicItems, createBooking, createBorrowing } from '@/api'
import { ElMessage } from 'element-plus'
import { UserFilled, Lock, Plus, ArrowDown, Box } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

const router = useRouter()
const userStore = useUserStore()

const todayStr = computed(() => dayjs().format('YYYY年M月D日 dddd'))

// Data
const stats = ref({ todayBookings: 0, availableRooms: 0, inUseRooms: 0, totalRooms: 0, totalItems: 0 })
const rooms = ref([])
const items = ref([])
const allTodayBookings = ref([])

const sortedBookings = computed(() =>
  [...allTodayBookings.value]
    .filter(b => b.status !== 'cancelled')
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
)

const formatTime = (t) => dayjs(t).format('HH:mm')

// Login
const showLoginDialog = ref(false)
const loginLoading = ref(false)
const loginFormRef = ref(null)
const loginForm = ref({ username: '', password: '' })
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// Booking
const bookingDialogVisible = ref(false)
const bookingLoading = ref(false)
const bookingFormRef = ref(null)
const selectedRoom = ref(null)
const bookingForm = ref({ room_id: null, date: new Date(), startTime: '09:00', endTime: '10:00', purpose: '' })
const bookingRules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入预约事由', trigger: 'blur' }]
}

// Borrow
const borrowDialogVisible = ref(false)
const borrowLoading = ref(false)
const borrowFormRef = ref(null)
const selectedItem = ref(null)
const borrowForm = ref({ item_id: null, quantity: 1, return_date: new Date(Date.now() + 7 * 86400000), notes: '' })
const borrowRules = {
  quantity: [{ required: true, message: '请输入借用数量', trigger: 'change' }],
  return_date: [{ required: true, message: '请选择归还日期', trigger: 'change' }]
}

// Time slots
const timeSlots = computed(() => {
  const slots = []
  const now = new Date()
  const selDate = bookingForm.value.date ? new Date(bookingForm.value.date).toDateString() : now.toDateString()
  for (let h = 8; h <= 20; h++) {
    for (const m of [0, 30]) {
      if (h === 20 && m > 0) break
      const v = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
      let disabled = false
      if (selDate === now.toDateString()) {
        const t = new Date(); t.setHours(h, m, 0, 0)
        if (t < now) disabled = true
      }
      slots.push({ value: v, label: v, disabled })
    }
  }
  return slots
})

// Default booking times
const getDefaultStartTime = () => {
  const now = new Date()
  let nextMinute = Math.ceil((now.getMinutes() + 1) / 30) * 30
  let nextHour = now.getHours()
  if (nextMinute >= 60) { nextMinute = 0; nextHour++ }
  if (nextHour > 20 || (nextHour === 20 && nextMinute > 0)) return '08:00'
  if (nextHour < 8) { nextHour = 8; nextMinute = 0 }
  return `${String(nextHour).padStart(2, '0')}:${String(nextMinute).padStart(2, '0')}`
}

const getDefaultEndTime = (start) => {
  const [h, m] = start.split(':').map(Number)
  return `${String(Math.min(h + 1, 20)).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

const resetBookingForm = (room) => {
  const start = getDefaultStartTime()
  bookingForm.value = { room_id: room.id, date: new Date(), startTime: start, endTime: getDefaultEndTime(start), purpose: '' }
}

watch(() => bookingForm.value.startTime, (val) => {
  if (val) bookingForm.value.endTime = getDefaultEndTime(val)
})

// Login handler
const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    loginLoading.value = true
    try {
      await userStore.login(loginForm.value.username, loginForm.value.password)
      ElMessage.success('登录成功')
      showLoginDialog.value = false
      if (pendingBookingRoom.value) {
        selectedRoom.value = pendingBookingRoom.value
        resetBookingForm(pendingBookingRoom.value)
        pendingBookingRoom.value = null
        bookingDialogVisible.value = true
      } else if (pendingBorrowItem.value) {
        const item = pendingBorrowItem.value
        selectedItem.value = item
        pendingBorrowItem.value = null
        openBorrowDialog(item)
      }
    } catch (e) { /* handled by interceptor */ }
    finally { loginLoading.value = false }
  })
}

// Booking
const pendingBookingRoom = ref(null)

const handleBookRoom = (room) => {
  if (!userStore.isLoggedIn) {
    pendingBookingRoom.value = room
    showLoginDialog.value = true
    return
  }
  selectedRoom.value = room
  resetBookingForm(room)
  bookingDialogVisible.value = true
}

const handleCreateBooking = async () => {
  if (!bookingFormRef.value) return
  await bookingFormRef.value.validate(async (valid) => {
    if (!valid) return
    bookingLoading.value = true
    try {
      const start = dayjs(bookingForm.value.date).format('YYYY-MM-DD') + 'T' + bookingForm.value.startTime + ':00'
      const end = dayjs(bookingForm.value.date).format('YYYY-MM-DD') + 'T' + bookingForm.value.endTime + ':00'
      await createBooking({ room_id: bookingForm.value.room_id, start_time: start, end_time: end, purpose: bookingForm.value.purpose })
      ElMessage.success('预约成功')
      bookingDialogVisible.value = false
      await refreshData()
    } catch (e) { ElMessage.error(e.response?.data?.detail || '预约失败') }
    finally { bookingLoading.value = false }
  })
}

// Borrow
const pendingBorrowItem = ref(null)

const openBorrowDialog = (item) => {
  borrowForm.value = {
    item_id: item.id,
    quantity: 1,
    return_date: new Date(Date.now() + 7 * 86400000),
    notes: ''
  }
  borrowDialogVisible.value = true
}

const handleBorrowItem = (item) => {
  if (!userStore.isLoggedIn) {
    pendingBorrowItem.value = item
    showLoginDialog.value = true
    return
  }
  selectedItem.value = item
  openBorrowDialog(item)
}

const handleCreateBorrowing = async () => {
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
      await refreshData()
    } catch (e) { ElMessage.error(e.response?.data?.detail || '借用失败') }
    finally { borrowLoading.value = false }
  })
}

// Fetch & refresh
const refreshData = async () => {
  try {
    const [bookingsRes, itemsRes] = await Promise.all([
      getPublicTodayBookings(),
      getPublicItems()
    ])
    allTodayBookings.value = bookingsRes || []
    items.value = itemsRes || []
    rooms.value = (rooms.value || []).map(r => {
      const rb = (bookingsRes || []).filter(b => b.room_id === r.id && b.status !== 'cancelled')
      const now = new Date()
      return {
        ...r,
        todayBookings: rb.sort((a, b) => new Date(a.start_time) - new Date(b.start_time)),
        isInUse: rb.some(b => new Date(b.start_time) <= now && new Date(b.end_time) >= now),
        statusClass: rb.some(b => new Date(b.start_time) <= now && new Date(b.end_time) >= now) ? 'in-use' : 'free'
      }
    })
  } catch (e) { console.error('refresh failed:', e) }
}

onMounted(async () => {
  try {
    const [bookingsRes, roomsRes, statsRes, itemsRes] = await Promise.all([
      getPublicTodayBookings(),
      getPublicRooms(),
      getPublicStats(),
      getPublicItems()
    ])
    allTodayBookings.value = bookingsRes || []
    stats.value = statsRes || {}
    items.value = itemsRes || []
    rooms.value = (roomsRes || []).map(r => {
      const rb = (bookingsRes || []).filter(b => b.room_id === r.id && b.status !== 'cancelled')
      const now = new Date()
      return {
        ...r,
        todayBookings: rb.sort((a, b) => new Date(a.start_time) - new Date(b.start_time)),
        isInUse: rb.some(b => new Date(b.start_time) <= now && new Date(b.end_time) >= now),
        statusClass: rb.some(b => new Date(b.start_time) <= now && new Date(b.end_time) >= now) ? 'in-use' : 'free'
      }
    })
  } catch (e) { console.error('HomePage load failed:', e) }
})

// User dropdown
const handleCommand = (cmd) => {
  if (cmd === 'logout') { userStore.logout(); ElMessage.success('已退出登录') }
  else if (cmd === 'dashboard') { router.push('/dashboard') }
  else if (cmd === 'profile') { router.push('/profile') }
}
</script>

<style scoped>
.home-page { min-height: 100vh; background: var(--bg-color); }

.top-bar {
  background: var(--card-bg); border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm); position: sticky; top: 0; z-index: 100;
}
.top-bar-inner { max-width: 1280px; margin: 0 auto; height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; }
.logo-area { display: flex; align-items: center; gap: 8px; }
.logo-emoji { font-size: 22px; }
.logo-title { font-size: 16px; font-weight: 600; background: linear-gradient(135deg, #4f6ef7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.user-badge { display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 4px 10px; border-radius: var(--radius-md); transition: background var(--transition-fast); }
.user-badge:hover { background: var(--bg-secondary); }
.user-badge .avatar { background: var(--primary-gradient) !important; }
.uname { font-size: 13px; color: var(--text-secondary); }

.main-content { max-width: 1280px; margin: 0 auto; padding: 32px 24px; }
.page-header { text-align: center; margin-bottom: 28px; }
.page-title { font-size: 28px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.page-date { font-size: 15px; color: var(--text-tertiary); }

.stats-bar { display: flex; gap: 16px; margin-bottom: 32px; }
.stat-item { flex: 1; background: var(--card-bg); border-radius: var(--radius-lg); padding: 20px; text-align: center; box-shadow: var(--shadow-sm); border: 1px solid var(--border-color); transition: all var(--transition-base); animation: fadeInUp 0.4s ease both; }
.stat-item:nth-child(1) { animation-delay: 0ms; }
.stat-item:nth-child(2) { animation-delay: 80ms; }
.stat-item:nth-child(3) { animation-delay: 160ms; }
.stat-item:nth-child(4) { animation-delay: 240ms; }
.stat-item:hover { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.stat-value { font-size: 32px; font-weight: 700; color: var(--stat-color, var(--text-primary)); display: block; line-height: 1; margin-bottom: 4px; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 13px; color: var(--text-tertiary); }

.two-col { display: flex; gap: 24px; align-items: flex-start; }
.col-left { flex: 1; min-width: 0; }
.col-right { width: 340px; flex-shrink: 0; }
@media (max-width: 900px) { .two-col { flex-direction: column; } .col-right { width: 100%; } }

.section-label { font-size: 14px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; padding-left: 4px; }

.room-grid { display: flex; flex-direction: column; gap: 16px; }
.room-card { background: var(--card-bg); border-radius: var(--radius-lg); border: 1px solid var(--border-color); overflow: hidden; box-shadow: var(--shadow-sm); transition: all var(--transition-base); animation: fadeInUp 0.5s ease both; animation-delay: var(--delay, 0ms); }
.room-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.room-top { padding: 16px 20px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border-color); position: relative; overflow: hidden; }
.room-top::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; transition: background var(--transition-base); }
.room-top.free::before { background: var(--success-color); }
.room-top.in-use::before { background: var(--danger-color); }
.room-icon-area { width: 44px; height: 44px; border-radius: var(--radius-md); background: var(--primary-light); color: var(--primary-color); display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
.room-meta { flex: 1; min-width: 0; }
.room-name { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.room-sub { display: flex; gap: 12px; font-size: 13px; color: var(--text-tertiary); }
.status-tag { flex-shrink: 0; border: none; }
.room-bookings-area { padding: 14px 20px; min-height: 80px; }
.bookings-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 12px; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.3px; }
.bookings-header .count { font-weight: 600; }
.bookings-timeline { display: flex; flex-direction: column; gap: 10px; }
.timeline-item { display: flex; gap: 10px; position: relative; }
.tl-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--border-color); margin-top: 5px; flex-shrink: 0; position: relative; }
.tl-dot.active { background: var(--success-color); box-shadow: 0 0 0 3px var(--success-light); }
.timeline-item:not(:last-child) .tl-dot::after { content: ''; position: absolute; top: 10px; left: 3.5px; width: 1px; height: calc(100% + 10px); background: var(--border-color); }
.tl-content { flex: 1; min-width: 0; }
.tl-time { font-size: 13px; font-weight: 500; color: var(--text-primary); margin-bottom: 2px; }
.tl-user { font-size: 12px; color: var(--text-secondary); display: flex; gap: 6px; }
.tl-org { color: var(--text-tertiary); }
.tl-purpose { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.room-actions { padding: 12px 20px; border-top: 1px solid var(--border-color); text-align: right; }

.timeline-card { background: var(--card-bg); border-radius: var(--radius-lg); border: 1px solid var(--border-color); padding: 16px; box-shadow: var(--shadow-sm); animation: fadeInUp 0.5s ease both; animation-delay: 200ms; }
.global-tl-item { display: flex; gap: 12px; padding: 12px 0; position: relative; }
.global-tl-item:not(:last-child) { border-bottom: 1px solid var(--border-color); }
.tl-time-col { width: 50px; flex-shrink: 0; text-align: right; display: flex; flex-direction: column; }
.tl-start { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.tl-end { font-size: 11px; color: var(--text-tertiary); }
.tl-line-col { width: 16px; display: flex; flex-direction: column; align-items: center; position: relative; }
.tl-line { width: 1px; flex: 1; background: var(--border-color); }
.global-tl-item:first-child .tl-line { margin-top: 5px; }
.global-tl-item:last-child .tl-line { display: none; }
.tl-info-col { flex: 1; min-width: 0; }
.tl-room { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.tl-person { font-size: 12px; color: var(--text-secondary); display: flex; gap: 4px; }
.global-tl-item .tl-purpose { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Items grid */
.items-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
.item-card { background: var(--card-bg); border-radius: var(--radius-lg); border: 1px solid var(--border-color); padding: 16px; box-shadow: var(--shadow-sm); transition: all var(--transition-base); animation: fadeInUp 0.5s ease both; animation-delay: var(--delay, 0ms); display: flex; flex-direction: column; }
.item-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.item-card-top { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.item-icon-area { width: 40px; height: 40px; border-radius: var(--radius-md); background: var(--primary-light); color: var(--primary-color); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.item-avail { display: flex; align-items: baseline; gap: 2px; }
.avail-num { font-size: 28px; font-weight: 700; color: var(--success-color); line-height: 1; font-variant-numeric: tabular-nums; }
.avail-num.empty { color: var(--danger-color); }
.avail-total { font-size: 14px; color: var(--text-tertiary); }
.item-name { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.item-category { font-size: 12px; color: var(--text-tertiary); margin-bottom: 4px; }
.item-desc { font-size: 12px; color: var(--text-tertiary); line-height: 1.5; margin-bottom: 12px; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.item-footer { margin-top: auto; }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .main-content { padding: 16px 12px; }
  .page-title { font-size: 22px; }
  .stats-bar { flex-wrap: wrap; gap: 10px; }
  .stat-item { flex: 1 0 calc(50% - 10px); padding: 14px; }
  .stat-value { font-size: 26px; }
  .room-top { padding: 12px 14px; flex-wrap: wrap; }
  .room-bookings-area { padding: 10px 14px; }
  .room-actions { padding: 10px 14px; }
  .items-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
  .avail-num { font-size: 22px; }
}
@media (max-width: 480px) {
  .page-title { font-size: 18px; }
  .stat-item { flex: 1 0 100%; }
  .items-grid { grid-template-columns: 1fr 1fr; }
  .avail-num { font-size: 20px; }
}
</style>
