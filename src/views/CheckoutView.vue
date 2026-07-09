<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { removeCartLineIds } from '@/utils/cart'

interface CheckoutItem {
  id: number
  productId: number
  skuId?: number
  skuName?: string
  name: string
  description: string
  price: number
  imageUrl: string | null
  category: string
  stock: number
  quantity: number
  selected: boolean
}

interface CheckoutDraft {
  items: CheckoutItem[]
  totalQuantity: number
  totalAmount: number
  totalSavings: number
  payableAmount: number
  createdAt: string
}

interface Address {
  id: number
  name: string
  phone: string
  detail: string
  isDefault?: boolean
}

const router = useRouter()
const draft = ref<CheckoutDraft | null>(null)
const selectedAddressId = ref(1)
const deliveryType = ref('standard')
const paymentType = ref('alipay')
const remark = ref('')
const actionMessage = ref('')

const addresses: Address[] = [
  {
    id: 1,
    name: '荣同学',
    phone: '138****2026',
    detail: '广东省广州市 天河区 默认收货地址',
    isDefault: true
  },
  {
    id: 2,
    name: '实习项目测试用户',
    phone: '139****0709',
    detail: '广东省深圳市 南山区 电商平台测试地址'
  }
]

const deliveryOptions = [
  { id: 'standard', name: '普通配送', desc: '预计 48 小时内发货', fee: 0 },
  { id: 'express', name: '加急配送', desc: '预计 24 小时内发货', fee: 12 }
]

const paymentOptions = [
  { id: 'alipay', name: '支付宝' },
  { id: 'wechat', name: '微信支付' },
  { id: 'card', name: '银行卡' }
]

const selectedDelivery = computed(() => {
  return deliveryOptions.find((item) => item.id === deliveryType.value) || deliveryOptions[0]
})

const payableAmount = computed(() => {
  return (draft.value?.payableAmount || 0) + selectedDelivery.value.fee
})

const readCheckoutDraft = () => {
  try {
    const data = JSON.parse(localStorage.getItem('checkoutDraft') || 'null') as CheckoutDraft | null
    draft.value = data?.items?.length ? data : null
  } catch {
    draft.value = null
  }
}

const recordBehavior = (action: string) => {
  const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
  logs.push({
    userId: 1,
    action,
    category: '订单',
    amount: payableAmount.value,
    itemCount: draft.value?.items.length || 0,
    timestamp: new Date().toISOString()
  })
  localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
}

const submitOrder = () => {
  if (!draft.value) return

  const orderId = Date.now()
  const selectedAddress = addresses.find((item) => item.id === selectedAddressId.value)
  const order = {
    orderId,
    status: 'pending_payment',
    items: draft.value.items,
    address: selectedAddress,
    deliveryType: deliveryType.value,
    paymentType: paymentType.value,
    remark: remark.value,
    totalAmount: draft.value.totalAmount,
    totalSavings: draft.value.totalSavings,
    deliveryFee: selectedDelivery.value.fee,
    payableAmount: payableAmount.value,
    createdAt: new Date().toISOString()
  }

  const orders = JSON.parse(localStorage.getItem('mockOrders') || '[]')
  localStorage.setItem('mockOrders', JSON.stringify([order, ...orders]))
  removeCartLineIds(draft.value.items.map((item) => item.id))
  localStorage.removeItem('checkoutDraft')
  recordBehavior('submit_order')
  actionMessage.value = `订单 ${orderId} 已提交`

  window.setTimeout(() => {
    router.push(`/payment/${orderId}`)
  }, 700)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

onMounted(() => {
  readCheckoutDraft()
})
</script>

<template>
  <main class="checkout-page">
    <p v-if="actionMessage" class="action-toast">{{ actionMessage }}</p>

    <section class="checkout-hero">
      <div>
        <span>Checkout</span>
        <h1>确认订单</h1>
        <p>核对收货地址、商品清单、配送方式和支付方式后提交订单。</p>
      </div>
      <button type="button" @click="router.push('/cart')">返回购物车</button>
    </section>

    <section v-if="!draft" class="empty-state">
      <h2>暂无待结算商品</h2>
      <p>请先在购物车选择商品，再进入订单确认页。</p>
      <button type="button" @click="router.push('/cart')">去购物车</button>
    </section>

    <template v-else>
      <section class="checkout-layout">
        <div class="checkout-main">
          <section class="checkout-card">
            <div class="section-title">
              <h2>收货地址</h2>
              <span>请选择本次订单的收货信息</span>
            </div>

            <div class="address-list">
              <label
                v-for="address in addresses"
                :key="address.id"
                :class="['address-card', { active: selectedAddressId === address.id }]"
              >
                <input v-model="selectedAddressId" type="radio" :value="address.id" />
                <span>
                  <strong>{{ address.name }} {{ address.phone }}</strong>
                  <small>{{ address.detail }}</small>
                </span>
                <em v-if="address.isDefault">默认</em>
              </label>
            </div>
          </section>

          <section class="checkout-card">
            <div class="section-title">
              <h2>商品清单</h2>
              <span>{{ draft.totalQuantity }} 件商品</span>
            </div>

            <article v-for="item in draft.items" :key="item.id" class="order-line">
              <img :src="item.imageUrl || undefined" :alt="item.name" @error="handleImageError" />
              <div>
              <span>{{ item.category }}</span>
              <h3>{{ item.name }}</h3>
              <p>{{ item.skuName || item.description }}</p>
              </div>
              <strong>¥{{ item.price }}</strong>
              <small>x {{ item.quantity }}</small>
              <b>¥{{ item.price * item.quantity }}</b>
            </article>
          </section>

          <section class="checkout-card">
            <div class="section-title">
              <h2>配送方式</h2>
              <span>{{ selectedDelivery.desc }}</span>
            </div>

            <div class="option-grid">
              <label
                v-for="option in deliveryOptions"
                :key="option.id"
                :class="['option-card', { active: deliveryType === option.id }]"
              >
                <input v-model="deliveryType" type="radio" :value="option.id" />
                <strong>{{ option.name }}</strong>
                <span>{{ option.desc }}</span>
                <small>{{ option.fee ? `+¥${option.fee}` : '免运费' }}</small>
              </label>
            </div>
          </section>

          <section class="checkout-card">
            <div class="section-title">
              <h2>支付方式</h2>
              <span>当前为前端模拟支付流程</span>
            </div>

            <div class="payment-options">
              <label
                v-for="option in paymentOptions"
                :key="option.id"
                :class="{ active: paymentType === option.id }"
              >
                <input v-model="paymentType" type="radio" :value="option.id" />
                {{ option.name }}
              </label>
            </div>

            <textarea v-model="remark" rows="3" placeholder="订单备注，可不填" />
          </section>
        </div>

        <aside class="summary-panel">
          <h2>金额明细</h2>
          <div class="summary-row">
            <span>商品总价</span>
            <strong>¥{{ draft.totalAmount }}</strong>
          </div>
          <div class="summary-row">
            <span>优惠金额</span>
            <strong>-¥{{ draft.totalSavings }}</strong>
          </div>
          <div class="summary-row">
            <span>配送费</span>
            <strong>¥{{ selectedDelivery.fee }}</strong>
          </div>
          <div class="summary-total">
            <span>应付金额</span>
            <strong>¥{{ payableAmount }}</strong>
          </div>
          <button type="button" @click="submitOrder">提交订单</button>
        </aside>
      </section>
    </template>
  </main>
</template>

<style>
.checkout-page {
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

.checkout-hero {
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

.checkout-hero span {
  color: #ffd7df;
  font-size: 0.86rem;
  font-weight: 900;
}

.checkout-hero h1 {
  margin: 0.2rem 0 0.4rem;
  font-size: 2rem;
}

.checkout-hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
}

.checkout-hero button,
.empty-state button,
.summary-panel button {
  min-height: 40px;
  padding: 0 1rem;
  border: 0;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

.checkout-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 1rem;
  align-items: start;
}

.checkout-main {
  display: grid;
  gap: 1rem;
}

.checkout-card,
.summary-panel,
.empty-state {
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.checkout-card {
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

.address-list,
.option-grid,
.payment-options {
  display: grid;
  gap: 0.75rem;
}

.address-card,
.option-card,
.payment-options label {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.75rem;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
}

.address-card.active,
.option-card.active,
.payment-options label.active {
  border-color: #fe2c55;
  background: #fff2f5;
}

.address-card strong,
.address-card small,
.option-card strong,
.option-card span,
.option-card small {
  display: block;
}

.address-card small,
.option-card span {
  margin-top: 0.25rem;
  color: #666;
}

.address-card em {
  color: #fe2c55;
  font-style: normal;
  font-weight: 900;
}

.order-line {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr) 80px 56px 88px;
  gap: 1rem;
  align-items: center;
  padding: 0.9rem 0;
  border-bottom: 1px solid #f1f2f4;
}

.order-line:last-child {
  border-bottom: 0;
}

.order-line img {
  width: 88px;
  height: 88px;
  border-radius: 12px;
  object-fit: cover;
}

.order-line span {
  color: #fe2c55;
  font-size: 0.78rem;
  font-weight: 900;
}

.order-line h3 {
  margin: 0.25rem 0;
  color: #111827;
  font-size: 1rem;
}

.order-line p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: #666;
  font-size: 0.84rem;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.order-line strong,
.order-line b {
  color: #fe2c55;
}

.payment-options {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.checkout-card textarea {
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  outline: none;
  resize: vertical;
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

.summary-panel button {
  width: 100%;
  min-height: 46px;
}

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

@media (max-width: 1100px) {
  .checkout-layout {
    grid-template-columns: 1fr;
  }

  .summary-panel {
    position: static;
  }
}

@media (max-width: 767px) {
  .checkout-hero,
  .section-title {
    align-items: flex-start;
    flex-direction: column;
  }

  .order-line {
    grid-template-columns: 72px minmax(0, 1fr);
  }

  .order-line strong,
  .order-line small,
  .order-line b {
    grid-column: 2;
  }

  .payment-options {
    grid-template-columns: 1fr;
  }
}
</style>
