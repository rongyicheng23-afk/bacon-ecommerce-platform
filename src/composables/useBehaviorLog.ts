import { ref } from 'vue'

const STORAGE_KEY = 'behaviorLogs'
const MAX_LOGS = 100

export interface BehaviorPayload {
  userId?: number
  productId?: number
  productName?: string
  action: string
  category?: string
  quantity?: number
  skuId?: number
  skuName?: string
  orderId?: number
  amount?: number
  itemCount?: number
  timestamp?: string
}

/** 读取所有行为日志 */
export const readBehaviorLogs = (): BehaviorPayload[] => {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(data) ? data : []
  } catch {
    return []
  }
}

/** 记录一条行为日志 */
export const recordBehavior = (payload: BehaviorPayload) => {
  const logs = readBehaviorLogs()
  logs.push({
    userId: 1,
    timestamp: new Date().toISOString(),
    ...payload
  })
  localStorage.setItem(STORAGE_KEY, JSON.stringify(logs.slice(-MAX_LOGS)))
}

/** 清空行为日志 */
export const clearBehaviorLogs = () => {
  localStorage.removeItem(STORAGE_KEY)
}

/** Vue composable：带 toast 消息的行为日志 */
export const useBehaviorLog = () => {
  const actionMessage = ref('')

  const log = (payload: BehaviorPayload, message?: string) => {
    recordBehavior(payload)
    if (message) {
      actionMessage.value = message
    }
  }

  const showMessage = (message: string) => {
    actionMessage.value = message
    window.setTimeout(() => {
      actionMessage.value = ''
    }, 1600)
  }

  return { actionMessage, log, showMessage }
}
