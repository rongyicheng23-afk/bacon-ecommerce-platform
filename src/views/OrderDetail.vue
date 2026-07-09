<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

type OrderStatus = 'pending_payment' | 'paid' | 'shipped' | 'completed' | 'cancelled'

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
  status: OrderStatus
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

const route = useRoute()
const router = useRouter()
const order = ref<MockOrder | null>(null)
const actionMessage = ref('')

const statusText: Record<OrderStatus, string> = {
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

const deliveryText = computed(() => {
  return order.value?.deliveryType === 'express' ? '加急配送' : '普通配送'
})

const itemQuantity = computed(() => {
  return order.value?.items.reduce((sum, item) => sum + item.quantity, 0) || 0
})

interface TimelineStep {
  key: string
  title: string
  description: string
  time?: string
  done: boolean
  active: boolean
  cancelled: boolean
}

const timelineSteps = computed<TimelineStep[]>(() => {
  if (!order.value) return []
  const { status, createdAt } = order.value
  const isCancelled = status === 'cancelled'
  const isDone = (step: string) => {
    const order_ = ['pending_payment', 'paid', 'shipped', 'completed']
    const stepIdx = order_.indexOf(step)
    const currentIdx = order_.indexOf(status)
    return currentIdx > stepIdx || (currentIdx === stepIdx && status !== 'cancelled')
  }
  const isActive = (step: string) => status === step

  return [
    {
      key: 'pending_payment',
      title: '提交订单',
      description: '订单已生成，等待付款',
      time: createdAt,
      done: isDone('pending_payment') || isActive('pending_payment'),
      active: isActive('pending_payment'),
      cancelled: isCancelled
    },
    {
      key: 'paid',
      title: '支付成功',
      description: '已付款，等待商家发货',
      time: status !== 'pending_payment' && !isCancelled ? createdAt : undefined,
      done: isDone('paid'),
      active: isActive('paid'),
      cancelled: isCancelled
    },
    {
      key: 'shipped',
      title: '已发货',
      description: '商品已出库，运输中',
      time: status === 'shipped' || status === 'completed' ? createdAt : undefined,
      done: isDone('shipped'),
      active: isActive('shipped'),
      cancelled: isCancelled
    },
    {
      key: 'completed',
      title: '已签收',
      description: isCancelled ? '订单已取消' : '确认收货，交易完成',
      time: status === 'completed' ? createdAt : undefined,
      done: status === 'completed',
      active: isActive('completed'),
      cancelled: isCancelled
    }
  ]
})

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

const readOrder = () => {
  const orderId = Number(route.params.id)
  if (Number.isNaN(orderId)) {
    router.push('/orders')
    return
  }

  try {
    const orders = JSON.parse(localStorage.getItem('mockOrders') || '[]') as MockOrder[]
    order.value = orders.find((item) => item.orderId === orderId) || null
  } catch {
    order.value = null
  }
}

const saveOrder = () => {
  if (!order.value) return
  const orders = JSON.parse(localStorage.getItem('mockOrders') || '[]') as MockOrder[]
  const nextOrders = orders.map((item) => (item.orderId === order.value?.orderId ? order.value : item))
  localStorage.setItem('mockOrders', JSON.stringify(nextOrders))
}

const recordBehavior = (action: string) => {
  if (!order.value) return
  const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  logs.push({
    userId: 1,
    action,
    orderId: order.value.orderId,
    amount: order.value.payableAmount,
    timestamp: new Date().toISOString()
  })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}

const showMessage = (message: string) => {
  actionMessage.value = message
  window.setTimeout(() => {
    actionMessage.value = ''
  }, 1600)
}

const updateStatus = (status: OrderStatus, message: string) => {
  if (!order.value) return
  order.value.status = status
  saveOrder()
  recordBehavior(`order_${status}`)
  showMessage(message)
}

const payOrder = () => {
  if (!order.value) return
  router.push(`/payment/${order.value.orderId}`)
}

const cancelOrder = () => {
  updateStatus('cancelled', '订单已取消')
}

const confirmReceive = () => {
  updateStatus('completed', '已确认收货')
}

onMounted(() => {
  readOrder()
})
</script>

<template>
  <main class="order-detail-page">
    <p v-if="actionMessage" class="order-detail-toast">{{ actionMessage }}</p>

    <button type="button" class="back-button" @click="router.push('/orders')">返回我的订单</button>

    <section v-if="!order" class="order-missing">
      <h1>订单不存在</h1>
      <p>可能是本地 mock 数据被清空，或者订单号不正确。</p>
      <button type="button" @click="router.push('/orders')">返回订单列表</button>
    </section>

    <template v-else>
      <section class="detail-hero">
        <div>
          <span>订单号 {{ order.orderId }}</span>
          <h1>{{ statusText[order.status] }}</h1>
          <p>下单时间：{{ formatDate(order.createdAt) }}</p>
        </div>

        <div class="detail-actions">
          <button v-if="order.status === 'pending_payment'" type="button" class="primary" @click="payOrder">立即付款</button>
          <button v-if="order.status === 'pending_payment'" type="button" @click="cancelOrder">取消订单</button>
          <button v-if="order.status === 'shipped'" type="button" class="primary" @click="confirmReceive">确认收货</button>
        </div>
      </section>

      <section class="logistics-timeline" aria-label="物流进度">
        <div class="timeline-track">
          <div
            v-for="(step, index) in timelineSteps"
            :key="step.key"
            :class="[
              'timeline-node',
              { done: step.done, active: step.active, cancelled: step.cancelled }
            ]"
          >
            <div class="timeline-dot">
              <span v-if="step.done && !step.cancelled">✓</span>
              <span v-else-if="step.cancelled">✕</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <div class="timeline-body">
              <strong>{{ step.title }}</strong>
              <p>{{ step.description }}</p>
              <time v-if="step.time">{{ formatDate(step.time) }}</time>
            </div>
          </div>
        </div>
      </section>

      <section class="detail-grid">
        <article class="detail-card">
          <h2>收货信息</h2>
          <p v-if="order.address">
            <strong>{{ order.address.name }} {{ order.address.phone }}</strong>
            <span>{{ order.address.detail }}</span>
          </p>
          <p v-else>
            <strong>暂无收货信息</strong>
            <span>后续接入后端时会保存用户地址表。</span>
          </p>
        </article>

        <article class="detail-card">
          <h2>订单信息</h2>
          <dl>
            <div>
              <dt>支付方式</dt>
              <dd>{{ paymentText[order.paymentType || ''] || '未选择' }}</dd>
            </div>
            <div>
              <dt>配送方式</dt>
              <dd>{{ deliveryText }}</dd>
            </div>
            <div>
              <dt>商品数量</dt>
              <dd>{{ itemQuantity }} 件</dd>
            </div>
            <div>
              <dt>订单状态</dt>
              <dd>{{ statusText[order.status] }}</dd>
            </div>
          </dl>
        </article>
      </section>

      <section class="detail-card item-card">
        <h2>商品清单</h2>
        <div class="detail-items">
          <article v-for="item in order.items" :key="`${order.orderId}-${item.id || item.skuId || item.productId}`" class="detail-item">
            <img :src="getItemImage(item)" :alt="getItemName(item)" @error="handleImageError" />
            <div>
              <h3>{{ getItemName(item) }}</h3>
              <p>{{ item.skuName || item.description || item.category || '精选好物' }}</p>
            </div>
            <span>¥{{ item.price.toFixed(2) }}</span>
            <strong>× {{ item.quantity }}</strong>
          </article>
        </div>
      </section>

      <section class="detail-card price-card">
        <dl>
          <div>
            <dt>商品总价</dt>
            <dd>¥{{ order.totalAmount.toFixed(2) }}</dd>
          </div>
          <div>
            <dt>优惠</dt>
            <dd>-¥{{ (order.totalSavings || 0).toFixed(2) }}</dd>
          </div>
          <div>
            <dt>运费</dt>
            <dd>¥{{ (order.deliveryFee || 0).toFixed(2) }}</dd>
          </div>
          <div class="payable">
            <dt>实付款</dt>
            <dd>¥{{ order.payableAmount.toFixed(2) }}</dd>
          </div>
        </dl>
      </section>
    </template>
  </main>
</template>

<style>
.order-detail-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.order-detail-toast {
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

.back-button {
  border: 0;
  color: #374151;
  background: #fff;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 800;
  box-shadow: 0 10px 24px rgba(17, 24, 39, 0.08);
  cursor: pointer;
}

.logistics-timeline {
  margin-top: 18px;
  padding: 28px 30px;
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
}

.timeline-track {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
}

.timeline-node {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0 12px;
}

.timeline-node::before {
  content: '';
  position: absolute;
  top: 18px;
  left: calc(50% + 24px);
  width: calc(100% - 48px);
  height: 3px;
  background: #e5e7eb;
  border-radius: 999px;
}

.timeline-node:last-child::before {
  display: none;
}

.timeline-node.done::before {
  background: #fe2c55;
}

.timeline-node.cancelled::before {
  background: #e5e7eb;
}

.timeline-dot {
  position: relative;
  z-index: 1;
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 50%;
  background: #e5e7eb;
  color: #9ca3af;
  font-weight: 900;
  font-size: 14px;
  margin-bottom: 14px;
  transition: all 0.3s ease;
}

.timeline-node.done .timeline-dot {
  background: #fe2c55;
  color: #fff;
}

.timeline-node.active .timeline-dot {
  background: #fe2c55;
  color: #fff;
  box-shadow: 0 0 0 6px rgba(254, 44, 85, 0.2);
  animation: dot-pulse 2s ease-in-out infinite;
}

.timeline-node.cancelled .timeline-dot {
  background: #9ca3af;
  color: #fff;
}

@keyframes dot-pulse {
  0%, 100% { box-shadow: 0 0 0 6px rgba(254, 44, 85, 0.2); }
  50% { box-shadow: 0 0 0 12px rgba(254, 44, 85, 0.08); }
}

.timeline-body strong {
  display: block;
  color: #9ca3af;
  font-size: 14px;
  font-weight: 900;
  transition: color 0.3s ease;
}

.timeline-node.done .timeline-body strong,
.timeline-node.active .timeline-body strong {
  color: #111827;
}

.timeline-node.active .timeline-body strong {
  color: #fe2c55;
}

.timeline-node.cancelled .timeline-body strong {
  color: #9ca3af;
}

.timeline-body p {
  margin: 4px 0;
  color: #9ca3af;
  font-size: 12px;
  line-height: 1.5;
  transition: color 0.3s ease;
}

.timeline-node.done .timeline-body p,
.timeline-node.active .timeline-body p {
  color: #6b7280;
}

.timeline-body time {
  color: #9ca3af;
  font-size: 11px;
}

.detail-hero,
.order-missing {
  margin-top: 18px;
  padding: 30px;
  color: #fff;
  background:
    linear-gradient(120deg, rgba(17, 24, 39, 0.86), rgba(254, 44, 85, 0.7)),
    url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1800&q=85') center/cover;
  border-radius: 16px;
}

.detail-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.detail-hero span {
  color: rgba(255, 255, 255, 0.76);
  font-weight: 800;
}

.detail-hero h1,
.order-missing h1 {
  margin: 8px 0;
  font-size: 34px;
}

.detail-hero p,
.order-missing p {
  margin: 0;
  color: rgba(255, 255, 255, 0.82);
}

.detail-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.detail-actions button,
.order-missing button {
  border: 1px solid rgba(255, 255, 255, 0.7);
  color: #fff;
  background: transparent;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 800;
  cursor: pointer;
}

.detail-actions button.primary,
.order-missing button {
  color: #111827;
  background: #fff;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 18px;
}

.detail-card {
  margin-top: 18px;
  padding: 22px;
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
}

.detail-grid .detail-card {
  margin-top: 0;
}

.detail-card h2 {
  margin: 0 0 16px;
  color: #111827;
  font-size: 20px;
}

.detail-card p {
  display: grid;
  gap: 6px;
  margin: 0;
}

.detail-card strong {
  color: #111827;
}

.detail-card span {
  color: #6b7280;
}

.detail-card dl {
  display: grid;
  gap: 12px;
  margin: 0;
}

.detail-card dl div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.detail-card dt {
  color: #6b7280;
}

.detail-card dd {
  margin: 0;
  color: #111827;
  font-weight: 800;
}

.detail-items {
  display: grid;
  gap: 14px;
}

.detail-item {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f1f2f4;
}

.detail-item:last-child {
  padding-bottom: 0;
  border-bottom: 0;
}

.detail-item img {
  width: 86px;
  height: 86px;
  object-fit: cover;
  border-radius: 12px;
  background: #f5f6f8;
}

.detail-item h3 {
  margin: 0 0 7px;
  color: #111827;
  font-size: 16px;
}

.detail-item p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.detail-item span,
.detail-item strong {
  color: #111827;
  font-weight: 900;
}

.price-card {
  margin-left: auto;
  max-width: 420px;
}

.price-card .payable {
  padding-top: 12px;
  border-top: 1px solid #f1f2f4;
}

.price-card .payable dd {
  color: #fe2c55;
  font-size: 24px;
}

@media (max-width: 820px) {
  .order-detail-page {
    padding: 16px 12px 40px;
  }

  .logistics-timeline {
    padding: 20px 16px;
  }

  .timeline-track {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px 0;
  }

  .timeline-node:nth-child(2)::before {
    display: none;
  }

  .detail-hero,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .detail-actions {
    justify-content: flex-start;
  }

  .detail-item {
    grid-template-columns: 72px minmax(0, 1fr);
  }

  .detail-item img {
    width: 72px;
    height: 72px;
  }

  .detail-item span,
  .detail-item strong {
    grid-column: 2;
  }

  .price-card {
    max-width: none;
  }

  @media (max-width: 480px) {
    .timeline-track {
      grid-template-columns: 1fr;
      gap: 24px 0;
    }

    .timeline-node::before {
      display: none;
    }
  }
}
</style>
