<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { addressService } from '@/services/addressService'
import api from '@/services/api'

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

const router = useRouter()
const draft = ref<CheckoutDraft | null>(null)
const selectedAddressId = ref(0)
const deliveryType = ref('standard')
const paymentType = ref('alipay')
const remark = ref('')
const actionMessage = ref('')
const showAddressForm = ref(false)
const savingAddress = ref(false)
const addressForm = ref({ name: '', phone: '', detail: '' })

const addresses = ref<Array<{ id: number; name: string; phone: string; detail: string; isDefault?: boolean }>>([])

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

const loadAddresses = async () => {
  try {
    addresses.value = await addressService.list()
  } catch {
    addresses.value = []
  }
  const defaultAddr = addresses.value.find((address) => address.isDefault)
  selectedAddressId.value = defaultAddr?.id ?? addresses.value[0]?.id ?? 0
}

const saveAddress = async () => {
  const form = addressForm.value
  if (!form.name.trim() || !form.phone.trim() || !form.detail.trim()) {
    actionMessage.value = '请完整填写收件人、手机号和详细地址'
    return
  }

  savingAddress.value = true
  try {
    const address = await addressService.create({
      name: form.name.trim(),
      phone: form.phone.trim(),
      detail: form.detail.trim(),
      isDefault: addresses.value.length === 0,
    })
    await loadAddresses()
    selectedAddressId.value = address.id
    addressForm.value = { name: '', phone: '', detail: '' }
    showAddressForm.value = false
    actionMessage.value = '收货地址已保存并选中'
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '保存地址失败'
  } finally {
    savingAddress.value = false
  }
}

const submitOrder = async () => {
  if (!draft.value) return
  if (!selectedAddressId.value) {
    actionMessage.value = '请先添加并选择收货地址'
    return
  }
  try {
    const response = await api.post<{ code: string; data: { orderId: number } }>('/orders', {
      addressId: selectedAddressId.value,
      deliveryType: deliveryType.value,
      paymentType: paymentType.value,
      remark: remark.value,
    })
    const orderId = response.data.data.orderId
    localStorage.removeItem('checkoutDraft')
    actionMessage.value = `订单 ${orderId} 已提交`
    window.setTimeout(() => router.push(`/payment/${orderId}`), 700)
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '提交订单失败'
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

onMounted(async () => {
  readCheckoutDraft()
  await loadAddresses()
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
              <div class="section-actions">
                <span>请选择本次订单的收货信息</span>
                <button type="button" class="add-address-button" @click="showAddressForm = !showAddressForm">
                  {{ showAddressForm ? '收起表单' : '新增地址' }}
                </button>
              </div>
            </div>

            <form v-if="showAddressForm" class="checkout-address-form" @submit.prevent="saveAddress">
              <input v-model="addressForm.name" required maxlength="50" placeholder="收件人姓名" />
              <input v-model="addressForm.phone" required maxlength="30" placeholder="手机号" />
              <input v-model="addressForm.detail" required maxlength="300" placeholder="省 / 市 / 区 / 街道 / 门牌号" />
              <button type="submit" :disabled="savingAddress">
                {{ savingAddress ? '保存中...' : '保存并使用' }}
              </button>
            </form>

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
  background: linear-gradient(135deg, #241B2F, #2d1b42);
  color: #fff;
}

.checkout-hero span {
  color: #AD1745;
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
  background: #980B32;
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
  color: #241B2F;
}

.section-title span {
  color: #777;
  font-size: 0.86rem;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.add-address-button,
.checkout-address-form button {
  min-height: 34px;
  padding: 0 0.85rem;
  border: 1px solid #980B32;
  border-radius: 8px;
  color: #980B32;
  background: #fff;
  cursor: pointer;
  font-weight: 800;
}

.checkout-address-form {
  display: grid;
  grid-template-columns: 140px 180px minmax(0, 1fr) auto;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding: 0.85rem;
  border-radius: 12px;
  background: #F7F4F8;
}

.checkout-address-form input {
  min-width: 0;
  min-height: 38px;
  padding: 0 0.75rem;
  border: 1px solid #D9D2DE;
  border-radius: 8px;
  outline: none;
}

.checkout-address-form input:focus {
  border-color: #980B32;
}

.checkout-address-form button {
  color: #fff;
  background: #980B32;
}

.checkout-address-form button:disabled {
  cursor: wait;
  opacity: 0.65;
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
  border: 1px solid #948B9D;
  border-radius: 12px;
  cursor: pointer;
}

.address-card.active,
.option-card.active,
.payment-options label.active {
  border-color: #980B32;
  background: #F4EFF7;
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
  color: #756D7E;
}

.address-card em {
  color: #980B32;
  font-style: normal;
  font-weight: 900;
}

.order-line {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr) 80px 56px 88px;
  gap: 1rem;
  align-items: center;
  padding: 0.9rem 0;
  border-bottom: 1px solid #E9E4EE;
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
  color: #980B32;
  font-size: 0.78rem;
  font-weight: 900;
}

.order-line h3 {
  margin: 0.25rem 0;
  color: #241B2F;
  font-size: 1rem;
}

.order-line p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: #756D7E;
  font-size: 0.84rem;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.order-line strong,
.order-line b {
  color: #980B32;
}

.payment-options {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.checkout-card textarea {
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem;
  border: 1px solid #948B9D;
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

.summary-panel button {
  width: 100%;
  min-height: 46px;
}

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

  .section-actions,
  .checkout-address-form {
    width: 100%;
  }

  .section-actions {
    justify-content: space-between;
  }

  .checkout-address-form {
    grid-template-columns: 1fr;
  }
}
</style>
