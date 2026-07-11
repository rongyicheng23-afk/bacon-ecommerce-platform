<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { useProductStore } from '@/stores/productStore'
import type { Product } from '@/types'
import { readFavoriteIds } from '@/utils/favorites'

interface BehaviorLog {
  userId?: number
  productId?: number
  productName?: string
  action: string
  category?: string
  amount?: number
  timestamp: string
}

interface MockOrder {
  orderId: number
  status: 'pending_payment' | 'paid' | 'shipped' | 'completed' | 'cancelled'
  payableAmount: number
  createdAt: string
}

const router = useRouter()
const userStore = useUserStore()
const productStore = useProductStore()
const behaviorLogs = ref<BehaviorLog[]>([])
const orders = ref<MockOrder[]>([])
const favoriteIds = ref<number[]>([])
const actionMessage = ref('')

const actionText: Record<string, string> = {
  view: '浏览',
  favorite: '收藏',
  cart: '加购',
  buy: '购买',
  checkout: '结算',
  submit_order: '提交订单',
  order_paid: '支付订单',
  order_cancelled: '取消订单',
  order_completed: '完成订单'
}

const statusText: Record<MockOrder['status'], string> = {
  pending_payment: '待付款',
  paid: '待发货',
  shipped: '待收货',
  completed: '已完成',
  cancelled: '已取消'
}

const readLocalData = () => {
  try {
    behaviorLogs.value = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  } catch {
    behaviorLogs.value = []
  }

  try {
    orders.value = JSON.parse(localStorage.getItem('mockOrders') || '[]')
  } catch {
    orders.value = []
  }

  favoriteIds.value = readFavoriteIds()
}

const recentLogs = computed(() => {
  return [...behaviorLogs.value]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 8)
})

const productLogs = computed(() => {
  return behaviorLogs.value.filter((log) => log.productId && log.category && log.category !== '订单')
})

const favoriteProducts = computed(() => {
  return favoriteIds.value
    .slice(0, 6)
    .map((id) => productStore.products.find((product) => product.productId === id))
    .filter((product): product is Product => Boolean(product))
})

const categoryPreference = computed(() => {
  const weights: Record<string, number> = {
    view: 1,
    favorite: 3,
    cart: 4,
    buy: 5
  }
  const scoreMap = productLogs.value.reduce<Record<string, number>>((result, log) => {
    const category = log.category || '未分类'
    result[category] = (result[category] || 0) + (weights[log.action] || 1)
    return result
  }, {})

  const maxScore = Math.max(...Object.values(scoreMap), 1)
  return Object.entries(scoreMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([category, score]) => ({
      category,
      score,
      percent: Math.max(10, Math.round((score / maxScore) * 100))
    }))
})

const orderStats = computed(() => {
  const activeOrders = orders.value.filter((order) => order.status !== 'cancelled')
  return {
    count: orders.value.length,
    pending: orders.value.filter((order) => order.status === 'pending_payment').length,
    completed: orders.value.filter((order) => order.status === 'completed').length,
    spending: activeOrders.reduce((sum, order) => sum + order.payableAmount, 0)
  }
})

const behaviorStats = computed(() => {
  return {
    views: behaviorLogs.value.filter((log) => log.action === 'view').length,
    favorites: behaviorLogs.value.filter((log) => log.action === 'favorite').length,
    carts: behaviorLogs.value.filter((log) => log.action === 'cart').length,
    orders: behaviorLogs.value.filter((log) => log.action === 'submit_order').length
  }
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const clearBehaviorLogs = () => {
  localStorage.removeItem('behaviorLogs')
  behaviorLogs.value = []
  actionMessage.value = '浏览和行为记录已清空'
  window.setTimeout(() => {
    actionMessage.value = ''
  }, 1600)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=500&q=85'
}

onMounted(async () => {
  readLocalData()

  if (productStore.products.length === 0) {
    await productStore.fetchProducts()
  }
})
</script>

<template>
  <main class="profile-page">
    <p v-if="actionMessage" class="profile-toast">{{ actionMessage }}</p>

    <section class="profile-hero">
      <div class="profile-avatar">
        {{ userStore.currentUser?.username?.slice(0, 1) || 'B' }}
      </div>
      <div class="profile-main">
        <span>Personal Center</span>
        <h1>{{ userStore.currentUser?.username || 'Bacon Mall 用户' }}</h1>
        <p>{{ userStore.currentUser?.email }} · {{ userStore.currentUser?.phone || '暂无手机号' }}</p>
      </div>
      <button type="button" @click="router.push('/orders')">查看我的订单</button>
    </section>

    <section class="profile-stats" aria-label="用户概览">
      <article>
        <span>订单总数</span>
        <strong>{{ orderStats.count }}</strong>
      </article>
      <article>
        <span>待付款</span>
        <strong>{{ orderStats.pending }}</strong>
      </article>
      <article>
        <span>已完成</span>
        <strong>{{ orderStats.completed }}</strong>
      </article>
      <article>
        <span>累计消费</span>
        <strong>¥{{ orderStats.spending.toFixed(2) }}</strong>
      </article>
    </section>

    <section class="profile-grid">
      <article class="profile-card behavior-card">
        <div class="card-head">
          <div>
            <span>Behavior</span>
            <h2>我的行为记录</h2>
          </div>
          <button type="button" :disabled="behaviorLogs.length === 0" @click="clearBehaviorLogs">清空记录</button>
        </div>

        <div class="behavior-summary">
          <span>浏览 {{ behaviorStats.views }}</span>
          <span>收藏 {{ behaviorStats.favorites }}</span>
          <span>加购 {{ behaviorStats.carts }}</span>
          <span>下单 {{ behaviorStats.orders }}</span>
        </div>

        <div v-if="recentLogs.length === 0" class="profile-empty">
          <h3>暂无行为记录</h3>
          <p>浏览商品、收藏、加购或下单后，这里会出现最近记录。</p>
        </div>

        <ul v-else class="behavior-list">
          <li v-for="log in recentLogs" :key="`${log.action}-${log.timestamp}`">
            <span>{{ actionText[log.action] || log.action }}</span>
            <strong>{{ log.productName || log.category || `订单 ¥${log.amount?.toFixed(2) || ''}` }}</strong>
            <time>{{ formatDate(log.timestamp) }}</time>
          </li>
        </ul>
      </article>

      <article class="profile-card preference-card">
        <div class="card-head">
          <div>
            <span>Preference</span>
            <h2>兴趣分类</h2>
          </div>
        </div>

        <div v-if="categoryPreference.length === 0" class="profile-empty">
          <h3>暂无偏好数据</h3>
          <p>多浏览几个商品后，这里会根据行为日志显示偏好分类。</p>
        </div>

        <div v-else class="preference-list">
          <div v-for="item in categoryPreference" :key="item.category" class="preference-item">
            <div>
              <strong>{{ item.category }}</strong>
              <span>{{ item.score }} 分</span>
            </div>
            <em>
              <i :style="{ width: `${item.percent}%` }"></i>
            </em>
          </div>
        </div>
      </article>
    </section>

    <section class="profile-card favorite-card">
      <div class="card-head">
        <div>
          <span>Favorites</span>
          <h2>最近收藏</h2>
        </div>
        <button type="button" @click="router.push('/products')">去逛商品</button>
      </div>

      <div v-if="favoriteProducts.length === 0" class="profile-empty">
        <h3>暂无收藏商品</h3>
        <p>在首页或商品列表点击“收藏”，这里会显示最近收藏的商品。</p>
      </div>

      <div v-else class="favorite-grid">
        <article
          v-for="product in favoriteProducts"
          :key="product.productId"
          class="favorite-item"
          @click="router.push(`/product/${product.productId}`)"
        >
          <img :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
          <div>
            <span>{{ product.category }}</span>
            <h3>{{ product.name }}</h3>
            <strong>¥{{ product.price.toFixed(2) }}</strong>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<style>
.profile-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.profile-toast {
  position: fixed;
  top: 92px;
  left: 50%;
  z-index: 20;
  transform: translateX(-50%);
  margin: 0;
  padding: 10px 18px;
  color: #fff;
  background: rgba(17, 24, 39, 0.88);
  border-radius: 999px;
  box-shadow: 0 12px 30px rgba(17, 24, 39, 0.18);
}

.profile-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 22px;
  align-items: center;
  padding: 30px;
  color: #fff;
  background:
    linear-gradient(120deg, rgba(17, 24, 39, 0.88), rgba(254, 44, 85, 0.66)),
    url('https://images.unsplash.com/photo-1556742031-c6961e8560b0?auto=format&fit=crop&w=1800&q=85') center/cover;
  border-radius: 16px;
}

.profile-avatar {
  display: grid;
  width: 78px;
  height: 78px;
  place-items: center;
  color: #241B2F;
  background: #fff;
  border-radius: 50%;
  font-size: 32px;
  font-weight: 900;
}

.profile-main span,
.card-head span {
  display: inline-flex;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.profile-main h1 {
  margin: 0;
  font-size: 34px;
}

.profile-main p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.82);
}

.profile-hero button,
.card-head button {
  border: 0;
  color: #241B2F;
  background: #fff;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 900;
  cursor: pointer;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 18px 0;
}

.profile-stats article,
.profile-card {
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
}

.profile-stats article {
  padding: 18px 20px;
}

.profile-stats span {
  display: block;
  color: #756D7E;
  font-size: 14px;
}

.profile-stats strong {
  display: block;
  margin-top: 8px;
  color: #241B2F;
  font-size: 26px;
  line-height: 1.1;
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 16px;
}

.profile-card {
  padding: 22px;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 18px;
}

.card-head span {
  color: #980B32;
}

.card-head h2 {
  margin: 0;
  color: #241B2F;
  font-size: 22px;
}

.card-head button {
  color: #374151;
  background: #f5f6f8;
}

.card-head button:disabled {
  color: #9ca3af;
  cursor: not-allowed;
}

.behavior-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.behavior-summary span {
  color: #374151;
  background: #f6f7f9;
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 800;
}

.behavior-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.behavior-list li {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 12px;
}

.behavior-list li span {
  color: #980B32;
  font-weight: 900;
}

.behavior-list li strong {
  overflow: hidden;
  color: #241B2F;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.behavior-list time {
  color: #9ca3af;
  font-size: 13px;
}

.preference-list {
  display: grid;
  gap: 16px;
}

.preference-item div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.preference-item strong {
  color: #241B2F;
}

.preference-item span {
  color: #756D7E;
  font-size: 13px;
}

.preference-item em {
  display: block;
  height: 10px;
  overflow: hidden;
  background: #E9E4EE;
  border-radius: 999px;
}

.preference-item i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #5A0B72, #241B2F);
  border-radius: inherit;
}

.favorite-card {
  margin-top: 16px;
}

.favorite-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.favorite-item {
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 14px;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.favorite-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(17, 24, 39, 0.08);
}

.favorite-item img {
  width: 96px;
  height: 96px;
  object-fit: cover;
  border-radius: 12px;
}

.favorite-item span {
  color: #980B32;
  font-size: 12px;
  font-weight: 900;
}

.favorite-item h3 {
  margin: 5px 0 8px;
  color: #241B2F;
  font-size: 16px;
  line-height: 1.35;
}

.favorite-item strong {
  color: #980B32;
  font-size: 18px;
}

.profile-empty {
  padding: 28px 18px;
  color: #756D7E;
  background: #fafafa;
  border-radius: 14px;
  text-align: center;
}

.profile-empty h3 {
  margin: 0 0 8px;
  color: #241B2F;
}

.profile-empty p {
  margin: 0;
}

@media (max-width: 960px) {
  .profile-page {
    padding: 16px 12px 40px;
  }

  .profile-hero {
    grid-template-columns: 1fr;
  }

  .profile-stats,
  .profile-grid,
  .favorite-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .profile-stats,
  .profile-grid,
  .favorite-grid {
    grid-template-columns: 1fr;
  }

  .behavior-list li {
    grid-template-columns: 1fr;
  }
}
</style>
