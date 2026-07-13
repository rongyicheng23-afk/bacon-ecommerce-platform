import api from './api'
import type { Product, ProductSku } from '@/types'

interface ApiResponse<T> {
  code: string
  info: string
  data: T
}

export const commerceService = {
  async favorites(): Promise<number[]> {
    const response = await api.get<ApiResponse<number[]>>('/favorites')
    return response.data.data
  },

  async toggleFavorite(productId: number, favored: boolean): Promise<number[]> {
    const response = favored
      ? await api.delete<ApiResponse<number[]>>(`/favorites/${productId}`)
      : await api.post<ApiResponse<number[]>>(`/favorites/${productId}`)
    return response.data.data
  },

  async addToCart(product: Product, sku?: ProductSku | null, quantity = 1): Promise<void> {
    await api.post('/cart/items', {
      productId: product.productId,
      skuId: sku?.skuId,
      quantity,
    })
  },
}
