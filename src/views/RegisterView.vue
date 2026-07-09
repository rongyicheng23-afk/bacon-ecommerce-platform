<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import type { RegisterRequest } from '@/types/user'

const router = useRouter()
const userStore = useUserStore()

const registerForm = ref<RegisterRequest>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  phone: ''
})

const loading = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  if (registerForm.value.password.length < 6) {
    errorMessage.value = '密码至少需要 6 位'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await userStore.register(registerForm.value)
    router.push('/')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page register-page">
    <section class="auth-visual register-visual">
      <div>
        <span>Join Bacon Mall</span>
        <h1>创建账号后体验完整电商购物流程</h1>
        <p>注册信息会暂时保存在浏览器本地，后续接 FastAPI 时会迁移到 SQLite 或 MySQL 用户表。</p>
      </div>

      <ul>
        <li>注册后自动登录，立即可以加购、结算、查看订单</li>
        <li>用户行为日志会作为后续推荐系统的数据来源</li>
        <li>当前是学习阶段 mock 数据，不涉及真实支付</li>
      </ul>
    </section>

    <section class="auth-panel" aria-label="注册表单">
      <div class="auth-heading">
        <span>Create account</span>
        <h2>注册账号</h2>
        <p>填写基础信息，先完成前端最小可运行版本。</p>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister">
        <label>
          <span>用户名</span>
          <input v-model="registerForm.username" type="text" required placeholder="例如：荣同学" autocomplete="username" />
        </label>

        <label>
          <span>邮箱</span>
          <input v-model="registerForm.email" type="email" required placeholder="请输入邮箱" autocomplete="email" />
        </label>

        <label>
          <span>手机号</span>
          <input v-model="registerForm.phone" type="tel" placeholder="选填，用于模拟收货联系" autocomplete="tel" />
        </label>

        <label>
          <span>密码</span>
          <input v-model="registerForm.password" type="password" required placeholder="至少 6 位" autocomplete="new-password" />
        </label>

        <label>
          <span>确认密码</span>
          <input v-model="registerForm.confirmPassword" type="password" required placeholder="请再次输入密码" autocomplete="new-password" />
        </label>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册并登录' }}
        </button>

        <footer>
          <span>已有账号？</span>
          <router-link to="/login">立即登录</router-link>
        </footer>
      </form>
    </section>
  </main>
</template>

<style>
.register-page .auth-panel {
  align-self: stretch;
}

.register-visual {
  background:
    linear-gradient(120deg, rgba(17, 24, 39, 0.88), rgba(14, 165, 233, 0.58)),
    url('https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1800&q=85') center/cover;
}
</style>
