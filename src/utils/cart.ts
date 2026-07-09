import type { Product } from '@/types'

export interface CartLine {
  id: number
  productId: number
  name: string
  description: string
  price: number
  imageUrl: string | null
  category: string
  stock: number
  quantity: number
  selected: boolean
}

const cartStorageKey = 'mockCartItems'
export const cartUpdatedEvent = 'mock-cart-updated'

export const readCartItems = () => {
  try {
    const items = JSON.parse(localStorage.getItem(cartStorageKey) || '[]') as CartLine[]
    return Array.isArray(items) ? items : []
  } catch {
    return []
  }
}

export const saveCartItems = (items: CartLine[]) => {
  localStorage.setItem(cartStorageKey, JSON.stringify(items))
  window.dispatchEvent(new CustomEvent(cartUpdatedEvent))
}

export const toCartLine = (product: Product, quantity = 1): CartLine => ({
  id: product.productId,
  productId: product.productId,
  name: product.name,
  description: product.description,
  price: product.price,
  imageUrl: product.imageUrls[0],
  category: product.category || '精选',
  stock: product.stock,
  quantity: Math.max(1, Math.min(quantity, product.stock || 1)),
  selected: true
})

export const addProductToCart = (product: Product, quantity = 1) => {
  const items = readCartItems()
  const existing = items.find((item) => item.productId === product.productId)

  const nextItems = existing
    ? items.map((item) => {
        if (item.productId !== product.productId) return item
        const nextQuantity = Math.max(1, Math.min(item.quantity + quantity, item.stock || 1))
        return { ...item, quantity: nextQuantity, selected: true }
      })
    : [toCartLine(product, quantity), ...items]

  saveCartItems(nextItems)
  return nextItems.find((item) => item.productId === product.productId)
}

export const getCartItemCount = () => {
  return readCartItems().reduce((sum, item) => sum + item.quantity, 0)
}

export const removeCartProductIds = (productIds: number[]) => {
  const idSet = new Set(productIds)
  const nextItems = readCartItems().filter((item) => !idSet.has(item.productId))
  saveCartItems(nextItems)
}
