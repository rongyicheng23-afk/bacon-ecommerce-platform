import api from './api'
import type { CartResponse, AddToCartRequest } from '../types/cart'

export const cartService = {
  async getCart(): Promise<CartResponse> {
    const response = await api.get<CartResponse>('/cart/get')
    return response.data
  },

  async addToCart(data: AddToCartRequest): Promise<CartResponse> {
    const response = await api.post<CartResponse>('/cart/add', {
      product_id: data.productId,
      quantity: data.quantity
    })
    return response.data
  },

  async updateQuantity(cartItemId: number, quantity: number): Promise<CartResponse> {
    const response = await api.put<CartResponse>('/cart/update', {
      cart_item_id: cartItemId,
      quantity
    })
    return response.data
  },

  async removeItem(cartItemId: number): Promise<CartResponse> {
    const response = await api.delete<CartResponse>(`/cart/remove/${cartItemId}`)
    return response.data
  },

  async clearCart(): Promise<CartResponse> {
    const response = await api.post<CartResponse>('/cart/clear')
    return response.data
  }
}
