<template>
  <div class="logs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">📋 系统日志</span>
          <div class="controls">
            <el-select 
              v-model="logType" 
              placeholder="选择日志类型"
              @change="fetchLogs"
              style="width: 150px; margin-right: 10px;"
            >
              <el-option 
                v-for="type in logTypes" 
                :key="type" 
                :label="getTypeLabel(type)" 
                :value="type" 
              />
            </el-select>
            
            <el-input
              v-model="searchKeyword"
              placeholder="搜索关键词..."
              clearable
              @keyup.enter="fetchLogs"
              style="width: 200px; margin-right: 10px;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-button type="primary" @click="fetchLogs">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>

            <template v-if="userStore.hasPermission('logs', 'delete')">
              <el-date-picker
                v-model="deleteDateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 240px; margin-right: 10px;"
              />
              <el-button type="danger" @click="handleDeleteLogs" :disabled="!deleteDateRange">
                <el-icon><Delete /></el-icon>
                删除选定范围
              </el-button>
            </template>
          </div>
        </div>
      </template>
      
      <div class="log-stats">
        <el-statistic title="总日志数" :value="totalLogs" />
        <el-statistic title="当前页" :value="currentPage + 1" />
        <el-statistic title="每页显示" :value="pageSize" />
      </div>
      
      <div class="log-actions">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          layout="prev, pager, next, jumper"
          :total="totalLogs"
          @current-change="handlePageChange"
        />
        
        <el-select 
          v-model="pageSize" 
          placeholder="每页数量"
          @change="handlePageSizeChange"
          style="width: 120px; margin-left: 10px;"
        >
          <el-option :value="10" label="10 条" />
          <el-option :value="20" label="20 条" />
          <el-option :value="50" label="50 条" />
          <el-option :value="100" label="100 条" />
        </el-select>
      </div>
      
      <div class="log-container">
        <div 
          v-for="(log, index) in logs" 
          :key="index" 
          class="log-item"
          :class="getLogLevelClass(log)"
        >
          <pre class="log-content">{{ log }}</pre>
        </div>
        
        <el-empty v-if="logs.length === 0" description="暂无日志数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getLogTypes, getLogs, deleteLogs } from '@/api'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Delete } from '@element-plus/icons-vue'

const userStore = useUserStore()

// 状态变量
const logType = ref('action')
const searchKeyword = ref('')
const currentPage = ref(0)
const pageSize = ref(20)
const totalLogs = ref(0)
const logs = ref([])
const logTypes = ref([])
const deleteDateRange = ref(null)

// 删除选定范围的日志
const handleDeleteLogs = async () => {
  if (!deleteDateRange.value) return
  const [startDate, endDate] = deleteDateRange.value
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${logType.value === 'action' ? '操作日志' : '错误日志'} 中 ${startDate} 至 ${endDate} 的所有记录吗？此操作不可恢复。`,
      '确认删除',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    const result = await deleteLogs({
      log_type: logType.value,
      start_date: startDate,
      end_date: endDate
    })
    ElMessage.success(result.message || `已删除 ${result.deleted_lines} 行日志`)
    deleteDateRange.value = null
    await fetchLogs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除日志失败:', error)
      ElMessage.error('删除日志失败')
    }
  }
}

// 获取日志类型
const fetchLogTypes = async () => {
  try {
    const response = await getLogTypes()
    logTypes.value = response.types || []
    if (logTypes.value.length > 0 && !logTypes.value.includes(logType.value)) {
      logType.value = logTypes.value[0]
    }
  } catch (error) {
    console.error('获取日志类型失败:', error)
    ElMessage.error('获取日志类型失败')
  }
}

// 获取日志数据
const fetchLogs = async () => {
  try {
    const response = await getLogs({
      log_type: logType.value,
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value || undefined
    })
    
    logs.value = response.logs || []
    totalLogs.value = response.total || 0
  } catch (error) {
    console.error('获取日志失败:', error)
    ElMessage.error('获取日志失败')
    logs.value = []
    totalLogs.value = 0
  }
}

// 分页变化处理
const handlePageChange = (page) => {
  currentPage.value = page - 1
  fetchLogs()
}

// 每页数量变化处理
const handlePageSizeChange = () => {
  currentPage.value = 0
  fetchLogs()
}

// 获取日志类型标签
const getTypeLabel = (type) => {
  const labels = {
    action: '操作日志',
    error: '错误日志',
    access: '访问日志'
  }
  return labels[type] || type
}

// 根据日志内容判断级别并返回对应样式类
const getLogLevelClass = (log) => {
  if (log.includes('ERROR') || log.includes('error')) {
    return 'log-error'
  } else if (log.includes('WARNING') || log.includes('warning')) {
    return 'log-warning'
  } else if (log.includes('INFO') || log.includes('info')) {
    return 'log-info'
  }
  return 'log-default'
}

// 页面加载时获取数据
onMounted(async () => {
  await fetchLogTypes()
  await fetchLogs()
})

// 监听日志类型变化
watch(logType, () => {
  currentPage.value = 0
  fetchLogs()
})

// 监听搜索关键词变化（防抖）
let searchTimer = null
watch(searchKeyword, (newVal) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 0
    fetchLogs()
  }, 500) // 500ms 防抖
})
</script>

<style scoped>
.logs-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.log-stats {
  display: flex;
  gap: 40px;
  margin: 20px 0;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
}

.log-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.log-container {
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: #fafafa;
}

.log-item {
  padding: 10px 15px;
  border-bottom: 1px solid #ebeef5;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  word-break: break-all;
  white-space: pre-wrap;
}

.log-item:last-child {
  border-bottom: none;
}

.log-error {
  background-color: #fef0f0;
  border-left: 4px solid #f56c6c;
  color: #f56c6c;
}

.log-warning {
  background-color: #fdf6ec;
  border-left: 4px solid #e6a23c;
  color: #e6a23c;
}

.log-info {
  background-color: #f0f9ff;
  border-left: 4px solid #409eff;
  color: #409eff;
}

.log-default {
  background-color: #fafafa;
  border-left: 4px solid #909399;
  color: #606266;
}

.log-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .log-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .log-actions {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>