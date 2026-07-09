import type { Product, ProductSku } from '@/types'

export interface CartLine {
  /** 唯一标识：有 SKU 时用 skuId，否则用 productId */
  id: number
  productId: number
  /** 选中的 SKU ID（可为空，表示未选规格） */
  skuId?: number
  /** 选中的 SKU 名称，如 "深空灰 · Pro 版" */
  skuName?: string
  name: string
  description: string
  /** 实际价格：选中 SKU 时用 SKU 价格，否则用商品最低价 */
  price: number
  imageUrl: string | null
  category: string
  /** 可用库存：选中 SKU 时用 SKU 库存，否则用商品总库存 */
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

export interface AddToCartOptions {
  quantity?: number
  sku?: ProductSku
}

export const toCartLine = (product: Product, options: AddToCartOptions = {}): CartLine => {
  const { quantity = 1, sku } = options

  // 有 SKU 时用 SKU 的信息，否则用商品主数据
  const id = sku ? sku.skuId : product.productId
  const price = sku ? sku.price : product.price
  const stock = sku ? sku.stock : product.stock
  const imageUrl = sku ? sku.imageUrl : product.imageUrls[0]

  return {
    id,
    productId: product.productId,
    skuId: sku?.skuId,
    skuName: sku?.name,
    name: product.name,
    description: product.description,
    price,
    imageUrl,
    category: product.category || '精选',
    stock,
    quantity: Math.max(1, Math.min(quantity, stock || 1)),
    selected: true
  }
}

export const addProductToCart = (product: Product, options: AddToCartOptions = {}) => {
  const { quantity = 1, sku } = options

  const items = readCartItems()

  // 有 SKU 时按 skuId 匹配已存在的行，否则按 productId 匹配
  const matchId = sku ? sku.skuId : product.productId
  const effectiveStock = sku ? sku.stock : product.stock

  const existing = items.find((item) => item.id === matchId)

  const nextItems = existing
    ? items.map((item) => {
        if (item.id !== matchId) return item
        const nextQuantity = Math.max(1, Math.min(item.quantity + quantity, effectiveStock || 1))
        return { ...item, quantity: nextQuantity, selected: true }
      })
    : [toCartLine(product, { quantity, sku }), ...items]

  saveCartItems(nextItems)
  return nextItems.find((item) => item.id === matchId)
}

export const getCartItemCount = () => {
  return readCartItems().reduce((sum, item) => sum + item.quantity, 0)
}

export const removeCartProductIds = (productIds: number[]) => {
  const idSet = new Set(productIds)
  const nextItems = readCartItems().filter((item) => !idSet.has(item.productId))
  saveCartItems(nextItems)
}
