<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '../stores/productStore'
import type { Product } from '../types'
import { addProductToCart } from '@/utils/cart'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'
import { getPersonalizedProducts, getRecommendationSummary } from '@/utils/recommendation'

type BehaviorAction = 'view' | 'favorite' | 'unfavorite' | 'cart' | 'buy'

const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const error = ref<string | null>(null)
const actionMessage = ref('')
const activeSlide = ref(0)
const favoriteIds = ref<number[]>([])
let slideTimer: number | undefined

const products = computed(() => productStore.products)
const bannerProducts = computed(() => products.value.slice(0, 3))
const promoProducts = computed(() => products.value.slice(3, 5))
const hotProducts = computed(() => products.value.slice(8, 16))
const feedProducts = computed(() => getPersonalizedProducts(products.value, 40))
const recommendationSummary = computed(() => getRecommendationSummary())
const channelCards: Array<{ title: string; subtitle: string; query: Record<string, string> }> = [
  { title: '今日特价', subtitle: '限时好价', query: { sort: 'price-asc' } },
  { title: '热卖榜单', subtitle: '高关注商品', query: { sort: 'stock-desc' } },
  { title: '新品首发', subtitle: '新鲜上架', query: { category: '数码' } },
  { title: '品质生活', subtitle: '家居优选', query: { category: '家居' } }
]
const serviceCards = ['正品保障', '快速配送', '售后无忧', '安全支付']
const categoryLinks = computed(() => {
  const categoryMap = products.value.reduce<Record<string, number>>((map, product) => {
    const category = product.category || '精选'
    map[category] = (map[category] || 0) + 1
    return map
  }, {})

  return Object.entries(categoryMap).slice(0, 6).map(([name, count], index) => ({
    name,
    count,
    tone: `tone-${index % 4}`
  }))
})

const actionText: Record<BehaviorAction, string> = {
  view: '浏览',
  favorite: '收藏',
  unfavorite: '取消收藏',
  cart: '加购',
  buy: '购买'
}

const readBehaviorLogs = () => {
  try {
    return JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  } catch {
    return []
  }
}

const recordBehavior = (product: Product, action: BehaviorAction) => {
  const logs = readBehaviorLogs()
  logs.push({
    userId: 1,
    productId: product.productId,
    productName: product.name,
    action,
    category: product.category || '未分类',
    timestamp: new Date().toISOString()
  })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}

const recordProductAction = (product: Product, action: Exclude<BehaviorAction, 'view'>) => {
  recordBehavior(product, action)
  actionMessage.value = `已${actionText[action]}《${product.name}》`
}

const isFavorite = (productId: number) => {
  return favoriteIds.value.includes(productId)
}

const toggleFavorite = (product: Product) => {
  const wasFavorite = isFavorite(product.productId)
  favoriteIds.value = toggleFavoriteId(product.productId)
  recordProductAction(product, wasFavorite ? 'unfavorite' : 'favorite')
}

const addToCart = (product: Product) => {
  addProductToCart(product)
  recordProductAction(product, 'cart')
}

const navigateToDetail = (product: Product) => {
  recordBehavior(product, 'view')
  router.push(`/product/${product.productId}`)
}

const switchSlide = (index: number) => {
  activeSlide.value = index
}

const prevSlide = () => {
  if (bannerProducts.value.length === 0) return
  activeSlide.value = (activeSlide.value - 1 + bannerProducts.value.length) % bannerProducts.value.length
}

const nextSlide = () => {
  if (bannerProducts.value.length === 0) return
  activeSlide.value = (activeSlide.value + 1) % bannerProducts.value.length
}

const browseChannel = (query: Record<string, string>) => {
  router.push({
    path: '/products',
    query
  })
}

const browseCategory = (category: string) => {
  router.push({
    path: '/products',
    query: { category }
  })
}

const getProductTags = (product: Product): Array<{ text: string; type: string }> => {
  const tags: Array<{ text: string; type: string }> = []
  if (product.stock < 50) tags.push({ text: '热卖', type: 'hot' })
  if (product.price < 100) tags.push({ text: '超值', type: 'value' })
  if (product.price >= 200) tags.push({ text: '满199减20', type: 'discount' })
  if (product.stock < 20) tags.push({ text: '库存紧张', type: 'urgent' })
  if (product.productId % 7 === 0) tags.push({ text: '新品', type: 'new' })
  return tags.slice(0, 2)
}

interface FlashProduct extends Product {
  flashPrice: number
  soldPercent: number
}

const flashSaleProducts = computed<FlashProduct[]>(() => {
  return products.value
    .filter((p) => p.price >= 80 && p.price <= 250)
    .slice(0, 4)
    .map((p, index) => ({
      ...p,
      flashPrice: Math.round(p.price * [0.65, 0.72, 0.78, 0.68][index]),
      soldPercent: [72, 88, 55, 91][index],
    }))
})

const flashCountdown = ref({ hours: 3, minutes: 27, seconds: 44 })
let countdownTimer: number | undefined

const startCountdown = () => {
  countdownTimer = window.setInterval(() => {
    if (flashCountdown.value.seconds > 0) {
      flashCountdown.value.seconds--
    } else if (flashCountdown.value.minutes > 0) {
      flashCountdown.value.minutes--
      flashCountdown.value.seconds = 59
    } else if (flashCountdown.value.hours > 0) {
      flashCountdown.value.hours--
      flashCountdown.value.minutes = 59
      flashCountdown.value.seconds = 59
    } else {
      flashCountdown.value = { hours: 23, minutes: 59, seconds: 59 }
    }
  }, 1000)
}

const padTime = (v: number) => String(v).padStart(2, '0')

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

onMounted(async () => {
  favoriteIds.value = readFavoriteIds()

  try {
    await productStore.fetchProducts()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载商品失败'
  } finally {
    loading.value = false
  }

  slideTimer = window.setInterval(() => {
    if (bannerProducts.value.length === 0) return
    activeSlide.value = (activeSlide.value + 1) % bannerProducts.value.length
  }, 4200)

  startCountdown()
})

onUnmounted(() => {
  if (slideTimer) {
    window.clearInterval(slideTimer)
  }
  if (countdownTimer) {
    window.clearInterval(countdownTimer)
  }
})
</script>

<template>
  <main class="home-page">
    <p v-if="actionMessage" class="action-toast">{{ actionMessage }}</p>

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <template v-else>
      <section class="home-hero-grid">
        <section v-if="bannerProducts.length" class="hero-carousel" aria-label="热门活动">
          <article
            v-for="(product, index) in bannerProducts"
            :key="`banner-${product.productId}`"
            :class="['hero-slide', { active: index === activeSlide }]"
            @click="navigateToDetail(product)"
          >
            <img :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
            <div class="hero-content">
              <span>{{ product.category || '精选' }} · 今日热卖</span>
              <h1>{{ product.name }}</h1>
              <p>{{ product.description }}</p>
              <div class="hero-bottom">
                <strong>¥{{ product.price }} 起</strong>
                <button type="button">立即查看</button>
              </div>
            </div>
          </article>

          <button
            type="button"
            class="hero-arrow hero-arrow-left"
            aria-label="上一张"
            @click.stop="prevSlide"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <button
            type="button"
            class="hero-arrow hero-arrow-right"
            aria-label="下一张"
            @click.stop="nextSlide"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>

          <div class="hero-dots" aria-label="切换活动">
            <button
              v-for="(_, index) in bannerProducts"
              :key="`dot-${index}`"
              type="button"
              :class="{ active: index === activeSlide }"
              :aria-label="`切换到第 ${index + 1} 张`"
              @click.stop="switchSlide(index)"
            />
          </div>
        </section>

        <aside class="promo-stack" aria-label="活动推荐">
          <article
            v-for="product in promoProducts"
            :key="`promo-${product.productId}`"
            class="promo-card"
            @click="navigateToDetail(product)"
          >
            <img :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
            <div>
              <span>{{ product.category || '精选' }}</span>
              <strong>{{ product.name }}</strong>
              <small>¥{{ product.price }} 起</small>
            </div>
          </article>
        </aside>
      </section>

      <section class="channel-section" aria-label="频道入口">
        <button
          v-for="channel in channelCards"
          :key="channel.title"
          type="button"
          class="channel-card"
          @click="browseChannel(channel.query)"
        >
          <strong>{{ channel.title }}</strong>
          <span>{{ channel.subtitle }}</span>
        </button>
      </section>

      <section v-if="flashSaleProducts.length" class="flash-section" aria-labelledby="flash-title">
        <div class="flash-header">
          <div class="flash-title-row">
            <span class="flash-badge">限时秒杀</span>
            <h2 id="flash-title">品牌闪购</h2>
            <div class="flash-countdown">
              <span>{{ padTime(flashCountdown.hours) }}</span>
              <em>:</em>
              <span>{{ padTime(flashCountdown.minutes) }}</span>
              <em>:</em>
              <span>{{ padTime(flashCountdown.seconds) }}</span>
            </div>
          </div>
          <button type="button" class="more-link" @click="router.push('/products?sort=price-asc')">
            查看更多闪购
          </button>
        </div>

        <div class="flash-row">
          <article
            v-for="product in flashSaleProducts"
            :key="`flash-${product.productId}`"
            class="flash-card"
            @click="navigateToDetail(product)"
          >
            <div class="flash-image">
              <img :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
              <span class="flash-discount-tag">{{ Math.round(((product.price - product.flashPrice) / product.price) * 100) }}% OFF</span>
            </div>
            <div class="flash-info">
              <div class="flash-price-row">
                <strong>¥{{ product.flashPrice }}</strong>
                <del>¥{{ product.price }}</del>
              </div>
              <p>{{ product.name }}</p>
              <div class="flash-progress">
                <div class="flash-bar">
                  <i :style="{ width: `${product.soldPercent}%` }"></i>
                </div>
                <small>已抢 {{ product.soldPercent }}%</small>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="service-strip" aria-label="平台服务">
        <span v-for="service in serviceCards" :key="service">{{ service }}</span>
      </section>

      <section class="category-section" aria-labelledby="category-title">
        <div class="section-title">
          <div>
            <span class="section-kicker">Shop by category</span>
            <h2 id="category-title">精选分类</h2>
          </div>
          <button type="button" class="more-link" @click="router.push('/products')">进入商品库</button>
        </div>

        <div class="category-grid">
          <button
            v-for="category in categoryLinks"
            :key="category.name"
            type="button"
            :class="['category-tile', category.tone]"
            @click="browseCategory(category.name)"
          >
            <span class="category-mark">{{ category.name.slice(0, 1) }}</span>
            <strong>{{ category.name }}</strong>
            <small>{{ category.count }} 件好物</small>
          </button>
        </div>
      </section>

      <section class="hot-section" aria-labelledby="hot-title">
        <div class="section-title">
          <div>
            <span class="section-kicker">Trending now</span>
            <h2 id="hot-title">热卖单品</h2>
          </div>
          <span>近期关注度较高</span>
        </div>

        <div class="hot-row">
          <article
            v-for="product in hotProducts"
            :key="`hot-${product.productId}`"
            class="hot-card"
            @click="navigateToDetail(product)"
          >
            <div class="hot-image">
              <img :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
              <div v-if="getProductTags(product).length" class="card-tags">
                <span
                  v-for="tag in getProductTags(product)"
                  :key="tag.text"
                  :class="['card-tag', `tag-${tag.type}`]"
                >{{ tag.text }}</span>
              </div>
            </div>
            <div class="hot-info">
              <span>{{ product.category || '精选' }}</span>
              <h3>{{ product.name }}</h3>
              <strong>¥{{ product.price }}</strong>
            </div>
          </article>
        </div>
      </section>

      <section class="feed-section" aria-labelledby="feed-title">
        <div class="section-title">
          <div>
            <span class="section-kicker">For you</span>
            <h2 id="feed-title">为你精选</h2>
            <p v-if="recommendationSummary.length" class="recommendation-hint">
              最近偏好：
              <span v-for="item in recommendationSummary" :key="item.category">{{ item.category }}</span>
            </p>
          </div>
          <button type="button" class="more-link" @click="router.push('/products')">查看更多</button>
        </div>

        <div class="waterfall-feed">
          <article
            v-for="product in feedProducts"
            :key="`feed-${product.productId}`"
            class="feed-card"
            @click="navigateToDetail(product)"
          >
            <div class="feed-image">
              <img :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
              <div v-if="getProductTags(product).length" class="card-tags">
                <span
                  v-for="tag in getProductTags(product)"
                  :key="tag.text"
                  :class="['card-tag', `tag-${tag.type}`]"
                >{{ tag.text }}</span>
              </div>
            </div>
            <div class="feed-info">
              <span class="category">{{ product.category || '精选' }}</span>
              <h3>{{ product.name }}</h3>
              <p>{{ product.description }}</p>
              <div class="feed-footer">
                <strong>¥{{ product.price }}</strong>
                <div class="feed-actions" @click.stop>
                  <button
                    type="button"
                    :class="{ active: isFavorite(product.productId) }"
                    @click="toggleFavorite(product)"
                  >
                    {{ isFavorite(product.productId) ? '已收藏' : '收藏' }}
                  </button>
                  <button type="button" @click="addToCart(product)">加购</button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </template>
  </main>
</template>

<style scoped>
.home-page {
  width: 100%;
  padding-bottom: 1rem;
}

.action-toast {
  position: fixed;
  z-index: 120;
  right: 2rem;
  top: 5.5rem;
  max-width: min(360px, calc(100vw - 2rem));
  padding: 0.75rem 1rem;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.92);
  color: #fff;
  font-size: 0.875rem;
  box-shadow: 0 12px 30px rgba(17, 24, 39, 0.2);
}

.home-hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 1rem;
  align-items: stretch;
  margin-bottom: 1.25rem;
}

.promo-stack,
.channel-section,
.service-strip {
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.hero-carousel {
  position: relative;
  min-height: 360px;
  overflow: hidden;
  border-radius: 18px;
  background: #111827;
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.18);
}

.hero-slide {
  position: absolute;
  inset: 0;
  cursor: pointer;
  opacity: 0;
  transform: scale(1.02);
  transition: opacity 0.5s ease, transform 0.8s ease;
}

.hero-slide.active {
  z-index: 1;
  opacity: 1;
  transform: scale(1);
}

.hero-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-slide::after {
  position: absolute;
  inset: 0;
  content: '';
  background: linear-gradient(90deg, rgba(17, 24, 39, 0.82), rgba(17, 24, 39, 0.34), rgba(17, 24, 39, 0.08));
}

.hero-content {
  position: absolute;
  z-index: 2;
  left: clamp(1.5rem, 5vw, 4.5rem);
  bottom: clamp(1.75rem, 5vw, 4rem);
  max-width: 560px;
  color: #fff;
}

.hero-content span {
  display: inline-block;
  margin-bottom: 0.875rem;
  padding: 0.35rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.32);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  font-size: 0.875rem;
  font-weight: 700;
}

.hero-content h1 {
  margin: 0 0 0.75rem;
  font-size: clamp(2rem, 4vw, 3.6rem);
  line-height: 1.08;
}

.hero-content p {
  max-width: 460px;
  margin: 0 0 1.25rem;
  color: rgba(255, 255, 255, 0.86);
  line-height: 1.7;
}

.hero-bottom {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.hero-bottom strong {
  font-size: 1.5rem;
}

.hero-bottom button {
  min-height: 2.75rem;
  padding: 0 1.25rem;
  border: 0;
  border-radius: 999px;
  background: #fff;
  color: #111827;
  cursor: pointer;
  font-weight: 800;
}

.hero-dots {
  position: absolute;
  z-index: 3;
  right: 2rem;
  bottom: 2rem;
  display: flex;
  gap: 0.5rem;
}

.hero-dots button {
  width: 2.25rem;
  height: 0.4rem;
  padding: 0;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.45);
  cursor: pointer;
}

.hero-dots button.active {
  background: #fff;
}

.hero-arrow {
  position: absolute;
  z-index: 5;
  top: 50%;
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(6px);
  color: #fff;
  cursor: pointer;
  opacity: 0;
  transform: translateY(-50%);
  transition: opacity 0.3s ease, background 0.2s ease;
}

.hero-arrow:hover {
  background: rgba(255, 255, 255, 0.32);
}

.hero-arrow svg {
  width: 22px;
  height: 22px;
}

.hero-arrow-left { left: 1rem; }
.hero-arrow-right { right: 1rem; }

.hero-carousel:hover .hero-arrow {
  opacity: 1;
}

.promo-stack {
  display: grid;
  gap: 0.85rem;
  min-height: 360px;
  padding: 0.85rem;
}

.promo-card {
  position: relative;
  overflow: hidden;
  min-height: 0;
  border-radius: 12px;
  background: #111827;
  cursor: pointer;
}

.promo-card img {
  width: 100%;
  height: 100%;
  min-height: 150px;
  object-fit: cover;
  opacity: 0.78;
  transition: transform 0.35s ease;
}

.promo-card:hover img {
  transform: scale(1.04);
}

.promo-card div {
  position: absolute;
  right: 0.85rem;
  bottom: 0.85rem;
  left: 0.85rem;
  color: #fff;
}

.promo-card span,
.promo-card strong,
.promo-card small {
  display: block;
}

.promo-card span {
  font-size: 0.75rem;
  font-weight: 800;
}

.promo-card strong {
  display: -webkit-box;
  margin: 0.25rem 0;
  overflow: hidden;
  font-size: 1rem;
  line-height: 1.35;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.promo-card small {
  color: rgba(255, 255, 255, 0.82);
  font-size: 0.82rem;
}

.channel-section {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.85rem;
}

.channel-card {
  min-height: 82px;
  padding: 1rem;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, #fff7f9, #fff);
  color: #111827;
  cursor: pointer;
  text-align: left;
}

.channel-card:hover {
  background: #fff2f5;
}

.channel-card strong,
.channel-card span {
  display: block;
}

.channel-card strong {
  margin-bottom: 0.3rem;
  font-size: 1.05rem;
}

.channel-card span {
  color: #6b7280;
  font-size: 0.84rem;
}

.flash-section {
  margin-bottom: 1.25rem;
  padding: 1rem;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: linear-gradient(135deg, #fff5f5, #fff);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.flash-header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
  margin-bottom: 1rem;
}

.flash-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.flash-badge {
  padding: 4px 12px;
  border-radius: 4px;
  background: linear-gradient(135deg, #fe2c55, #ff4757);
  color: #fff;
  font-size: 13px;
  font-weight: 900;
}

.flash-title-row h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #111827;
}

.flash-countdown {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-left: 0.5rem;
}

.flash-countdown span {
  display: inline-grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 4px;
  background: #111827;
  color: #fff;
  font-size: 14px;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
}

.flash-countdown em {
  color: #111827;
  font-style: normal;
  font-weight: 900;
  margin: 0 1px;
}

.flash-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.flash-card {
  overflow: hidden;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.flash-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.1);
}

.flash-image {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: #f7f8fa;
}

.flash-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.flash-discount-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(254, 44, 85, 0.92);
  color: #fff;
  font-size: 11px;
  font-weight: 900;
}

.flash-info {
  padding: 0.75rem;
}

.flash-price-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}

.flash-price-row strong {
  color: #fe2c55;
  font-size: 1.25rem;
  font-weight: 900;
}

.flash-price-row del {
  color: #9ca3af;
  font-size: 0.82rem;
}

.flash-info > p {
  display: -webkit-box;
  margin: 0 0 0.5rem;
  overflow: hidden;
  color: #111827;
  font-size: 0.88rem;
  line-height: 1.35;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.flash-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.flash-bar {
  flex: 1;
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: #f1f2f4;
}

.flash-bar i {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #fe2c55, #ff6b81);
}

.flash-progress small {
  flex: 0 0 auto;
  color: #fe2c55;
  font-size: 0.75rem;
  font-weight: 800;
}

.service-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 0.85rem 1rem;
}

.service-strip span {
  display: flex;
  gap: 0.4rem;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 0.9rem;
  font-weight: 800;
}

.service-strip span::before {
  display: inline-grid;
  width: 18px;
  height: 18px;
  place-items: center;
  border-radius: 50%;
  background: #fe2c55;
  color: #fff;
  content: '✓';
  font-size: 0.7rem;
}

.section-title {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1rem;
}

.section-title h2 {
  margin: 0;
  color: #111827;
  font-size: 1.5rem;
}

.section-title > span,
.section-kicker {
  color: #6b7280;
  font-size: 0.875rem;
}

.more-link {
  min-height: 34px;
  padding: 0 0.9rem;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #fff;
  color: #111827;
  cursor: pointer;
  font-weight: 700;
}

.more-link:hover {
  border-color: #fe2c55;
  color: #fe2c55;
}

.section-kicker {
  display: block;
  margin-bottom: 0.15rem;
}

.recommendation-hint {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
  margin: 0.35rem 0 0;
  color: #6b7280;
  font-size: 0.82rem;
}

.recommendation-hint span {
  display: inline-flex;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  background: #fff1f2;
  color: #fe2c55;
  font-weight: 800;
}

.category-section,
.hot-section,
.feed-section {
  margin-bottom: 2rem;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.category-tile {
  min-height: 104px;
  padding: 1rem;
  border: 1px solid rgba(17, 24, 39, 0.08);
  border-radius: 14px;
  background: #fff;
  color: #111827;
  text-align: left;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.category-tile:hover,
.hot-card:hover,
.feed-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.12);
}

.category-mark {
  display: grid;
  width: 36px;
  height: 36px;
  margin-bottom: 0.75rem;
  place-items: center;
  border-radius: 50%;
  color: #fff;
  font-weight: 900;
}

.tone-0 .category-mark { background: #ff2f68; }
.tone-1 .category-mark { background: #1677ff; }
.tone-2 .category-mark { background: #16a34a; }
.tone-3 .category-mark { background: #7c3aed; }

.category-tile strong,
.category-tile small {
  display: block;
}

.category-tile strong {
  font-size: 1.1rem;
}

.category-tile small {
  margin-top: 0.25rem;
  color: #6b7280;
}

.hot-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  padding: 0.25rem 0;
}

.hot-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 14px;
  background: #fff;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hot-image,
.feed-image {
  position: relative;
}

.card-tags {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 2;
}

.card-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 900;
  line-height: 1.6;
}

.tag-hot { background: #fe2c55; color: #fff; }
.tag-value { background: #ff6b35; color: #fff; }
.tag-discount { background: linear-gradient(135deg, #ff4757, #ff6b81); color: #fff; }
.tag-urgent { background: #ff6348; color: #fff; }
.tag-new { background: #2ed573; color: #fff; }

.hot-image {
  aspect-ratio: 1;
  overflow: hidden;
}

.hot-image img,
.feed-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.35s ease;
}

.hot-card:hover img,
.feed-card:hover img {
  transform: scale(1.04);
}

.hot-info {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0.75rem;
}

.hot-info span,
.category {
  color: #fe2c55;
  font-size: 0.78rem;
  font-weight: 800;
}

.hot-info h3,
.feed-info h3 {
  display: -webkit-box;
  min-height: 2.7rem;
  margin: 0.35rem 0 0.5rem;
  overflow: hidden;
  color: #111827;
  font-size: 0.95rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.hot-info strong,
.feed-footer strong {
  margin-top: auto;
  color: #fe2c55;
  font-size: 1.05rem;
}

.waterfall-feed {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1rem;
}

.feed-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 14px;
  background: #fff;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feed-image {
  aspect-ratio: 1;
  overflow: hidden;
}

.feed-info {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0.75rem;
}

.feed-info p {
  display: -webkit-box;
  min-height: 2.4rem;
  margin: 0 0 0.75rem;
  overflow: hidden;
  color: #6b7280;
  font-size: 0.8rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.feed-footer {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
  margin-top: auto;
}

.feed-actions {
  display: flex;
  gap: 0.35rem;
}

.feed-actions button {
  min-height: 1.8rem;
  padding: 0 0.55rem;
  border: 1px solid #f1f1f1;
  border-radius: 999px;
  background: #fafafa;
  color: #111827;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
}

.feed-actions button:hover {
  border-color: #fe2c55;
  color: #fe2c55;
}

.feed-actions button.active {
  border-color: #fe2c55;
  background: #fff1f2;
  color: #fe2c55;
}

.loading-state,
.error-state {
  padding: 3rem;
  color: #6b7280;
  text-align: center;
}

.error-state {
  color: #ff4d4f;
}

@media (max-width: 767px) {
  .section-title {
    align-items: flex-start;
    flex-direction: column;
  }

  .home-hero-grid {
    grid-template-columns: 1fr;
  }

  .promo-stack {
    min-height: auto;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-carousel {
    min-height: 440px;
    border-radius: 16px;
  }

  .hero-slide::after {
    background: linear-gradient(180deg, rgba(17, 24, 39, 0.12), rgba(17, 24, 39, 0.88));
  }

  .hero-content {
    right: 1.25rem;
  }

  .channel-section,
  .service-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hot-row,
  .waterfall-feed {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 768px) and (max-width: 1100px) {
  .home-hero-grid {
    grid-template-columns: 1fr;
  }

  .promo-stack {
    display: none;
  }

  .hot-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .waterfall-feed {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (min-width: 1400px) {
  .waterfall-feed {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .feed-footer {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
