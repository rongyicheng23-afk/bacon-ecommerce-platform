<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import type { Product } from '@/types'
import { addProductToCart } from '@/utils/cart'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'

const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const error = ref<string | null>(null)
const actionMessage = ref('')
const favoriteIds = ref<number[]>([])
const sortBy = ref<'sales' | 'price-asc' | 'price-desc'>('sales')

const products = computed(() => productStore.products)

const hotProducts = computed(() => {
  return [...products.value]
    .sort((a, b) => {
      if (sortBy.value === 'price-asc') return a.price - b.price
      if (sortBy.value === 'price-desc') return b.price - a.price
      return a.stock - b.stock
    })
})

const getRank = (index: number) => index + 1
const getSoldPct = (p: Product) => Math.min(98, Math.round((1 - p.stock / 200) * 100))
const getDiscount = (p: Product) => Math.round((1 - (p.price * 0.7) / p.price) * 100)
const getDealPrice = (p: Product) => Math.round(p.price * 0.7)

const isFavorite = (id: number) => favoriteIds.value.includes(id)
const toggleFavorite = (p: Product) => {
  favoriteIds.value = toggleFavoriteId(p.productId)
  actionMessage.value = isFavorite(p.productId) ? `已收藏《${p.name}》` : `已取消收藏`
  setTimeout(() => actionMessage.value = '', 1500)
}
const addToCart = (p: Product) => { addProductToCart(p); actionMessage.value = `已加购《${p.name}》`; setTimeout(() => actionMessage.value = '', 1500) }
const goDetail = (p: Product) => router.push(`/product/${p.productId}`)
const handleImageError = (e: Event) => { (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85' }

onMounted(async () => {
  favoriteIds.value = readFavoriteIds()
  try { if (products.value.length === 0) await productStore.fetchProducts() }
  catch (err) { error.value = err instanceof Error ? err.message : '加载失败' }
  finally { loading.value = false }
})
</script>

<template>
  <div class="hs-page">
    <p v-if="actionMessage" class="hs-toast">{{ actionMessage }}</p>

    <!-- hero -->
    <section class="hs-hero">
      <div class="hs-hero-text">
        <span class="hs-kicker">HOT SALES</span>
        <h1>热卖榜单</h1>
        <p>实时销量排行，大家都在买的好物</p>
      </div>
      <div class="hs-stats">
        <div class="hs-stat"><strong>{{ products.length }}+</strong><span>热门商品</span></div>
        <div class="hs-stat"><strong>TOP 20</strong><span>实时排名</span></div>
        <div class="hs-stat"><strong>24h</strong><span>更新一次</span></div>
      </div>
    </section>

    <!-- sort bar -->
    <div class="hs-toolbar">
      <span class="hs-count">共 {{ hotProducts.length }} 件热卖商品</span>
      <div class="hs-sort">
        <button :class="{ active: sortBy === 'sales' }" @click="sortBy = 'sales'">按销量</button>
        <button :class="{ active: sortBy === 'price-asc' }" @click="sortBy = 'price-asc'">价格 ↑</button>
        <button :class="{ active: sortBy === 'price-desc' }" @click="sortBy = 'price-desc'">价格 ↓</button>
      </div>
    </div>

    <div v-if="loading" class="hs-state">加载中...</div>
    <div v-else-if="error" class="hs-state err">{{ error }}</div>

    <div v-else class="hs-list">
      <article
        v-for="(p, idx) in hotProducts"
        :key="p.productId"
        :class="['hs-card', { top3: getRank(idx) <= 3 }]"
        @click="goDetail(p)"
      >
        <div class="hs-rank" :class="'rank-' + getRank(idx)">
          <span v-if="getRank(idx) <= 3" class="rank-icon">{{ getRank(idx) === 1 ? '👑' : getRank(idx) === 2 ? '🥈' : '🥉' }}</span>
          <span v-else class="rank-num">{{ getRank(idx) }}</span>
        </div>
        <div class="hs-img">
          <img :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" />
          <span v-if="getRank(idx) <= 3" class="hs-tag">TOP</span>
        </div>
        <div class="hs-info">
          <span class="hs-cat">{{ p.category || '精选' }}</span>
          <h3>{{ p.name }}</h3>
          <div class="hs-price-row">
            <strong>¥{{ getDealPrice(p) }}</strong>
            <del>¥{{ p.price }}</del>
            <span class="hs-discount">{{ getDiscount(p) }}% OFF</span>
          </div>
          <div class="hs-progress">
            <div class="hs-bar"><i :style="{ width: getSoldPct(p) + '%' }"></i></div>
            <small>已售 {{ getSoldPct(p) }}%</small>
          </div>
        </div>
        <div class="hs-actions" @click.stop>
          <button :class="{ active: isFavorite(p.productId) }" @click="toggleFavorite(p)">
            <svg viewBox="0 0 24 24" :fill="isFavorite(p.productId) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </button>
          <button class="hs-cart" @click="addToCart(p)">加购</button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.hs-page { max-width: 100%; }

.hs-toast {
  position: fixed; z-index: 120; right: 2rem; top: 5.5rem;
  padding: 0.7rem 1rem; border-radius: 999px; background: rgba(36,27,47,0.92);
  color: #fff; font-size: 0.84rem; box-shadow: 0 12px 30px rgba(15,23,42,0.2);
}

/* hero */
.hs-hero {
  display: flex; justify-content: space-between; align-items: flex-start; gap: 2rem;
  margin-bottom: 1.25rem; padding: 2.25rem 2.5rem; border-radius: 18px;
  background: linear-gradient(135deg, #351044 0%, #5A0B72 48%, #7B189F 100%); color: #fff;
}
.hs-kicker { display: inline-block; padding: 4px 14px; border: 1px solid rgba(255,255,255,0.3); border-radius: 999px; color: #F4D35E; font-size: 0.72rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 0.5rem; }
.hs-hero-text h1 { margin: 0; font-size: 2.2rem; font-weight: 900; }
.hs-hero-text > p { margin: 0.4rem 0 0; color: rgba(255,255,255,0.75); font-size: 0.92rem; }
.hs-stats { display: flex; gap: 1.5rem; }
.hs-stat strong { display: block; font-size: 1.1rem; }
.hs-stat span { color: #F4D35E; font-size: 0.72rem; font-weight: 700; }

/* toolbar */
.hs-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.hs-count { color: #756D7E; font-size: 0.85rem; font-weight: 700; }
.hs-sort { display: flex; gap: 0.35rem; }
.hs-sort button { min-height: 30px; padding: 0 0.7rem; border: 1px solid #e5e7eb; border-radius: 999px; background: #fff; color: #756D7E; cursor: pointer; font-size: 0.78rem; font-weight: 700; transition: all 0.15s; }
.hs-sort button.active { background: #F3EAF8; color: #7B189F; border-color: #7B189F; }

/* list */
.hs-list { display: flex; flex-direction: column; gap: 0.65rem; }

.hs-card {
  display: flex; align-items: center; gap: 1rem; padding: 1rem 1.25rem;
  border-radius: 14px; background: #fff; cursor: pointer;
  box-shadow: 0 2px 12px rgba(15,23,42,0.04); transition: transform 0.2s, box-shadow 0.2s;
}
.hs-card:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(64,36,78,0.12); }
.hs-card.top3 { border: 1.5px solid #F4D35E; }

.hs-rank { width: 48px; text-align: center; flex-shrink: 0; }
.rank-icon { font-size: 1.6rem; }
.rank-num { display: grid; width: 32px; height: 32px; place-items: center; border-radius: 50%; background: #f1f5f9; color: #756D7E; font-size: 0.9rem; font-weight: 900; margin: 0 auto; }
.rank-1 .rank-num, .rank-2 .rank-num, .rank-3 .rank-num { background: #F4D35E; color: #5A4300; }

.hs-img { position: relative; width: 80px; height: 80px; border-radius: 10px; overflow: hidden; flex-shrink: 0; background: #f8fafc; }
.hs-img img { width: 100%; height: 100%; object-fit: cover; }
.hs-tag { position: absolute; top: 4px; left: 4px; padding: 2px 6px; border-radius: 3px; background: #7B189F; color: #fff; font-size: 0.58rem; font-weight: 900; }

.hs-info { flex: 1; min-width: 0; }
.hs-cat { color: #7B189F; font-size: 0.7rem; font-weight: 800; }
.hs-info h3 { margin: 0.15rem 0 0.3rem; color: #241B2F; font-size: 0.92rem; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hs-price-row { display: flex; align-items: baseline; gap: 6px; }
.hs-price-row strong { color: #980B32; font-size: 1rem; font-weight: 800; }
.hs-price-row del { color: #A39BAA; font-size: 0.76rem; text-decoration: line-through; }
.hs-discount { color: #F4D35E; font-size: 0.7rem; font-weight: 900; background: rgba(244,211,94,0.15); padding: 1px 6px; border-radius: 4px; }
.hs-progress { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
.hs-bar { flex: 1; height: 4px; border-radius: 999px; background: #E8E3D8; overflow: hidden; }
.hs-bar i { display: block; height: 100%; border-radius: 999px; background: #F4D35E; }
.hs-progress small { color: #7A5B00; font-size: 0.66rem; font-weight: 700; flex-shrink: 0; }

.hs-actions { display: flex; gap: 6px; flex-shrink: 0; }
.hs-actions button {
  display: grid; width: 36px; height: 36px; place-items: center; border-radius: 50%;
  cursor: pointer; transition: all 0.15s;
}
.hs-actions button:first-child { border: 1.5px solid #980B32; background: #fff; color: #980B32; }
.hs-actions button:first-child svg { width: 15px; height: 15px; }
.hs-actions button:first-child.active, .hs-actions button:first-child:hover { background: #F8EDF1; }
.hs-cart { border: 0; background: #7B189F; color: #fff; font-size: 0.72rem; font-weight: 700; width: auto !important; padding: 0 14px; border-radius: 999px !important; }
.hs-cart:hover { background: #5A0B72; }

.hs-state { padding: 3rem; text-align: center; color: #756D7E; }
.hs-state.err { color: #ff2f68; }

@media (max-width: 768px) {
  .hs-hero { flex-direction: column; padding: 1.5rem; }
  .hs-card { flex-wrap: wrap; gap: 0.65rem; padding: 0.85rem; }
  .hs-actions { width: 100%; justify-content: flex-end; }
}
</style>
