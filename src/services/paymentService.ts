import axios from 'axios'
import type { PaymentResponse } from '../types/payment'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
const ORDERS_KEY = 'mockOrders'

interface LocalOrder {
  orderId: number
  status: string
  paymentType?: string
  payableAmount: number
  paidAt?: string
  [key: string]: unknown
}

const readLocalOrders = (): LocalOrder[] => {
  try {
    const data = JSON.parse(localStorage.getItem(ORDERS_KEY) || '[]')
    return Array.isArray(data) ? data : []
  } catch {
    return []
  }
}

const saveLocalOrders = (orders: LocalOrder[]) => {
  localStorage.setItem(ORDERS_KEY, JSON.stringify(orders))
}

const mockSuccess = (): PaymentResponse => ({
  code: '0000',
  info: '支付成功',
  data: { success: true, paymentId: Date.now(), status: 'success' }
})

const mockFailed = (info: string): PaymentResponse => ({
  code: '0001',
  info,
  data: { success: false }
})

export const paymentService = {
  async makePayment(orderId: number, paymentMethod: number): Promise<PaymentResponse> {
    try {
      const response = await axios.post<PaymentResponse>(`${BASE_URL}/payment/pay`, {
        orderId,
        paymentMethod
      })
      return response.data
    } catch {
      const orders = readLocalOrders()
      const found = orders.find((o) => o.orderId === orderId)

      if (!found) {
        return mockFailed('订单不存在')
      }

      if (found.status !== 'pending_payment') {
        return mockFailed('该订单当前状态不可支付')
      }

      const paymentTypeMap: Record<number, string> = { 1: 'alipay', 2: 'wechat', 3: 'card' }
      const updated = orders.map((o) =>
        o.orderId === orderId
          ? { ...o, status: 'paid', paymentType: paymentTypeMap[paymentMethod] || 'alipay', paidAt: new Date().toISOString() }
          : o
      )
      saveLocalOrders(updated)

      // 记录行为日志
      try {
        const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]')
        logs.push({
          userId: 1,
          action: 'order_paid',
          orderId,
          amount: found.payableAmount,
          timestamp: new Date().toISOString()
        })
        localStorage.setItem('behaviorLogs', JSON.stringify(logs.slice(-100)))
      } catch { /* ignore */ }

      return mockSuccess()
    }
  },

  async cancelPayment(paymentId: number): Promise<PaymentResponse> {
    try {
      const response = await axios.post<PaymentResponse>(`${BASE_URL}/payment/cancel`, { paymentId })
      return response.data
    } catch {
      return { code: '0000', info: '支付已取消', data: { success: false, status: 'cancelled' } }
    }
  }
}
