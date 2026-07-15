import api from './api'

interface ApiResponse<T> {
  code: string
  info: string
  data: T
}

export interface SellerDashboard {
  totalProducts: number
  activeProducts: number
  totalStock: number
  totalOrders: number
  pendingShipment: number
  totalRevenue: number
  recentOrders: SellerOrder[]
}

export interface SellerOrder {
  orderId: number
  userId: number
  totalAmount: number
  payableAmount: number
  status: string
  createdAt: string
  items: SellerOrderItem[]
}

export interface SellerOrderItem {
  orderItemId: number
  productId: number
  productName: string
  quantity: number
  price: number
}

export interface SellerProduct {
  productId: number
  name: string
  description: string
  price: number
  stock: number
  status: string
  category: string
  imageUrls: string[]
  skus: { skuId: number; name: string; price: number; stock: number; imageUrl: string }[]
}

export const sellerService = {
  async getDashboard(): Promise<SellerDashboard> {
    const response = await api.get<ApiResponse<SellerDashboard>>('/seller/dashboard')
    return response.data.data
  },

  async getOrders(): Promise<SellerOrder[]> {
    const response = await api.get<ApiResponse<SellerOrder[]>>('/seller/orders')
    return response.data.data
  },

  async shipOrder(orderId: number): Promise<SellerOrder> {
    const response = await api.post<ApiResponse<SellerOrder>>(`/seller/orders/${orderId}/ship`)
    return response.data.data
  },

  async getProducts(): Promise<SellerProduct[]> {
    const response = await api.get<ApiResponse<SellerProduct[]>>('/seller/products')
    return response.data.data
  },

  async createProduct(data: {
    name: string; description: string; price: number; stock: number; category: string; imageUrls?: string[]
  }): Promise<SellerProduct> {
    const response = await api.post<ApiResponse<SellerProduct>>('/seller/products', data)
    return response.data.data
  },

  async updateProduct(productId: number, data: Record<string, unknown>): Promise<SellerProduct> {
    const response = await api.put<ApiResponse<SellerProduct>>(`/seller/products/${productId}`, data)
    return response.data.data
  },

  async updateProductStatus(productId: number, status: string): Promise<SellerProduct> {
    const response = await api.patch<ApiResponse<SellerProduct>>(`/seller/products/${productId}/status`, { status })
    return response.data.data
  }
}
