<script setup lang="ts">
import { RouterView } from 'vue-router'
import TheHeader from './components/layout/TheHeader.vue'
import TheFooter from './components/layout/TheFooter.vue'
import FloatingAssistant from './components/FloatingAssistant.vue'
import RecommendationSidebar from './components/RecommendationSidebar.vue'
</script>

<template>
  <div class="app-wrapper">
    <TheHeader />
    <div class="content-wrapper">
      <RouterView />
    </div>
    <TheFooter />
    <FloatingAssistant />
    <RecommendationSidebar />
  </div>
</template>

<style>
.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  background: var(--page-bg);
  overflow-x: clip;
}

.content-wrapper {
  flex: 1;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 1.25rem 2rem 2rem;
}

@media (min-width: 768px) {
  .content-wrapper {
    padding: 1.5rem 3rem 2.5rem;
  }
}

@media (max-width: 640px) {
  .content-wrapper {
    padding: 1rem 1.25rem 1.5rem;
  }
}
</style>
