import api from './api'
import type { CreateOrderRequest, OrderResponse, OrderListResponse } from '../types/order'

export const orderService = {
  async createOrder(request: CreateOrderRequest): Promise<OrderResponse> {
    const response = await api.post<OrderResponse>('/order/create', request)
    return response.data
  },

  async getOrders(): Promise<OrderListResponse> {
    const response = await api.get<OrderListResponse>('/order/list')
    return response.data
  },

  async getOrderById(orderId: number): Promise<OrderResponse> {
    const response = await api.get<OrderResponse>(`/order/get/${orderId}`)
    return response.data
  },

  async cancelOrder(orderId: number): Promise<OrderResponse> {
    const response = await api.post<OrderResponse>(`/order/cancel/${orderId}`)
    return response.data
  },

  async checkOrderStatus(orderId: number): Promise<OrderResponse> {
    const response = await api.get<OrderResponse>(`/order/status/${orderId}`)
    return response.data
  }
}
