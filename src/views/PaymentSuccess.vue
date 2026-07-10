<template>
  <div class="success-container">
    <section class="success-hero">
      <div class="success-icon">
        <svg viewBox="0 0 24 24" width="56" height="56">
          <path
            fill="currentColor"
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
          />
        </svg>
      </div>
      <div>
        <span>Payment Success</span>
        <h1>支付成功</h1>
        <p>您的订单已支付成功，我们将尽快为您发货。</p>
      </div>
    </section>

    <div class="success-content">
      <div class="order-details" v-if="orderInfo">
        <div class="info-row">
          <span class="label">订单号</span>
          <span class="value">{{ orderInfo.orderId }}</span>
        </div>
        <div class="info-row">
          <span class="label">实付金额</span>
          <span class="value amount">¥{{ orderInfo.payableAmount.toFixed(2) }}</span>
        </div>
        <div class="info-row">
          <span class="label">支付方式</span>
          <span class="value">{{ getPaymentMethodName(orderInfo.payType) }}</span>
        </div>
        <div class="info-row">
          <span class="label">支付时间</span>
          <span class="value">{{ orderInfo.payTime ? formatDate(orderInfo.payTime) : '刚刚' }}</span>
        </div>
      </div>

      <div class="loading-state" v-else>
        加载订单信息...
      </div>

      <div class="action-buttons">
        <button @click="viewOrder" class="primary-button">查看订单详情</button>
        <button @click="backToHome" class="secondary-button">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { orderService } from '../services/orderService'
import type { Order } from '../types/order'

const route = useRoute()
const router = useRouter()
const orderId = route.params.orderId
const orderInfo = ref<Order | null>(null)

const getPaymentMethodName = (payType?: number) => {
  switch (payType) {
    case 1:
      return '支付宝支付'
    case 2:
      return '微信支付'
    case 3:
      return '信用卡支付'
    default:
      return '未知支付方式'
  }
}

const formatDate = (date?: string) => {
  if (!date) return '未知时间'
  return new Date(date).toLocaleString()
}

const viewOrder = () => {
  router.push({ name: 'order-detail', params: { id: orderId } })
}

const backToHome = () => {
  router.push({ name: 'home' })
}

onMounted(async () => {
  try {
    const response = await orderService.getOrderById(Number(orderId))
    if (response.code === '0000') {
      orderInfo.value = response.data
    }
  } catch (error) {
    console.error('获取订单信息失败:', error)
  }
})
</script>

<style scoped>
.success-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.success-hero {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 30px;
  color: #fff;
  background: linear-gradient(120deg, rgba(17, 24, 39, 0.88), rgba(46, 213, 115, 0.6)),
    url('https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1800&q=85') center/cover;
  border-radius: 16px;
  margin-bottom: 18px;
}

.success-hero span {
  color: rgba(255, 255, 255, 0.74);
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.success-hero h1 {
  margin: 6px 0;
  font-size: 34px;
}

.success-hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.82);
}

.success-content {
  background: white;
  padding: 28px;
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  text-align: center;
}

.success-icon {
  flex-shrink: 0;
  color: #2ed573;
}

.order-details {
  display: grid;
  gap: 14px;
  margin: 0 0 24px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #f7f8fa;
  border-radius: 12px;
}

.label {
  color: #64748b;
  font-weight: 800;
}

.value {
  color: #0f172a;
  font-weight: 700;
}

.amount {
  color: #ff2f68;
  font-size: 1.25rem;
  font-weight: 900;
}

.loading-state {
  padding: 20px;
  color: #64748b;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.primary-button,
.secondary-button {
  min-height: 44px;
  padding: 0 24px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-weight: 900;
  font-size: 14px;
  transition: opacity 0.2s ease;
}

.primary-button {
  background: #ff2f68;
  color: #fff;
}

.primary-button:hover {
  opacity: 0.9;
}

.secondary-button {
  background: #f1f2f4;
  color: #374151;
}

.secondary-button:hover {
  background: #e5e7eb;
}

@media (max-width: 520px) {
  .success-hero {
    flex-direction: column;
    text-align: center;
  }

  .action-buttons {
    flex-direction: column;
  }

  .primary-button,
  .secondary-button {
    width: 100%;
  }
}
</style>
