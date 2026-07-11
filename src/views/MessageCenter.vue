<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface Message {
  id: number
  title: string
  content: string
  time: string
  read: boolean
  type: 'system' | 'order' | 'promo' | 'recommend'
}

const messages = ref<Message[]>([])
const expandedId = ref<number | null>(null)
const filterType = ref<string>('all')

const typeConfig: Record<string, { icon: string; label: string }> = {
  system: { icon: '🔔', label: '系统通知' },
  order: { icon: '📦', label: '订单消息' },
  promo: { icon: '🎉', label: '促销活动' },
  recommend: { icon: '💡', label: '智能推荐' },
}

const loadMessages = () => {
  try {
    messages.value = JSON.parse(localStorage.getItem('messages') || '[]')
  } catch {
    messages.value = []
  }
  if (messages.value.length === 0) {
    messages.value = [
      { id: 1, title: '欢迎来到 Bacon Mall', content: '感谢您的注册！浏览商品、加入购物车，开启您的购物之旅吧。我们为您准备了丰富的商品和个性化的推荐服务。', time: new Date().toISOString(), read: false, type: 'system' },
      { id: 2, title: '今日特价提醒', content: '数码家电专场限时秒杀进行中，无线耳机、机械键盘低至 6 折起，数量有限先到先得。', time: new Date(Date.now() - 3600000).toISOString(), read: false, type: 'promo' },
      { id: 3, title: '您的订单已发货', content: '订单 #20260710001 已发货，预计 2-3 天送达，请注意查收。如有问题请联系客服。', time: new Date(Date.now() - 86400000).toISOString(), read: true, type: 'order' },
      { id: 4, title: '智能推荐已更新', content: '根据您的浏览记录，我们为您推荐了 3 款新商品。数码配件、家居好物等您发现。', time: new Date(Date.now() - 172800000).toISOString(), read: true, type: 'recommend' },
    ]
    localStorage.setItem('messages', JSON.stringify(messages.value))
  }
}

const toggleExpand = (id: number) => {
  expandedId.value = expandedId.value === id ? null : id
  const msg = messages.value.find((m) => m.id === id)
  if (msg && !msg.read) {
    msg.read = true
    localStorage.setItem('messages', JSON.stringify(messages.value))
  }
}

const deleteMsg = (id: number) => {
  messages.value = messages.value.filter((m) => m.id !== id)
  localStorage.setItem('messages', JSON.stringify(messages.value))
}

const markAllRead = () => {
  messages.value.forEach((m) => { m.read = true })
  localStorage.setItem('messages', JSON.stringify(messages.value))
}

const filteredMessages = () => {
  if (filterType.value === 'all') return messages.value
  if (filterType.value === 'unread') return messages.value.filter((m) => !m.read)
  return messages.value.filter((m) => m.type === filterType.value)
}

const unreadCount = () => messages.value.filter((m) => !m.read).length

const formatTime = (iso: string) => {
  const d = new Date(iso)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

onMounted(() => loadMessages())
</script>

<template>
  <div class="msg-page">
    <div class="msg-hero">
      <h1>🔔 消息中心</h1>
      <p v-if="unreadCount() > 0">您有 {{ unreadCount() }} 条未读消息</p>
      <p v-else>全部已读</p>
    </div>

    <div class="msg-toolbar">
      <div class="filter-tabs">
        <button :class="{ active: filterType === 'all' }" @click="filterType = 'all'">全部</button>
        <button :class="{ active: filterType === 'unread' }" @click="filterType = 'unread'">
          未读<span v-if="unreadCount() > 0" class="count">{{ unreadCount() }}</span>
        </button>
        <button :class="{ active: filterType === 'order' }" @click="filterType = 'order'">📦 订单</button>
        <button :class="{ active: filterType === 'promo' }" @click="filterType = 'promo'">🎉 促销</button>
        <button :class="{ active: filterType === 'recommend' }" @click="filterType = 'recommend'">💡 推荐</button>
        <button :class="{ active: filterType === 'system' }" @click="filterType = 'system'">🔔 系统</button>
      </div>
      <button v-if="unreadCount() > 0" class="mark-all-btn" @click="markAllRead">全部已读</button>
    </div>

    <div class="msg-list">
      <template v-if="filteredMessages().length > 0">
        <div
          v-for="msg in filteredMessages()"
          :key="msg.id"
          :class="['msg-card', { unread: !msg.read, expanded: expandedId === msg.id }]"
          @click="toggleExpand(msg.id)"
        >
          <div class="msg-head">
            <span class="msg-icon">{{ typeConfig[msg.type]?.icon }}</span>
            <div class="msg-info">
              <span class="msg-title">{{ msg.title }}</span>
              <span class="msg-meta">{{ typeConfig[msg.type]?.label }} · {{ formatTime(msg.time) }}</span>
            </div>
            <span v-if="!msg.read" class="msg-dot"></span>
            <button class="msg-delete" title="删除" @click.stop="deleteMsg(msg.id)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </div>
          <div v-if="expandedId === msg.id" class="msg-body">
            <p>{{ msg.content }}</p>
          </div>
        </div>
      </template>
      <div v-else class="msg-empty">
        <span>📭</span>
        <p>暂无此类消息</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.msg-page {
  max-width: 800px;
  margin: 0 auto;
}

.msg-hero {
  margin-bottom: 1.5rem;
}

.msg-hero h1 {
  margin: 0 0 0.25rem;
  color: #241B2F;
  font-size: 1.5rem;
}

.msg-hero p {
  margin: 0;
  color: #756D7E;
  font-size: 0.9rem;
}

.msg-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.filter-tabs button {
  min-height: 32px;
  padding: 0 0.8rem;
  border: 1px solid #948B9D;
  border-radius: 999px;
  background: #fff;
  color: #756D7E;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 700;
  transition: all 0.15s ease;
}

.filter-tabs button.active {
  border-color: #980B32;
  background: #F4EFF7;
  color: #980B32;
}

.filter-tabs button .count {
  margin-left: 4px;
  display: inline-grid;
  width: 18px;
  height: 18px;
  place-items: center;
  border-radius: 50%;
  background: #980B32;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 900;
}

.filter-tabs button.active .count {
  background: #980B32;
  color: #fff;
}

.mark-all-btn {
  min-height: 32px;
  padding: 0 1rem;
  border: 0;
  border-radius: 999px;
  background: #F4EFF7;
  color: #756D7E;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 700;
}

.mark-all-btn:hover {
  background: #e2e8f0;
  color: #241B2F;
}

.msg-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.msg-card {
  padding: 1rem 1.15rem;
  border: 1px solid #E9E4EE;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.msg-card:hover { background: #fafbfc; }
.msg-card.unread { background: #F4EFF7; border-color: #E9E4EE; }
.msg-card.expanded { background: #fff; border-color: #e2e8f0; }

.msg-head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.msg-icon { font-size: 1.4rem; flex-shrink: 0; }

.msg-info {
  flex: 1;
  min-width: 0;
}

.msg-title {
  display: block;
  color: #241B2F;
  font-size: 0.92rem;
  font-weight: 800;
}

.msg-meta {
  display: block;
  color: #948B9D;
  font-size: 0.74rem;
  margin-top: 2px;
}

.msg-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #980B32;
  flex-shrink: 0;
}

.msg-delete {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #948B9D;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.msg-delete svg {
  width: 16px;
  height: 16px;
}

.msg-delete:hover {
  background: #F4EFF7;
  color: #980B32;
}

.msg-body {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #E9E4EE;
}

.msg-body p {
  margin: 0;
  color: #756D7E;
  font-size: 0.88rem;
  line-height: 1.7;
}

.msg-empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #948B9D;
}
.msg-empty span { font-size: 2.5rem; }
.msg-empty p { margin: 0.5rem 0 0; font-size: 0.9rem; }
</style>
