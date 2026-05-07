<template>
  <div class="borrowings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>借用记录</span>
          <el-select v-model="statusFilter" placeholder="筛选状态" clearable style="width: 150px" @change="fetchBorrowings">
            <el-option label="全部" value="" />
            <el-option label="借用中" value="borrowed" />
            <el-option label="已归还" value="returned" />
          </el-select>
        </div>
      </template>
      
      <el-table :data="borrowings" style="width: 100%" v-loading="loading">
        <el-table-column label="物品" min-width="150">
          <template #default="{ row }">
            <span v-if="row.itemName">{{ row.itemName }}</span>
            <el-tag v-else type="info" size="small">加载中</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column label="借用日期" width="140">
          <template #default="{ row }">
            {{ formatDateTime(row.borrow_date) }}
          </template>
        </el-table-column>
        <el-table-column label="应还日期" width="140">
          <template #default="{ row }">
            {{ row.return_date ? formatDateTime(row.return_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="实际归还" width="140">
          <template #default="{ row }">
            {{ row.actual_return_date ? formatDateTime(row.actual_return_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="借用人" width="120">
          <template #default="{ row }">
            {{ row.userName || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="部门" width="120">
          <template #default="{ row }">
            {{ row.userOrgName || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="success" 
              @click="handleReturn(row)" 
              v-if="row.status === 'borrowed' && (userStore.isAdmin || row.user_id === userStore.userInfo?.id)"
            >
              归还
            </el-button>
            <span v-else-if="row.status !== 'borrowed'" style="color: #999">已归还</span>
            <span v-else style="color: #999">-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { getBorrowings, returnItem, getItems, getUsers } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const borrowings = ref([])
const items = ref([])
const users = ref([])
const statusFilter = ref('')
const loading = ref(false)

const formatDate = (time) => {
  if (!time) return '-'
  try {
    return dayjs(time).format('YYYY-MM-DD')
  } catch (e) {
    return '-'
  }
}

const formatDateTime = (time) => {
  if (!time) return '-'
  try {
    return dayjs(time).format('YYYY-MM-DD HH:mm')
  } catch (e) {
    return '-'
  }
}

const getStatusType = (status) => {
  const types = {
    borrowed: 'warning',
    returned: 'success',
    overdue: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    borrowed: '借用中',
    returned: '已归还',
    overdue: '逾期'
  }
  return texts[status] || status
}

onMounted(async () => {
  await fetchBorrowings()
})

// 监听用户登录状态，登录后重新加载数据
watch(() => userStore.isLoggedIn, async (newVal) => {
  if (newVal) {
    await fetchBorrowings()
  }
}, { immediate: true })

const fetchBorrowings = async () => {
  loading.value = true
  try {
    console.log('Current user:', userStore.userInfo)
    console.log('Is admin:', userStore.isAdmin)
    
    // 先获取物品列表
    items.value = await getItems()
    
    // 管理员才获取用户列表
    if (userStore.isAdmin) {
      users.value = await getUsers()
    }
    
    console.log('Fetched items:', items.value)
    console.log('Fetched users:', users.value)
    
    // 获取借用记录
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const borrowingsRes = await getBorrowings(params)
    
    console.log('Fetched borrowings:', borrowingsRes)
    
    // 关联物品名称和用户名
    borrowings.value = borrowingsRes.map(b => {
      const item = items.value.find(i => i.id === b.item_id)
      const user = userStore.isAdmin ? users.value.find(u => u.id === b.user_id) : null
      console.log('Mapping borrowing:', b, 'Found item:', item, 'Found user:', user)
      return {
        ...b,
        itemName: item ? item.name : `未知物品 (ID:${b.item_id})`,
        userName: b.user_name || (user ? user.username : '-'),
        userOrgName: b.user_org_name || null,
        // 确保 actual_return_date 字段存在
        actual_return_date: b.actual_return_date || null
      }
    })
    
    console.log('Final borrowings:', borrowings.value)
  } catch (error) {
    console.error('Fetch borrowings error:', error)
    ElMessage.error('加载借用记录失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleReturn = async (row) => {
  try {
    await returnItem(row.id)
    ElMessage.success('归还成功')
    await fetchBorrowings()
  } catch (error) {
    console.error('Return error:', error)
    ElMessage.error('归还失败：' + (error.message || '未知错误'))
  }
}
</script>

<style scoped>
.borrowings-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
