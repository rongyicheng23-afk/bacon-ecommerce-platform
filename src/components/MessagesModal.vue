<script setup lang="ts">
import { ref } from 'vue'

const visible = defineModel<boolean>({ required: true })

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

const typeConfig: Record<string, { icon: string; label: string }> = {
  system: { icon: '🔔', label: '系统' },
  order: { icon: '📦', label: '订单' },
  promo: { icon: '🎉', label: '促销' },
  recommend: { icon: '💡', label: '推荐' },
}

const loadMessages = () => {
  try {
    messages.value = JSON.parse(localStorage.getItem('messages') || '[]')
  } catch {
    messages.value = []
  }

  // seed demo messages if empty
  if (messages.value.length === 0) {
    messages.value = [
      { id: 1, title: '欢迎来到 Bacon Mall', content: '感谢您的注册！浏览商品、加入购物车，开启您的购物之旅吧。', time: new Date().toISOString(), read: false, type: 'system' },
      { id: 2, title: '今日特价提醒', content: '数码家电专场限时秒杀进行中，无线耳机、机械键盘低至 6 折起。', time: new Date(Date.now() - 3600000).toISOString(), read: false, type: 'promo' },
      { id: 3, title: '您的订单已发货', content: '订单 #20260710001 已发货，预计 2-3 天送达，请注意查收。', time: new Date(Date.now() - 86400000).toISOString(), read: true, type: 'order' },
      { id: 4, title: '智能推荐已更新', content: '根据您的浏览记录，我们为您推荐了 3 款新商品，点击查看个性化推荐。', time: new Date(Date.now() - 172800000).toISOString(), read: true, type: 'recommend' },
    ]
    localStorage.setItem('messages', JSON.stringify(messages.value))
  }
}

const toggleExpand = (id: number) => {
  expandedId.value = expandedId.value === id ? null : id
  // mark as read
  const msg = messages.value.find((m) => m.id === id)
  if (msg && !msg.read) {
    msg.read = true
    localStorage.setItem('messages', JSON.stringify(messages.value))
  }
}

const unreadCount = () => messages.value.filter((m) => !m.read).length

const deleteMsg = (id: number) => {
  messages.value = messages.value.filter((m) => m.id !== id)
  localStorage.setItem('messages', JSON.stringify(messages.value))
}

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

const close = () => {
  visible.value = false
  expandedId.value = null
}

defineExpose({ open: () => { visible.value = true; loadMessages() } })
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="messages-overlay" @click.self="close">
        <div class="messages-modal">
          <div class="modal-header">
            <h2>
              🔔 消息中心
              <span v-if="unreadCount() > 0" class="unread-badge">{{ unreadCount() }}</span>
            </h2>
            <button type="button" class="modal-close" @click="close">✕</button>
          </div>

          <div class="modal-body">
            <template v-if="messages.length > 0">
              <div class="msg-list">
                <div
                  v-for="msg in messages"
                  :key="msg.id"
                  :class="['msg-item', { unread: !msg.read, expanded: expandedId === msg.id }]"
                  @click="toggleExpand(msg.id)"
                >
                  <div class="msg-head">
                    <span class="msg-icon">{{ typeConfig[msg.type]?.icon || '📌' }}</span>
                    <div class="msg-info">
                      <span class="msg-title">{{ msg.title }}</span>
                      <span class="msg-time">{{ formatTime(msg.time) }}</span>
                    </div>
                    <span v-if="!msg.read" class="msg-dot"></span>
                    <button type="button" class="msg-delete" title="删除" @click.stop="deleteMsg(msg.id)">🗑</button>
                  </div>
                  <div v-if="expandedId === msg.id" class="msg-body">
                    <p>{{ msg.content }}</p>
                    <span class="msg-type-tag">{{ typeConfig[msg.type]?.label }}</span>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="empty-msg">
                <span>📭</span>
                <p>暂无消息</p>
              </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.messages-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
}

.messages-modal {
  width: min(480px, calc(100vw - 40px));
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #E9E4EE;
}

.modal-header h2 {
  margin: 0;
  color: #241B2F;
  font-size: 1.15rem;
  font-weight: 900;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.unread-badge {
  display: inline-grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border-radius: 50%;
  background: #980B32;
  color: #fff;
  font-size: 0.72rem;
  font-weight: 900;
}

.modal-close {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: #F7F6FA;
  color: #999;
  cursor: pointer;
  font-size: 0.85rem;
}

.modal-close:hover {
  background: #F4EFF7;
  color: #980B32;
}

.modal-body {
  min-height: 240px;
}

.msg-list {
  display: flex;
  flex-direction: column;
}

.msg-item {
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid #E9E4EE;
  cursor: pointer;
  transition: background 0.15s ease;
}

.msg-item:hover {
  background: #fafbfc;
}

.msg-item.unread {
  background: #F4EFF7;
}

.msg-item.expanded {
  background: #fff;
}

.msg-head {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.msg-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
}

.msg-info {
  flex: 1;
  min-width: 0;
}

.msg-title {
  display: block;
  color: #241B2F;
  font-size: 0.9rem;
  font-weight: 800;
}

.msg-time {
  display: block;
  color: #948B9D;
  font-size: 0.72rem;
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
  width: 30px;
  height: 30px;
  place-items: center;
  border: 0;
  border-radius: 6px;
  background: transparent;
  font-size: 0.9rem;
  cursor: pointer;
  opacity: 0.4;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.msg-delete:hover {
  background: #F4EFF7;
  opacity: 1;
}

.msg-body {
  margin-top: 0.65rem;
  padding-top: 0.65rem;
  border-top: 1px solid #E9E4EE;
}

.msg-body p {
  margin: 0;
  color: #756D7E;
  font-size: 0.86rem;
  line-height: 1.6;
}

.msg-type-tag {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 2px 10px;
  border-radius: 999px;
  background: #F4EFF7;
  color: #756D7E;
  font-size: 0.7rem;
  font-weight: 800;
}

.empty-msg {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 240px;
  gap: 0.5rem;
  color: #948B9D;
}

.empty-msg span {
  font-size: 2.5rem;
}

.empty-msg p {
  margin: 0;
  font-size: 0.9rem;
}

/* modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-active .messages-modal,
.modal-leave-active .messages-modal {
  transition: transform 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .messages-modal {
  transform: scale(0.94) translateY(20px);
}

.modal-leave-to .messages-modal {
  transform: scale(0.94) translateY(20px);
}
</style>
