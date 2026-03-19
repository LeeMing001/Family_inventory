<template>
  <div class="login-container">
    <div class="login-card">
      <h1>家庭物资管理系统</h1>
      
      <div class="tabs">
        <button 
          :class="{ active: isLogin }" 
          @click="isLogin = true"
        >登录</button>
        <button 
          :class="{ active: !isLogin }" 
          @click="isLogin = false"
        >注册</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码"
            required
          />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { login, register, getCurrentUser } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  loading.value = true
  error.value = ''

  try {
    if (isLogin.value) {
      // 登录
      const result = await login(form.value.username, form.value.password)
      authStore.setToken(result.access_token)
      
      // 获取用户信息
      const user = await getCurrentUser()
      authStore.setUser(user)
      
      router.push('/dashboard')
    } else {
      // 注册
      await register(form.value.username, form.value.password)
      
      // 注册成功后自动登录
      const result = await login(form.value.username, form.value.password)
      authStore.setToken(result.access_token)
      
      const user = await getCurrentUser()
      authStore.setUser(user)
      
      router.push('/dashboard')
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.tabs {
  display: flex;
  margin-bottom: 25px;
  border-bottom: 2px solid #eee;
}

.tabs button {
  flex: 1;
  padding: 12px;
  background: none;
  border: none;
  color: #666;
  font-size: 16px;
  cursor: pointer;
  position: relative;
}

.tabs button.active {
  color: #667eea;
  font-weight: 600;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #667eea;
}

.tabs button:hover:not(.active) {
  background: #f5f5f5;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #eee;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

button[type="submit"] {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  margin-top: 15px;
  padding: 10px;
  background: #fee;
  color: #c33;
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
}
</style>
