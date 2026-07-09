<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

type OrderStatus = 'all' | 'pending_payment' | 'paid' | 'shipped' | 'completed' | 'cancelled'

interface MockOrderItem {
  id?: number
  productId: number
  skuId?: number
  skuName?: string
  name?: string
  productName?: string
  description?: string
  price: number
  imageUrl?: string | null
  productImage?: string
  category?: string
  quantity: number
}

interface MockAddress {
  name: string
  phone: string
  detail: string
}

interface MockOrder {
  orderId: number
  status: Exclude<OrderStatus, 'all'>
  items: MockOrderItem[]
  address?: MockAddress
  deliveryType?: string
  paymentType?: string
  remark?: string
  totalAmount: number
  totalSavings?: number
  deliveryFee?: number
  payableAmount: number
  createdAt: string
}

const router = useRouter()
const orders = ref<MockOrder[]>([])
const activeStatus = ref<OrderStatus>('all')
const actionMessage = ref('')

const statusTabs: Array<{ key: OrderStatus; label: string }> = [
  { key: 'all', label: '全部订单' },
  { key: 'pending_payment', label: '待付款' },
  { key: 'paid', label: '待发货' },
  { key: 'shipped', label: '待收货' },
  { key: 'completed', label: '已完成' },
  { key: 'cancelled', label: '已取消' }
]

const statusText: Record<Exclude<OrderStatus, 'all'>, string> = {
  pending_payment: '待付款',
  paid: '待发货',
  shipped: '待收货',
  completed: '已完成',
  cancelled: '已取消'
}

const paymentText: Record<string, string> = {
  alipay: '支付宝',
  wechat: '微信支付',
  card: '银行卡'
}

const readOrders = () => {
  try {
    const data = JSON.parse(localStorage.getItem('mockOrders') || '[]') as MockOrder[]
    orders.value = Array.isArray(data) ? data : []
  } catch {
    orders.value = []
  }
}

const saveOrders = () => {
  localStorage.setItem('mockOrders', JSON.stringify(orders.value))
}

const showMessage = (message: string) => {
  actionMessage.value = message
  window.setTimeout(() => {
    actionMessage.value = ''
  }, 1600)
}

const recordBehavior = (action: string, order: MockOrder) => {
  const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  logs.push({
    userId: 1,
    action,
    orderId: order.orderId,
    amount: order.payableAmount,
    timestamp: new Date().toISOString()
  })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}

const filteredOrders = computed(() => {
  if (activeStatus.value === 'all') return orders.value
  return orders.value.filter((order) => order.status === activeStatus.value)
})

const orderStats = computed(() => {
  const pending = orders.value.filter((order) => order.status === 'pending_payment').length
  const shipping = orders.value.filter((order) => order.status === 'paid' || order.status === 'shipped').length
  const completed = orders.value.filter((order) => order.status === 'completed').length
  const spending = orders.value
    .filter((order) => order.status !== 'cancelled')
    .reduce((sum, order) => sum + order.payableAmount, 0)

  return { pending, shipping, completed, spending }
})

const tabCount = (status: OrderStatus) => {
  if (status === 'all') return orders.value.length
  return orders.value.filter((order) => order.status === status).length
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getItemName = (item: MockOrderItem) => item.name || item.productName || '商品'

const getItemImage = (item: MockOrderItem) => {
  return item.imageUrl || item.productImage || 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=500&q=85'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=500&q=85'
}

const updateStatus = (order: MockOrder, status: MockOrder['status'], message: string) => {
  order.status = status
  saveOrders()
  recordBehavior(`order_${status}`, order)
  showMessage(message)
}

const cancelOrder = (order: MockOrder) => {
  updateStatus(order, 'cancelled', '订单已取消')
}

const payOrder = (order: MockOrder) => {
  router.push(`/payment/${order.orderId}`)
}

const confirmReceive = (order: MockOrder) => {
  updateStatus(order, 'completed', '已确认收货')
}

const removeOrder = (orderId: number) => {
  orders.value = orders.value.filter((order) => order.orderId !== orderId)
  saveOrders()
  showMessage('订单记录已删除')
}

onMounted(() => {
  readOrders()
})
</script>

<template>
  <main class="orders-page">
    <p v-if="actionMessage" class="order-toast">{{ actionMessage }}</p>

    <section class="orders-hero">
      <div>
        <span>My Orders</span>
        <h1>我的订单</h1>
        <p>查看订单进度、支付状态、商品清单和收货信息。</p>
      </div>
      <button type="button" @click="router.push('/products')">继续购物</button>
    </section>

    <section class="orders-overview" aria-label="订单概览">
      <article>
        <span>待付款</span>
        <strong>{{ orderStats.pending }}</strong>
      </article>
      <article>
        <span>配送中</span>
        <strong>{{ orderStats.shipping }}</strong>
      </article>
      <article>
        <span>已完成</span>
        <strong>{{ orderStats.completed }}</strong>
      </article>
      <article>
        <span>累计消费</span>
        <strong>¥{{ orderStats.spending.toFixed(2) }}</strong>
      </article>
    </section>

    <section class="orders-panel">
      <div class="order-tabs" role="tablist" aria-label="订单状态筛选">
        <button
          v-for="tab in statusTabs"
          :key="tab.key"
          type="button"
          :class="{ active: activeStatus === tab.key }"
          @click="activeStatus = tab.key"
        >
          {{ tab.label }}
          <span>{{ tabCount(tab.key) }}</span>
        </button>
      </div>

      <div v-if="filteredOrders.length === 0" class="empty-orders">
        <h2>暂无{{ activeStatus === 'all' ? '' : statusTabs.find((tab) => tab.key === activeStatus)?.label }}订单</h2>
        <p>去逛逛首页推荐和分类商品，下单后这里会显示完整订单流程。</p>
        <button type="button" @click="router.push('/')">去首页看看</button>
      </div>

      <div v-else class="order-list">
        <article v-for="order in filteredOrders" :key="order.orderId" class="order-card">
          <header class="order-card-head">
            <div>
              <strong>订单号 {{ order.orderId }}</strong>
              <span>{{ formatDate(order.createdAt) }}</span>
            </div>
            <em :class="['order-status', `status-${order.status}`]">
              {{ statusText[order.status] }}
            </em>
          </header>

          <div class="order-card-body">
            <div class="order-items">
              <div v-for="item in order.items" :key="`${order.orderId}-${item.id || item.skuId || item.productId}`" class="order-item">
                <img :src="getItemImage(item)" :alt="getItemName(item)" @error="handleImageError" />
                <div>
                  <h3>{{ getItemName(item) }}</h3>
                  <p>{{ item.skuName || item.description || item.category || '精选好物' }}</p>
                  <span>¥{{ item.price.toFixed(2) }} × {{ item.quantity }}</span>
                </div>
              </div>
            </div>

            <aside class="order-summary">
              <p>
                <span>支付方式</span>
                <strong>{{ paymentText[order.paymentType || ''] || '未选择' }}</strong>
              </p>
              <p>
                <span>配送方式</span>
                <strong>{{ order.deliveryType === 'express' ? '加急配送' : '普通配送' }}</strong>
              </p>
              <p v-if="order.address">
                <span>收货人</span>
                <strong>{{ order.address.name }} {{ order.address.phone }}</strong>
              </p>
              <p class="payable">
                <span>实付款</span>
                <strong>¥{{ order.payableAmount.toFixed(2) }}</strong>
              </p>
            </aside>
          </div>

          <footer class="order-actions">
            <button type="button" @click="router.push(`/order/${order.orderId}`)">查看详情</button>
            <button v-if="order.status === 'pending_payment'" type="button" class="primary" @click="payOrder(order)">
              立即付款
            </button>
            <button v-if="order.status === 'pending_payment'" type="button" @click="cancelOrder(order)">
              取消订单
            </button>
            <button v-if="order.status === 'shipped'" type="button" class="primary" @click="confirmReceive(order)">
              确认收货
            </button>
            <button v-if="order.status === 'cancelled' || order.status === 'completed'" type="button" @click="removeOrder(order.orderId)">
              删除记录
            </button>
          </footer>
        </article>
      </div>
    </section>
  </main>
</template>

<style>
.orders-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.order-toast {
  position: fixed;
  top: 92px;
  left: 50%;
  z-index: 20;
  transform: translateX(-50%);
  margin: 0;
  padding: 10px 18px;
  color: #fff;
  background: rgba(17, 24, 39, 0.88);
  border-radius: 999px;
  box-shadow: 0 12px 30px rgba(17, 24, 39, 0.18);
}

.orders-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 26px 30px;
  color: #fff;
  background:
    linear-gradient(120deg, rgba(17, 24, 39, 0.86), rgba(254, 44, 85, 0.72)),
    url('https://images.unsplash.com/photo-1556741533-6e6a62bd8b49?auto=format&fit=crop&w=1800&q=85') center/cover;
  border-radius: 16px;
}

.orders-hero span {
  display: inline-flex;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.75);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}

.orders-hero h1 {
  margin: 0;
  font-size: 32px;
  line-height: 1.2;
}

.orders-hero p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.82);
}

.orders-hero button,
.empty-orders button {
  border: 0;
  color: #111827;
  background: #fff;
  border-radius: 999px;
  padding: 11px 18px;
  font-weight: 800;
  cursor: pointer;
}

.orders-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 18px 0;
}

.orders-overview article,
.orders-panel {
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
}

.orders-overview article {
  padding: 18px 20px;
}

.orders-overview span {
  display: block;
  color: #6b7280;
  font-size: 14px;
}

.orders-overview strong {
  display: block;
  margin-top: 8px;
  color: #111827;
  font-size: 26px;
  line-height: 1.1;
}

.orders-panel {
  overflow: hidden;
}

.order-tabs {
  display: flex;
  gap: 8px;
  padding: 14px;
  border-bottom: 1px solid #f1f2f4;
  overflow-x: auto;
}

.order-tabs button {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  color: #374151;
  background: #f6f7f9;
  border-radius: 999px;
  padding: 10px 15px;
  font-weight: 800;
  cursor: pointer;
}

.order-tabs button.active {
  color: #fff;
  background: #fe2c55;
}

.order-tabs span {
  color: inherit;
  opacity: 0.72;
}

.empty-orders {
  padding: 58px 20px;
  text-align: center;
}

.empty-orders h2 {
  margin: 0;
  color: #111827;
  font-size: 24px;
}

.empty-orders p {
  margin: 10px 0 22px;
  color: #6b7280;
}

.empty-orders button {
  color: #fff;
  background: #111827;
}

.order-list {
  display: grid;
  gap: 14px;
  padding: 14px;
}

.order-card {
  border: 1px solid #eef0f3;
  border-radius: 14px;
  background: #fff;
  overflow: hidden;
}

.order-card-head,
.order-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 18px;
  background: #fafafa;
}

.order-card-head div {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.order-card-head strong {
  color: #111827;
  font-size: 15px;
}

.order-card-head span {
  color: #6b7280;
  font-size: 13px;
}

.order-status {
  font-style: normal;
  font-size: 13px;
  font-weight: 900;
}

.status-pending_payment {
  color: #fe2c55;
}

.status-paid,
.status-shipped {
  color: #2563eb;
}

.status-completed {
  color: #059669;
}

.status-cancelled {
  color: #9ca3af;
}

.order-card-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 18px;
  padding: 18px;
}

.order-items {
  display: grid;
  gap: 12px;
}

.order-item {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr);
  gap: 14px;
}

.order-item img {
  width: 86px;
  height: 86px;
  object-fit: cover;
  border-radius: 12px;
  background: #f5f6f8;
}

.order-item h3 {
  margin: 2px 0 6px;
  color: #111827;
  font-size: 16px;
  line-height: 1.35;
}

.order-item p {
  margin: 0 0 8px;
  color: #6b7280;
  font-size: 13px;
}

.order-item span {
  color: #374151;
  font-weight: 800;
}

.order-summary {
  display: grid;
  align-content: start;
  gap: 10px;
  padding-left: 18px;
  border-left: 1px solid #f1f2f4;
}

.order-summary p {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.order-summary strong {
  color: #111827;
  text-align: right;
}

.order-summary .payable {
  padding-top: 10px;
  border-top: 1px solid #f1f2f4;
}

.order-summary .payable strong {
  color: #fe2c55;
  font-size: 20px;
}

.order-actions {
  justify-content: flex-end;
  border-top: 1px solid #f1f2f4;
}

.order-actions button {
  border: 1px solid #e5e7eb;
  color: #374151;
  background: #fff;
  border-radius: 999px;
  padding: 9px 15px;
  font-weight: 800;
  cursor: pointer;
}

.order-actions button.primary {
  color: #fff;
  border-color: #fe2c55;
  background: #fe2c55;
}

@media (max-width: 820px) {
  .orders-page {
    padding: 16px 12px 40px;
  }

  .orders-hero {
    align-items: flex-start;
    flex-direction: column;
    border-radius: 14px;
  }

  .orders-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .order-card-body {
    grid-template-columns: 1fr;
  }

  .order-summary {
    padding-left: 0;
    border-left: 0;
    padding-top: 14px;
    border-top: 1px solid #f1f2f4;
  }
}

@media (max-width: 560px) {
  .orders-overview {
    grid-template-columns: 1fr;
  }

  .order-card-head,
  .order-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .order-actions button {
    width: 100%;
  }
}
</style>
