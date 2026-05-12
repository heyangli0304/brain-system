<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">算网大脑</h1>
      <p class="login-subtitle">算力网络智能编排调度平台</p>
      
      <el-alert
        title="登录说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px; font-size: 13px;"
      >
        <div style="margin-bottom: 8px;"><strong>管理员账号：</strong>admin（任意密码）</div>
        <div style="margin-bottom: 8px;"><strong>普通用户：</strong>user（任意密码）</div>
        <el-divider style="margin: 12px 0;">权限说明</el-divider>
        <div style="color: #409EFF;">
          <div><strong>管理员权限：</strong>部署任务、任务列表、多模态推理、网络拓扑、资源概况</div>
        </div>
        <div style="color: #67C23A; margin-top: 6px;">
          <div><strong>普通用户权限：</strong>任务列表、多模态推理、网络拓扑、资源概况</div>
        </div>
        <div style="margin-top: 8px; color: #E6A23C;">💡 提示：用户名决定角色，密码任意输入即可</div>
      </el-alert>
      
      <el-form :model="loginForm" :rules="rules" ref="formRef" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名（admin 或 user）" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码（任意密码均可）" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin" class="login-btn">登 录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { loginApi } from "@/api/modules/auth"
import { useUserStore } from "@/store/modules/user"

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const loginForm = reactive({ username: "", password: "" })
const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }]
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    // 登录前先清除旧的 token，避免携带无效 token 请求
    userStore.logout()
    
    // 前端 Mock 登录，不依赖后端
    const res: any = await loginApi(loginForm.username, loginForm.password)
    
    // 前端返回的数据格式：{ respCode: 0, respBody: { token, username, role } }
    const token = res?.respBody?.token
    const username = res?.respBody?.username
    const role = res?.respBody?.role
    
    userStore.setToken(token)
    userStore.setUserInfo({ username, role })
    
    ElMessage.success(`登录成功，欢迎 ${username} (${role === 'admin' ? '管理员' : '用户'})`)
    router.replace("/")
  } catch (error: any) {
    ElMessage.error(error.message || "登录失败")
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
.login-card {
  width: 400px; padding: 40px;
  background: #fff; border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  .login-title { text-align: center; font-size: 28px; color: #1a1a2e; margin-bottom: 4px; }
  .login-subtitle { text-align: center; font-size: 14px; color: #999; margin-bottom: 32px; }
  .login-btn { width: 100%; }
}
</style>
