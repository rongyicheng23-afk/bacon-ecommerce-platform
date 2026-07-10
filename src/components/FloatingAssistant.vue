<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'

const router = useRouter()
const productStore = useProductStore()
const isOpen = ref(false)
const activeSuggestion = ref('')

/* ---- falling particles on double-click ---- */
interface Particle {
  id: number
  emoji: string
  x: number  // horizontal offset px
  delay: number
}
const particles = ref<Particle[]>([])
let particleId = 0
let lastClickTime = 0

const EMOJIS = ['🖱️', '🎧', '🎒', '💡', '🛍️', '❤️', '🧸']

const spawnParticles = () => {
  const now = Date.now()
  if (now - lastClickTime < 350) {
    // double click detected
    const newParticles: Particle[] = []
    for (let i = 0; i < 14; i++) {
      newParticles.push({
        id: ++particleId,
        emoji: EMOJIS[Math.floor(Math.random() * EMOJIS.length)],
        x: (Math.random() - 0.5) * 120,
        delay: Math.random() * 0.25,
      })
    }
    particles.value = [...particles.value, ...newParticles]

    // remove after 1.2s
    setTimeout(() => {
      particles.value = particles.value.filter((p) => !newParticles.includes(p))
    }, 1200)
  }
  lastClickTime = now
}

/* ---- drag & snap state ---- */
const SNAP_GAP = 24 // px from edge when snapped
const TRIGGER_SIZE = 48

// read persisted side preference
const storedSide = (() => {
  try { return localStorage.getItem('assistant_side') } catch { return null }
})()
const side = ref<'left' | 'right'>(storedSide === 'right' ? 'right' : 'left')
const posX = ref(0) // current x (px from left edge of trigger)
const posY = ref(0) // current y (px from top of trigger)
const dragging = ref(false)

let dragStartX = 0
let dragStartY = 0
let dragStartLeft = 0
let dragStartTop = 0
let hasMoved = false

const calcCenterY = (): number => Math.max(80, (window.innerHeight - TRIGGER_SIZE) / 2)

const centerY = () => {
  posY.value = calcCenterY()
}

const assistantStyle = computed(() => {
  const top = posY.value || calcCenterY()
  const transition = dragging.value
    ? 'none'
    : 'left 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), right 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), top 0.35s ease'

  if (dragging.value) {
    return {
      left: `${posX.value}px`,
      right: 'auto',
      top: `${top}px`,
      transform: 'none',
      transition: 'none',
    }
  }

  // snapped state: position from the snapped side
  if (side.value === 'right') {
    return {
      left: 'auto',
      right: `${SNAP_GAP}px`,
      top: `${top}px`,
      transform: 'none',
      transition,
    }
  }

  return {
    left: `${SNAP_GAP}px`,
    right: 'auto',
    top: `${top}px`,
    transform: 'none',
    transition,
  }
})

/* ---- drag handlers ---- */
const startDrag = (e: PointerEvent) => {
  if ((e.target as HTMLElement).closest('.bubble')) return
  e.preventDefault()
  dragging.value = true
  hasMoved = false
  dragStartX = e.clientX
  dragStartY = e.clientY
  dragStartLeft = posX.value
  dragStartTop = posY.value

  document.addEventListener('pointermove', onDrag, { passive: false })
  document.addEventListener('pointerup', stopDrag)
}

const onDrag = (e: PointerEvent) => {
  if (!dragging.value) return
  const dx = e.clientX - dragStartX
  const dy = e.clientY - dragStartY
  if (Math.abs(dx) > 2 || Math.abs(dy) > 2) hasMoved = true

  posX.value = Math.max(0, Math.min(dragStartLeft + dx, window.innerWidth - TRIGGER_SIZE))
  posY.value = Math.max(80, Math.min(dragStartTop + dy, window.innerHeight - TRIGGER_SIZE))
}

const stopDrag = () => {
  if (!dragging.value) return
  dragging.value = false

  document.removeEventListener('pointermove', onDrag)
  document.removeEventListener('pointerup', stopDrag)

  // snap to nearest side: if centre is past 40% of screen → right
  const triggerCenter = posX.value + TRIGGER_SIZE / 2
  const newSide: 'left' | 'right' = triggerCenter > window.innerWidth * 0.4 ? 'right' : 'left'

  side.value = newSide
  try { localStorage.setItem('assistant_side', newSide) } catch { /* noop */ }

  // update posX to reflect actual position from left edge
  if (newSide === 'right') {
    posX.value = window.innerWidth - TRIGGER_SIZE - SNAP_GAP
  } else {
    posX.value = SNAP_GAP
  }

  if (!hasMoved) {
    isOpen.value = !isOpen.value
  }
}

onBeforeUnmount(() => {
  document.removeEventListener('pointermove', onDrag)
  document.removeEventListener('pointerup', stopDrag)
})

/* ---- init ---- */
onMounted(() => {
  if (side.value === 'right') {
    posX.value = window.innerWidth - TRIGGER_SIZE - SNAP_GAP
  } else {
    posX.value = SNAP_GAP
  }
  posY.value = calcCenterY()
  window.addEventListener('resize', centerY)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', centerY)
})

/* ---- suggestions ---- */
const products = computed(() => productStore.products)

const suggestions = computed(() => {
  if (products.value.length === 0) return []

  const categories = [...new Set(products.value.map((p) => p.category || '精选'))]
  const randomCategory = categories[Math.floor(Math.random() * categories.length)]

  const hotCount = products.value.filter((p) => p.stock < 50).length
  const randomProducts = [...products.value].sort(() => Math.random() - 0.5).slice(0, 3)

  return [
    { label: `猜你喜欢${randomCategory}？`, action: 'category', payload: randomCategory },
    { label: `今日热卖榜（${hotCount}件热卖）`, action: 'hot' },
    { label: `为你挑 3 件`, action: 'pick', payload: randomProducts },
    { label: '换一批推荐', action: 'refresh' },
  ]
})

const handleSuggestion = (suggestion: (typeof suggestions.value)[number]) => {
  if (suggestion.action === 'category') {
    router.push({ path: '/products', query: { category: suggestion.payload as string } })
  } else if (suggestion.action === 'hot') {
    router.push({ path: '/products', query: { sort: 'stock-desc' } })
  } else if (suggestion.action === 'pick') {
    const list = suggestion.payload as Array<{ productId: number }>
    if (list.length > 0) {
      router.push(`/product/${list[0].productId}`)
    }
  } else if (suggestion.action === 'refresh') {
    activeSuggestion.value = '已为你刷新推荐 ✨'
    setTimeout(() => (activeSuggestion.value = ''), 1500)
  }

  isOpen.value = false
}
</script>

<template>
  <Teleport to="body">
    <div
      :class="['floating-assistant', side, { open: isOpen, dragging }]"
      :style="assistantStyle"
    >
    <div v-if="isOpen" class="assistant-bubbles">
      <button
        v-for="(item, index) in suggestions"
        :key="index"
        type="button"
        class="bubble"
        :style="{ animationDelay: `${index * 0.06}s` }"
        @click="handleSuggestion(item)"
      >
        {{ item.label }}
      </button>
    </div>

    <button
      type="button"
      class="assistant-trigger"
      :title="isOpen ? '关闭助手' : 'Bacon 推荐官 · 可拖拽'"
      @pointerdown="spawnParticles(); startDrag($event)"
    >
      <span class="trigger-mark">B</span>
      <span class="trigger-pulse"></span>
    </button>

    <!-- falling particles -->
    <span
      v-for="p in particles"
      :key="p.id"
      class="falling-particle"
      :style="{
        '--dx': `${p.x}px`,
        '--origin-x': `${posX + TRIGGER_SIZE / 2}px`,
        '--origin-y': `${posY}px`,
        animationDelay: `${p.delay}s`,
      }"
    >{{ p.emoji }}</span>

    <Transition name="tooltip">
      <span v-if="activeSuggestion" class="mini-tooltip">{{ activeSuggestion }}</span>
    </Transition>
    </div>
  </Teleport>
</template>

<style scoped>
.floating-assistant {
  position: fixed;
  z-index: 110;
  display: flex;
  flex-direction: column-reverse;
  align-items: flex-start;
  gap: 10px;
  user-select: none;
}

/* ---- bubbles face outward from the side ---- */
.floating-assistant.right {
  align-items: flex-end;
}

.floating-assistant.right .bubble:hover {
  transform: translateX(-6px);
}

@keyframes bubble-in-left {
  from { opacity: 0; transform: translateX(-12px); }
  to   { opacity: 1; transform: translateX(0); }
}

@keyframes bubble-in-right {
  from { opacity: 0; transform: translateX(12px); }
  to   { opacity: 1; transform: translateX(0); }
}

.floating-assistant.left  .bubble { animation-name: bubble-in-left; }
.floating-assistant.right .bubble { animation-name: bubble-in-right; }

/* ---- trigger button ---- */
.assistant-trigger {
  position: relative;
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff2f68, #0f172a);
  color: #fff;
  cursor: grab;
  box-shadow: 0 8px 28px rgba(254, 44, 85, 0.3);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  touch-action: none;
}

.floating-assistant.dragging .assistant-trigger {
  cursor: grabbing;
  transform: scale(1.12);
  box-shadow: 0 14px 40px rgba(254, 44, 85, 0.45);
}

.assistant-trigger:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 36px rgba(254, 44, 85, 0.42);
}

.floating-assistant.dragging .assistant-trigger:hover {
  transform: scale(1.12);
}

.trigger-mark {
  font-size: 1.25rem;
  font-weight: 900;
  line-height: 1;
  pointer-events: none;
}

.trigger-pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid rgba(254, 44, 85, 0.45);
  animation: assistant-pulse 2.4s ease-in-out infinite;
  pointer-events: none;
}

@keyframes assistant-pulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50%      { transform: scale(1.18); opacity: 0; }
}

/* ---- falling particles ---- */
.falling-particle {
  position: fixed;
  z-index: 111;
  top: var(--origin-y, 50%);
  left: var(--origin-x, 50%);
  font-size: 1.4rem;
  pointer-events: none;
  animation: particle-drop 1s ease-out both;
}

@keyframes particle-drop {
  0% {
    opacity: 1;
    transform: translate(0, 0) rotate(0deg) scale(0.6);
  }
  20% {
    opacity: 1;
    transform: translate(var(--dx), 20px) rotate(60deg) scale(1.1);
  }
  100% {
    opacity: 0;
    transform: translate(var(--dx), 260px) rotate(400deg) scale(0.3);
  }
}

/* ---- bubbles ---- */
.assistant-bubbles {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 4px;
}

.bubble {
  min-height: 36px;
  padding: 0 1rem;
  border: 1px solid rgba(254, 44, 85, 0.18);
  border-radius: 18px;
  background: #fff;
  color: #333;
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 700;
  white-space: nowrap;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.1);
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
  animation: bubble-in-left 0.35s ease both;
}

.bubble:hover {
  transform: translateX(6px);
  background: #fff5f7;
  border-color: #ff2f68;
  color: #ff2f68;
}

.mini-tooltip {
  position: absolute;
  bottom: 12px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.88);
  color: #fff;
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
  pointer-events: none;
}

.floating-assistant.left  .mini-tooltip { left: 60px; }
.floating-assistant.right .mini-tooltip { right: 60px; left: auto; }

.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

@media (max-width: 767px) {
  .assistant-trigger {
    width: 42px;
    height: 42px;
  }

  .bubble {
    font-size: 0.78rem;
    min-height: 32px;
    padding: 0 0.85rem;
  }
}
</style>
