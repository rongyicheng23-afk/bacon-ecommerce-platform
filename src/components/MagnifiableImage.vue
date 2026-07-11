<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  src: string
  alt: string
  zoomScale?: number
}>()

const zoom = props.zoomScale ?? 3
const containerRef = ref<HTMLElement | null>(null)
const lensSize = 180

const showLens = ref(false)
const bgX = ref(0)
const bgY = ref(0)

const onEnter = () => {
  showLens.value = true
}

const onMove = (e: MouseEvent) => {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // percentage position in the image
  bgX.value = (x / rect.width) * 100
  bgY.value = (y / rect.height) * 100
}

const onLeave = () => {
  showLens.value = false
}
</script>

<template>
  <div
    ref="containerRef"
    class="magnifiable-wrap"
    @mouseenter="onEnter"
    @mousemove="onMove"
    @mouseleave="onLeave"
  >
    <div class="main-img-area">
      <img :src="src" :alt="alt" class="main-img" />
      <!-- cursor tracker dot -->
      <div
        v-if="showLens"
        class="cursor-tracker"
        :style="{
          left: `${bgX}%`,
          top: `${bgY}%`,
        }"
      ></div>
    </div>

    <!-- zoomed lens on the right -->
    <div v-if="showLens" class="zoom-panel">
      <div
        class="zoom-lens"
        :style="{
          width: `${lensSize}px`,
          height: `${lensSize}px`,
          backgroundImage: `url(${src})`,
          backgroundSize: `${zoom * 100}%`,
          backgroundPosition: `${bgX}% ${bgY}%`,
        }"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.magnifiable-wrap {
  position: relative;
  width: 100%;
  height: 100%;
}

.main-img-area {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: crosshair;
  overflow: hidden;
  border-radius: 12px;
  background: #f8fafc;
}

.main-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* cursor tracker */
.cursor-tracker {
  position: absolute;
  width: 40px;
  height: 40px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.15);
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 5;
}

/* zoom panel - positioned to the right, outside image */
.zoom-panel {
  position: absolute;
  top: 0;
  left: calc(100% + 16px);
  z-index: 20;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.2);
}

.zoom-lens {
  border-radius: 50%;
  border: 3px solid #fff;
  background-repeat: no-repeat;
  flex-shrink: 0;
  box-shadow: none;
}

@media (max-width: 1000px) {
  .zoom-panel {
    display: none;
  }
}
</style>
