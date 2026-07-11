<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

type OrderStatus = 'pending_payment' | 'paid' | 'shipped' | 'completed' | 'cancelled'

interface MockOrderItem {
  productId: number
  name?: string
  productName?: string
  price: number
  imageUrl?: string | null
  productImage?: string
  quantity: number
}

interface MockOrder {
  orderId: number
  status: OrderStatus
  items: MockOrderItem[]
  paymentType?: string
  payableAmount: number
  createdAt: string
  paidAt?: string
}

const route = useRoute()
const router = useRouter()
const order = ref<MockOrder | null>(null)
const selectedMethod = ref('alipay')
const loading = ref(false)
const error = ref('')
const actionMessage = ref('')

const paymentMethods = [
  { id: 'alipay', name: '支付宝', desc: '推荐使用，支付后立即更新订单' },
  { id: 'wechat', name: '微信支付', desc: '适合移动端扫码支付' },
  { id: 'card', name: '银行卡', desc: '模拟银行卡快捷支付' }
]

const totalQuantity = computed(() => {
  return order.value?.items.reduce((sum, item) => sum + item.quantity, 0) || 0
})

const readOrder = () => {
  const orderId = Number(route.params.orderId)
  if (Number.isNaN(orderId)) {
    error.value = '订单号不正确'
    return
  }

  try {
    const orders = JSON.parse(localStorage.getItem('mockOrders') || '[]') as MockOrder[]
    order.value = orders.find((item) => item.orderId === orderId) || null
    selectedMethod.value = order.value?.paymentType || 'alipay'

    if (!order.value) {
      error.value = '没有找到这个订单'
    }
  } catch {
    error.value = '读取订单失败'
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
    category: '订单',
    amount: order.value.payableAmount,
    timestamp: new Date().toISOString()
  })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}

const handlePayment = () => {
  if (!order.value || loading.value) return
  loading.value = true

  window.setTimeout(() => {
    if (!order.value) return
    order.value.status = 'paid'
    order.value.paymentType = selectedMethod.value
    order.value.paidAt = new Date().toISOString()
    saveOrder()
    recordBehavior('order_paid')
    actionMessage.value = '支付成功，订单已进入待发货'
    loading.value = false

    window.setTimeout(() => {
      router.push(`/payment-success/${order.value!.orderId}`)
    }, 700)
  }, 700)
}

const cancelPayment = () => {
  router.push('/orders')
}

onMounted(() => {
  readOrder()
})
</script>

<template>
  <main class="payment-page">
    <p v-if="actionMessage" class="payment-toast">{{ actionMessage }}</p>

    <section class="payment-hero">
      <div>
        <span>Payment</span>
        <h1>订单支付</h1>
        <p>当前为前端模拟支付，用于跑通电商下单流程。</p>
      </div>
      <button type="button" @click="router.push('/orders')">返回订单</button>
    </section>

    <section v-if="error" class="payment-empty">
      <h2>{{ error }}</h2>
      <p>请返回订单列表重新选择需要支付的订单。</p>
      <button type="button" @click="router.push('/orders')">返回订单列表</button>
    </section>

    <section v-else-if="order" class="payment-layout">
      <div class="payment-main">
        <article class="payment-card">
          <div class="payment-card-head">
            <div>
              <span>订单号</span>
              <h2>{{ order.orderId }}</h2>
            </div>
            <strong>¥{{ order.payableAmount.toFixed(2) }}</strong>
          </div>

          <div class="payment-meta">
            <p>
              <span>商品数量</span>
              <strong>{{ totalQuantity }} 件</strong>
            </p>
            <p>
              <span>下单时间</span>
              <strong>{{ new Date(order.createdAt).toLocaleString('zh-CN') }}</strong>
            </p>
          </div>

          <div class="payment-items">
            <article v-for="item in order.items.slice(0, 3)" :key="item.productId">
              <span>{{ item.name || item.productName || '商品' }}</span>
              <strong>¥{{ item.price.toFixed(2) }} × {{ item.quantity }}</strong>
            </article>
          </div>
        </article>

        <article class="payment-card">
          <h2>选择支付方式</h2>
          <div class="payment-method-list">
            <label
              v-for="method in paymentMethods"
              :key="method.id"
              :class="{ active: selectedMethod === method.id }"
            >
              <input v-model="selectedMethod" type="radio" :value="method.id" />
              <span>
                <strong>{{ method.name }}</strong>
                <small>{{ method.desc }}</small>
              </span>
            </label>
          </div>
        </article>
      </div>

      <aside class="payment-summary">
        <h2>应付金额</h2>
        <strong>¥{{ order.payableAmount.toFixed(2) }}</strong>
        <p>支付成功后，订单状态会从“待付款”变为“待发货”。</p>
        <button type="button" class="pay-button" :disabled="loading || order.status !== 'pending_payment'" @click="handlePayment">
          {{ order.status === 'pending_payment' ? (loading ? '支付处理中...' : '立即支付') : '该订单无需支付' }}
        </button>
        <button type="button" class="cancel-button" :disabled="loading" @click="cancelPayment">稍后支付</button>
      </aside>
    </section>
  </main>
</template>

<style>
.payment-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.payment-toast {
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

.payment-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 30px;
  color: #fff;
  background:
    linear-gradient(120deg, rgba(17, 24, 39, 0.88), rgba(254, 44, 85, 0.66)),
    url('https://images.unsplash.com/photo-1556742111-a301076d9d18?auto=format&fit=crop&w=1800&q=85') center/cover;
  border-radius: 16px;
}

.payment-hero span {
  color: rgba(255, 255, 255, 0.74);
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.payment-hero h1 {
  margin: 6px 0;
  font-size: 34px;
}

.payment-hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.82);
}

.payment-hero button,
.payment-empty button {
  border: 0;
  color: #241B2F;
  background: #fff;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 900;
  cursor: pointer;
}

.payment-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 16px;
  align-items: start;
  margin-top: 18px;
}

.payment-main {
  display: grid;
  gap: 16px;
}

.payment-card,
.payment-summary,
.payment-empty {
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
}

.payment-card,
.payment-summary {
  padding: 22px;
}

.payment-card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.payment-card-head span,
.payment-meta span {
  color: #756D7E;
  font-size: 13px;
}

.payment-card h2,
.payment-card-head h2,
.payment-summary h2 {
  margin: 0;
  color: #241B2F;
}

.payment-card-head > strong {
  color: #980B32;
  font-size: 28px;
}

.payment-meta {
  display: grid;
  gap: 10px;
  margin: 18px 0;
}

.payment-meta p,
.payment-items article {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin: 0;
}

.payment-items {
  display: grid;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid #E9E4EE;
}

.payment-method-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.payment-method-list label {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 14px;
  border: 1px solid #948B9D;
  border-radius: 14px;
  cursor: pointer;
}

.payment-method-list label.active {
  border-color: #980B32;
  background: #F4EFF7;
}

.payment-method-list span {
  display: grid;
  gap: 4px;
}

.payment-method-list small,
.payment-summary p {
  color: #756D7E;
}

.payment-summary {
  position: sticky;
  top: 150px;
}

.payment-summary > strong {
  display: block;
  margin: 12px 0;
  color: #980B32;
  font-size: 34px;
}

.pay-button,
.cancel-button {
  width: 100%;
  min-height: 46px;
  border-radius: 999px;
  font-weight: 900;
  cursor: pointer;
}

.pay-button {
  border: 0;
  color: #fff;
  background: #980B32;
}

.pay-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.cancel-button {
  margin-top: 10px;
  border: 1px solid #948B9D;
  color: #374151;
  background: #fff;
}

.payment-empty {
  margin-top: 18px;
  padding: 50px 20px;
  text-align: center;
}

.payment-empty h2 {
  margin: 0 0 8px;
  color: #241B2F;
}

@media (max-width: 820px) {
  .payment-page {
    padding: 16px 12px 40px;
  }

  .payment-hero,
  .payment-layout {
    grid-template-columns: 1fr;
  }

  .payment-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .payment-summary {
    position: static;
  }
}
</style>
