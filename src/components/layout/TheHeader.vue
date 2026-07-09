<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useCartStore } from '@/stores/cartStore'
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()
const { itemCount } = storeToRefs(cartStore)
const keyword = ref('')

const submitSearch = () => {
  router.push({
    path: '/products',
    query: {
      q: keyword.value.trim() || undefined
    }
  })
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}
</script>

<template>
  <header class="site-header">
    <div class="top-bar">
      <div class="top-inner">
        <span>
          {{ userStore.isAuthenticated ? `欢迎回来，${userStore.currentUser?.username}` : '欢迎来到 Bacon Mall' }}
        </span>
        <div class="top-links">
          <RouterLink to="/orders">我的订单</RouterLink>
          <RouterLink to="/cart">购物车</RouterLink>
          <RouterLink to="/login" v-if="!userStore.isAuthenticated">登录</RouterLink>
          <RouterLink to="/register" v-if="!userStore.isAuthenticated">注册</RouterLink>
          <button v-else type="button" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>

    <div class="main-header">
      <RouterLink to="/" class="brand" aria-label="Bacon Mall 首页">
        <span class="brand-mark">B</span>
        <span>
          <strong>Bacon Mall</strong>
          <small>电商推荐平台</small>
        </span>
      </RouterLink>

      <form class="header-search" @submit.prevent="submitSearch">
        <input v-model="keyword" type="search" placeholder="搜索商品、分类、关键词" />
        <button type="submit">搜索</button>
      </form>

      <RouterLink to="/cart" class="cart-entry">
        <span>购物车</span>
        <strong>{{ itemCount }}</strong>
      </RouterLink>
    </div>

    <nav class="channel-nav" aria-label="主导航">
      <div class="channel-inner">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/products">全部商品</RouterLink>
        <RouterLink to="/products?category=数码">数码家电</RouterLink>
        <RouterLink to="/products?category=服饰">服饰穿搭</RouterLink>
        <RouterLink to="/products?category=家居">家居生活</RouterLink>
        <RouterLink to="/orders">我的订单</RouterLink>
      </div>
    </nav>
  </header>
</template>

<style>
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid #eee;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(16px);
}

.top-bar {
  background: #f7f8fa;
  border-bottom: 1px solid #eee;
  color: #666;
  font-size: 0.8rem;
}

.top-inner,
.main-header,
.channel-inner {
  width: min(1400px, calc(100vw - 48px));
  margin: 0 auto;
}

.top-inner {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  min-height: 34px;
}

.top-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.top-links a,
.top-links button {
  border: 0;
  background: transparent;
  color: #666;
  cursor: pointer;
  font: inherit;
  text-decoration: none;
}

.top-links a:hover,
.top-links button:hover {
  color: var(--primary-color);
}

.main-header {
  display: grid;
  grid-template-columns: 240px minmax(320px, 1fr) 130px;
  gap: 1.5rem;
  align-items: center;
  padding: 1.1rem 0;
}

.brand {
  display: inline-flex;
  gap: 0.75rem;
  align-items: center;
  color: #111827;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #fe2c55, #111827);
  color: #fff;
  font-size: 1.4rem;
  font-weight: 900;
}

.brand strong,
.brand small {
  display: block;
}

.brand strong {
  font-size: 1.35rem;
  line-height: 1.1;
}

.brand small {
  margin-top: 0.25rem;
  color: #777;
  font-size: 0.78rem;
}

.header-search {
  display: flex;
  box-sizing: border-box;
  width: 100%;
  min-height: 46px;
  overflow: hidden;
  padding: 0.25rem;
  border: 2px solid var(--primary-color);
  border-radius: 999px;
  background: #fff;
}

.header-search input {
  flex: 1;
  min-width: 0;
  padding: 0 1rem;
  border-radius: 999px 0 0 999px;
  border: 0;
  outline: none;
  color: #111827;
  font-size: 0.95rem;
}

.header-search button {
  min-width: 86px;
  border: 0;
  border-radius: 999px;
  background: var(--primary-color);
  color: #fff;
  cursor: pointer;
  font-weight: 800;
}

.cart-entry {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  align-items: center;
  min-height: 44px;
  border: 1px solid #eee;
  border-radius: 999px;
  background: #fff;
  color: #111827;
  text-decoration: none;
  font-weight: 700;
}

.cart-entry strong {
  display: grid;
  min-width: 22px;
  height: 22px;
  padding: 0 0.35rem;
  place-items: center;
  border-radius: 999px;
  background: var(--primary-color);
  color: #fff;
  font-size: 0.78rem;
}

.channel-nav {
  border-top: 1px solid #f1f1f1;
}

.channel-inner {
  display: flex;
  gap: 2rem;
  align-items: center;
  min-height: 42px;
  overflow-x: auto;
}

.channel-inner a {
  position: relative;
  flex: 0 0 auto;
  color: #333;
  text-decoration: none;
  font-weight: 700;
}

.channel-inner a:hover,
.channel-inner a.router-link-active {
  color: var(--primary-color);
}

.channel-inner a.router-link-active::after {
  position: absolute;
  right: 0;
  bottom: -10px;
  left: 0;
  height: 3px;
  border-radius: 999px;
  background: var(--primary-color);
  content: '';
}

@media (max-width: 900px) {
  .top-inner,
  .main-header,
  .channel-inner {
    width: min(100% - 24px, 1400px);
  }

  .main-header {
    grid-template-columns: 1fr;
    gap: 0.8rem;
  }

  .header-search {
    justify-self: stretch;
  }

  .cart-entry {
    justify-self: start;
    padding: 0 1rem;
  }
}

@media (max-width: 640px) {
  .top-inner {
    align-items: flex-start;
    flex-direction: column;
    padding: 0.45rem 0;
  }

  .top-links {
    flex-wrap: wrap;
  }

  .channel-inner {
    gap: 1.2rem;
  }
}
</style>
