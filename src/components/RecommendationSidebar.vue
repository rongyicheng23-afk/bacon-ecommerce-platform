<script setup lang="ts">
import { ref } from 'vue'
import FeedbackModal from './FeedbackModal.vue'

const showFeedback = ref(false)

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <FeedbackModal v-model="showFeedback" />

  <div class="util-sidebar">
    <div class="util-items">
      <button type="button" class="util-btn" title="反馈" @click="showFeedback = true">
        <span class="util-icon">💬</span>
        <span class="util-label">反馈</span>
      </button>

      <button type="button" class="util-btn" title="客服">
        <span class="util-icon">🎧</span>
        <span class="util-label">客服</span>
      </button>

      <button type="button" class="util-btn" title="回到顶部" @click="scrollToTop">
        <span class="util-icon">⬆</span>
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
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.1);
  overflow: hidden;
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
  color: #777;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.util-btn:hover {
  background: #fdf2f4;
  color: #ff2f68;
}

.util-icon {
  font-size: 1.25rem;
  line-height: 1;
}

.util-label {
  font-size: 0.7rem;
  font-weight: 800;
  line-height: 1;
}

@media (max-width: 1350px) {
  .util-sidebar {
    display: none;
  }
}
</style>
