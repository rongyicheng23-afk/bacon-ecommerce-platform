import { behaviorService } from '@/services/behaviorService'
import type { Product } from '@/types'

type BehaviorAction = 'view' | 'search' | 'favorite' | 'unfavorite' | 'cart' | 'purchase'

export function useBehaviorLog() {
  const recordBehavior = (
    action: BehaviorAction,
    product: Product,
    extra?: { quantity?: number; skuId?: number; skuName?: string; orderId?: number; amount?: number; source?: string }
  ) => {
    behaviorService.send({
      productId: product.productId,
      productName: product.name,
      action,
      category: product.category,
      quantity: extra?.quantity,
      skuId: extra?.skuId,
      skuName: extra?.skuName,
      orderId: extra?.orderId,
      amount: extra?.amount,
      source: extra?.source,
    })
  }

  return { recordBehavior }
}
