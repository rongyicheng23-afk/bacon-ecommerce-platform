import type { Product } from '@/types'

interface BehaviorLog {
  productId?: number
  action?: string
  category?: string
  timestamp?: string
}

const actionWeights: Record<string, number> = {
  view: 1,
  favorite: 4,
  cart: 6,
  buy: 8,
  submit_order: 10,
  view_recommendation: 2
}

export const readBehaviorLogs = () => {
  try {
    const logs = JSON.parse(localStorage.getItem('behaviorLogs') || '[]') as BehaviorLog[]
    return Array.isArray(logs) ? logs : []
  } catch {
    return []
  }
}

const recencyBoost = (timestamp?: string) => {
  if (!timestamp) return 1
  const hours = (Date.now() - new Date(timestamp).getTime()) / (1000 * 60 * 60)
  if (hours <= 1) return 1.4
  if (hours <= 24) return 1.2
  if (hours <= 72) return 1.05
  return 1
}

export const getPersonalizedProducts = (products: Product[], limit = 40) => {
  const logs = readBehaviorLogs()

  if (logs.length === 0) {
    return products.slice(16, 16 + limit)
  }

  const productScores = new Map<number, number>()
  const categoryScores = new Map<string, number>()

  logs.forEach((log) => {
    const weight = (actionWeights[log.action || ''] || 1) * recencyBoost(log.timestamp)

    if (log.productId) {
      productScores.set(log.productId, (productScores.get(log.productId) || 0) + weight)
    }

    if (log.category && log.category !== '订单') {
      categoryScores.set(log.category, (categoryScores.get(log.category) || 0) + weight)
    }
  })

  return [...products]
    .map((product) => {
      const productScore = productScores.get(product.productId) || 0
      const categoryScore = product.category ? categoryScores.get(product.category) || 0 : 0
      const stockScore = product.stock > 0 ? 0.5 : -10

      return {
        product,
        score: productScore * 1.4 + categoryScore + stockScore
      }
    })
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score
      return b.product.stock - a.product.stock
    })
    .map((item) => item.product)
    .slice(0, limit)
}

export const getRecommendationSummary = () => {
  const logs = readBehaviorLogs()
  const categoryScores = new Map<string, number>()

  logs.forEach((log) => {
    if (!log.category || log.category === '订单') return
    const weight = actionWeights[log.action || ''] || 1
    categoryScores.set(log.category, (categoryScores.get(log.category) || 0) + weight)
  })

  return [...categoryScores.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([category, score]) => ({ category, score }))
}
