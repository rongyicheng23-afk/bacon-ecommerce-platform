<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '../stores/productStore'
import type { Product } from '../types'
import { addProductToCart } from '@/utils/cart'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'

type BehaviorAction = 'view' | 'favorite' | 'unfavorite' | 'cart' | 'buy'
type SortType = 'default' | 'discount-desc' | 'price-asc' | 'price-desc' | 'sales-desc'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const error = ref<string | null>(null)
const keyword = ref('')
const selectedCategory = ref('全部')
const selectedSubcategory = ref('全部')
const sortType = ref<SortType>('default')
const minPrice = ref('')
const maxPrice = ref('')
const stockOnly = ref(false)
const actionMessage = ref('')
const favoriteIds = ref<number[]>([])
const dealTab = ref('all')

/* countdown */
const countdown = ref({ hours: 3, minutes: 26, seconds: 18 })
let timer: number | undefined

const pad = (n: number) => String(n).padStart(2, '0')

const products = computed(() => productStore.products)
const mainCategories = computed(() => ['全部', ...new Set(products.value.map((p) => p.category || '精选'))])
const subcategories = computed(() => {
  if (selectedCategory.value === '全部') return []
  return ['全部', ...new Set(
    products.value.filter((p) => (p.category || '精选') === selectedCategory.value && p.subcategory).map((p) => p.subcategory!)
  )]
})
const categories = computed(() => selectedCategory.value !== '全部' && subcategories.value.length > 1 ? subcategories.value : mainCategories.value)

const dealStats = computed(() => {
  const list = products.value
  const maxDrop = Math.max(...list.map((p) => Math.round((1 - (p.price * 0.65) / p.price) * 100)))
  const minPrice2 = Math.min(...list.map((p) => Math.round(p.price * 0.65)))
  return { count: list.length, maxDrop, minPrice: minPrice2 }
})

const quickTabs = ['限时秒杀', '大牌直降', '百元以内', '满减专区', '清仓好物', '今日上新']

const filteredProducts = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase()
  const min = Number(minPrice.value)
  const max = Number(maxPrice.value)
  let list = products.value.filter((product) => {
    const matchedCategory = selectedCategory.value === '全部' || (product.category || '精选') === selectedCategory.value
    const matchedSubcategory = selectedSubcategory.value === '全部' || product.subcategory === selectedSubcategory.value
    const matchedKeyword = !normalizedKeyword || product.name.toLowerCase().includes(normalizedKeyword) || product.description.toLowerCase().includes(normalizedKeyword)
    const matchedMinPrice = !minPrice.value || product.price >= min
    const matchedMaxPrice = !maxPrice.value || product.price <= max
    const matchedStock = !stockOnly.value || product.stock > 0
    return matchedCategory && matchedSubcategory && matchedKeyword && matchedMinPrice && matchedMaxPrice && matchedStock
  })
  if (dealTab.value === 'flash') list = list.filter((_p: Product, i: number) => i % 3 === 0)
  if (dealTab.value === 'under100') list = list.filter((p: Product) => p.price < 100)
  return [...list].sort((a, b) => {
    if (sortType.value === 'price-asc') return a.price - b.price
    if (sortType.value === 'price-desc') return b.price - a.price
    if (sortType.value === 'sales-desc') return b.stock - a.stock
    if (sortType.value === 'discount-desc') return (b.price - a.price) - (a.price - b.price)
    return a.productId - b.productId
  })
})

const flashDeals = computed(() => products.value.slice(0, 5))
const under100Deals = computed(() => products.value.filter((p) => p.price < 100).slice(0, 5))
const digitalDeals = computed(() => products.value.filter((p) => p.category === '数码').slice(0, 5))
const fashionDeals = computed(() => products.value.filter((p) => p.category === '服饰').slice(0, 5))
const homeDeals = computed(() => products.value.filter((p) => p.category === '家居').slice(0, 5))

const getDiscount = (p: Product) => Math.round((1 - (p.price * 0.65) / p.price) * 100)
const getDealPrice = (p: Product) => Math.round(p.price * 0.65)
const getSoldPct = (p: Product) => Math.min(95, Math.round((1 - p.stock / 200) * 100))

const syncQuery = () => {
  keyword.value = typeof route.query.q === 'string' ? route.query.q : ''
  selectedCategory.value = typeof route.query.category === 'string' ? route.query.category : '全部'
  selectedSubcategory.value = typeof route.query.subcategory === 'string' ? route.query.subcategory : '全部'
  sortType.value = isSortType(route.query.sort) ? route.query.sort : 'default'
  minPrice.value = typeof route.query.minPrice === 'string' ? route.query.minPrice : ''
  maxPrice.value = typeof route.query.maxPrice === 'string' ? route.query.maxPrice : ''
  stockOnly.value = route.query.stock === '1'
}

const isSortType = (v: unknown): v is SortType => ['default', 'discount-desc', 'price-asc', 'price-desc', 'sales-desc'].includes(v as string)

const recordBehavior = (product: Product, action: BehaviorAction) => {
  const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  logs.push({ userId: 1, productId: product.productId, productName: product.name, action, category: product.category || '未分类', timestamp: new Date().toISOString() })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}
const navigateToDetail = (product: Product) => { recordBehavior(product, 'view'); router.push(`/product/${product.productId}`) }

const isFavorite = (id: number) => favoriteIds.value.includes(id)
const toggleFavorite = (p: Product) => {
  const was = isFavorite(p.productId)
  favoriteIds.value = toggleFavoriteId(p.productId)
  actionMessage.value = was ? `已取消收藏` : `已收藏《${p.name}》`
  setTimeout(() => actionMessage.value = '', 1500)
}
const addToCart = (p: Product) => { addProductToCart(p); actionMessage.value = `已加购《${p.name}》`; setTimeout(() => actionMessage.value = '', 1500) }
const submitSearch = () => router.replace({ path: '/products', query: { q: keyword.value.trim() || undefined, category: selectedCategory.value === '全部' ? undefined : selectedCategory.value, subcategory: selectedSubcategory.value === '全部' ? undefined : selectedSubcategory.value, sort: sortType.value === 'default' ? undefined : sortType.value, minPrice: minPrice.value || undefined, maxPrice: maxPrice.value || undefined, stock: stockOnly.value ? '1' : undefined } })
const selectCategory = (c: string) => {
  if (c === '全部') { if (selectedSubcategory.value !== '全部') selectedSubcategory.value = '全部'; else selectedCategory.value = '全部' }
  else if (mainCategories.value.includes(c)) { selectedCategory.value = c; selectedSubcategory.value = '全部' }
  else selectedSubcategory.value = c
  submitSearch()
}
const resetFilters = () => { keyword.value = ''; selectedCategory.value = '全部'; selectedSubcategory.value = '全部'; sortType.value = 'default'; minPrice.value = ''; maxPrice.value = ''; stockOnly.value = false; submitSearch() }
const handleImageError = (e: Event) => { (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85' }

watch(() => route.query, syncQuery)
onMounted(async () => {
  syncQuery(); favoriteIds.value = readFavoriteIds()
  try { if (products.value.length === 0) await productStore.fetchProducts() } catch (err) { error.value = err instanceof Error ? err.message : '加载失败' } finally { loading.value = false }
  timer = window.setInterval(() => {
    if (countdown.value.seconds > 0) countdown.value.seconds--
    else if (countdown.value.minutes > 0) { countdown.value.minutes--; countdown.value.seconds = 59 }
    else if (countdown.value.hours > 0) { countdown.value.hours--; countdown.value.minutes = 59; countdown.value.seconds = 59 }
  }, 1000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<template>
  <main class="catalog-page">
    <p v-if="actionMessage" class="action-toast">{{ actionMessage }}</p>

    <!-- hero -->
    <section class="deal-hero">
      <div class="deal-hero-bg">
        <span class="dh-deco dh-d1">SALE</span>
        <span class="dh-deco dh-d2">DEAL</span>
        <span class="dh-deco dh-d3">%</span>
      </div>
      <div class="deal-hero-content">
        <div class="deal-hero-left">
          <span class="deal-kicker">DAILY DEALS</span>
          <h1>今日特价</h1>
          <p>精选好物限时直降 · 每日更新，错过需再等一天</p>
          <div class="deal-stats">
            <div class="deal-stat"><strong>{{ dealStats.count }} 件</strong><span>今日特价</span></div>
            <div class="deal-stat"><strong>最高{{ dealStats.maxDrop }}%</strong><span>直降</span></div>
            <div class="deal-stat"><strong>¥{{ dealStats.minPrice }} 起</strong><span>最低价</span></div>
          </div>
        </div>
        <div class="deal-hero-right">
          <span class="countdown-label">距离今日特价结束</span>
          <div class="countdown-box">
            <span>{{ pad(countdown.hours) }}</span><em>:</em>
            <span>{{ pad(countdown.minutes) }}</span><em>:</em>
            <span>{{ pad(countdown.seconds) }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- quick entry chips -->
    <div class="deal-quick-chips">
      <button v-for="tab in quickTabs" :key="tab" :class="['dq-chip', { active: dealTab === (tab === '限时秒杀' ? 'flash' : tab === '百元以内' ? 'under100' : '') }]" @click="dealTab = tab === '限时秒杀' ? 'flash' : tab === '百元以内' ? 'under100' : 'all'">{{ tab }}</button>
    </div>

    <!-- filter panel -->
    <section class="filter-panel">
      <div class="filter-line">
        <span class="filter-label">分类</span>
        <div class="category-tabs">
          <button v-for="c in categories" :key="c" :class="{ active: c === selectedCategory || c === selectedSubcategory }" @click="selectCategory(c)">{{ c }}</button>
        </div>
      </div>
      <div class="filter-line">
        <span class="filter-label">价格</span>
        <form class="price-filter" @submit.prevent="submitSearch">
          <input v-model="minPrice" type="number" placeholder="最低价" />
          <span>-</span>
          <input v-model="maxPrice" type="number" placeholder="最高价" />
          <label class="stock-check"><input v-model="stockOnly" type="checkbox" />仅看有货</label>
          <button type="submit" class="confirm-btn">确定</button>
          <button type="button" class="ghost-btn" @click="resetFilters">重置</button>
        </form>
      </div>
      <div class="sort-row">
        <strong>共 {{ filteredProducts.length }} 件特价商品</strong>
        <select v-model="sortType" @change="submitSearch">
          <option value="default">综合排序</option>
          <option value="discount-desc">折扣从高到低</option>
          <option value="price-asc">价格从低到高</option>
          <option value="price-desc">价格从高到低</option>
          <option value="sales-desc">销量优先</option>
        </select>
      </div>

      <form class="search-box" @submit.prevent="submitSearch">
        <input v-model="keyword" type="search" placeholder="搜索耳机、背包、台灯..." />
        <button type="submit">搜索</button>
      </form>
    </section>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <template v-else>
      <!-- Flash deals -->
      <section v-if="flashDeals.length && dealTab === 'all'" class="deal-section">
        <div class="deal-section-head"><h3>⚡ 限时秒杀</h3><button class="more-link" @click="dealTab = 'flash'">查看全部 →</button></div>
        <div class="deal-grid">
          <article v-for="p in flashDeals" :key="'f-'+p.productId" class="deal-card" @click="navigateToDetail(p)">
            <div class="deal-img">
              <img :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" />
              <span class="discount-badge">{{ getDiscount(p) }}% OFF</span>
            </div>
            <div class="deal-body">
              <h4>{{ p.name }}</h4>
              <div class="deal-price-row"><strong>¥{{ getDealPrice(p) }}</strong><del>¥{{ p.price }}</del></div>
              <span class="deal-save">今日立省 ¥{{ p.price - getDealPrice(p) }}</span>
              <div class="deal-progress"><div class="deal-bar"><i :style="{ width: getSoldPct(p) + '%' }"></i></div><small>已抢 {{ getSoldPct(p) }}%</small></div>
              <div class="deal-actions" @click.stop>
                <button :class="{ active: isFavorite(p.productId) }" @click="toggleFavorite(p)">收藏</button>
                <button class="cart-btn" @click="addToCart(p)">加购</button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Under 100 -->
      <section v-if="under100Deals.length && dealTab === 'all'" class="deal-section">
        <div class="deal-section-head"><h3>💰 百元好物</h3><button class="more-link" @click="dealTab = 'under100'">查看全部 →</button></div>
        <div class="deal-grid">
          <article v-for="p in under100Deals" :key="'u-'+p.productId" class="deal-card" @click="navigateToDetail(p)">
            <div class="deal-img">
              <img :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" />
              <span class="discount-badge">{{ getDiscount(p) }}% OFF</span>
            </div>
            <div class="deal-body">
              <h4>{{ p.name }}</h4>
              <div class="deal-price-row"><strong>¥{{ getDealPrice(p) }}</strong><del>¥{{ p.price }}</del></div>
              <span class="deal-save">今日立省 ¥{{ p.price - getDealPrice(p) }}</span>
              <div class="deal-actions" @click.stop>
                <button :class="{ active: isFavorite(p.productId) }" @click="toggleFavorite(p)">收藏</button>
                <button class="cart-btn" @click="addToCart(p)">加购</button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Category deals -->
      <section v-if="digitalDeals.length && dealTab === 'all'" class="deal-section">
        <div class="deal-section-head"><h3>🔵 数码特价</h3><button class="more-link" @click="selectCategory('数码')">查看全部 →</button></div>
        <div class="deal-grid">
          <article v-for="p in digitalDeals" :key="'d-'+p.productId" class="deal-card" @click="navigateToDetail(p)">
            <div class="deal-img"><img :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" /><span class="discount-badge">{{ getDiscount(p) }}% OFF</span></div>
            <div class="deal-body"><h4>{{ p.name }}</h4><div class="deal-price-row"><strong>¥{{ getDealPrice(p) }}</strong><del>¥{{ p.price }}</del></div><div class="deal-actions" @click.stop><button :class="{ active: isFavorite(p.productId) }" @click="toggleFavorite(p)">收藏</button><button class="cart-btn" @click="addToCart(p)">加购</button></div></div>
          </article>
        </div>
      </section>

      <!-- Full grid -->
      <section class="deal-section">
        <div class="deal-section-head"><h3>全部特价商品</h3></div>
        <div class="deal-grid full-grid">
          <article v-for="p in filteredProducts" :key="'a-'+p.productId" class="deal-card" @click="navigateToDetail(p)">
            <div class="deal-img">
              <img :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" />
              <span class="discount-badge">{{ getDiscount(p) }}% OFF</span>
            </div>
            <div class="deal-body">
              <h4>{{ p.name }}</h4>
              <div class="deal-price-row"><strong>¥{{ getDealPrice(p) }}</strong><del>¥{{ p.price }}</del></div>
              <span class="deal-save">今日立省 ¥{{ p.price - getDealPrice(p) }}</span>
              <div class="deal-progress"><div class="deal-bar"><i :style="{ width: getSoldPct(p) + '%' }"></i></div><small>已抢 {{ getSoldPct(p) }}%</small></div>
              <div class="deal-actions" @click.stop>
                <button :class="{ active: isFavorite(p.productId) }" @click="toggleFavorite(p)">收藏</button>
                <button class="cart-btn" @click="addToCart(p)">加购</button>
              </div>
            </div>
          </article>
        </div>
      </section>
    </template>
  </main>
</template>

<style scoped>
.catalog-page { max-width: 100%; }

.action-toast {
  position: fixed; z-index: 120; right: 2rem; top: 5.5rem;
  padding: 0.75rem 1rem; border-radius: 999px; background: rgba(36,27,47,0.92);
  color: #fff; font-size: 0.875rem; box-shadow: 0 12px 30px rgba(15,23,42,0.2);
}

/* ---- hero ---- */
.deal-hero {
  position: relative; overflow: hidden;
  margin-bottom: 1.25rem; padding: 2.25rem 2.5rem; border-radius: 18px;
  background: linear-gradient(135deg, #351044 0%, #5A0B72 48%, #7B189F 100%); color: #fff;
}
.deal-hero-bg { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.dh-deco {
  position: absolute; font-family: "Arial Black", sans-serif; font-weight: 900;
  color: rgba(255,255,255,0.06); font-size: clamp(100px,14vw,240px); white-space: nowrap;
}
.dh-d1 { top: -20px; left: -10px; }
.dh-d2 { bottom: -30px; right: -20px; font-size: clamp(80px,10vw,180px); }
.dh-d3 { top: 40%; right: 15%; font-size: clamp(140px,18vw,300px); }
.deal-hero-content { position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: flex-start; gap: 2rem; }
.deal-kicker { display: inline-block; padding: 4px 14px; border: 1px solid rgba(255,255,255,0.3); border-radius: 999px; color: #F4D35E; font-size: 0.72rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 0.5rem; }
.deal-hero-left h1 { margin: 0; font-size: 2.2rem; font-weight: 900; }
.deal-hero-left > p { margin: 0.4rem 0 0; color: rgba(255,255,255,0.75); font-size: 0.92rem; }
.deal-stats { display: flex; gap: 1.5rem; margin-top: 1rem; }
.deal-stat strong { display: block; font-size: 1.1rem; }
.deal-stat span { color: #F4D35E; font-size: 0.72rem; font-weight: 700; }
.deal-hero-right { text-align: center; flex-shrink: 0; }
.countdown-label { display: block; color: rgba(255,255,255,0.7); font-size: 0.76rem; margin-bottom: 0.5rem; }
.countdown-box { display: flex; align-items: center; gap: 3px; }
.countdown-box span { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 6px; background: rgba(255,255,255,0.12); color: #F4D35E; font-size: 1.2rem; font-weight: 900; font-variant-numeric: tabular-nums; }
.countdown-box em { color: rgba(255,255,255,0.5); font-style: normal; font-size: 1.1rem; }

/* ---- quick chips ---- */
.deal-quick-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
.dq-chip {
  min-height: 34px; padding: 0 1rem; border: 1px solid #e5e7eb; border-radius: 999px;
  background: #fff; color: #241B2F; cursor: pointer; font-size: 0.82rem; font-weight: 700; transition: all 0.15s;
}
.dq-chip.active { background: #7B189F; color: #fff; border-color: #7B189F; }
.dq-chip:hover:not(.active) { background: #F3EAF8; border-color: #C9B2F0; }

/* ---- filter panel ---- */
.filter-panel { margin-bottom: 1rem; padding: 0.8rem 1rem; border-radius: 14px; background: #fff; box-shadow: 0 4px 16px rgba(15,23,42,0.05); }
.filter-line { display: flex; align-items: center; gap: 0.75rem; padding: 0.4rem 0; border-bottom: 1px solid #f1f2f4; }
.filter-line:last-of-type { border-bottom: 0; }
.filter-label { color: #241B2F; font-weight: 900; font-size: 0.84rem; width: 40px; flex-shrink: 0; }
.category-tabs { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.category-tabs button {
  min-height: 30px; padding: 0 0.75rem; border: 1px solid #e5e7eb; border-radius: 999px;
  background: #fff; color: #756D7E; cursor: pointer; font-size: 0.8rem; font-weight: 700; transition: all 0.15s;
}
.category-tabs button.active { background: #F3EAF8; color: #7B189F; border-color: #7B189F; }
.category-tabs button:hover:not(.active) { border-color: #C9B2F0; }
.price-filter { display: flex; flex-wrap: wrap; align-items: center; gap: 0.4rem; }
.price-filter input[type='number'] { width: 90px; min-height: 32px; padding: 0 0.5rem; border: 1px solid #e5e7eb; border-radius: 8px; outline: none; font-size: 0.82rem; }
.price-filter input:focus { border-color: #7B189F; }
.stock-check { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; color: #756D7E; cursor: pointer; font-weight: 700; }
.confirm-btn { min-height: 32px; padding: 0 1rem; border: 0; border-radius: 999px; background: #7B189F; color: #fff; cursor: pointer; font-size: 0.8rem; font-weight: 800; }
.ghost-btn { min-height: 32px; padding: 0 0.8rem; border: 1px solid #e5e7eb; border-radius: 999px; background: #fff; color: #756D7E; cursor: pointer; font-size: 0.8rem; font-weight: 700; }
.sort-row { display: flex; justify-content: space-between; align-items: center; padding-top: 0.5rem; }
.sort-row strong { color: #241B2F; font-size: 0.85rem; }
.sort-row select { min-height: 32px; padding: 0 0.5rem; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; font-size: 0.82rem; }

/* ---- deal sections ---- */
.deal-section { margin-bottom: 2rem; }
.deal-section-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.75rem; }
.deal-section-head h3 { margin: 0; color: #241B2F; font-size: 1.1rem; font-weight: 900; }
.more-link { border: 0; background: none; color: #7B189F; cursor: pointer; font-size: 0.82rem; font-weight: 700; }
.more-link:hover { text-decoration: underline; }

/* ---- deal grid ---- */
.deal-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1rem; }
.full-grid { gap: 22px; }

.deal-card {
  border-radius: 14px; background: #fff; overflow: hidden; cursor: pointer;
  box-shadow: 0 4px 14px rgba(15,23,42,0.05); transition: transform 0.25s, box-shadow 0.25s;
}
.deal-card:hover { transform: translateY(-4px); box-shadow: 0 16px 36px rgba(64,36,78,0.14); }
.deal-img { position: relative; aspect-ratio: 1; overflow: hidden; background: #f8fafc; }
.deal-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.35s; }
.deal-card:hover .deal-img img { transform: scale(1.03); }
.discount-badge {
  position: absolute; top: 8px; right: 8px; padding: 4px 10px; border-radius: 4px;
  background: #F4D35E; color: #5A4300; font-size: 0.72rem; font-weight: 900;
}
.deal-body { padding: 0.8rem; }
.deal-body h4 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0 0 0.3rem; color: #241B2F; font-size: 0.85rem; line-height: 1.3; }
.deal-price-row { display: flex; align-items: baseline; gap: 6px; }
.deal-price-row strong { color: #980B32; font-size: 1.05rem; font-weight: 800; }
.deal-price-row del { color: #A39BAA; font-size: 0.78rem; text-decoration: line-through; }
.deal-save { display: block; color: #980B32; font-size: 0.7rem; font-weight: 700; margin-top: 2px; }
.deal-progress { display: flex; align-items: center; gap: 6px; margin-top: 6px; }
.deal-bar { flex: 1; height: 5px; border-radius: 999px; background: #E8E3D8; overflow: hidden; }
.deal-bar i { display: block; height: 100%; border-radius: 999px; background: #F4D35E; }
.deal-progress small { color: #7A5B00; font-size: 0.66rem; font-weight: 700; flex-shrink: 0; }
.deal-actions { display: flex; gap: 6px; margin-top: 8px; }
.deal-actions button {
  flex: 1; min-height: 30px; padding: 0 0.5rem; border-radius: 999px; cursor: pointer;
  font-size: 0.72rem; font-weight: 700; transition: all 0.15s;
}
.deal-actions button:first-child { border: 1.5px solid #980B32; background: #fff; color: #980B32; }
.deal-actions button:first-child:hover, .deal-actions button:first-child.active { background: #F8EDF1; }
.deal-actions .cart-btn { border: 0; background: #7B189F; color: #fff; }
.deal-actions .cart-btn:hover { background: #5A0B72; }

.state { padding: 3rem; text-align: center; color: #756D7E; }
.state.error { color: #ff2f68; }

@media (min-width: 1500px) { .deal-grid { grid-template-columns: repeat(6, minmax(0, 1fr)); } }
@media (max-width: 1200px) { .deal-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 900px) { .deal-hero-content { flex-direction: column; } .deal-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 640px) {
  .deal-hero { padding: 1.5rem; }
  .deal-hero-left h1 { font-size: 1.6rem; }
  .deal-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.65rem; }
}
</style>
