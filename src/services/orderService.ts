import axios from 'axios'
import type { CreateOrderRequest, OrderResponse, OrderListResponse, Order, OrderItem, OrderStatus } from '../types/order'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
const STORAGE_KEY = 'mockOrders'

interface LocalOrder {
  orderId: number
  status: string
  items: Array<{
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
  }>
  address?: { name: string; phone: string; detail: string }
  deliveryType?: string
  paymentType?: string
  remark?: string
  totalAmount: number
  totalSavings?: number
  deliveryFee?: number
  payableAmount: number
  createdAt: string
  paidAt?: string
}

const readLocalOrders = (): LocalOrder[] => {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(data) ? data : []
  } catch {
    return []
  }
}

const saveLocalOrders = (orders: LocalOrder[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(orders))
}

/** 将本地订单转为后端 Order 格式 */
const toOrder = (local: LocalOrder): Order => ({
  orderId: local.orderId,
  userId: 1,
  totalAmount: local.totalAmount,
  payableAmount: local.payableAmount,
  status: local.status as OrderStatus,
  payType: (local.paymentType === 'alipay' ? 1 : local.paymentType === 'wechat' ? 2 : 3) as Order['payType'],
  payTime: local.paidAt,
  createdAt: local.createdAt,
  updatedAt: local.createdAt,
  items: local.items.map(
    (item): OrderItem => ({
      orderItemId: item.id || item.skuId || item.productId,
      productId: item.productId,
      skuId: item.skuId,
      skuName: item.skuName,
      quantity: item.quantity,
      price: item.price,
      productName: item.name || item.productName || '商品',
      productImage: item.imageUrl || item.productImage
    })
  )
})

const mockOrderResponse = (order: Order): OrderResponse => ({
  code: '0000',
  info: 'mock data',
  data: order
})

const mockListResponse = (orders: Order[]): OrderListResponse => ({
  code: '0000',
  info: 'mock data',
  data: orders
})

export const orderService = {
  async createOrder(request: CreateOrderRequest): Promise<OrderResponse> {
    try {
      const response = await axios.post<OrderResponse>(`${BASE_URL}/order/create`, request)
      return response.data
    } catch {
      // 创建 mock 订单
      const items: LocalOrder['items'] = request.products.map((p) => ({
        productId: p.productId,
        quantity: p.quantity,
        price: 0,
        name: `商品 #${p.productId}`
      }))

      const now = new Date().toISOString()
      const order: LocalOrder = {
        orderId: Date.now(),
        status: 'pending_payment',
        items,
        totalAmount: 0,
        payableAmount: 0,
        createdAt: now
      }

      const allOrders = readLocalOrders()
      saveLocalOrders([order, ...allOrders])
      return mockOrderResponse(toOrder(order))
    }
  },

  async getOrders(): Promise<OrderListResponse> {
    try {
      const response = await axios.get<OrderListResponse>(`${BASE_URL}/order/list`)
      return response.data
    } catch {
      const localOrders = readLocalOrders()
      return mockListResponse(localOrders.map(toOrder))
    }
  },

  async getOrderById(orderId: number): Promise<OrderResponse> {
    try {
      const response = await axios.get<OrderResponse>(`${BASE_URL}/order/get/${orderId}`)
      return response.data
    } catch {
      const localOrders = readLocalOrders()
      const found = localOrders.find((o) => o.orderId === orderId)
      if (!found) {
        return { code: '0001', info: '订单不存在', data: null as unknown as Order }
      }
      return mockOrderResponse(toOrder(found))
    }
  },

  async cancelOrder(orderId: number): Promise<OrderResponse> {
    try {
      const response = await axios.post<OrderResponse>(`${BASE_URL}/order/cancel/${orderId}`)
      return response.data
    } catch {
      const localOrders = readLocalOrders()
      const updated = localOrders.map((o) =>
        o.orderId === orderId ? { ...o, status: 'cancelled' } : o
      )
      saveLocalOrders(updated)
      const found = updated.find((o) => o.orderId === orderId)!
      return mockOrderResponse(toOrder(found))
    }
  },

  async checkOrderStatus(orderId: number): Promise<OrderResponse> {
    try {
      const response = await axios.get<OrderResponse>(`${BASE_URL}/order/status/${orderId}`)
      return response.data
    } catch {
      const localOrders = readLocalOrders()
      const found = localOrders.find((o) => o.orderId === orderId)
      if (!found) {
        return { code: '0001', info: '订单不存在', data: null as unknown as Order }
      }
      return mockOrderResponse(toOrder(found))
    }
  }
}
