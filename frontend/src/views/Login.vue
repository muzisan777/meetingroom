<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="title">📋 会议室预约系统</h1>
      <p class="subtitle">极简 · 高效 · 易用</p>
      
      <el-form :model="form" :rules="rules" ref="formRef" class="login-form" label-width="0">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="default"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="default"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="default"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少 3 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  // 先验证表单
  await formRef.value.validate(async (valid, fields) => {
    if (!valid) {
      // 显示第一个验证错误
      const firstError = Object.values(fields)[0]
      if (firstError && firstError[0]) {
        ElMessage.warning(firstError[0].message)
      }
      return
    }
    
    loading.value = true
    try {
      await userStore.login(form.username, form.password)
      ElMessage.success('登录成功')
      // 强制刷新路由
      router.push({ path: '/dashboard', replace: true })
    } catch (error) {
      // 响应拦截器应该显示错误，但如果未显示，这里补充错误提示
      console.error('Login error:', error)
      // 如果错误有响应数据，显示具体错误信息
      if (error.response && error.response.data && error.response.data.detail) {
        ElMessage.error(error.response.data.detail || '登录失败')
      } else {
        ElMessage.error('登录失败，请检查网络连接')
      }
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.title {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #999;
  margin-bottom: 32px;
  font-size: 14px;
}

.login-form {
  margin-top: 24px;
}
</style>
