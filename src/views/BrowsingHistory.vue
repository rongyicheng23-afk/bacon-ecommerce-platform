<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import api from '@/services/api'

interface BehaviorEntry {
  userId: number
  productId: number
  productName: string
  action: string
  category: string
  timestamp: string
}

const router = useRouter()
const productStore = useProductStore()
const logs = ref<BehaviorEntry[]>([])
const filterAction = ref<string>('all')
const todayStr = new Date().toISOString().slice(0, 10)

const readLogs = async () => {
  const response = await api.get<{ code: string; data: BehaviorEntry[] }>('/history')
  logs.value = response.data.data || []
}

const actionLabel: Record<string, string> = {
  view: '浏览', favorite: '收藏', unfavorite: '取消收藏',
  cart: '加购', buy: '购买', view_recommendation: '推荐点击'
}

const actionIcon: Record<string, string> = {
  view: '👁', favorite: '❤️', unfavorite: '💔',
  cart: '🛒', buy: '💰', view_recommendation: '🎯'
}

const filteredLogs = computed(() => {
  if (filterAction.value === 'all') return logs.value
  return logs.value.filter(l => l.action === filterAction.value)
})

/** 按日期分组 */
const groupedLogs = computed(() => {
  const groups: Record<string, BehaviorEntry[]> = {}
  filteredLogs.value.forEach(log => {
    const date = log.timestamp.slice(0, 10)
    if (!groups[date]) groups[date] = []
    groups[date].push(log)
  })
  // 按日期倒序
  return Object.entries(groups).sort((a, b) => b[0].localeCompare(a[0]))
})

const formatTime = (ts: string) => {
  return new Date(ts).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const dateLabel = (dateStr: string) => {
  if (dateStr === todayStr) return '今天'
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  if (dateStr === yesterday.toISOString().slice(0, 10)) return '昨天'
  return dateStr
}

const goProduct = (productId: number) => {
  router.push(`/product/${productId}`)
}

const clearLogs = async () => {
  if (confirm('确定要清空所有浏览记录吗？')) {
    await api.delete('/history')
    logs.value = []
  }
}

const handleImageError = (e: Event) => {
  (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=200&q=85'
}

onMounted(async () => {
  try { await readLogs() } catch { logs.value = [] }
  if (productStore.products.length === 0) {
    await productStore.fetchProducts()
  }
})
</script>

<template>
  <main class="history-page">
    <header class="history-hero">
      <div>
        <span>Browsing History</span>
        <h1>浏览足迹</h1>
        <p>记录你在平台的每一次浏览和互动，方便回访心仪的商品。</p>
      </div>
      <button v-if="logs.length > 0" type="button" class="clear-btn" @click="clearLogs">清空记录</button>
    </header>

    <nav class="history-filters" v-if="logs.length > 0">
      <button :class="{ active: filterAction === 'all' }" @click="filterAction = 'all'">全部</button>
      <button :class="{ active: filterAction === 'view' }" @click="filterAction = 'view'">👁 浏览</button>
      <button :class="{ active: filterAction === 'favorite' }" @click="filterAction = 'favorite'">❤️ 收藏</button>
      <button :class="{ active: filterAction === 'cart' }" @click="filterAction = 'cart'">🛒 加购</button>
      <button :class="{ active: filterAction === 'buy' }" @click="filterAction = 'buy'">💰 购买</button>
    </nav>

    <div v-if="groupedLogs.length === 0" class="history-empty">
      <p>📭 暂无浏览记录</p>
      <span>去首页逛逛，发现好商品吧！</span>
      <button type="button" @click="router.push('/')">去逛逛</button>
    </div>

    <section v-for="[date, items] in groupedLogs" :key="date" class="history-day">
      <h2>{{ dateLabel(date) }} <small>{{ items.length }} 条记录</small></h2>
      <div class="history-list">
        <article v-for="(log, idx) in items" :key="idx" class="history-item" @click="goProduct(log.productId)">
          <span class="history-icon">{{ actionIcon[log.action] || '📌' }}</span>
          <div class="history-info">
            <strong>{{ log.productName }}</strong>
            <small>{{ log.category }} · {{ actionLabel[log.action] || log.action }} · {{ formatTime(log.timestamp) }}</small>
          </div>
          <span class="history-arrow">→</span>
        </article>
      </div>
    </section>
  </main>
</template>

<style>
.history-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.history-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.history-hero span {
  display: inline-flex;
  margin-bottom: 4px;
  color: #fe2c55;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.history-hero h1 {
  margin: 0;
  color: #111827;
  font-size: 30px;
}

.history-hero p {
  margin: 6px 0 0;
  color: #6b7280;
}

.clear-btn {
  border: 1px solid #fee2e2;
  padding: 8px 16px;
  border-radius: 999px;
  background: #fff1f2;
  color: #dc2626;
  font-weight: 900;
  cursor: pointer;
  white-space: nowrap;
}

.history-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.history-filters button {
  padding: 6px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #fff;
  color: #555;
  font-weight: 800;
  cursor: pointer;
}

.history-filters button.active {
  border-color: #fe2c55;
  background: #fff1f2;
  color: #fe2c55;
}

.history-empty {
  padding: 60px 20px;
  text-align: center;
}

.history-empty p {
  margin: 0;
  color: #111827;
  font-size: 18px;
  font-weight: 800;
}

.history-empty span {
  display: block;
  margin: 8px 0 16px;
  color: #999;
}

.history-empty button {
  padding: 10px 28px;
  border: 0;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
}

.history-day {
  margin-bottom: 24px;
}

.history-day h2 {
  margin: 0 0 12px;
  color: #111827;
  font-size: 18px;
}

.history-day small {
  color: #999;
  font-weight: 400;
  font-size: 14px;
}

.history-list {
  display: grid;
  gap: 6px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid #f1f2f4;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
}

.history-item:hover {
  border-color: #fe2c55;
  background: #fffafb;
}

.history-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-info strong {
  display: block;
  color: #111827;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-info small {
  display: block;
  margin-top: 2px;
  color: #999;
  font-size: 12px;
}

.history-arrow {
  color: #ccc;
  font-size: 14px;
  flex-shrink: 0;
}

@media (max-width: 640px) {
  .history-page {
    padding: 16px 12px 40px;
  }

  .history-hero {
    flex-direction: column;
  }
}
</style>
