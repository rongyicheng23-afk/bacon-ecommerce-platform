<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import type { LoginRequest } from '@/types/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginForm = ref<LoginRequest>({
  email: 'student@example.com',
  password: '123456'
})

const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    await userStore.login(loginForm.value)
    router.push(userStore.getLoginRedirect(route.query.redirect as string | undefined))
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-visual">
      <div>
        <span>Bacon Mall</span>
        <h1>登录后查看购物车、订单和专属推荐</h1>
        <p>当前阶段使用本地 mock 登录，后续接入 FastAPI 后会替换成真实用户接口。</p>
      </div>

      <ul>
        <li>商品浏览、收藏、加购行为会记录到本地日志</li>
        <li>订单流程先用前端 mock 跑通，方便后续接后端</li>
        <li>测试账号已自动填好，可直接登录体验</li>
      </ul>
    </section>

    <section class="auth-panel" aria-label="登录表单">
      <div class="auth-heading">
        <span>Welcome back</span>
        <h2>登录账号</h2>
        <p>买家：student@example.com / 123456<br />商家：seller@example.com / 123456</p>
      </div>

      <form class="auth-form" @submit.prevent="handleLogin">
        <label>
          <span>邮箱</span>
          <input v-model="loginForm.email" type="email" required placeholder="请输入邮箱" autocomplete="email" />
        </label>

        <label>
          <span>密码</span>
          <input v-model="loginForm.password" type="password" required placeholder="请输入密码" autocomplete="current-password" />
        </label>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <footer>
          <span>还没有账号？</span>
          <router-link to="/register">立即注册</router-link>
        </footer>
      </form>
    </section>
  </main>
</template>
