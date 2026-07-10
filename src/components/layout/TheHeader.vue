<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { useProductStore } from '@/stores/productStore'
import { cartUpdatedEvent, getCartItemCount } from '@/utils/cart'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const productStore = useProductStore()
const keyword = ref('')
const cartItemCount = ref(0)
const showSuggestions = ref(false)
let blurTimer: number | undefined

const hotSearches = ['耳机', '机械键盘', '背包', '台灯', '加湿器', '鼠标', '充电宝', 'T恤']

const suggestionList = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return hotSearches.map((t) => ({ text: t, hot: true }))
  const names = productStore.products
    .filter((p) => p.name.toLowerCase().includes(kw))
    .slice(0, 6)
    .map((p) => ({ text: p.name, hot: false }))
  return names.length > 0 ? names : [{ text: `搜索 "${kw}"`, hot: false }]
})

const navigateToSuggestion = (text: string) => {
  keyword.value = text
  showSuggestions.value = false
  router.push({ path: '/products', query: { q: text } })
}

const submitSearch = () => {
  showSuggestions.value = false
  router.push({
    path: '/products',
    query: { q: keyword.value.trim() || undefined }
  })
}

const onSearchFocus = () => {
  if (blurTimer) clearTimeout(blurTimer)
  showSuggestions.value = true
}

const onSearchBlur = () => {
  blurTimer = window.setTimeout(() => {
    showSuggestions.value = false
  }, 180)
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

const refreshCartCount = () => {
  cartItemCount.value = getCartItemCount()
}

onMounted(async () => {
  refreshCartCount()
  window.addEventListener(cartUpdatedEvent, refreshCartCount)
  window.addEventListener('storage', refreshCartCount)
  if (productStore.products.length === 0) {
    await productStore.fetchProducts()
  }
})

onUnmounted(() => {
  window.removeEventListener(cartUpdatedEvent, refreshCartCount)
  window.removeEventListener('storage', refreshCartCount)
})
</script>

<template>
  <header class="site-header">
    <div class="top-bar">
      <div class="top-inner">
        <span>
          {{
            userStore.isAuthenticated
              ? `欢迎回来，${userStore.currentUser?.role === 'seller' ? userStore.currentUser?.shopName || userStore.currentUser?.username : userStore.currentUser?.username}`
              : '欢迎来到 Bacon Mall'
          }}
        </span>
        <div class="top-links">
          <RouterLink v-if="userStore.isSeller" to="/seller">商家中心</RouterLink>
          <RouterLink v-if="userStore.isBuyer" to="/orders">我的订单</RouterLink>
          <RouterLink v-if="userStore.isBuyer" to="/profile">个人中心</RouterLink>
          <RouterLink v-if="userStore.isBuyer" to="/history">浏览足迹</RouterLink>
          <RouterLink to="/login" v-if="!userStore.isAuthenticated">登录</RouterLink>
          <RouterLink to="/register" v-if="!userStore.isAuthenticated">注册</RouterLink>
          <button v-if="userStore.isAuthenticated" type="button" @click="handleLogout">退出登录</button>
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
        <div class="search-wrapper">
          <input
            v-model="keyword"
            type="search"
            placeholder="搜索商品、分类、关键词"
            @focus="onSearchFocus"
            @blur="onSearchBlur"
          />
          <div v-if="showSuggestions && suggestionList.length" class="search-dropdown" @mousedown.prevent>
            <button
              v-for="item in suggestionList"
              :key="item.text"
              type="button"
              @click="navigateToSuggestion(item.text)"
            >
              <span v-if="item.hot" class="hot-mark">热</span>
              {{ item.text }}
            </button>
          </div>
        </div>
        <button type="submit">搜索</button>
      </form>

      <RouterLink v-if="userStore.isBuyer" to="/cart" class="cart-entry">
        <span>购物车</span>
        <strong>{{ cartItemCount }}</strong>
      </RouterLink>
      <RouterLink v-else-if="userStore.isSeller" to="/seller" class="cart-entry">
        <span>商家中心</span>
        <strong>店</strong>
      </RouterLink>
    </div>

    <nav class="channel-nav" aria-label="主导航">
      <div class="channel-inner">
        <RouterLink to="/" :class="{ active: route.path === '/' }">首页</RouterLink>
        <RouterLink to="/products?category=数码" :class="{ active: route.query.category === '数码' }">数码家电</RouterLink>
        <RouterLink to="/products?category=服饰" :class="{ active: route.query.category === '服饰' }">服饰穿搭</RouterLink>
        <RouterLink to="/products?category=家居" :class="{ active: route.query.category === '家居' }">家居生活</RouterLink>
        <RouterLink to="/products?category=运动" :class="{ active: route.query.category === '运动' }">运动户外</RouterLink>
        <RouterLink to="/products?category=食品" :class="{ active: route.query.category === '食品' }">食品生鲜</RouterLink>
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
  background: #f1f5f9;
  border-bottom: 1px solid #eee;
  color: #64748b;
  font-size: 0.8rem;
}

.top-inner,
.main-header,
.channel-inner {
  width: min(1400px, calc(100vw - 80px));
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
  color: #64748b;
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
  grid-template-columns: 240px minmax(320px, 1fr) auto;
  gap: 1.5rem;
  align-items: center;
  padding: 1.1rem 0;
}

.brand {
  display: inline-flex;
  gap: 0.75rem;
  align-items: center;
  color: #0f172a;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #ff2f68, #0f172a);
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
  overflow: visible;
  padding: 0.25rem;
  border: 2px solid var(--primary-color);
  border-radius: 999px;
  background: #fff;
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 0;
}

.header-search input {
  width: 100%;
  min-width: 0;
  min-height: 38px;
  padding: 0 1rem;
  border: 0;
  border-radius: 999px;
  outline: none;
  color: #0f172a;
  font-size: 0.95rem;
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  padding: 6px;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 16px 40px rgba(17, 24, 39, 0.16);
  z-index: 50;
}

.search-dropdown button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 40px;
  padding: 0 12px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #0f172a;
  font-size: 14px;
  cursor: pointer;
  text-align: left;
}

.search-dropdown button:hover {
  background: #f1f5f9;
}

.hot-mark {
  display: inline-grid;
  width: 20px;
  height: 20px;
  place-items: center;
  border-radius: 4px;
  background: #ff2f68;
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  flex-shrink: 0;
}

.header-search > button {
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
  padding: 0 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 999px;
  background: #fff;
  color: #0f172a;
  text-decoration: none;
  font-weight: 700;
  white-space: nowrap;
}

.cart-entry:hover {
  border-color: var(--primary-color);
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
  position: relative;
}

.channel-nav::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #ff2f68, #6366f1, #2563eb, #a855f7, #16a34a);
}

.channel-inner {
  display: flex;
  gap: 2rem;
  align-items: center;
  min-height: 42px;
  overflow: hidden;
}

.channel-inner a {
  position: relative;
  flex: 0 0 auto;
  color: #0f172a;
  text-decoration: none;
  font-weight: 700;
}

.channel-inner a:hover,
.channel-inner a.active {
  color: var(--primary-color);
}

.channel-inner a.active::after {
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
    width: min(100% - 32px, 1400px);
  }

  .main-header {
    grid-template-columns: 1fr;
    gap: 0.8rem;
  }

  .header-search {
    justify-self: stretch;
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
