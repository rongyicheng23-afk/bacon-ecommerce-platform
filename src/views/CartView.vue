<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import type { Product } from '@/types'

interface CartLine {
  id: number
  productId: number
  name: string
  description: string
  price: number
  imageUrl: string | null
  category: string
  stock: number
  quantity: number
  selected: boolean
}

type BehaviorAction = 'cart_update' | 'cart_remove' | 'checkout' | 'view_recommendation'

const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const actionMessage = ref('')
const cartItems = ref<CartLine[]>([])

const recommendedProducts = computed(() => {
  const cartProductIds = new Set(cartItems.value.map((item) => item.productId))
  const preferredCategory = cartItems.value[0]?.category
  return productStore.products
    .filter((product) => !cartProductIds.has(product.productId))
    .filter((product) => !preferredCategory || product.category === preferredCategory)
    .slice(0, 6)
})

const selectedItems = computed(() => cartItems.value.filter((item) => item.selected))
const allSelected = computed(() => cartItems.value.length > 0 && selectedItems.value.length === cartItems.value.length)
const totalQuantity = computed(() => selectedItems.value.reduce((sum, item) => sum + item.quantity, 0))
const totalAmount = computed(() => selectedItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0))
const totalSavings = computed(() => Math.round(totalAmount.value * 0.08))

const toCartLine = (product: Product, index: number): CartLine => ({
  id: product.productId,
  productId: product.productId,
  name: product.name,
  description: product.description,
  price: product.price,
  imageUrl: product.imageUrl,
  category: product.category || '精选',
  stock: product.stock,
  quantity: index + 1,
  selected: true
})

const saveCart = () => {
  localStorage.setItem('mockCartItems', JSON.stringify(cartItems.value))
}

const readSavedCart = () => {
  try {
    return JSON.parse(localStorage.getItem('mockCartItems') || '[]') as CartLine[]
  } catch {
    return []
  }
}

const recordBehavior = (product: Pick<CartLine, 'productId' | 'name' | 'category'>, action: BehaviorAction) => {
  const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  logs.push({
    userId: 1,
    productId: product.productId,
    productName: product.name,
    action,
    category: product.category,
    timestamp: new Date().toISOString()
  })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}

const setAllSelected = (checked: boolean) => {
  cartItems.value = cartItems.value.map((item) => ({ ...item, selected: checked }))
}

const toggleItem = (id: number) => {
  cartItems.value = cartItems.value.map((item) => (item.id === id ? { ...item, selected: !item.selected } : item))
}

const setQuantity = (id: number, quantity: number) => {
  cartItems.value = cartItems.value.map((item) => {
    if (item.id !== id) return item
    const nextQuantity = Math.max(1, Math.min(quantity, item.stock || 1))
    recordBehavior(item, 'cart_update')
    return { ...item, quantity: nextQuantity }
  })
}

const removeItem = (id: number) => {
  const target = cartItems.value.find((item) => item.id === id)
  if (target) recordBehavior(target, 'cart_remove')
  cartItems.value = cartItems.value.filter((item) => item.id !== id)
}

const clearSelected = () => {
  selectedItems.value.forEach((item) => recordBehavior(item, 'cart_remove'))
  cartItems.value = cartItems.value.filter((item) => !item.selected)
}

const checkout = () => {
  if (selectedItems.value.length === 0) {
    actionMessage.value = '请先选择要结算的商品'
    return
  }

  selectedItems.value.forEach((item) => recordBehavior(item, 'checkout'))
  localStorage.setItem(
    'checkoutDraft',
    JSON.stringify({
      items: selectedItems.value,
      totalQuantity: totalQuantity.value,
      totalAmount: totalAmount.value,
      totalSavings: totalSavings.value,
      payableAmount: totalAmount.value - totalSavings.value,
      createdAt: new Date().toISOString()
    })
  )
  router.push('/checkout')
}

const openProduct = (productId: number) => {
  router.push(`/product/${productId}`)
}

const openRecommendation = (product: Product) => {
  recordBehavior(
    {
      productId: product.productId,
      name: product.name,
      category: product.category || '精选'
    },
    'view_recommendation'
  )
  router.push(`/product/${product.productId}`)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

watch(cartItems, saveCart, { deep: true })

onMounted(async () => {
  try {
    if (productStore.products.length === 0) {
      await productStore.fetchProducts()
    }

    const savedCart = readSavedCart()
    cartItems.value = savedCart.length > 0 ? savedCart : productStore.products.slice(0, 3).map(toCartLine)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="cart-page">
    <p v-if="actionMessage" class="action-toast">{{ actionMessage }}</p>

    <section class="cart-hero">
      <div>
        <span>Shopping cart</span>
        <h1>购物车</h1>
        <p>管理已选商品、调整数量，并在结算前查看搭配推荐。</p>
      </div>
      <button type="button" @click="router.push('/products')">继续购物</button>
    </section>

    <div v-if="loading" class="state">加载中...</div>

    <section v-else-if="cartItems.length === 0" class="empty-state">
      <h2>购物车还是空的</h2>
      <p>去首页或商品发现页逛一逛，把喜欢的商品加入购物车。</p>
      <button type="button" @click="router.push('/products')">去挑选商品</button>
    </section>

    <template v-else>
      <section class="cart-layout">
        <div class="cart-main">
          <div class="cart-toolbar">
            <label>
              <input type="checkbox" :checked="allSelected" @change="setAllSelected(($event.target as HTMLInputElement).checked)" />
              全选
            </label>
            <span>已选 {{ selectedItems.length }} 件商品</span>
            <button type="button" @click="clearSelected">删除已选</button>
          </div>

          <article v-for="item in cartItems" :key="item.id" class="cart-line">
            <label class="line-check">
              <input type="checkbox" :checked="item.selected" @change="toggleItem(item.id)" />
            </label>

            <button type="button" class="line-image" @click="openProduct(item.productId)">
              <img :src="item.imageUrl || undefined" :alt="item.name" @error="handleImageError" />
            </button>

            <div class="line-info">
              <span>{{ item.category }}</span>
              <h2 @click="openProduct(item.productId)">{{ item.name }}</h2>
              <p>{{ item.description }}</p>
              <small>正品保障 · 48小时内发货</small>
            </div>

            <div class="line-price">¥{{ item.price }}</div>

            <div class="quantity-stepper">
              <button type="button" :disabled="item.quantity <= 1" @click="setQuantity(item.id, item.quantity - 1)">-</button>
              <input :value="item.quantity" type="number" min="1" :max="item.stock" @input="setQuantity(item.id, Number(($event.target as HTMLInputElement).value))" />
              <button type="button" :disabled="item.quantity >= item.stock" @click="setQuantity(item.id, item.quantity + 1)">+</button>
            </div>

            <div class="line-total">¥{{ item.price * item.quantity }}</div>

            <button type="button" class="remove-button" @click="removeItem(item.id)">删除</button>
          </article>
        </div>

        <aside class="summary-panel">
          <h2>结算明细</h2>
          <div class="summary-row">
            <span>商品数量</span>
            <strong>{{ totalQuantity }} 件</strong>
          </div>
          <div class="summary-row">
            <span>商品总价</span>
            <strong>¥{{ totalAmount }}</strong>
          </div>
          <div class="summary-row">
            <span>预计优惠</span>
            <strong>-¥{{ totalSavings }}</strong>
          </div>
          <div class="summary-total">
            <span>应付金额</span>
            <strong>¥{{ totalAmount - totalSavings }}</strong>
          </div>
          <button type="button" class="checkout-button" @click="checkout">去结算</button>
        </aside>
      </section>

      <section class="recommend-section">
        <div class="section-title">
          <h2>搭配推荐</h2>
          <span>根据购物车商品分类推荐</span>
        </div>

        <div class="recommend-grid">
          <article
            v-for="product in recommendedProducts"
            :key="product.productId"
            class="recommend-card"
            @click="openRecommendation(product)"
          >
            <img :src="product.imageUrl || undefined" :alt="product.name" @error="handleImageError" />
            <div>
              <span>{{ product.category || '精选' }}</span>
              <h3>{{ product.name }}</h3>
              <strong>¥{{ product.price }}</strong>
            </div>
          </article>
        </div>
      </section>
    </template>
  </main>
</template>

<style>
.cart-page {
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

.cart-hero {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1.25rem;
  padding: 1.5rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #111827, #2d1b42);
  color: #fff;
}

.cart-hero span {
  color: #ffd7df;
  font-size: 0.86rem;
  font-weight: 900;
}

.cart-hero h1 {
  margin: 0.2rem 0 0.4rem;
  font-size: 2rem;
}

.cart-hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
}

.cart-hero button,
.empty-state button,
.checkout-button {
  min-height: 40px;
  padding: 0 1rem;
  border: 0;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

.cart-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 1rem;
  align-items: start;
}

.cart-main,
.summary-panel,
.empty-state,
.recommend-section {
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.cart-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #f1f2f4;
  color: #666;
}

.cart-toolbar label {
  display: inline-flex;
  gap: 0.4rem;
  align-items: center;
  color: #111827;
  font-weight: 900;
}

.cart-toolbar button,
.remove-button {
  border: 0;
  background: transparent;
  color: #666;
  cursor: pointer;
  font-weight: 800;
}

.cart-toolbar button:hover,
.remove-button:hover {
  color: #fe2c55;
}

.cart-line {
  display: grid;
  grid-template-columns: 28px 104px minmax(0, 1fr) 88px 112px 96px 48px;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #f1f2f4;
}

.cart-line:last-child {
  border-bottom: 0;
}

.line-check {
  display: grid;
  place-items: center;
}

.line-image {
  overflow: hidden;
  aspect-ratio: 1;
  padding: 0;
  border: 0;
  border-radius: 12px;
  background: #f5f6f8;
  cursor: pointer;
}

.line-image img,
.recommend-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.line-info span,
.recommend-card span {
  color: #fe2c55;
  font-size: 0.78rem;
  font-weight: 900;
}

.line-info h2 {
  display: -webkit-box;
  margin: 0.25rem 0;
  overflow: hidden;
  color: #111827;
  font-size: 1rem;
  line-height: 1.4;
  cursor: pointer;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.line-info p {
  display: -webkit-box;
  margin: 0 0 0.25rem;
  overflow: hidden;
  color: #666;
  font-size: 0.84rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.line-info small {
  color: #999;
}

.line-price,
.line-total {
  color: #fe2c55;
  font-weight: 900;
}

.quantity-stepper {
  display: inline-grid;
  grid-template-columns: 32px 48px 32px;
  overflow: hidden;
  width: max-content;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.quantity-stepper button,
.quantity-stepper input {
  min-height: 32px;
  border: 0;
  background: #fff;
  text-align: center;
}

.quantity-stepper button {
  cursor: pointer;
  font-weight: 900;
}

.quantity-stepper button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.quantity-stepper input {
  border-right: 1px solid #e5e7eb;
  border-left: 1px solid #e5e7eb;
  outline: none;
}

.summary-panel {
  position: sticky;
  top: 150px;
  padding: 1rem;
}

.summary-panel h2 {
  margin: 0 0 1rem;
  color: #111827;
  font-size: 1.2rem;
}

.summary-row,
.summary-total {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.85rem;
  color: #666;
}

.summary-row strong {
  color: #111827;
}

.summary-total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f2f4;
  color: #111827;
  font-weight: 900;
}

.summary-total strong {
  color: #fe2c55;
  font-size: 1.5rem;
}

.checkout-button {
  width: 100%;
  min-height: 46px;
}

.recommend-section {
  margin-top: 1.25rem;
  padding: 1rem;
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
}

.section-title span {
  color: #777;
  font-size: 0.86rem;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 1rem;
}

.recommend-card {
  overflow: hidden;
  border: 1px solid #f1f2f4;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
}

.recommend-card img {
  aspect-ratio: 1;
}

.recommend-card div {
  padding: 0.75rem;
}

.recommend-card h3 {
  display: -webkit-box;
  min-height: 2.5rem;
  margin: 0.25rem 0 0.4rem;
  overflow: hidden;
  color: #111827;
  font-size: 0.9rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.recommend-card strong {
  color: #fe2c55;
}

.state,
.empty-state {
  padding: 3rem;
  color: #666;
  text-align: center;
}

.empty-state h2 {
  margin: 0 0 0.5rem;
  color: #111827;
}

.empty-state p {
  margin: 0 0 1rem;
}

@media (min-width: 768px) and (max-width: 1180px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }

  .summary-panel {
    position: static;
  }

  .cart-line {
    grid-template-columns: 28px 96px minmax(0, 1fr) 84px 112px;
  }

  .line-total,
  .remove-button {
    justify-self: end;
  }

  .recommend-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .cart-hero,
  .cart-toolbar,
  .section-title {
    align-items: flex-start;
    flex-direction: column;
  }

  .cart-layout {
    grid-template-columns: 1fr;
  }

  .summary-panel {
    position: static;
  }

  .cart-line {
    grid-template-columns: 28px 82px minmax(0, 1fr);
  }

  .line-price,
  .quantity-stepper,
  .line-total,
  .remove-button {
    grid-column: 3;
  }

  .recommend-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
