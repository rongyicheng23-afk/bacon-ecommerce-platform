<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import type { Product } from '@/types'
import type { CartLine } from '@/utils/cart'
import api from '@/services/api'
import { computeBestDiscount, claimCoupon, allCoupons, readClaimedCoupons, type Coupon } from '@/utils/coupons'

const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const actionMessage = ref('')
const cartItems = ref<CartLine[]>([])
const showCouponPanel = ref(false)

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
const dominantCategory = computed(() => {
  if (selectedItems.value.length === 0) return undefined
  const counts: Record<string, number> = {}
  selectedItems.value.forEach(i => { counts[i.category] = (counts[i.category] || 0) + 1 })
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0]
})
const claimedIds = ref<number[]>(readClaimedCoupons())
const availableCoupons = computed(() =>
  allCoupons.filter(
    (c) => !claimedIds.value.includes(c.id) && new Date(c.expireAt) > new Date()
  )
)
const claimedCoupons = computed(() =>
  allCoupons.filter((c) => claimedIds.value.includes(c.id))
)
const bestCoupon = computed(() => computeBestDiscount(totalAmount.value, dominantCategory.value))
const couponDiscount = computed(() => bestCoupon.value.discountAmount)
const totalSavings = computed(() => Math.round(totalAmount.value * 0.08) + couponDiscount.value)

const handleClaim = (couponId: number) => {
  if (claimCoupon(couponId)) {
    claimedIds.value = readClaimedCoupons()
    actionMessage.value = '优惠券已领取'
  }
}

type CartApiItem = Omit<CartLine, 'id'> & { cartItemId: number }

const applyCart = (items: CartApiItem[]) => {
  const selected = new Set(cartItems.value.filter((item) => item.selected).map((item) => item.id))
  cartItems.value = items.map((item) => ({
    ...item,
    id: item.cartItemId,
    selected: selected.size ? selected.has(item.cartItemId) : item.selected,
  }))
}

const fetchCart = async () => {
  const response = await api.get<{ code: string; data: { items: CartApiItem[] } }>('/cart')
  applyCart(response.data.data.items || [])
}

const setAllSelected = async (checked: boolean) => {
  try {
    await Promise.all(cartItems.value.map((item) => api.put(`/cart/items/${item.id}`, { selected: checked })))
    await fetchCart()
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '更新勾选状态失败'
  }
}

const toggleItem = async (id: number) => {
  const item = cartItems.value.find((line) => line.id === id)
  if (!item) return
  try {
    const response = await api.put<{ code: string; data: { items: CartApiItem[] } }>(`/cart/items/${id}`, { selected: !item.selected })
    applyCart(response.data.data.items || [])
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '更新勾选状态失败'
  }
}

const setQuantity = async (id: number, quantity: number) => {
  try {
    const response = await api.put<{ code: string; data: { items: CartApiItem[] } }>(`/cart/items/${id}`, { quantity })
    applyCart(response.data.data.items || [])
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '更新数量失败'
  }
}

const removeItem = async (id: number) => {
  try {
    const response = await api.delete<{ code: string; data: { items: CartApiItem[] } }>(`/cart/items/${id}`)
    applyCart(response.data.data.items || [])
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '删除商品失败'
  }
}

const clearSelected = async () => {
  try {
    await Promise.all(selectedItems.value.map((item) => api.delete(`/cart/items/${item.id}`)))
    await fetchCart()
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '删除商品失败'
  }
}

const checkout = () => {
  if (selectedItems.value.length === 0) {
    actionMessage.value = '请先选择要结算的商品'
    return
  }

  localStorage.setItem(
    'checkoutDraft',
    JSON.stringify({
      items: selectedItems.value,
      totalQuantity: totalQuantity.value,
      totalAmount: totalAmount.value,
      totalSavings: totalSavings.value,
      couponDiscount: couponDiscount.value,
      couponName: bestCoupon.value.coupon?.name || '',
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
  router.push(`/product/${product.productId}`)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

onMounted(async () => {
  try {
    if (productStore.products.length === 0) {
      await productStore.fetchProducts()
    }

    await fetchCart()
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
              <p>{{ item.skuName || item.description }}</p>
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
            <span>平台优惠</span>
            <strong>-¥{{ Math.round(totalAmount * 0.08) }}</strong>
          </div>
          <div v-if="couponDiscount > 0" class="summary-row coupon-row">
            <span>优惠券「{{ bestCoupon.coupon?.name }}」</span>
            <strong>-¥{{ couponDiscount }}</strong>
          </div>
          <div class="summary-row">
            <span>合计优惠</span>
            <strong>-¥{{ totalSavings }}</strong>
          </div>
          <div class="summary-total">
            <span>应付金额</span>
            <strong>¥{{ totalAmount - totalSavings }}</strong>
          </div>

          <!-- 可用券 -->
          <div v-if="claimedCoupons.length || availableCoupons.length" class="coupon-mini">
            <div v-if="claimedCoupons.length" class="coupon-mini-title">已领 {{ claimedCoupons.length }} 张券</div>
            <div v-if="bestCoupon.coupon" class="coupon-best">
              🎫 最优：{{ bestCoupon.coupon.name }}（省 ¥{{ couponDiscount }}）
            </div>
            <div v-if="availableCoupons.length" class="coupon-claim-row">
              <span>可领 {{ availableCoupons.length }} 张</span>
              <button type="button" class="claim-toggle" @click="showCouponPanel = !showCouponPanel">
                {{ showCouponPanel ? '收起' : '领券' }}
              </button>
            </div>
          </div>

          <button type="button" class="checkout-button" @click="checkout">去结算</button>
        </aside>
      </section>

      <!-- 领券面板 -->
      <section v-if="showCouponPanel" class="coupon-section">
        <div class="section-title">
          <h2>领券中心</h2>
          <button type="button" class="more-link" @click="showCouponPanel = false">收起</button>
        </div>

        <div v-if="claimedCoupons.length" class="coupon-sub">
          <span>已领取</span>
          <div class="coupon-grid">
            <div v-for="c in claimedCoupons" :key="c.id" class="coupon-card owned">
              <div class="coupon-left">
                <strong>{{ c.type === 'percentage' ? c.discount + '%' : '¥' + c.discount }}</strong>
                <small>满 ¥{{ c.threshold }} 可用</small>
              </div>
              <div class="coupon-right">
                <span>{{ c.name }}</span>
                <small>{{ c.description }}</small>
                <time>有效期至 {{ new Date(c.expireAt).toLocaleDateString('zh-CN') }}</time>
              </div>
            </div>
          </div>
        </div>

        <div v-if="availableCoupons.length" class="coupon-sub">
          <span>可领取（{{ availableCoupons.length }} 张）</span>
          <div class="coupon-grid">
            <div v-for="c in availableCoupons" :key="c.id" class="coupon-card">
              <div class="coupon-left">
                <strong>{{ c.type === 'percentage' ? c.discount + '%' : '¥' + c.discount }}</strong>
                <small>满 ¥{{ c.threshold }} 可用</small>
              </div>
              <div class="coupon-right">
                <span>{{ c.name }}</span>
                <small>{{ c.description }}</small>
                <time>有效期至 {{ new Date(c.expireAt).toLocaleDateString('zh-CN') }}</time>
              </div>
              <button type="button" class="claim-btn" @click="handleClaim(c.id)">立即领取</button>
            </div>
          </div>
        </div>
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
            <img :src="product.imageUrls[0]" :alt="product.name" @error="handleImageError" />
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
  background: linear-gradient(135deg, #241B2F, #2d1b42);
  color: #fff;
}

.cart-hero span {
  color: #AD1745;
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
  background: #980B32;
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
  border-bottom: 1px solid #E9E4EE;
  color: #756D7E;
}

.cart-toolbar label {
  display: inline-flex;
  gap: 0.4rem;
  align-items: center;
  color: #241B2F;
  font-weight: 900;
}

.cart-toolbar button,
.remove-button {
  border: 0;
  background: transparent;
  color: #756D7E;
  cursor: pointer;
  font-weight: 800;
}

.cart-toolbar button:hover,
.remove-button:hover {
  color: #980B32;
}

.cart-line {
  display: grid;
  grid-template-columns: 28px 104px minmax(0, 1fr) 88px 112px 96px 48px;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #E9E4EE;
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
  color: #980B32;
  font-size: 0.78rem;
  font-weight: 900;
}

.line-info h2 {
  display: -webkit-box;
  margin: 0.25rem 0;
  overflow: hidden;
  color: #241B2F;
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
  color: #756D7E;
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
  color: #980B32;
  font-weight: 900;
}

.quantity-stepper {
  display: inline-grid;
  grid-template-columns: 32px 48px 32px;
  overflow: hidden;
  width: max-content;
  border: 1px solid #948B9D;
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
  border-right: 1px solid #948B9D;
  border-left: 1px solid #948B9D;
  outline: none;
}

.summary-panel {
  position: sticky;
  top: 150px;
  padding: 1rem;
}

.summary-panel h2 {
  margin: 0 0 1rem;
  color: #241B2F;
  font-size: 1.2rem;
}

.summary-row,
.summary-total {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.85rem;
  color: #756D7E;
}

.summary-row strong {
  color: #241B2F;
}

.summary-total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #E9E4EE;
  color: #241B2F;
  font-weight: 900;
}

.summary-total strong {
  color: #980B32;
  font-size: 1.5rem;
}

.checkout-button {
  width: 100%;
  min-height: 46px;
  margin-top: 0.75rem;
}

.coupon-mini {
  margin-top: 0.75rem;
  padding: 0.75rem;
  border-radius: 12px;
  background: #fff8f0;
  font-size: 0.82rem;
}

.coupon-mini-title {
  color: #111827;
  font-weight: 900;
  margin-bottom: 4px;
}

.coupon-best {
  color: #fe2c55;
  font-weight: 800;
  margin-bottom: 4px;
}

.coupon-claim-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #6b7280;
}

.claim-toggle {
  border: 0;
  background: #fe2c55;
  color: #fff;
  border-radius: 999px;
  padding: 4px 12px;
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
}

/* 领券面板 */
.coupon-section {
  margin-top: 1.25rem;
  padding: 1rem;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.coupon-sub {
  margin-bottom: 0.75rem;
}

.coupon-sub > span {
  display: block;
  margin-bottom: 0.5rem;
  color: #6b7280;
  font-size: 0.82rem;
  font-weight: 800;
}

.coupon-grid {
  display: grid;
  gap: 0.6rem;
}

.coupon-card {
  display: flex;
  align-items: stretch;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid #fee2e2;
  background: #fff;
}

.coupon-card.owned {
  border-color: #d1d5db;
  opacity: 0.7;
}

.coupon-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 88px;
  padding: 0.75rem;
  background: #fff1f2;
  color: #fe2c55;
  flex-shrink: 0;
}

.coupon-card.owned .coupon-left {
  background: #f3f4f6;
  color: #9ca3af;
}

.coupon-left strong {
  font-size: 1.2rem;
  font-weight: 900;
}

.coupon-left small {
  font-size: 0.7rem;
  margin-top: 2px;
}

.coupon-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0.75rem;
  min-width: 0;
}

.coupon-right span {
  color: #111827;
  font-weight: 900;
  font-size: 0.88rem;
}

.coupon-right small {
  color: #6b7280;
  font-size: 0.76rem;
  margin: 2px 0;
}

.coupon-right time {
  color: #9ca3af;
  font-size: 0.7rem;
}

.claim-btn {
  align-self: center;
  margin-right: 0.75rem;
  padding: 6px 14px;
  border: 0;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}

.claim-btn:hover {
  opacity: 0.9;
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
  color: #241B2F;
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
  border: 1px solid #E9E4EE;
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
  color: #241B2F;
  font-size: 0.9rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.recommend-card strong {
  color: #980B32;
}

.state,
.empty-state {
  padding: 3rem;
  color: #756D7E;
  text-align: center;
}

.empty-state h2 {
  margin: 0 0 0.5rem;
  color: #241B2F;
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
