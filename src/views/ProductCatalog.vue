<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '../stores/productStore'
import type { Product } from '../types'

type BehaviorAction = 'view' | 'favorite' | 'cart' | 'buy'
type SortType = 'default' | 'price-asc' | 'price-desc' | 'stock-desc'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const error = ref<string | null>(null)
const keyword = ref('')
const selectedCategory = ref('全部')
const sortType = ref<SortType>('default')
const minPrice = ref('')
const maxPrice = ref('')
const stockOnly = ref(false)
const actionMessage = ref('')

const products = computed(() => productStore.products)
const categories = computed(() => ['全部', ...new Set(products.value.map((product) => product.category || '精选'))])
const priceRange = computed(() => {
  if (products.value.length === 0) return { min: 0, max: 0 }
  const prices = products.value.map((product) => product.price)
  return {
    min: Math.min(...prices),
    max: Math.max(...prices)
  }
})

const activeFilters = computed(() => {
  const filters = []
  if (selectedCategory.value !== '全部') filters.push(`分类：${selectedCategory.value}`)
  if (keyword.value.trim()) filters.push(`搜索：${keyword.value.trim()}`)
  if (minPrice.value || maxPrice.value) {
    filters.push(`价格：${minPrice.value || priceRange.value.min} - ${maxPrice.value || priceRange.value.max}`)
  }
  if (stockOnly.value) filters.push('仅看有货')
  return filters
})

const filteredProducts = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase()
  const min = Number(minPrice.value)
  const max = Number(maxPrice.value)
  const list = products.value.filter((product) => {
    const matchedCategory = selectedCategory.value === '全部' || (product.category || '精选') === selectedCategory.value
    const matchedKeyword =
      !normalizedKeyword ||
      product.name.toLowerCase().includes(normalizedKeyword) ||
      product.description.toLowerCase().includes(normalizedKeyword)
    const matchedMinPrice = !minPrice.value || product.price >= min
    const matchedMaxPrice = !maxPrice.value || product.price <= max
    const matchedStock = !stockOnly.value || product.stock > 0

    return matchedCategory && matchedKeyword && matchedMinPrice && matchedMaxPrice && matchedStock
  })

  return [...list].sort((a, b) => {
    if (sortType.value === 'price-asc') return a.price - b.price
    if (sortType.value === 'price-desc') return b.price - a.price
    if (sortType.value === 'stock-desc') return b.stock - a.stock
    return a.productId - b.productId
  })
})

const syncQuery = () => {
  keyword.value = typeof route.query.q === 'string' ? route.query.q : ''
  selectedCategory.value = typeof route.query.category === 'string' ? route.query.category : '全部'
  sortType.value = isSortType(route.query.sort) ? route.query.sort : 'default'
  minPrice.value = typeof route.query.minPrice === 'string' ? route.query.minPrice : ''
  maxPrice.value = typeof route.query.maxPrice === 'string' ? route.query.maxPrice : ''
  stockOnly.value = route.query.stock === '1'
}

const isSortType = (value: unknown): value is SortType => {
  return value === 'default' || value === 'price-asc' || value === 'price-desc' || value === 'stock-desc'
}

const recordBehavior = (product: Product, action: BehaviorAction) => {
  const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
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

const navigateToDetail = (product: Product) => {
  recordBehavior(product, 'view')
  router.push(`/product/${product.productId}`)
}

const recordProductAction = (product: Product, action: Exclude<BehaviorAction, 'view'>) => {
  recordBehavior(product, action)
  const actionText = action === 'favorite' ? '收藏' : action === 'cart' ? '加购' : '购买'
  actionMessage.value = `已${actionText}《${product.name}》`
}

const submitSearch = () => {
  router.replace({
    path: '/products',
    query: {
      q: keyword.value.trim() || undefined,
      category: selectedCategory.value === '全部' ? undefined : selectedCategory.value,
      sort: sortType.value === 'default' ? undefined : sortType.value,
      minPrice: minPrice.value || undefined,
      maxPrice: maxPrice.value || undefined,
      stock: stockOnly.value ? '1' : undefined
    }
  })
}

const selectCategory = (category: string) => {
  selectedCategory.value = category
  submitSearch()
}

const resetFilters = () => {
  keyword.value = ''
  selectedCategory.value = '全部'
  sortType.value = 'default'
  minPrice.value = ''
  maxPrice.value = ''
  stockOnly.value = false
  submitSearch()
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

watch(() => route.query, syncQuery)

onMounted(async () => {
  syncQuery()
  try {
    if (productStore.products.length === 0) {
      await productStore.fetchProducts()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载商品失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="catalog-page">
    <p v-if="actionMessage" class="action-toast">{{ actionMessage }}</p>

    <section class="catalog-hero">
      <div>
        <span>Product discovery</span>
        <h1>发现好物</h1>
        <p>搜索、分类、价格区间和排序集中在这里，完整商品库由这个页面承载。</p>
      </div>

      <form class="search-box" @submit.prevent="submitSearch">
        <input v-model="keyword" type="search" placeholder="搜索耳机、背包、台灯..." />
        <button type="submit">搜索</button>
      </form>
    </section>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <template v-else>
      <section class="filter-panel" aria-label="商品筛选">
        <div class="filter-line">
          <span class="filter-label">分类</span>
          <div class="category-tabs">
            <button
              v-for="category in categories"
              :key="category"
              type="button"
              :class="{ active: category === selectedCategory }"
              @click="selectCategory(category)"
            >
              {{ category }}
            </button>
          </div>
        </div>

        <div class="filter-line">
          <span class="filter-label">价格</span>
          <form class="price-filter" @submit.prevent="submitSearch">
            <input v-model="minPrice" type="number" min="0" :placeholder="`最低 ${priceRange.min}`" />
            <span>-</span>
            <input v-model="maxPrice" type="number" min="0" :placeholder="`最高 ${priceRange.max}`" />
            <label class="stock-check">
              <input v-model="stockOnly" type="checkbox" />
              仅看有货
            </label>
            <button type="submit">确定</button>
            <button type="button" class="ghost-button" @click="resetFilters">重置</button>
          </form>
        </div>

        <div class="sort-row">
          <div class="result-summary">
            <strong>共 {{ filteredProducts.length }} 件商品</strong>
            <span v-if="activeFilters.length">已筛选：{{ activeFilters.join(' / ') }}</span>
          </div>
          <select v-model="sortType" aria-label="商品排序" @change="submitSearch">
            <option value="default">综合排序</option>
            <option value="price-asc">价格从低到高</option>
            <option value="price-desc">价格从高到低</option>
            <option value="stock-desc">库存优先</option>
          </select>
        </div>
      </section>

      <section v-if="filteredProducts.length" class="product-grid" aria-label="商品列表">
        <article
          v-for="product in filteredProducts"
          :key="product.productId"
          class="product-card"
          @click="navigateToDetail(product)"
        >
          <div class="product-image">
            <img :src="product.imageUrl || undefined" :alt="product.name" @error="handleImageError" />
          </div>
          <div class="product-info">
            <span>{{ product.category || '精选' }}</span>
            <h2>{{ product.name }}</h2>
            <p>{{ product.description }}</p>
            <div class="product-footer">
              <strong>¥{{ product.price }}</strong>
              <small>库存 {{ product.stock }}</small>
            </div>
            <div class="product-actions" @click.stop>
              <button type="button" @click="recordProductAction(product, 'favorite')">收藏</button>
              <button type="button" @click="recordProductAction(product, 'cart')">加购</button>
              <button type="button" class="buy-button" @click="recordProductAction(product, 'buy')">购买</button>
            </div>
          </div>
        </article>
      </section>

      <section v-else class="empty-state">
        <h2>没有找到相关商品</h2>
        <p>可以换个关键词，或者重置筛选条件再试一次。</p>
        <button type="button" @click="resetFilters">重置筛选</button>
      </section>
    </template>
  </main>
</template>

<style scoped>
.catalog-page {
  width: 100%;
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

.catalog-hero {
  display: grid;
  grid-template-columns: 1fr minmax(360px, 520px);
  gap: 2rem;
  align-items: end;
  margin-bottom: 1.5rem;
  padding: 2rem;
  border-radius: 18px;
  background: linear-gradient(135deg, #111827, #2d1b42);
  color: #fff;
}

.catalog-hero span {
  color: #ffd7df;
  font-size: 0.875rem;
  font-weight: 800;
}

.catalog-hero h1 {
  margin: 0.25rem 0 0.5rem;
  font-size: 2.4rem;
}

.catalog-hero p {
  max-width: 520px;
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
}

.search-box {
  display: flex;
  min-height: 48px;
  padding: 0.3rem;
  border-radius: 999px;
  background: #fff;
}

.search-box input {
  flex: 1;
  min-width: 0;
  padding: 0 1rem;
  border: 0;
  outline: none;
  font-size: 1rem;
}

.search-box button {
  min-width: 88px;
  border: 0;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  cursor: pointer;
  font-weight: 800;
}

.filter-panel {
  margin-bottom: 1rem;
  padding: 1rem 1.1rem;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.filter-line {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 1rem;
  align-items: start;
  padding: 0.8rem 0;
  border-bottom: 1px solid #f1f2f4;
}

.filter-line:first-child {
  padding-top: 0;
}

.filter-label {
  color: #111827;
  font-weight: 900;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.category-tabs button {
  min-height: 36px;
  padding: 0 0.9rem;
  border: 1px solid #ececec;
  border-radius: 999px;
  background: #fafafa;
  color: #333;
  cursor: pointer;
  font-weight: 700;
}

.category-tabs button.active {
  border-color: #fe2c55;
  background: #fff2f5;
  color: #fe2c55;
}

.price-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}

.price-filter input[type='number'] {
  width: 112px;
  min-height: 36px;
  padding: 0 0.7rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  outline: none;
}

.price-filter input[type='number']:focus {
  border-color: #fe2c55;
}

.stock-check {
  display: inline-flex;
  gap: 0.35rem;
  align-items: center;
  min-height: 36px;
  color: #333;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
}

.price-filter button,
.empty-state button {
  min-height: 36px;
  padding: 0 0.9rem;
  border: 0;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  cursor: pointer;
  font-weight: 800;
}

.price-filter .ghost-button {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #333;
}

.sort-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding-top: 0.8rem;
  color: #666;
}

.result-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}

.result-summary strong {
  color: #111827;
}

.result-summary span {
  color: #777;
  font-size: 0.86rem;
}

.sort-row select {
  min-height: 36px;
  padding: 0 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 14px;
  background: #fff;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.12);
}

.product-image {
  aspect-ratio: 1;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.35s ease;
}

.product-card:hover img {
  transform: scale(1.04);
}

.product-info {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0.75rem;
}

.product-info span {
  color: #fe2c55;
  font-size: 0.78rem;
  font-weight: 800;
}

.product-info h2 {
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

.product-info p {
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

.product-footer {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
  margin-top: auto;
}

.product-footer strong {
  color: #fe2c55;
  font-size: 1.05rem;
}

.product-footer small {
  color: #999;
}

.product-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.35rem;
  margin-top: 0.75rem;
}

.product-actions button {
  min-height: 1.8rem;
  padding: 0 0.45rem;
  border: 1px solid #f1f1f1;
  border-radius: 999px;
  background: #fafafa;
  color: #111827;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
}

.product-actions button:hover {
  border-color: #fe2c55;
  color: #fe2c55;
}

.product-actions .buy-button {
  border-color: #fe2c55;
  background: #fe2c55;
  color: #fff;
}

.state {
  padding: 3rem;
  color: #6b7280;
  text-align: center;
}

.error {
  color: #ff4d4f;
}

.empty-state {
  padding: 4rem 1rem;
  border-radius: 14px;
  background: #fff;
  color: #666;
  text-align: center;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.empty-state h2 {
  margin: 0 0 0.5rem;
  color: #111827;
}

.empty-state p {
  margin: 0 0 1rem;
}

@media (min-width: 1400px) {
  .product-grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}

@media (min-width: 768px) and (max-width: 1100px) {
  .catalog-hero {
    grid-template-columns: 1fr;
  }

  .product-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .catalog-hero {
    grid-template-columns: 1fr;
    padding: 1.25rem;
  }

  .catalog-hero h1 {
    font-size: 2rem;
  }

  .sort-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .filter-line {
    grid-template-columns: 1fr;
    gap: 0.6rem;
  }

  .product-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
