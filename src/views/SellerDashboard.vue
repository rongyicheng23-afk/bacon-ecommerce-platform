<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { useProductStore } from '@/stores/productStore'

interface SellerOrderItem {
  category?: string
  [key: string]: unknown
}

interface SellerOrder {
  orderId: number
  status: 'pending_payment' | 'paid' | 'shipped' | 'completed' | 'cancelled'
  payableAmount: number
  items?: SellerOrderItem[]
  createdAt: string
}

const router = useRouter()
const userStore = useUserStore()
const productStore = useProductStore()
const orders = ref<SellerOrder[]>([])

const sellerName = computed(() => userStore.currentUser?.shopName || userStore.currentUser?.username || 'Bacon 商家')
const mainCategory = computed(() => userStore.currentUser?.mainCategory || '综合类目')

/** 过滤出属于该商家类目的订单 */
const sellerOrders = computed(() => {
  const cat = userStore.currentUser?.mainCategory
  if (!cat) return orders.value
  return orders.value.filter((order) => {
    if (!order.items || order.items.length === 0) return true // 无商品信息不过滤
    return order.items.some((item) => item.category === cat)
  })
})

const paidOrders = computed(() => sellerOrders.value.filter((order) => order.status === 'paid'))
const shippedOrders = computed(() => sellerOrders.value.filter((order) => order.status === 'shipped'))
const completedOrders = computed(() => sellerOrders.value.filter((order) => order.status === 'completed'))
const totalSales = computed(() => {
  return sellerOrders.value
    .filter((order) => order.status !== 'pending_payment' && order.status !== 'cancelled')
    .reduce((sum, order) => sum + order.payableAmount, 0)
})

const sellerProducts = computed(() => {
  const cat = userStore.currentUser?.mainCategory
  if (!cat) return productStore.products
  return productStore.products.filter((p) => p.category === cat)
})

const sellerProductCount = computed(() => sellerProducts.value.length)

const lowStockProducts = computed(() => {
  return sellerProducts.value.filter((product) => product.stock < 30).slice(0, 5)
})

const recentOrders = computed(() => {
  return [...sellerOrders.value]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5)
})

const statusText: Record<SellerOrder['status'], string> = {
  pending_payment: '待付款',
  paid: '待发货',
  shipped: '待收货',
  completed: '已完成',
  cancelled: '已取消'
}

const readOrders = () => {
  try {
    const data = JSON.parse(localStorage.getItem('mockOrders') || '[]') as SellerOrder[]
    orders.value = Array.isArray(data) ? data : []
  } catch {
    orders.value = []
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  readOrders()
  if (productStore.products.length === 0) {
    await productStore.fetchProducts()
  }
})
</script>

<template>
  <main class="seller-page">
    <section class="seller-hero">
      <div>
        <span>Seller Center</span>
        <h1>{{ sellerName }}</h1>
        <p>主营类目：{{ mainCategory }}。这里用于商家管理商品、订单和经营数据。</p>
      </div>
      <button type="button" @click="router.push('/products')">查看前台店铺</button>
    </section>

    <section class="seller-stats" aria-label="商家经营概览">
      <article>
        <span>商品总数</span>
        <strong>{{ sellerProductCount }}</strong>
      </article>
      <article>
        <span>待发货</span>
        <strong>{{ paidOrders.length }}</strong>
      </article>
      <article>
        <span>配送中</span>
        <strong>{{ shippedOrders.length }}</strong>
      </article>
      <article>
        <span>累计销售额</span>
        <strong>¥{{ totalSales.toFixed(2) }}</strong>
      </article>
    </section>

    <section class="seller-grid">
      <article class="seller-card">
        <div class="card-head">
          <div>
            <span>Orders</span>
            <h2>近期订单</h2>
          </div>
          <button type="button" disabled>商家订单即将开放</button>
        </div>

        <div v-if="recentOrders.length === 0" class="seller-empty">
          暂无订单，买家下单后会出现在这里。
        </div>
        <div v-else class="seller-order-list">
          <div v-for="order in recentOrders" :key="order.orderId">
            <span>订单 {{ order.orderId }}</span>
            <strong>{{ statusText[order.status] }}</strong>
            <em>¥{{ order.payableAmount.toFixed(2) }}</em>
            <time>{{ formatDate(order.createdAt) }}</time>
          </div>
        </div>
      </article>

      <article class="seller-card">
        <div class="card-head">
          <div>
            <span>Inventory</span>
            <h2>库存提醒</h2>
          </div>
        </div>

        <div v-if="lowStockProducts.length === 0" class="seller-empty">
          当前暂无低库存商品。
        </div>
        <div v-else class="stock-list">
          <div v-for="product in lowStockProducts" :key="product.productId">
            <span>{{ product.name }}</span>
            <strong>库存 {{ product.stock }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="seller-actions">
      <button type="button" disabled>商品管理即将开放</button>
      <button type="button" disabled>商家订单即将开放</button>
      <button type="button" disabled>经营分析即将开放</button>
    </section>
  </main>
</template>

<style>
.seller-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.seller-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 30px;
  color: #fff;
  background:
    linear-gradient(120deg, rgba(17, 24, 39, 0.9), rgba(14, 165, 233, 0.58)),
    url('https://images.unsplash.com/photo-1556740758-90de374c12ad?auto=format&fit=crop&w=1800&q=85') center/cover;
  border-radius: 16px;
}

.seller-hero span,
.card-head span {
  display: inline-flex;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.seller-hero h1 {
  margin: 0;
  font-size: 34px;
}

.seller-hero p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.82);
}

.seller-hero button,
.card-head button,
.seller-actions button {
  border: 0;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 900;
  cursor: pointer;
}

.seller-hero button {
  color: #111827;
  background: #fff;
}

.card-head button:disabled,
.seller-actions button:disabled {
  color: #9ca3af;
  background: #f5f6f8;
  cursor: not-allowed;
}

.seller-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 18px 0;
}

.seller-stats article,
.seller-card {
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
}

.seller-stats article {
  padding: 18px 20px;
}

.seller-stats span {
  color: #6b7280;
  font-size: 14px;
}

.seller-stats strong {
  display: block;
  margin-top: 8px;
  color: #111827;
  font-size: 26px;
}

.seller-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 16px;
}

.seller-card {
  padding: 22px;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.card-head span {
  color: #0ea5e9;
}

.card-head h2 {
  margin: 0;
  color: #111827;
}

.card-head button,
.seller-actions button {
  color: #374151;
  background: #f5f6f8;
}

.seller-order-list,
.stock-list {
  display: grid;
  gap: 10px;
}

.seller-order-list div,
.stock-list div {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto auto;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 12px;
}

.seller-order-list span,
.stock-list span {
  overflow: hidden;
  color: #111827;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.seller-order-list strong,
.stock-list strong {
  color: #0ea5e9;
}

.seller-order-list em {
  color: #fe2c55;
  font-style: normal;
  font-weight: 900;
}

.seller-order-list time {
  color: #9ca3af;
  font-size: 13px;
}

.seller-empty {
  padding: 26px 18px;
  color: #6b7280;
  background: #fafafa;
  border-radius: 14px;
  text-align: center;
}

.seller-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

@media (max-width: 860px) {
  .seller-page {
    padding: 16px 12px 40px;
  }

  .seller-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .seller-stats,
  .seller-grid {
    grid-template-columns: 1fr;
  }

  .seller-order-list div {
    grid-template-columns: 1fr;
  }
}
</style>
