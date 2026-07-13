<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '../stores/productStore'
import type { Product } from '../types'
import { addProductToCart } from '@/utils/cart'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'
import { behaviorService } from '@/services/behaviorService'
import api from '@/services/api'

type BehaviorAction = 'view' | 'favorite' | 'unfavorite' | 'cart' | 'buy'

const router = useRouter()
const productStore = useProductStore()
const loading = ref(false)
const error = ref<string | null>(null)
const actionMessage = ref('')
const activeSlide = ref(0)
const favoriteIds = ref<number[]>([])
const products = computed(() => productStore.products)
const bannerProducts = computed(() => products.value.slice(0, 3))
const recommendedProducts = ref<Product[]>([])

const fetchRecommendations = async () => {
  try {
    const res = await api.get('/recommendations', { params: { limit: 60 } })
    if (res.data.code === '0000') {
      recommendedProducts.value = res.data.data || []
    }
  } catch {
    // 兜底：用全量商品
    recommendedProducts.value = products.value.slice(0, 60)
  }
}

// feedProducts 优先用推荐结果，无结果时用全量
const feedProducts = computed(() => {
  if (recommendedProducts.value.length > 0) return recommendedProducts.value
  return products.value.slice(0, 60)
})
const serviceCards = ['正品保障', '快速配送', '售后无忧', '安全支付']
const subscribeEmail2 = ref('')
const subscribed2 = ref(false)
const recentViewed = ref<Product[]>([])

const categoryCards = [
  { label: '数码设备', img: 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=400&q=85', query: { category: '数码' } },
  { label: '电脑配件', img: 'https://images.unsplash.com/photo-1609091219090-a6d81d3085bf?auto=format&fit=crop&w=400&q=85', query: { category: '数码', subcategory: '电脑配件' } },
  { label: '充电设备', img: 'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=400&q=85', query: { category: '数码', subcategory: '充电设备' } },
  { label: '通勤背包', img: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=400&q=85', query: { category: '服饰' } },
  { label: '家居好物', img: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=400&q=85', query: { category: '家居' } },
  { label: '品质生活', img: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=400&q=85', query: { category: '家居' } },
]

const trendList = computed(() => products.value.slice(0, 5).map((p, i) => ({ ...p, trend: [42, 35, 28, 21, 18][i] })))

const lifestyleCards = [
  { label: '高效学习', desc: '键盘、耳机、护眼灯', img: 'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=800&q=85', path: '/category/digital' },
  { label: '轻松通勤', desc: '背包、移动电源、保温杯', img: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=85', path: '/category/fashion' },
  { label: '舒适居家', desc: '香薰加湿器、灯具、家居用品', img: 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=800&q=85', path: '/category/home' },
  { label: '品质数码', desc: '无线充电、智能配件、桌面设备', img: 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=800&q=85', path: '/category/digital' },
]


const loadRecentViewed = () => { try { recentViewed.value = JSON.parse(localStorage.getItem('recentViewed') || '[]') } catch { recentViewed.value = [] } }

const subscribe2 = () => { if (!subscribeEmail2.value.trim()) return; subscribed2.value = true; setTimeout(() => subscribed2.value = false, 3000) }

const viewCategory = (q: Record<string, string>) => router.push({ path: '/products', query: q })

const catTrack = ref<HTMLElement | null>(null)
const catScrollPos = ref(0)
const catMaxScroll = ref(0)

const circleCategories = [
  { label: '数码家电', img: '/circle-digital.png', path: '/category/digital' },
  { label: '电脑配件', img: '/circle-digital.png', path: '/category/digital' },
  { label: '充电设备', img: '/circle-digital.png', path: '/category/digital' },
  { label: '服饰穿搭', img: '/circle-digital.png', path: '/category/fashion' },
  { label: '家居生活', img: '/circle-digital.png', path: '/category/home' },
  { label: '灯具照明', img: '/circle-digital.png', path: '/category/home' },
  { label: '品质生活', img: '/circle-digital.png', path: '/category/quality' },
  { label: '智能设备', img: '/circle-digital.png', path: '/category/digital' },
]

const scrollCatCircles = (dir: number) => {
  if (!catTrack.value) return
  const amount = catTrack.value.children[0]?.clientWidth * 3 + 84 || 600
  catTrack.value.scrollBy({ left: amount * dir, behavior: 'smooth' })
  setTimeout(() => { if (catTrack.value) { catScrollPos.value = catTrack.value.scrollLeft; catMaxScroll.value = catTrack.value.scrollWidth - catTrack.value.clientWidth } }, 400)
}

const actionText: Record<BehaviorAction, string> = {
  view: '浏览',
  favorite: '收藏',
  unfavorite: '取消收藏',
  cart: '加购',
  buy: '购买'
}

const recordBehavior = (product: Product, action: BehaviorAction) => {
  behaviorService.send({
    productId: product.productId,
    productName: product.name,
    action: action === 'buy' ? 'purchase' : action,
    category: product.category,
    source: 'home_page',
  })
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

const totalSlides = computed(() => bannerProducts.value.length + 1)

const prevSlide = () => {
  activeSlide.value = (activeSlide.value - 1 + totalSlides.value) % totalSlides.value
}

const nextSlide = () => {
  activeSlide.value = (activeSlide.value + 1) % totalSlides.value
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
  startCountdown()
  loadRecentViewed()

  loading.value = products.value.length === 0
  try {
    if (products.value.length === 0) {
      await productStore.fetchProducts()
    }
    await fetchRecommendations()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
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
          <!-- new arrivals promo slide -->
          <article
            :class="['hero-slide', 'new-arrival-slide', { active: 0 === activeSlide }]"
            @click="router.push('/new-arrivals')"
          >
            <div class="na-notify-bar">NEW ARRIVALS 2026 | 本季新品焕新登场 →</div>
            <div class="na-slide-bg">
              <span class="na-deco-row na-row1">NEW&nbsp;&nbsp;2026&nbsp;&nbsp;NEW</span>
              <span class="na-deco-row na-row2">ARRIVALS&nbsp;&nbsp;NEW&nbsp;&nbsp;2026</span>
              <span class="na-acc na-acc-1"></span><span class="na-acc na-acc-2"></span><span class="na-acc na-acc-3"></span><span class="na-acc na-acc-4"></span>
            </div>
            <div class="na-badge">
              <span class="na-badge-new">NEW</span>
              <span class="na-badge-year">2026</span>
            </div>
            <div class="na-slide-card">
              <h2 class="flip-title">
                <span class="flip-word">NEW</span>
                <span class="flip-word">ARRIVALS</span>
              </h2>
              <h2 class="new-arrival-cn">新品首发 · 焕新登场</h2>
              <p class="new-arrival-sub">本季好物抢先上新，发现你的下一件心动单品</p>
              <button type="button" class="new-arrival-btn" @click.stop="router.push('/new-arrivals')">立即探索</button>
            </div>
          </article>

          <article
            v-for="(product, index) in bannerProducts"
            :key="`banner-${product.productId}`"
            :class="['hero-slide', { active: index + 1 === activeSlide }]"
            @click="navigateToDetail(product)"
          >
            <img loading="lazy" :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
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
              v-for="i in totalSlides"
              :key="`dot-${i}`"
              type="button"
              :class="{ active: i - 1 === activeSlide }"
              :aria-label="`切换到第 ${i} 张`"
              @click.stop="switchSlide(i - 1)"
            />
          </div>
        </section>
      </section>

      <section class="hot-section" aria-labelledby="hot-title">
        <div class="section-title">
          <div>
            <h2 id="hot-title">热卖单品</h2>
          </div>
          <span class="hot-trend-tag">近期热度上升 ↗</span>
        </div>
        <div class="hot-with-trend">
        <div class="hot-row">
          <article v-for="t in trendList.slice(0,5)" :key="'hot-'+t.productId" class="hot-card" @click="navigateToDetail(t)">
            <div class="hot-image">
              <img loading="lazy" :src="t.imageUrls[0]" :alt="t.name" @error="handleImageError" />
              <div v-if="getProductTags(t).length" class="card-tags">
                <span v-for="tag in getProductTags(t)" :key="tag.text" :class="['card-tag', `tag-${tag.type}`]">{{ tag.text }}</span>
              </div>
            </div>
            <div class="hot-info"><span>{{ t.category || '精选' }}</span><h3>{{ t.name }}</h3><strong>¥{{ t.price }}</strong></div>
          </article>
        </div>
        <div class="trend-panel">
          <h4>趋势榜单</h4>
          <div v-for="(t, i) in trendList.slice(0,4)" :key="'t2-'+t.productId" class="trend-item" @click="navigateToDetail(t)">
            <span class="trend-rank">{{ String(i+1).padStart(2,'0') }}</span><img loading="lazy" :src="t.imageUrls[0]" :alt="t.name" @error="handleImageError" />
            <div><span class="trend-name">{{ t.name }}</span><span class="trend-pct">+{{ t.trend }}%</span></div>
          </div>
          <button class="trend-more" @click="router.push('/hot-sales')">查看更多 →</button>
        </div>
        </div>
      </section>

      <!-- Category Circle Carousel -->
      <section class="circle-cat-section" aria-label="热门分类">
        <div class="circle-cat-head"><div><span class="section-kicker">Shop by category</span><h2>热门分类</h2></div><button class="circle-cat-view-all" @click="router.push('/products')">查看全部 →</button></div>
        <div class="circle-cat-wrap">
          <button class="circle-arrow circle-arrow-left" @click="scrollCatCircles(-1)" :disabled="catScrollPos <= 0">‹</button>
          <div class="circle-cat-track" ref="catTrack"><button v-for="c in circleCategories" :key="c.label" class="circle-cat-item" @click="router.push(c.path)"><div class="circle-img-wrap"><img loading="lazy" :src="c.img" :alt="c.label" @error="handleImageError" /></div><span>{{ c.label }}</span></button></div>
          <button class="circle-arrow circle-arrow-right" @click="scrollCatCircles(1)" :disabled="catScrollPos >= catMaxScroll">›</button>
        </div>
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
              <img loading="lazy" :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
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
      <section class="feed-section" aria-labelledby="feed-title">
        <div class="section-title">
          <div>
            <span class="section-kicker">For you</span>
            <h2 id="feed-title">为你精选</h2>
            <p v-if="recommendationSummary" class="recommendation-hint">{{ recommendationSummary }}
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
              <img loading="lazy" :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
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

      <!-- Hot Categories -->
      <!-- Lifestyle -->
      <section class="lifestyle-section" aria-label="生活场景">
        <div class="section-title"><div><span class="section-kicker">Shop by lifestyle</span><h2>按生活场景选购</h2></div></div>
        <div class="lifestyle-grid">
          <button v-for="l in lifestyleCards" :key="l.label" class="lifestyle-card" @click="router.push(l.path)">
            <img loading="lazy" :src="l.img" :alt="l.label" @error="handleImageError" /><div class="lifestyle-overlay"></div>
            <div class="lifestyle-text"><strong>{{ l.label }}</strong><span>{{ l.desc }}</span><small>探索场景 →</small></div>
          </button>
        </div>
      </section>

      <!-- Editorials -->
      <section class="editorial-section" aria-label="编辑精选">
        <div class="editorial-card reverse">
          <div class="editorial-img"><img src="https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85" alt="数码" @error="handleImageError" /></div>
          <div class="editorial-text"><span class="editorial-kicker">EDITOR'S PICK</span><h3>数码焕新计划</h3><p>从高效办公到沉浸娱乐，用更适合的设备改善日常体验。</p><button class="more-link" @click="router.push('/category/digital')">探索数码精选 →</button></div>
        </div>
        <div class="editorial-card">
          <div class="editorial-text"><span class="editorial-kicker">LIFESTYLE EDIT</span><h3>舒适生活提案</h3><p>从灯光、香气和随身用品开始，为日常增加一点舒适感。</p><button class="more-link" @click="router.push('/category/home')">探索生活好物 →</button></div>
          <div class="editorial-img"><img src="https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85" alt="家居" @error="handleImageError" /></div>
        </div>
      </section>

      <!-- Continue Browsing -->
      <section v-if="recentViewed.length" class="recent-section" aria-label="继续浏览">
        <div class="section-title"><div><span class="section-kicker">Continue browsing</span><h2>继续浏览</h2></div></div>
        <div class="recent-row">
          <article v-for="p in recentViewed.slice(0,6)" :key="'rv-'+p.productId" class="recent-card" @click="navigateToDetail(p)">
            <img loading="lazy" :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" /><span>{{ p.name }}</span><strong>¥{{ p.price }}</strong>
          </article>
        </div>
      </section>

      <!-- Why Recommendations -->
      <section class="why-section" aria-label="推荐说明">
        <div class="section-title"><div><span class="section-kicker">Why different?</span><h2>为什么推荐不一样？</h2></div></div>
        <div class="why-grid">
          <div class="why-card"><span class="why-icon">🎯</span><h4>了解你的兴趣</h4><p>分析浏览、收藏、加购和购买行为。</p></div>
          <div class="why-card"><span class="why-icon">⚙️</span><h4>离线数据计算</h4><p>行为日志定期进入 HDFS，离线任务计算偏好。</p></div>
          <div class="why-card"><span class="why-icon">🔄</span><h4>持续更新推荐</h4><p>推荐会随着新的用户行为不断调整。</p></div>
        </div>
      </section>

      <!-- Subscribe -->
      <section class="home-subscribe" aria-label="订阅">
        <h3>不要错过下一次上新</h3><p>订阅新品、限时优惠和个性推荐通知。</p>
        <form v-if="!subscribed2" class="home-sub-form" @submit.prevent="subscribe2"><input v-model="subscribeEmail2" type="email" placeholder="输入您的邮箱" /><button type="submit">立即订阅</button></form>
        <p v-else class="home-sub-ok">✓ 订阅成功！新品上线时我们将第一时间通知您。</p>
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
  grid-template-columns: minmax(0, 1fr);
  gap: 0;
  align-items: stretch;
  width: 100vw;
  margin: -1.5rem 0 1.5rem;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
  position: relative;
  background: #fff;
}

.service-strip {
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.hero-carousel {
  position: relative;
  height: 500px;
  overflow: hidden;
  border-radius: 0;
  background: #241B2F;
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
  color: #241B2F;
  cursor: pointer;
  font-weight: 800;
}

.hero-dots {
  position: absolute;
  z-index: 6;
  left: 50%;
  bottom: 20px;
  transform: translateX(-50%);
  display: flex;
  gap: 9px;
}

.hero-dots button {
  width: 10px;
  height: 10px;
  padding: 0;
  border: 1px solid #756D7E;
  border-radius: 50%;
  background: #fff;
  cursor: pointer;
}

.hero-dots button.active {
  background: #241B2F;
  border-color: #241B2F;
}

.hero-arrow {
  position: absolute;
  z-index: 6;
  top: 55%;
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  border: 1.5px solid #7B189F;
  border-radius: 50%;
  background: #fff;
  color: #7B189F;
  cursor: pointer;
  opacity: 1;
  transform: translateY(-50%);
  transition: all 0.2s ease;
}

.hero-arrow:hover {
  background: #7B189F;
  color: #fff;
  transform: translateY(-50%) scale(1.06);
}

.hero-arrow svg {
  width: 24px;
  height: 24px;
}

.hero-arrow-left {
  left: 20px;
}

.hero-arrow-right {
  right: 100px;
}

.hero-carousel:hover .hero-arrow {
  opacity: 1;
}

/* ====== new arrival promo slide ====== */
.new-arrival-slide {
  background: #FAF2CB;
  cursor: pointer;
}
/* purple notify bar */
.na-notify-bar {
  position: absolute; top: 0; left: 0; right: 0; height: 40px; z-index: 5;
  background: linear-gradient(90deg, #5A0B72 0%, #7B189F 50%, #9226B3 100%);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 16px; font-weight: 600; letter-spacing: 0.02em;
  white-space: nowrap;
}

.na-slide-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.na-slide-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.na-deco-row {
  font-family: "Arial Black", "Montserrat", sans-serif;
  font-size: clamp(220px, 19vw, 360px);
  font-weight: 900;
  line-height: 0.78;
  letter-spacing: -0.07em;
  color: #F0A828;
  opacity: 0.62;
  white-space: nowrap;
  pointer-events: none;
  user-select: none;
  text-align: center;
}

.na-row1 { transform: rotate(-3deg) scaleX(1.08); }
.na-row2 { transform: rotate(-3deg) scaleX(1.05); }

/* subtle accent decorations */
.na-acc { position: absolute; pointer-events: none; z-index: 1; opacity: 0.10; }
.na-acc-1 { top: 8%; right: 20%; width: 28px; height: 28px; border: 2px solid #7B189F; border-radius: 50%; }
.na-acc-2 { top: 15%; right: 28%; width: 16px; height: 16px; background: #E3B52A; border-radius: 50%; }
.na-acc-3 { bottom: 12%; left: 18%; width: 32px; height: 32px; border: 2px solid #7B189F; border-radius: 50%; opacity: 0.08; }
.na-acc-4 { top: 65%; right: 8%; width: 12px; height: 12px; background: #fff; border-radius: 2px; transform: rotate(45deg); opacity: 0.12; }

/* tablet */
@media (max-width: 1100px) {
  .na-deco-row { font-size: clamp(140px, 14vw, 260px); }
}

/* mobile */
@media (max-width: 767px) {
  .na-deco-row { font-size: clamp(100px, 18vw, 200px); opacity: 0.40; }
}

.na-slide-card {
  position: absolute;
  left: 50%;
  top: 52%;
  transform: translate(-50%, -50%);
  width: min(760px, 48vw);
  min-width: 600px;
  height: 325px;
  padding: 1.5rem 2.5rem;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 18px 42px rgba(68, 35, 85, 0.10);
  text-align: center;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* ====== hanging NEW badge ====== */
.na-badge {
  position: absolute;
  left: calc(50% - 510px);
  top: 40px;
  z-index: 5;
  width: 145px;
  height: 180px;
  padding-bottom: 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  background: linear-gradient(180deg, #5A0B72 0%, #7B189F 40%, #9226B3 100%);
  color: #fff;
  clip-path: polygon(0 0, 100% 0, 100% 78%, 50% 100%, 0 78%);
  box-shadow: 0 12px 28px rgba(90, 11, 114, 0.24);
}

.na-badge-new { font-size: 18px; font-weight: 700; letter-spacing: 0.08em; line-height: 1.1; }
.na-badge-year { font-size: 50px; font-weight: 900; line-height: 1; }

@media (max-width: 1100px) {
  .na-badge { left: 10px; top: 40px; width: 150px; height: 180px; }
  .na-badge-year { font-size: 44px; }
  .na-badge-new { font-size: 18px; }
  .na-badge-cn { font-size: 20px; }
  .na-slide-card { min-width: 0; width: 76%; height: auto; min-height: 300px; padding: 1.5rem 2rem; }
}

@media (max-width: 767px) {
  .na-badge { width: 100px; height: 130px; left: 8px; top: 40px; padding-bottom: 10px; }
  .na-badge-year { display: none; }
  .na-badge-new, .na-badge-cn { font-size: 16px; }
  .na-slide-card { min-width: 0; width: calc(100% - 32px); height: auto; min-height: 260px; padding: 1.25rem; }
  .new-arrival-btn { min-width: 180px; height: 56px; font-size: 16px; }
}

/* flip title — single spin */
.flip-title {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 14px;
  margin: 0.5rem 0 0;
}

.flip-word {
  display: inline-block;
  font-family: "Montserrat", "Poppins", "Arial Black", sans-serif;
  font-size: clamp(22px, 2vw, 34px);
  font-weight: 800;
  letter-spacing: 0.12em;
  line-height: 1.2;
  color: #7B189F;
  transition: color 0.5s ease;
}

.new-arrival-slide:hover .flip-word {
  color: #D3A21B;
}

@media (prefers-reduced-motion: reduce) {
  .flip-word { animation: none !important; }
}

.new-arrival-cn {
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif;
  font-size: clamp(48px, 4.2vw, 64px);
  font-weight: 900;
  letter-spacing: 0.01em;
  line-height: 1.12;
  color: #D3A21B;
  margin: 0;
  transition: color 0.5s ease, text-shadow 0.35s ease;
}

.new-arrival-sub {
  color: #7B7182;
  font-size: clamp(0.85rem, 1.1vw, 1.05rem);
  margin: 0;
  max-width: 420px;
  transition: color 0.5s ease;
}

.new-arrival-slide:hover .new-arrival-sub { color: #D3A21B; }

.new-arrival-btn {
  min-width: 230px;
  height: 72px;
  padding: 0 42px;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, #5A0B72 0%, #7B189F 55%, #9226B3 100%);
  color: #fff;
  cursor: pointer;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.06em;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.new-arrival-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(90, 11, 114, 0.28);
}

.new-arrival-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 26px rgba(90, 11, 114, 0.28);
}

.new-arrival-slide:hover .new-arrival-cn {
  color: #7B189F;
  text-shadow: 0 8px 22px rgba(123, 24, 159, 0.14);
}

.new-arrival-slide::after {
  display: none !important;
}

@media (max-width: 1100px) {
  .na-slide-card {
    width: 78%;
    min-width: 0;
    padding: 2rem;
  }
  .na-deco-2 { right: -60px; }
}

@media (max-width: 767px) {
  .na-slide-card {
    width: calc(100% - 32px);
    min-width: 0;
    padding: 1.5rem 1.25rem;
    border-radius: 18px;
  }
  .new-arrival-cn { font-size: clamp(32px, 8vw, 48px); }
  .flip-word { font-size: clamp(18px, 4vw, 24px); }
  .na-slide-tag { left: 16px; padding: 6px 10px 12px; }
  .na-slide-tag span { font-size: 0.6rem; }
  .na-d7, .na-d8, .na-d9, .na-d10, .na-d11, .na-d12 { display: none; }
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
  background: linear-gradient(135deg, #980B32, #5A0B72);
  color: #fff;
  font-size: 13px;
  font-weight: 900;
}

.flash-title-row h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #241B2F;
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
  background: #241B2F;
  color: #fff;
  font-size: 14px;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
}

.flash-countdown em {
  color: #241B2F;
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
  background: #F7F6FA;
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
  background: #980B32;
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
  color: #980B32;
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
  color: #241B2F;
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
  background: #E9E4EE;
}

.flash-bar i {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #85072B, #AD1745);
}

.flash-progress small {
  flex: 0 0 auto;
  color: #980B32;
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
  background: #F4D35E;
  color: #6A4A00;
  box-shadow: 0 4px 12px rgba(244, 211, 94, 0.24);
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
  color: #241B2F;
  font-size: 1.5rem;
}

.section-title > span,
.section-kicker {
  color: #756D7E;
  font-size: 0.875rem;
}

.more-link {
  min-height: 34px;
  padding: 0 0.9rem;
  border: 1px solid #948B9D;
  border-radius: 999px;
  background: #fff;
  color: #241B2F;
  cursor: pointer;
  font-weight: 700;
}

.more-link:hover {
  border-color: #980B32;
  color: #980B32;
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
  color: #756D7E;
  font-size: 0.82rem;
}

.recommendation-hint span {
  display: inline-flex;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  background: #F4EFF7;
  color: #980B32;
  font-weight: 800;
}

.hot-trend-tag {
  padding: 6px 12px; border-radius: 16px; background: #F4EDF7; color: #7B189F; font-size: 13px; font-weight: 500;
}
.hot-section .section-title h2::after {
  content: '';
  display: block;
  width: 48px; height: 3px; margin-top: 8px; border-radius: 3px;
  background: linear-gradient(90deg, #7B189F, #E3B52A);
}
.hot-section { margin-bottom: 1rem; }
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

.tag-hot { background: linear-gradient(135deg, #980B32, #5A0B72); color: #fff; }
.tag-value { background: #980B32; color: #fff; }
.tag-discount { background: #980B32; color: #fff; }
.tag-urgent { background: #F4D35E; color: #594B1F; }
.tag-new { background: #F4D35E; color: #594B1F; }

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
  color: #980B32;
  font-size: 0.78rem;
  font-weight: 800;
}

.hot-info h3,
.feed-info h3 {
  display: -webkit-box;
  min-height: 2.7rem;
  margin: 0.35rem 0 0.5rem;
  overflow: hidden;
  color: #241B2F;
  font-size: 0.95rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.hot-info strong,
.feed-footer strong {
  margin-top: auto;
  color: #980B32;
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
  color: #756D7E;
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
  color: #241B2F;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
}

.feed-actions button:hover {
  border-color: #980B32;
  color: #980B32;
  background: #F4EFF7;
}

.feed-actions button.active {
  border-color: #980B32;
  background: #F4EFF7;
  color: #980B32;
}

.feed-actions button:last-child {
  background: linear-gradient(135deg, #85072B, #7B189F);
  border-color: transparent;
  color: #fff;
}

.feed-actions button:last-child:hover {
  background: linear-gradient(135deg, #85072B, #7B189F);
  border-color: transparent;
  color: #fff;
  filter: brightness(1.08);
  box-shadow: 0 6px 16px rgba(111, 76, 195, 0.20);
}

.loading-state,
.error-state {
  padding: 3rem;
  color: #756D7E;
  text-align: center;
}

.error-state {
  color: #ff4d4f;
}

/* Circle Category Carousel */
.circle-cat-section { background: #fff; width: calc(100vw - 192px); margin-left: calc(-50vw + 50% + 96px); margin-right: 0; padding: 7px 0 36px; box-sizing: border-box; border-radius: 0; box-shadow: none; border: none; border-top: 1px solid #F0E9DD; border-bottom: 1px solid #F0E9DD; }
.circle-cat-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; padding: 0 28px 0 28px; }
.circle-cat-head h2 { margin: 0; color: #241B2F; font-size: 18px; font-weight: 700; }
.circle-cat-view-all { height: 36px; padding: 0 18px; border: 1px solid #D8CDD9; border-radius: 999px; background: #fff; color: #5A0B72; cursor: pointer; font-size: 0.84rem; font-weight: 700; transition: all 0.15s; }
.circle-cat-view-all:hover { border-color: #7B189F; color: #7B189F; }
.circle-cat-wrap { display: flex; align-items: center; gap: 0; padding: 0 8px; }
.circle-cat-track { display: flex; gap: 28px; overflow-x: auto; scroll-behavior: smooth; scrollbar-width: none; padding: 6px 0; flex: 1; }
.circle-cat-track::-webkit-scrollbar { display: none; }
.circle-cat-item { border: 0; background: none; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 12px; flex: 0 0 auto; width: 148px; transition: transform 0.25s ease; scroll-snap-align: start; padding: 0; }
.circle-cat-item:hover { transform: translateY(-4px); }
.circle-cat-item:hover .circle-img-wrap { box-shadow: 0 10px 24px rgba(91,25,117,0.14); }
.circle-cat-item:hover span { color: #7B189F; }
.circle-img-wrap { width: 132px; height: 132px; border-radius: 50%; background: #F1E2FF; border: 1px solid #D9C8EB; display: grid; place-items: center; overflow: hidden; transition: box-shadow 0.25s ease; }
.circle-img-wrap img { width: 72%; height: 72%; object-fit: contain; transition: transform 0.25s ease; }
.circle-cat-item:hover .circle-img-wrap img { transform: scale(1.05); }
.circle-cat-item span { color: #33283D; font-size: 15px; font-weight: 600; text-align: center; transition: color 0.25s ease; line-height: 1.3; }
.circle-arrow { width: 40px; height: 40px; border-radius: 50%; background: #fff; border: 1.5px solid #7B189F; color: #7B189F; cursor: pointer; font-size: 1.15rem; display: grid; place-items: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(91,25,117,0.12); transition: all 0.2s ease; line-height: 1; margin: 0 6px; align-self: center; margin-bottom: 28px; }
.circle-arrow:hover:not(:disabled) { background: #7B189F; color: #fff; transform: scale(1.05); }
.circle-arrow:disabled { opacity: 0.3; cursor: default; }

@media (max-width: 1200px) { .circle-cat-section { width: calc(100vw - 112px); margin-left: calc(-50vw + 50% + 20px); } .circle-cat-head { padding: 0 20px 0 20px; } }
@media (max-width: 1100px) { .circle-img-wrap { width: 115px; height: 115px; } .circle-cat-item { width: 130px; } .circle-cat-track { gap: 20px; } }
@media (max-width: 767px) { .circle-arrow { display: none; } .circle-cat-section { width: 100%; margin-left: 0; } .circle-cat-head { padding: 0; } .circle-img-wrap { width: 100px; height: 100px; } .circle-cat-item { width: 110px; } .circle-cat-item span { font-size: 13px; } .circle-cat-track { gap: 14px; } .circle-cat-section { padding: 20px 0 24px; } }

/* Hot + Trend */
.hot-section { max-width: none; width: calc(100vw - 192px); margin-left: calc(-50vw + 50% + 96px); margin-right: 0; }
.hot-with-trend { display: grid; grid-template-columns: 80fr 20fr; gap: 0.75rem; align-items: start; }
.hot-with-trend .hot-row { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.75rem; }
.hot-with-trend .hot-card { padding: 0.6rem; }
.hot-with-trend .hot-image { aspect-ratio: 1; }
.hot-with-trend .hot-image img { object-fit: cover; }
.hot-with-trend .hot-info { padding: 0.5rem 0; }
.hot-with-trend .hot-info span { font-size: 0.74rem; }
.hot-with-trend .hot-info h3 { font-size: 0.84rem; min-height: auto; margin: 0.2rem 0; }
.hot-with-trend .hot-info strong { font-size: 0.95rem; }
.trend-panel { background: #fff; border-radius: 14px; padding: 0.7rem; box-shadow: 0 2px 10px rgba(15,23,42,0.16); }
.trend-panel h4 { margin: 0 0 0.6rem; color: #241B2F; font-size: 0.98rem; font-weight: 900; }
.trend-item { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-radius: 8px; cursor: pointer; transition: background 0.15s; }
.trend-item:hover { background: #F7F6FA; }
.trend-rank { width: 24px; color: #7B189F; font-size: 0.9rem; font-weight: 900; }
.trend-item img { width: 38px; height: 38px; border-radius: 6px; object-fit: cover; }
.trend-item > div { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.trend-name { color: #241B2F; font-size: 0.86rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.trend-more { display: block; width: 100%; margin-top: 8px; padding: 6px 0; border: 0; border-radius: 8px; background: #F3EAF8; color: #7B189F; cursor: pointer; font-size: 0.8rem; font-weight: 700; text-align: center; transition: background 0.15s; }
.trend-more:hover { background: #E8D6F3; }
.trend-pct { color: #16a34a; font-size: 0.72rem; font-weight: 800; }
.trend-pct.up { color: #7B189F; }

/* Lifestyle */
.lifestyle-section { margin-bottom: 2rem; }
.lifestyle-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }
.lifestyle-card { position: relative; border: 0; border-radius: 16px; overflow: hidden; cursor: pointer; height: 360px; }
.lifestyle-card img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
.lifestyle-card:hover img { transform: scale(1.04); }
.lifestyle-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(15,5,25,0.2) 0%, rgba(15,5,25,0.6) 100%); }
.lifestyle-text { position: absolute; bottom: 0; left: 0; right: 0; padding: 1.5rem; color: #fff; text-align: left; }
.lifestyle-text strong { display: block; font-size: 1.15rem; font-weight: 900; margin-bottom: 4px; }
.lifestyle-text span { display: block; font-size: 0.82rem; opacity: 0.85; margin-bottom: 6px; }
.lifestyle-text small { font-size: 0.78rem; font-weight: 700; }

/* Editorials */
.editorial-section { display: flex; flex-direction: column; gap: 80px; margin-bottom: 80px; }
.editorial-card { display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-radius: 18px; overflow: hidden; background: #fff; box-shadow: 0 4px 20px rgba(15,23,42,0.18); }
.editorial-card.reverse { direction: ltr; }
.editorial-img { height: 440px; overflow: hidden; }
.editorial-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
.editorial-card:hover .editorial-img img { transform: scale(1.03); }
.editorial-text { display: flex; flex-direction: column; justify-content: center; padding: 3rem; }
.editorial-text.reverse { direction: ltr; }
.editorial-kicker { color: #7B189F; font-size: 0.7rem; font-weight: 900; letter-spacing: 1px; margin-bottom: 0.5rem; }
.editorial-text h3 { margin: 0 0 0.75rem; color: #241B2F; font-size: 1.5rem; font-weight: 900; }
.editorial-text p { color: #756D7E; font-size: 0.92rem; line-height: 1.6; margin: 0 0 1rem; }

/* Recent */
.recent-section { margin-bottom: 2rem; }
.recent-row { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 1rem; }
.recent-card { border-radius: 12px; background: #fff; overflow: hidden; cursor: pointer; box-shadow: 0 2px 8px rgba(15,23,42,0.16); transition: transform 0.2s; text-align: center; }
.recent-card:hover { transform: translateY(-3px); }
.recent-card img { width: 100%; aspect-ratio: 1; object-fit: cover; }
.recent-card span { display: block; padding: 0.5rem 0.5rem 0; color: #241B2F; font-size: 0.78rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.recent-card strong { display: block; padding: 0.2rem 0.5rem 0.6rem; color: #980B32; font-size: 0.85rem; font-weight: 800; }

/* Why */
.why-section { margin-bottom: 2rem; }
.why-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.5rem; }
.why-card { text-align: center; padding: 2rem 1.5rem; background: #F4EEFA; border-radius: 16px; }
.why-icon { font-size: 2rem; }
.why-card h4 { margin: 0.5rem 0 0.3rem; color: #7B189F; font-size: 0.95rem; font-weight: 900; }
.why-card p { color: #756D7E; font-size: 0.82rem; line-height: 1.5; margin: 0; }

/* Home Subscribe */
.home-subscribe { text-align: center; padding: 3rem 2rem; border-radius: 18px; background: linear-gradient(135deg, #5A0B72 0%, #7B189F 55%, #9226B3 100%); color: #fff; margin-bottom: 2rem; }
.home-subscribe h3 { margin: 0; font-size: 1.3rem; font-weight: 900; }
.home-subscribe > p { margin: 0.4rem 0 1.25rem; color: rgba(255,255,255,0.75); font-size: 0.9rem; }
.home-sub-form { display: flex; justify-content: center; gap: 0.65rem; max-width: 420px; margin: 0 auto; }
.home-sub-form input { flex: 1; min-height: 44px; padding: 0 1rem; border: 1.5px solid rgba(255,255,255,0.3); border-radius: 999px; background: rgba(255,255,255,0.1); color: #fff; font-size: 0.88rem; outline: none; min-width: 0; }
.home-sub-form input::placeholder { color: rgba(255,255,255,0.5); }
.home-sub-form input:focus { border-color: #FFC551; }
.home-sub-form button { min-height: 44px; padding: 0 1.5rem; border: 0; border-radius: 999px; background: #FFC551; color: #4C3500; cursor: pointer; font-size: 0.9rem; font-weight: 800; transition: transform 0.2s; }
.home-sub-form button:hover { transform: translateY(-2px); }
.home-sub-ok { color: #FFC551; font-size: 0.9rem; font-weight: 700; }

@media (max-width: 1100px) {
  .cat-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .hot-section { width: 100%; margin-left: 0; }
  .hot-with-trend { grid-template-columns: 1fr; }
  .hot-with-trend .hot-row { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .lifestyle-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .editorial-card { grid-template-columns: 1fr; }
  .editorial-img { height: 280px; }
  .recent-row { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .why-grid { grid-template-columns: 1fr; }
}

@media (max-width: 767px) {
  .section-title {
    align-items: flex-start;
    flex-direction: column;
  }

  .home-hero-grid {
    grid-template-columns: 1fr;
  }
  .hero-carousel {
    height: 380px;
    border-radius: 0;
  }

  .hero-slide::after {
    background: linear-gradient(180deg, rgba(17, 24, 39, 0.12), rgba(17, 24, 39, 0.88));
  }

  .hero-content {
    right: 1.25rem;
  }

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
