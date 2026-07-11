<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Product, ProductSku } from '@/types'
import { productService } from '@/services/productService'
import { useProductStore } from '@/stores/productStore'
import { addProductToCart } from '@/utils/cart'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'
import MagnifiableImage from '@/components/MagnifiableImage.vue'

type BehaviorAction = 'view' | 'favorite' | 'unfavorite' | 'cart' | 'buy' | 'view_recommendation'
type DetailTab = 'detail' | 'reviews' | 'recommend'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const product = ref<Product | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const selectedSkuId = ref<number>(0)
const mainImageIndex = ref(0)
const quantity = ref(1)
const activeTab = ref<DetailTab>('detail')
const actionMessage = ref('')
const favoriteIds = ref<number[]>([])

const serviceItems = ['正品保障', '极速配送', '7天无理由', '售后无忧']
const reviews = [
  { user: '用户 A', rating: 5, content: '商品质感不错，物流也很快，整体符合预期。' },
  { user: '用户 B', rating: 5, content: '包装完整，价格合适，日常使用很方便。' },
  { user: '用户 C', rating: 4, content: '功能比较实用，后续还会继续关注同类商品。' }
]

/** 当前选中的 SKU */
const selectedSku = computed<ProductSku | null>(() => {
  if (!product.value) return null
  const skus = product.value.skus
  if (skus.length === 0) return null
  return skus.find((s) => s.skuId === selectedSkuId.value) || skus[0]
})

/** 当前展示价格（选中 SKU 的价格，无 SKU 则用商品最低价） */
const currentPrice = computed(() => {
  return selectedSku.value?.price ?? product.value?.price ?? 0
})

/** 当前可用库存（选中 SKU 的库存，无 SKU 则用总库存） */
const currentStock = computed(() => {
  return selectedSku.value?.stock ?? product.value?.stock ?? 0
})

/** 按属性分组 SKU，用于渲染规格选择面板 */
const skuGroups = computed(() => {
  if (!product.value) return []
  const skus = product.value.skus
  const attrKeys = skus.length > 0 ? Object.keys(skus[0].attributes) : []
  return attrKeys.map((key) => ({
    label: key,
    values: [...new Set(skus.map((s) => s.attributes[key] as string))].map(
      (value) => ({
        value,
        available: skus.some((s) => s.attributes[key] === value)
      })
    )
  }))
})

/** 选中某个规格值 */
const selectSkuAttribute = (attrLabel: string, attrValue: string) => {
  if (!product.value) return
  const { skus } = product.value
  // 尝试找到完全匹配当前所有已选属性的 SKU
  let targetSku: ProductSku | undefined

  if (selectedSku.value) {
    const currentAttrs = { ...selectedSku.value.attributes, [attrLabel]: attrValue }
    targetSku = skus.find((s) =>
      Object.entries(currentAttrs).every(([k, v]) => s.attributes[k] === v)
    )
  }

  if (!targetSku) {
    targetSku = skus.find((s) => s.attributes[attrLabel] === attrValue)
  }

  if (targetSku) {
    selectedSkuId.value = targetSku.skuId
    // 切换 SKU 时更新主图为该 SKU 对应的图片
    const skuImageIndex = product.value.imageUrls.indexOf(targetSku.imageUrl)
    if (skuImageIndex >= 0) {
      mainImageIndex.value = skuImageIndex
    }
    // 数量不能超过 SKU 库存
    quantity.value = Math.max(1, Math.min(quantity.value, targetSku.stock))
  }
}

const relatedProducts = computed(() => {
  if (!product.value) return []
  return productStore.products
    .filter((item) => item.productId !== product.value?.productId && item.category === product.value?.category)
    .slice(0, 6)
})

const canBuy = computed(() => {
  return Boolean(product.value && product.value.status === 'active' && currentStock.value > 0)
})

const readBehaviorLogs = () => {
  try {
    return JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  } catch {
    return []
  }
}

const recordBehavior = (target: Product, action: BehaviorAction) => {
  const logs = readBehaviorLogs()
  logs.push({
    userId: 1,
    productId: target.productId,
    productName: target.name,
    action,
    category: target.category || '未分类',
    quantity: quantity.value,
    skuId: selectedSkuId.value,
    skuName: selectedSku.value?.name || '',
    timestamp: new Date().toISOString()
  })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}

const fetchProduct = async () => {
  const productId = Number(route.params.id)
  if (Number.isNaN(productId)) {
    error.value = '无效的商品ID'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null
    const response = await productService.getProduct(productId)
    if (response.code === '0000' && response.data) {
      product.value = Array.isArray(response.data) ? response.data[0] : response.data
      if (product.value) {
        recordBehavior(product.value, 'view')
      }
      if (productStore.products.length === 0) {
        await productStore.fetchProducts()
      }
    } else {
      error.value = response.info || '获取商品信息失败'
    }
  } catch {
    error.value = '获取商品信息失败'
  } finally {
    loading.value = false
  }
}

const setQuantity = (value: number) => {
  quantity.value = Math.max(1, Math.min(value, currentStock.value || 1))
}

const handleAction = (action: Exclude<BehaviorAction, 'view' | 'view_recommendation'>) => {
  if (!product.value || !canBuy.value) return
  recordBehavior(product.value, action)
  const actionText = action === 'favorite' ? '收藏' : action === 'unfavorite' ? '取消收藏' : action === 'cart' ? '加入购物车' : '立即购买'
  actionMessage.value = `已${actionText}《${product.value.name}》`
}

const isFavorite = computed(() => {
  return Boolean(product.value && favoriteIds.value.includes(product.value.productId))
})

const toggleFavorite = () => {
  if (!product.value || !canBuy.value) return
  const wasFavorite = isFavorite.value
  favoriteIds.value = toggleFavoriteId(product.value.productId)
  handleAction(wasFavorite ? 'unfavorite' : 'favorite')
}

const addToCart = () => {
  if (!product.value || !canBuy.value) return
  addProductToCart(product.value, {
    quantity: quantity.value,
    sku: selectedSku.value ?? undefined
  })
  handleAction('cart')
}

const buyNow = () => {
  if (!product.value || !canBuy.value) return
  addProductToCart(product.value, {
    quantity: quantity.value,
    sku: selectedSku.value ?? undefined
  })
  handleAction('buy')
  router.push('/cart')
}

const openRelatedProduct = (target: Product) => {
  recordBehavior(target, 'view_recommendation')
  router.push(`/product/${target.productId}`)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

watch(() => route.params.id, fetchProduct)

onMounted(() => {
  favoriteIds.value = readFavoriteIds()
  fetchProduct()
})
</script>

<template>
  <main class="detail-page">
    <p v-if="actionMessage" class="action-toast">{{ actionMessage }}</p>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <template v-else-if="product">
      <section class="product-shell">
        <div class="gallery-panel">
          <div class="main-image">
            <MagnifiableImage
              :src="product.imageUrls[mainImageIndex] || product.imageUrls[0]"
              :alt="product.name"
              :zoom-scale="2.5"
            />
          </div>
          <div v-if="product.imageUrls.length > 1" class="thumb-row">
            <button
              v-for="(img, index) in product.imageUrls"
              :key="index"
              type="button"
              :class="['thumb-button', { active: mainImageIndex === index }]"
              @click="mainImageIndex = index"
            >
              <img :src="img" :alt="`${product.name} 图 ${index + 1}`" @error="handleImageError" />
            </button>
          </div>
        </div>

        <section class="purchase-panel">
          <div class="title-row">
            <span class="category">{{ product.category || '精选' }}</span>
            <h1>{{ product.name }}</h1>
            <p>{{ product.description }}</p>
          </div>

          <div class="price-box">
            <span>平台价</span>
            <strong>¥{{ currentPrice }}</strong>
            <small v-if="selectedSku">已选：{{ selectedSku.name }}</small>
            <small>累计评价 {{ reviews.length * 128 }}+</small>
          </div>

          <div class="meta-grid">
            <div>
              <span>库存</span>
              <strong>{{ currentStock }}</strong>
            </div>
            <div>
              <span>销量</span>
              <strong>{{ 300 + product.productId }}</strong>
            </div>
            <div>
              <span>评分</span>
              <strong>4.8</strong>
            </div>
          </div>

          <div
            v-for="group in skuGroups"
            :key="group.label"
            class="option-block"
          >
            <span class="option-label">{{ group.label }}</span>
            <div class="spec-row">
              <button
                v-for="option in group.values"
                :key="option.value"
                type="button"
                :class="{
                  active: selectedSku?.attributes[group.label] === option.value,
                  disabled: !option.available
                }"
                :disabled="!option.available"
                @click="selectSkuAttribute(group.label, option.value)"
              >
                {{ option.value }}
              </button>
            </div>
          </div>

          <div class="option-block">
            <span class="option-label">配送</span>
            <p class="delivery-text">广东广州 至 默认地址，预计 48 小时内发货</p>
          </div>

          <div class="option-block">
            <span class="option-label">数量</span>
            <div class="quantity-stepper">
              <button type="button" @click="setQuantity(quantity - 1)">-</button>
              <input :value="quantity" type="number" min="1" :max="product.stock" @input="setQuantity(Number(($event.target as HTMLInputElement).value))" />
              <button type="button" @click="setQuantity(quantity + 1)">+</button>
            </div>
          </div>

          <div class="service-row">
            <span v-for="item in serviceItems" :key="item">{{ item }}</span>
          </div>

          <div class="action-buttons">
            <button
              type="button"
              :class="['ghost-button', { active: isFavorite }]"
              :disabled="!canBuy"
              @click="toggleFavorite"
            >
              {{ isFavorite ? '已收藏' : '收藏' }}
            </button>
            <button type="button" class="cart-button" :disabled="!canBuy" @click="addToCart">加入购物车</button>
            <button type="button" class="buy-button" :disabled="!canBuy" @click="buyNow">立即购买</button>
          </div>
        </section>
      </section>

      <section class="detail-tabs">
        <div class="tab-header">
          <button type="button" :class="{ active: activeTab === 'detail' }" @click="activeTab = 'detail'">商品详情</button>
          <button type="button" :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">用户评价</button>
          <button type="button" :class="{ active: activeTab === 'recommend' }" @click="activeTab = 'recommend'">相关推荐</button>
        </div>

        <div v-if="activeTab === 'detail'" class="tab-body detail-copy">
          <h2>{{ product.name }}</h2>
          <p>{{ product.description }}</p>
          <div class="detail-grid">
            <span>分类：{{ product.category || '精选' }}</span>
            <span>规格：{{ selectedSku?.name || '默认' }}</span>
            <span>库存：{{ currentStock }}</span>
            <span>状态：{{ product.status === 'active' ? '在售' : '下架' }}</span>
          </div>
        </div>

        <div v-else-if="activeTab === 'reviews'" class="tab-body review-list">
          <article v-for="review in reviews" :key="review.user" class="review-card">
            <strong>{{ review.user }}</strong>
            <span>{{ '★'.repeat(review.rating) }}</span>
            <p>{{ review.content }}</p>
          </article>
        </div>

        <div v-else class="tab-body related-grid">
          <article
            v-for="item in relatedProducts"
            :key="item.productId"
            class="related-card"
            @click="openRelatedProduct(item)"
          >
            <img :src="item.imageUrls[0]" :alt="item.name" @error="handleImageError" />
            <div>
              <span>{{ item.category || '精选' }}</span>
              <h3>{{ item.name }}</h3>
              <strong>¥{{ item.price }}</strong>
            </div>
          </article>
          <p v-if="relatedProducts.length === 0" class="empty-related">暂无相关推荐</p>
        </div>
      </section>
    </template>

    <div v-else class="state error">商品不存在</div>
  </main>
</template>

<style>
.detail-page {
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

.product-shell {
  display: grid;
  grid-template-columns: minmax(360px, 480px) minmax(0, 1fr);
  gap: 1.5rem;
  align-items: start;
}

.gallery-panel,
.purchase-panel,
.detail-tabs {
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.gallery-panel {
  padding: 1rem;
  overflow: visible;
}

.main-image {
  overflow: visible;
  aspect-ratio: 1;
  border-radius: 14px;
  background: #f5f6f8;
}

.main-image img,
.thumb-button img,
.related-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.thumb-button {
  overflow: hidden;
  aspect-ratio: 1;
  padding: 0;
  border: 2px solid #E9E4EE;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
}

.thumb-button.active {
  border-color: #980B32;
}

.purchase-panel {
  padding: 1.25rem;
}

.title-row {
  padding-bottom: 1rem;
  border-bottom: 1px solid #E9E4EE;
}

.category {
  color: #980B32;
  font-size: 0.82rem;
  font-weight: 900;
}

.title-row h1 {
  margin: 0.35rem 0 0.5rem;
  color: #241B2F;
  font-size: 1.7rem;
  line-height: 1.25;
}

.title-row p {
  margin: 0;
  color: #756D7E;
  line-height: 1.6;
}

.price-box {
  display: flex;
  gap: 0.9rem;
  align-items: baseline;
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 12px;
  background: #F4EFF7;
}

.price-box span {
  color: #756D7E;
  font-size: 0.9rem;
}

.price-box strong {
  color: #980B32;
  font-size: 2.2rem;
  line-height: 1;
}

.price-box small {
  margin-left: auto;
  color: #999;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.meta-grid div {
  padding: 0.75rem;
  border-radius: 10px;
  background: #F7F6FA;
}

.meta-grid span,
.meta-grid strong {
  display: block;
}

.meta-grid span {
  color: #777;
  font-size: 0.8rem;
}

.meta-grid strong {
  color: #241B2F;
  font-size: 1rem;
}

.option-block {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 1rem;
  align-items: center;
  margin: 1rem 0;
}

.option-label {
  color: #756D7E;
  font-weight: 800;
}

.spec-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.spec-row button {
  min-height: 36px;
  padding: 0 0.9rem;
  border: 1px solid #948B9D;
  border-radius: 999px;
  background: #fff;
  color: #333;
  cursor: pointer;
  font-weight: 700;
}

.spec-row button.active {
  border-color: #980B32;
  background: #F4EFF7;
  color: #980B32;
}

.spec-row button.disabled {
  border-color: #E9E4EE;
  color: #ccc;
  cursor: not-allowed;
  opacity: 0.5;
}

.delivery-text {
  margin: 0;
  color: #555;
}

.quantity-stepper {
  display: inline-grid;
  grid-template-columns: 36px 56px 36px;
  overflow: hidden;
  width: max-content;
  border: 1px solid #948B9D;
  border-radius: 8px;
}

.quantity-stepper button,
.quantity-stepper input {
  min-height: 36px;
  border: 0;
  background: #fff;
  text-align: center;
}

.quantity-stepper button {
  cursor: pointer;
  font-weight: 900;
}

.quantity-stepper input {
  border-right: 1px solid #948B9D;
  border-left: 1px solid #948B9D;
  outline: none;
}

.service-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1.25rem 0;
  color: #756D7E;
  font-size: 0.88rem;
}

.service-row span::before {
  margin-right: 0.25rem;
  color: #980B32;
  content: '✓';
  font-weight: 900;
}

.action-buttons {
  display: grid;
  grid-template-columns: 0.8fr 1fr 1fr;
  gap: 0.75rem;
}

.action-buttons button {
  min-height: 46px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 900;
}

.ghost-button {
  border: 1px solid #948B9D;
  background: #fff;
  color: #333;
}

.ghost-button.active {
  border-color: #980B32;
  background: #F4EFF7;
  color: #980B32;
}

.cart-button {
  border: 1px solid #5A0B72;
  background: #F4EFF7;
  color: #980B32;
}

.buy-button {
  border: 1px solid #5A0B72;
  background: #980B32;
  color: #fff;
}

.action-buttons button:disabled {
  border-color: #ddd;
  background: #f5f5f5;
  color: #aaa;
  cursor: not-allowed;
}

.detail-tabs {
  margin-top: 1.5rem;
  overflow: hidden;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #E9E4EE;
}

.tab-header button {
  min-height: 48px;
  padding: 0 1.25rem;
  border: 0;
  background: #fff;
  color: #555;
  cursor: pointer;
  font-weight: 900;
}

.tab-header button.active {
  color: #980B32;
  box-shadow: inset 0 -3px 0 #5A0B72;
}

.tab-body {
  padding: 1.25rem;
}

.detail-copy h2 {
  margin: 0 0 0.75rem;
  color: #241B2F;
}

.detail-copy p {
  margin: 0 0 1rem;
  color: #756D7E;
  line-height: 1.8;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

.detail-grid span {
  padding: 0.75rem;
  border-radius: 10px;
  background: #F7F6FA;
  color: #555;
}

.review-list {
  display: grid;
  gap: 0.75rem;
}

.review-card {
  padding: 1rem;
  border-radius: 12px;
  background: #F7F6FA;
}

.review-card strong {
  margin-right: 0.75rem;
}

.review-card span {
  color: #980B32;
}

.review-card p {
  margin: 0.5rem 0 0;
  color: #756D7E;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 1rem;
}

.related-card {
  overflow: hidden;
  border: 1px solid #E9E4EE;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
}

.related-card img {
  aspect-ratio: 1;
}

.related-card div {
  padding: 0.75rem;
}

.related-card span {
  color: #980B32;
  font-size: 0.76rem;
  font-weight: 900;
}

.related-card h3 {
  display: -webkit-box;
  min-height: 2.5rem;
  margin: 0.25rem 0 0.4rem;
  overflow: hidden;
  color: #241B2F;
  font-size: 0.9rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.related-card strong {
  color: #980B32;
}

.empty-related {
  grid-column: 1 / -1;
  margin: 0;
  color: #756D7E;
}

.state {
  padding: 3rem;
  color: #756D7E;
  text-align: center;
}

.error {
  color: #ff4d4f;
}

@media (min-width: 768px) and (max-width: 1100px) {
  .product-shell {
    grid-template-columns: 360px minmax(0, 1fr);
  }

  .related-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .product-shell {
    grid-template-columns: 1fr;
  }

  .option-block,
  .action-buttons {
    grid-template-columns: 1fr;
  }

  .price-box {
    align-items: flex-start;
    flex-direction: column;
  }

  .price-box small {
    margin-left: 0;
  }

  .detail-grid,
  .related-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
