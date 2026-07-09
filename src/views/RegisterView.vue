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
  phone: '',
  role: 'buyer',
  shopName: '',
  mainCategory: ''
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

  if (registerForm.value.role === 'seller' && !registerForm.value.shopName?.trim()) {
    errorMessage.value = '商家账号需要填写店铺名称'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await userStore.register(registerForm.value)
    router.push(userStore.landingPath)
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
        <fieldset class="auth-choice">
          <legend>账号类型</legend>
          <label :class="{ active: registerForm.role === 'buyer' }">
            <input v-model="registerForm.role" type="radio" value="buyer" />
            <span>
              <strong>我是买家</strong>
              <small>浏览商品、加购下单、查看推荐</small>
            </span>
          </label>
          <label :class="{ active: registerForm.role === 'seller' }">
            <input v-model="registerForm.role" type="radio" value="seller" />
            <span>
              <strong>我是商家</strong>
              <small>管理商品、订单和经营数据</small>
            </span>
          </label>
        </fieldset>

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

        <template v-if="registerForm.role === 'seller'">
          <label>
            <span>店铺名称</span>
            <input v-model="registerForm.shopName" type="text" required placeholder="例如：Bacon 数码旗舰店" />
          </label>

          <label>
            <span>主营类目</span>
            <input v-model="registerForm.mainCategory" type="text" placeholder="例如：数码、服饰、家居" />
          </label>
        </template>

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

.auth-choice {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 0;
  padding: 0;
  border: 0;
}

.auth-choice legend {
  grid-column: 1 / -1;
  margin-bottom: 2px;
  color: #374151;
  font-size: 14px;
  font-weight: 800;
}

.auth-choice label {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fafafa;
  cursor: pointer;
}

.auth-choice label.active {
  border-color: #fe2c55;
  background: #fff1f2;
}

.auth-choice input {
  width: auto;
  min-height: auto;
  margin-top: 4px;
}

.auth-choice span {
  display: grid;
  gap: 3px;
}

.auth-choice strong {
  color: #111827;
}

.auth-choice small {
  color: #6b7280;
  line-height: 1.4;
}

@media (max-width: 560px) {
  .auth-choice {
    grid-template-columns: 1fr;
  }
}
</style>
