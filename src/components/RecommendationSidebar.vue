<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import FeedbackModal from './FeedbackModal.vue'

const router = useRouter()
const showFeedback = ref(false)
const posY = ref(0)
const dragging = ref(false)

let dragStartY = 0
let dragStartTop = 0
let hasMoved = false

const calcCenterY = () => Math.max(160, (window.innerHeight - 200) / 2 + 260)

const startDrag = (e: PointerEvent) => {
  e.preventDefault()
  dragging.value = true
  hasMoved = false
  dragStartY = e.clientY
  dragStartTop = posY.value || calcCenterY()
  document.addEventListener('pointermove', onDrag, { passive: false })
  document.addEventListener('pointerup', stopDrag)
}

const onDrag = (e: PointerEvent) => {
  if (!dragging.value) return
  const dy = e.clientY - dragStartY
  if (Math.abs(dy) > 3) hasMoved = true
  posY.value = Math.max(200, Math.min(dragStartTop + dy, window.innerHeight - 130))
}

const stopDrag = () => {
  dragging.value = false
  document.removeEventListener('pointermove', onDrag)
  document.removeEventListener('pointerup', stopDrag)
}

const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })
const goMessages = () => router.push('/messages')
const goCustomerService = () => router.push('/customer-service')

onMounted(() => { posY.value = calcCenterY() })
onBeforeUnmount(() => {
  document.removeEventListener('pointermove', onDrag)
  document.removeEventListener('pointerup', stopDrag)
})
</script>

<template>
  <FeedbackModal v-model="showFeedback" />

  <div
    :class="['util-sidebar', { dragging }]"
    :style="{ top: `${posY || calcCenterY()}px`, transition: dragging ? 'none' : 'top 0.3s ease' }"
    @pointerdown="startDrag"
  >
    <div class="util-items">
      <!-- 消息 -->
      <button type="button" class="util-btn" title="消息" @click="goMessages">
        <svg class="util-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <span class="util-label">消息</span>
      </button>

      <!-- 反馈 -->
      <button type="button" class="util-btn" title="反馈" @click="showFeedback = true">
        <svg class="util-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          <line x1="12" y1="8" x2="12" y2="13"/>
          <circle cx="12" cy="16" r="0.5" fill="currentColor" stroke="none"/>
        </svg>
        <span class="util-label">反馈</span>
      </button>

      <!-- 客服 -->
      <button type="button" class="util-btn" title="客服" @click="goCustomerService">
        <svg class="util-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 18v-6a9 9 0 0 1 18 0v6"/>
          <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>
        </svg>
        <span class="util-label">客服</span>
      </button>

      <!-- 顶部 -->
      <button type="button" class="util-btn" title="回到顶部" @click="scrollToTop">
        <svg class="util-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="18 15 12 9 6 15"/>
        </svg>
        <span class="util-label">顶部</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.util-sidebar {
  position: fixed;
  z-index: 80;
  right: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.1);
  overflow: hidden;
  cursor: grab;
  user-select: none;
  touch-action: none;
}

.util-sidebar.dragging {
  cursor: grabbing;
}

.util-items {
  display: flex;
  flex-direction: column;
  padding: 5px;
  gap: 3px;
}

.util-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 54px;
  min-height: 54px;
  padding: 8px 4px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #980B32;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.util-btn .util-label {
  color: #475569;
  transition: color 0.2s ease;
}

.util-btn:hover {
  background: #F4EFF7;
  color: #7E22CE;
  transform: scale(1.06);
}

.util-btn:hover .util-label {
  color: #7E22CE;
}

.util-svg {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.util-label {
  font-size: 0.7rem;
  font-weight: 800;
  line-height: 1;
}

@media (max-width: 1350px) {
  .util-sidebar { display: none; }
}
</style>
