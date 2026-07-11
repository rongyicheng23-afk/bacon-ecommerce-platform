<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import type { Product } from '@/types'
import { addProductToCart } from '@/utils/cart'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const error = ref<string | null>(null)
const actionMessage = ref('')
const favoriteIds = ref<number[]>([])
const sortType = ref<'default' | 'price-asc' | 'price-desc' | 'stock-desc'>('default')
const minPrice = ref('')
const maxPrice = ref('')
const stockOnly = ref(false)

const categoryKey = computed(() => (route.params.category as string) || '')
const categoryLabel = computed(() => {
  const map: Record<string, string> = { digital: '数码家电', fashion: '服饰穿搭', home: '家居生活', quality: '品质生活' }
  return map[categoryKey.value] || '商品分类'
})
const categoryFilter = computed(() => {
  const map: Record<string, string> = { digital: '数码', fashion: '服饰', home: '家居', quality: '家居' }
  return map[categoryKey.value] || ''
})

const products = computed(() => productStore.products)
const selectedMainCategory = ref('全部')
const selectedSubcategory = ref('全部')

const mainCategories = computed(() => ['全部', ...new Set(products.value.map((p) => p.category || '精选'))])
const isMainCat = (v: string) => mainCategories.value.includes(v)

const subcategories = computed(() => {
  if (selectedMainCategory.value === '全部') return []
  return ['全部', ...new Set(
    products.value.filter((p) => (p.category || '精选') === selectedMainCategory.value && p.subcategory).map((p) => p.subcategory!)
  )]
})

const categories = computed(() => {
  if (selectedMainCategory.value !== '全部' && subcategories.value.length > 1) return subcategories.value
  return mainCategories.value
})

const selectCategory = (c: string) => {
  if (c === '全部') {
    if (selectedSubcategory.value !== '全部') selectedSubcategory.value = '全部'
    else selectedMainCategory.value = '全部'
  } else if (isMainCat(c)) { selectedMainCategory.value = c; selectedSubcategory.value = '全部' }
  else selectedSubcategory.value = c
}

const filteredProducts = computed(() => {
  const min = Number(minPrice.value)
  const max = Number(maxPrice.value)
  let list = products.value.filter((p) => {
    const mainOk = selectedMainCategory.value === '全部' || (p.category || '精选') === selectedMainCategory.value
    const subOk = selectedSubcategory.value === '全部' || p.subcategory === selectedSubcategory.value
    const minOk = !minPrice.value || p.price >= min
    const maxOk = !maxPrice.value || p.price <= max
    const stockOk = !stockOnly.value || p.stock > 0
    return mainOk && subOk && minOk && maxOk && stockOk
  })
  return [...list].sort((a, b) => {
    if (sortType.value === 'price-asc') return a.price - b.price
    if (sortType.value === 'price-desc') return b.price - a.price
    if (sortType.value === 'stock-desc') return b.stock - a.stock
    return a.productId - b.productId
  })
})

const getProductTags = (p: Product) => {
  const tags: Array<{ text: string; type: string }> = []
  if (p.stock < 50) tags.push({ text: '热卖', type: 'hot' })
  if (p.price < 100) tags.push({ text: '超值', type: 'value' })
  if (p.stock < 20) tags.push({ text: '库存紧张', type: 'urgent' })
  if (p.productId % 7 === 0) tags.push({ text: '新品', type: 'new' })
  return tags.slice(0, 2)
}

const isFavorite = (id: number) => favoriteIds.value.includes(id)
const toggleFavorite = (p: Product) => {
  favoriteIds.value = toggleFavoriteId(p.productId)
  actionMessage.value = isFavorite(p.productId) ? `已收藏《${p.name}》` : `已取消收藏`
  setTimeout(() => actionMessage.value = '', 1500)
}
const addToCart = (p: Product) => { addProductToCart(p); actionMessage.value = `已加购《${p.name}》`; setTimeout(() => actionMessage.value = '', 1500) }
const goDetail = (p: Product) => router.push(`/product/${p.productId}`)
const resetFilters = () => { selectedMainCategory.value = '全部'; selectedSubcategory.value = '全部'; sortType.value = 'default'; minPrice.value = ''; maxPrice.value = ''; stockOnly.value = false }
const handleImageError = (e: Event) => { (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85' }

const heroContent: Record<string, { en: string; title: string; desc: string; gradient: string }> = {
  digital:  { en: 'DIGITAL ELECTRONICS', title: '数码家电', desc: '智能设备、高效办公、便携生活', gradient: 'linear-gradient(135deg, #1e293b 0%, #1e3a5f 50%, #2563eb 100%)' },
  fashion:  { en: 'FASHION & STYLE', title: '服饰穿搭', desc: '背包、出行与日常搭配好物', gradient: 'linear-gradient(135deg, #2d1b2e 0%, #4a1d5e 50%, #a855f7 100%)' },
  home:     { en: 'HOME & LIVING', title: '家居生活', desc: '温馨居家、品质生活、好物优选', gradient: 'linear-gradient(135deg, #1e293b 0%, #1e3a5f 50%, #2563eb 100%)' },
  quality:  { en: 'QUALITY LIFE', title: '品质生活', desc: '精选好物，提升日常生活品质', gradient: 'linear-gradient(135deg, #1e293b 0%, #3b2d5b 50%, #7B189F 100%)' },
}

watch(() => route.params.category, () => { selectedMainCategory.value = categoryFilter.value || '全部' })

onMounted(async () => {
  favoriteIds.value = readFavoriteIds()
  selectedMainCategory.value = categoryFilter.value || '全部'
  try { if (products.value.length === 0) await productStore.fetchProducts() } catch (err) { error.value = err instanceof Error ? err.message : '加载失败' } finally { loading.value = false }
})
</script>

<template>
  <main class="cat-page">
    <p v-if="actionMessage" class="cat-toast">{{ actionMessage }}</p>

    <!-- Hero -->
    <section class="cat-hero" :style="{ background: heroContent[categoryKey]?.gradient || heroContent.digital.gradient }">
      <div>
        <span>{{ heroContent[categoryKey]?.en || 'CATEGORY' }}</span>
        <h1>{{ heroContent[categoryKey]?.title || categoryLabel }}</h1>
        <p>{{ heroContent[categoryKey]?.desc || '探索精选好物' }}</p>
      </div>
    </section>

    <div v-if="loading" class="cat-state">加载中...</div>
    <div v-else-if="error" class="cat-state err">{{ error }}</div>

    <template v-else>
      <!-- Filter -->
      <section class="cat-filter">
        <div class="cat-filter-line">
          <span class="cat-filter-label">分类</span>
          <div class="cat-tabs">
            <button v-for="c in categories" :key="c" :class="{ active: c === selectedMainCategory || c === selectedSubcategory }" @click="selectCategory(c)">{{ c }}</button>
          </div>
        </div>
        <div class="cat-filter-line">
          <span class="cat-filter-label">价格</span>
          <form class="cat-price-row" @submit.prevent>
            <input v-model="minPrice" type="number" placeholder="最低价" />
            <span>-</span>
            <input v-model="maxPrice" type="number" placeholder="最高价" />
            <label class="cat-check"><input v-model="stockOnly" type="checkbox" />仅看有货</label>
            <button type="submit" class="cat-confirm" @click="() => {}">确定</button>
            <button type="button" class="cat-reset" @click="resetFilters">重置</button>
          </form>
        </div>
        <div class="cat-sort-row">
          <strong>共 {{ filteredProducts.length }} 件商品</strong>
          <select v-model="sortType">
            <option value="default">综合排序</option>
            <option value="price-asc">价格从低到高</option>
            <option value="price-desc">价格从高到低</option>
            <option value="stock-desc">库存优先</option>
          </select>
        </div>
      </section>

      <!-- Grid -->
      <div v-if="filteredProducts.length" class="cat-grid">
        <article v-for="p in filteredProducts" :key="p.productId" class="cat-card" @click="goDetail(p)">
          <div class="cat-card-img">
            <img :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" />
            <div v-if="getProductTags(p).length" class="cat-card-tags">
              <span v-for="t in getProductTags(p)" :key="t.text" :class="['cat-tag', t.type]">{{ t.text }}</span>
            </div>
          </div>
          <div class="cat-card-body">
            <span class="cat-card-cat">{{ p.category || '精选' }}</span>
            <h2>{{ p.name }}</h2>
            <p>{{ p.description }}</p>
            <div class="cat-card-footer">
              <strong>¥{{ p.price }}</strong>
              <small>库存 {{ p.stock }}</small>
            </div>
            <div class="cat-card-btns" @click.stop>
              <button :class="{ active: isFavorite(p.productId) }" @click="toggleFavorite(p)">收藏</button>
              <button @click="addToCart(p)">加购</button>
            </div>
          </div>
        </article>
      </div>
      <div v-else class="cat-empty">
        <h2>没有找到相关商品</h2>
        <p>可以换个分类或重置筛选条件再试一次。</p>
        <button @click="resetFilters">重置筛选</button>
      </div>
    </template>
  </main>
</template>

<style scoped>
.cat-page { max-width: 100%; }
.cat-toast { position: fixed; z-index: 120; right: 2rem; top: 5.5rem; padding: 0.65rem 1rem; border-radius: 999px; background: rgba(36,27,47,0.92); color: #fff; font-size: 0.84rem; font-weight: 700; }

.cat-hero { padding: 2rem 2.5rem; border-radius: 18px; color: #fff; margin-bottom: 1.5rem; }
.cat-hero span { font-size: 0.78rem; font-weight: 800; letter-spacing: 1px; opacity: 0.8; }
.cat-hero h1 { margin: 0.25rem 0 0.4rem; font-size: 2.2rem; font-weight: 900; }
.cat-hero p { margin: 0; opacity: 0.78; font-size: 0.92rem; }

.cat-filter { margin-bottom: 1rem; padding: 1rem; border-radius: 14px; background: #fff; box-shadow: 0 4px 14px rgba(15,23,42,0.04); }
.cat-filter-line { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.5rem 0; border-bottom: 1px solid #f1f2f4; }
.cat-filter-line:last-of-type { border-bottom: 0; }
.cat-filter-label { color: #241B2F; font-weight: 900; font-size: 0.84rem; width: 36px; flex-shrink: 0; padding-top: 4px; }
.cat-tabs { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.cat-tabs button { min-height: 30px; padding: 0 0.75rem; border: 1px solid #e5e7eb; border-radius: 999px; background: #fff; color: #756D7E; cursor: pointer; font-size: 0.8rem; font-weight: 700; transition: all 0.15s; }
.cat-tabs button.active { background: #F3EAF8; color: #7B189F; border-color: #7B189F; }
.cat-price-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.4rem; }
.cat-price-row input[type='number'] { width: 90px; min-height: 32px; padding: 0 0.5rem; border: 1px solid #e5e7eb; border-radius: 8px; outline: none; font-size: 0.8rem; }
.cat-price-row input:focus { border-color: #7B189F; }
.cat-check { display: flex; align-items: center; gap: 4px; font-size: 0.78rem; color: #756D7E; cursor: pointer; font-weight: 700; }
.cat-confirm { min-height: 32px; padding: 0 1rem; border: 0; border-radius: 999px; background: #7B189F; color: #fff; cursor: pointer; font-size: 0.8rem; font-weight: 800; }
.cat-reset { min-height: 32px; padding: 0 0.8rem; border: 1px solid #e5e7eb; border-radius: 999px; background: #fff; color: #756D7E; cursor: pointer; font-size: 0.8rem; font-weight: 700; }
.cat-sort-row { display: flex; justify-content: space-between; align-items: center; padding-top: 0.5rem; }
.cat-sort-row strong { color: #241B2F; font-size: 0.84rem; }
.cat-sort-row select { min-height: 30px; padding: 0 0.5rem; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 0.8rem; }

.cat-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1rem; }
.cat-card { border-radius: 14px; background: #fff; overflow: hidden; cursor: pointer; box-shadow: 0 2px 10px rgba(15,23,42,0.04); transition: transform 0.2s, box-shadow 0.2s; }
.cat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 28px rgba(64,36,78,0.1); }
.cat-card-img { position: relative; aspect-ratio: 1; overflow: hidden; background: #f8fafc; }
.cat-card-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.35s; }
.cat-card:hover .cat-card-img img { transform: scale(1.04); }
.cat-card-tags { position: absolute; top: 8px; left: 8px; display: flex; flex-direction: column; gap: 4px; }
.cat-tag { padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 900; }
.cat-tag.hot { background: linear-gradient(135deg, #FF5A36, #ff2f68); color: #fff; }
.cat-tag.value { background: #6366f1; color: #fff; }
.cat-tag.urgent { background: #FFD84D; color: #422006; }
.cat-tag.new { background: #FFD84D; color: #422006; }
.cat-card-body { padding: 0.75rem; }
.cat-card-cat { color: #7B189F; font-size: 0.7rem; font-weight: 800; }
.cat-card-body h2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0.2rem 0 0.3rem; color: #241B2F; font-size: 0.88rem; line-height: 1.35; }
.cat-card-body p { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0 0 0.5rem; color: #756D7E; font-size: 0.76rem; line-height: 1.5; }
.cat-card-footer { display: flex; justify-content: space-between; align-items: center; }
.cat-card-footer strong { color: #980B32; font-size: 0.95rem; font-weight: 800; }
.cat-card-footer small { color: #A39BAA; font-size: 0.7rem; }
.cat-card-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 8px; }
.cat-card-btns button { min-height: 28px; padding: 0 0.4rem; border-radius: 999px; cursor: pointer; font-size: 0.7rem; font-weight: 700; transition: all 0.15s; }
.cat-card-btns button:first-child { border: 1.5px solid #980B32; background: #fff; color: #980B32; }
.cat-card-btns button:first-child:hover, .cat-card-btns button:first-child.active { background: #F8EDF1; }
.cat-card-btns button:last-child { border: 0; background: #7B189F; color: #fff; }
.cat-card-btns button:last-child:hover { background: #5A0B72; }
.cat-empty { text-align: center; padding: 3rem 1rem; background: #fff; border-radius: 14px; }
.cat-empty h2 { color: #241B2F; margin: 0 0 0.4rem; }
.cat-empty p { color: #756D7E; font-size: 0.88rem; margin: 0 0 1rem; }
.cat-empty button { min-height: 36px; padding: 0 1.25rem; border: 0; border-radius: 999px; background: #7B189F; color: #fff; cursor: pointer; font-weight: 800; }
.cat-state { padding: 3rem; text-align: center; color: #756D7E; } .cat-state.err { color: #ff2f68; }

@media (min-width: 1500px) { .cat-grid { grid-template-columns: repeat(6, minmax(0, 1fr)); } }
@media (max-width: 1100px) { .cat-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 767px) { .cat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .cat-hero { padding: 1.25rem; } .cat-hero h1 { font-size: 1.6rem; } }
</style>
