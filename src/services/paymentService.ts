import api from './api'
import type { PaymentResponse } from '../types/payment'

export const paymentService = {
  async makePayment(orderId: number, paymentMethod: number): Promise<PaymentResponse> {
    const response = await api.post<PaymentResponse>('/payment/pay', {
      orderId,
      paymentMethod
    })
    return response.data
  },

  async cancelPayment(paymentId: number): Promise<PaymentResponse> {
    const response = await api.post<PaymentResponse>('/payment/cancel', { paymentId })
    return response.data
  }
}
