import api from './api'

type BehaviorAction = 'view' | 'search' | 'favorite' | 'unfavorite' | 'cart' | 'buy' | 'purchase'

interface BehaviorPayload {
  productId: number
  productName?: string
  action: BehaviorAction
  category?: string
  quantity?: number
  skuId?: number
  skuName?: string
  orderId?: number
  amount?: number
  source?: string
}

interface BehaviorResponse {
  code: string
  info: string
  data: { logId: number; eventId: string; createdAt: string }
}

export const behaviorService = {
  async send(payload: BehaviorPayload): Promise<void> {
    let sessionId = sessionStorage.getItem('bacon_session_id')
    if (!sessionId) {
      sessionId = 'sess-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8)
      sessionStorage.setItem('bacon_session_id', sessionId)
    }

    // 'buy' 映射为后端标准 action 'purchase'
    const action = payload.action === 'buy' ? 'purchase' : payload.action

    try {
      await api.post<BehaviorResponse>('/behaviors', {
        productId: payload.productId,
        productName: payload.productName,
        action,
        category: payload.category,
        quantity: payload.quantity,
        skuId: payload.skuId,
        skuName: payload.skuName,
        orderId: payload.orderId,
        amount: payload.amount,
        source: payload.source,
        sessionId,
      })
    } catch {
      // 静默失败
    }
  }
}
