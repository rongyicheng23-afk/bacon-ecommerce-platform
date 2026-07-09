import axios from 'axios'
import type { CartResponse, AddToCartRequest, Cart, CartItem } from '../types/cart'
import { readCartItems, saveCartItems } from '@/utils/cart'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

/** 将本地 CartLine 转为后端 Cart 格式的 mock 响应 */
const buildMockCart = (): Cart => {
  const lines = readCartItems()
  const now = new Date().toISOString()
  const items: CartItem[] = lines.map((line) => ({
    cartItemId: line.id,
    cartId: 1,
    productId: line.productId,
    quantity: line.quantity,
    totalPrice: line.price * line.quantity,
    createdAt: now,
    updatedAt: now,
    product: {
      name: line.name,
      description: line.description,
      price: line.price,
      imageUrl: line.imageUrl || undefined
    }
  }))

  return {
    cartId: 1,
    userId: 1,
    items,
    createdAt: now,
    updatedAt: now
  }
}

const mockResponse = (cart: Cart): CartResponse => ({
  code: '0000',
  info: 'mock data',
  data: cart
})

export const cartService = {
  async getCart(): Promise<CartResponse> {
    try {
      const response = await axios.get<CartResponse>(`${BASE_URL}/cart/get`)
      return response.data
    } catch {
      return mockResponse(buildMockCart())
    }
  },

  async addToCart(data: AddToCartRequest): Promise<CartResponse> {
    try {
      const response = await axios.post<CartResponse>(`${BASE_URL}/cart/add`, {
        product_id: data.productId,
        quantity: data.quantity
      })
      return response.data
    } catch {
      // 委托给 utils/cart.ts 的 addProductToCart，需要 product 对象
      // 这里直接从 productStore 或 mock 数据中获取是困难的
      // 对于纯 mock 场景，调用方（cartStore）会通过 productStore.fetchProducts 先拿到数据
      // 此处做最小 mock：直接返回当前购物车状态
      return mockResponse(buildMockCart())
    }
  },

  async updateQuantity(cartItemId: number, quantity: number): Promise<CartResponse> {
    try {
      const response = await axios.put<CartResponse>(`${BASE_URL}/cart/update`, {
        cart_item_id: cartItemId,
        quantity
      })
      return response.data
    } catch {
      const items = readCartItems()
      const updated = items.map((item) =>
        item.id === cartItemId
          ? { ...item, quantity: Math.max(1, Math.min(quantity, item.stock || 1)) }
          : item
      )
      saveCartItems(updated)
      return mockResponse(buildMockCart())
    }
  },

  async removeItem(cartItemId: number): Promise<CartResponse> {
    try {
      const response = await axios.delete<CartResponse>(`${BASE_URL}/cart/remove/${cartItemId}`)
      return response.data
    } catch {
      const items = readCartItems().filter((item) => item.id !== cartItemId)
      saveCartItems(items)
      return mockResponse(buildMockCart())
    }
  },

  async clearCart(): Promise<CartResponse> {
    try {
      const response = await axios.post<CartResponse>(`${BASE_URL}/cart/clear`)
      return response.data
    } catch {
      saveCartItems([])
      return mockResponse(buildMockCart())
    }
  }
}
