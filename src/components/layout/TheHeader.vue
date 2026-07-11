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
const searchHistory = ref<string[]>([])
const showHistory = ref(false)

const loadHistory = () => {
  try { searchHistory.value = JSON.parse(localStorage.getItem('searchHistory') || '[]') } catch { searchHistory.value = [] }
}

const saveHistory = (term: string) => {
  if (!term) return
  searchHistory.value = [term, ...searchHistory.value.filter((h) => h !== term)].slice(0, 8)
  localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
}

const removeHistory = (term: string) => {
  searchHistory.value = searchHistory.value.filter((h) => h !== term)
  localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
}

const submitSearch = () => {
  const term = keyword.value.trim()
  if (term) saveHistory(term)
  router.push({ path: '/products', query: { q: term || undefined } })
  showHistory.value = false
}

const searchFromHistory = (term: string) => {
  keyword.value = term
  saveHistory(term)
  router.push({ path: '/products', query: { q: term } })
  showHistory.value = false
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
  loadHistory()
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
    <!-- ====== top bar: purple gradient ====== -->
    <div class="top-bar">
      <div class="top-inner">
        <div class="top-left">
          <span class="top-welcome">
            {{ userStore.isAuthenticated ? `欢迎回来，${userStore.currentUser?.username}` : '欢迎来到 Bacon Mall' }}
          </span>
          <span class="top-sep">|</span>
          <RouterLink to="/products?sort=price-asc" class="top-entry">今日特价</RouterLink>
          <RouterLink to="/hot-sales" class="top-entry">热卖榜单</RouterLink>
          <RouterLink to="/new-arrivals" class="top-entry">新品首发</RouterLink>
        </div>

        <div class="top-right">
          <RouterLink to="/orders" v-if="userStore.isAuthenticated">我的订单</RouterLink>
          <RouterLink to="/profile" v-if="userStore.isAuthenticated">个人中心</RouterLink>
          <RouterLink to="/login" v-if="!userStore.isAuthenticated">登录</RouterLink>
          <RouterLink to="/register" v-if="!userStore.isAuthenticated">注册</RouterLink>
          <button v-if="userStore.isAuthenticated" type="button" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>

    <!-- ====== main header: logo + search + cart ====== -->
    <div class="main-header">
      <RouterLink to="/" class="brand" aria-label="Bacon Mall 首页">
        <span class="brand-mark">B</span>
        <span>
          <strong>Bacon Mall</strong>
          <small>电商推荐平台</small>
        </span>
      </RouterLink>

      <div class="search-wrap">
        <form class="header-search" @submit.prevent="submitSearch">
          <input v-model="keyword" type="search" placeholder="搜索商品、分类、关键词" />
          <button type="submit">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            搜索
          </button>
        </form>
        <div class="search-history" @mousedown.prevent>
          <span class="history-label">历史记录</span>
          <button v-for="h in searchHistory" :key="h" type="button" class="history-tag" @click="searchFromHistory(h)">{{ h }}<span class="history-del" @click.stop="removeHistory(h)">×</span></button>
        </div>
      </div>

      <RouterLink v-if="userStore.isBuyer" to="/cart" class="cart-entry">
        <span>购物车</span>
        <strong>{{ cartItemCount }}</strong>
      </RouterLink>
      <RouterLink v-else-if="userStore.isSeller" to="/seller" class="cart-entry">
        <span>商家中心</span>
        <strong>店</strong>
      </RouterLink>
    </div>

    <!-- ====== channel nav ====== -->
    <nav class="channel-nav" aria-label="主导航">
      <div class="channel-inner">
        <RouterLink to="/" exact-active-class="" :class="{ active: route.path === '/' }">首页</RouterLink>
        <RouterLink to="/category/quality" :class="{ active: route.path.startsWith('/category/quality') }">品质生活</RouterLink>
        <RouterLink to="/category/digital" :class="{ active: route.path.startsWith('/category/digital') }">数码家电</RouterLink>
        <RouterLink to="/category/fashion" :class="{ active: route.path.startsWith('/category/fashion') }">服饰穿搭</RouterLink>
        <RouterLink to="/category/home" :class="{ active: route.path.startsWith('/category/home') }">家居生活</RouterLink>
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

/* ====== top bar: purple gradient ====== */
.top-bar {
  background: linear-gradient(90deg, #5A0B72 0%, #7B189F 50%, #9226B3 100%);
  color: #fff;
  font-size: 0.8rem;
}

.top-inner,
.main-header,
.channel-inner {
  width: min(1320px, calc(100vw - 48px));
  margin: 0 auto;
}

.top-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 38px;
}

.top-left {
  display: flex;
  align-items: center;
  gap: 28px;
}

.top-welcome {
  color: rgba(255, 255, 255, 0.88);
  font-weight: 500;
  white-space: nowrap;
}

.top-sep {
  color: rgba(255, 255, 255, 0.2);
  font-weight: 200;
  user-select: none;
}

.top-entry {
  color: rgba(255, 255, 255, 0.88);
  text-decoration: none;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.top-entry:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  text-decoration: underline;
  text-underline-offset: 4px;
}

.top-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.top-right a,
.top-right button {
  border: 0;
  background: transparent;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  font: inherit;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.top-right a:hover,
.top-right button:hover {
  color: #fff;
  text-decoration: underline;
  text-underline-offset: 4px;
}

/* ====== main header ====== */
.main-header {
  display: grid;
  grid-template-columns: 240px minmax(320px, 1fr) auto;
  gap: 1.5rem;
  align-items: start;
  padding: 1.1rem 0 0.25rem;
  position: relative;
}

.brand {
  display: inline-flex;
  gap: 0.75rem;
  align-items: center;
  color: #241B2F;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #5A0B72 0%, #7B189F 55%, #9226B3 100%);
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
  border: 2px solid transparent;
  border-radius: 999px;
  background: linear-gradient(#fff, #fff) padding-box,
              linear-gradient(90deg, #5A0B72 0%, #7B189F 50%, #9226B3 100%) border-box;
  transition: box-shadow 0.25s ease;
}

.header-search:focus-within {
  box-shadow:
    0 0 0 4px rgba(123, 24, 159, 0.12),
    0 8px 22px rgba(90, 11, 114, 0.12);
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
  color: #241B2F;
  font-size: 0.95rem;
}

.header-search input::placeholder {
  color: #948B9D;
}

.header-search button {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 86px;
  padding: 0 0.8rem;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, #85072B 0%, #7B189F 65%, #9226B3 100%);
  color: #fff;
  cursor: pointer;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.header-search button svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.header-search button:hover {
  transform: translateY(-1px);
  filter: brightness(1.08);
  box-shadow: 0 8px 20px rgba(111, 76, 195, 0.26);
}

.search-wrap { position: relative; }

.search-history {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 4px 0 0;
}

.history-label {
  font-size: 0.74rem;
  color: #948B9D;
  font-weight: 700;
  margin-right: 4px;
  white-space: nowrap;
}

.history-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border: 1px solid #E9E4EE;
  border-radius: 999px;
  background: #fff;
  color: #756D7E;
  cursor: pointer;
  font-size: 0.74rem;
  font-weight: 600;
  transition: all 0.15s;
}

.history-tag:hover { border-color: #7B189F; color: #7B189F; background: #F3EAF8; }

.history-del {
  display: inline-grid;
  width: 14px; height: 14px; place-items: center;
  border-radius: 50%;
  background: #E9E4EE;
  color: #948B9D;
  font-size: 0.6rem; line-height: 1;
  transition: all 0.15s;
}

.history-del:hover { background: #7B189F; color: #fff; }

.cart-entry {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  align-items: center;
  min-height: 44px;
  padding: 0 1rem;
  border: 2px solid #948B9D;
  border-radius: 999px;
  background: #fff;
  color: #241B2F;
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

/* ====== channel nav ====== */
.channel-nav {
  border-top: 1px solid #f1f1f1;
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
  color: #241B2F;
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
    width: min(100% - 28px, 1320px);
  }

  .top-left { gap: 16px; }
  .top-sep { display: none; }

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
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding: 6px 0;
  }

  .top-left,
  .top-right {
    flex-wrap: wrap;
  }

  .top-left { gap: 12px; }

  .channel-inner {
    gap: 1.2rem;
  }
}
</style>
