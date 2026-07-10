export interface Coupon {
  id: number
  name: string
  description: string
  type: 'full_reduction' | 'percentage' | 'fixed'
  threshold: number    // 满多少可用
  discount: number     // 减多少 / 折扣百分比 / 固定减
  maxDiscount?: number // 百分比折扣上限
  category?: string    // 适用类目，空表示全场通用
  expireAt: string
  claimed: boolean
}

const now = Date.now()
const day = 86400000

export const allCoupons: Coupon[] = [
  { id: 1, name: '新人专享券', description: '首单满99减15', type: 'full_reduction', threshold: 99, discount: 15, expireAt: new Date(now + 30 * day).toISOString(), claimed: false },
  { id: 2, name: '满199减30', description: '全场满199减30', type: 'full_reduction', threshold: 199, discount: 30, expireAt: new Date(now + 15 * day).toISOString(), claimed: false },
  { id: 3, name: '满299减50', description: '全场满299减50', type: 'full_reduction', threshold: 299, discount: 50, expireAt: new Date(now + 15 * day).toISOString(), claimed: false },
  { id: 4, name: '数码专享9折', description: '数码类目满100享9折，最高减50', type: 'percentage', threshold: 100, discount: 10, maxDiscount: 50, category: '数码', expireAt: new Date(now + 7 * day).toISOString(), claimed: false },
  { id: 5, name: '全场95折', description: '全场满200享95折，最高减30', type: 'percentage', threshold: 200, discount: 5, maxDiscount: 30, expireAt: new Date(now + 20 * day).toISOString(), claimed: false },
  { id: 6, name: '满500减80', description: '全场满500减80', type: 'full_reduction', threshold: 500, discount: 80, expireAt: new Date(now + 10 * day).toISOString(), claimed: false },
  { id: 7, name: '服饰满减券', description: '服饰类目满150减20', type: 'full_reduction', threshold: 150, discount: 20, category: '服饰', expireAt: new Date(now + 14 * day).toISOString(), claimed: false },
  { id: 8, name: '食品8折券', description: '食品类目满50享8折，最高减15', type: 'percentage', threshold: 50, discount: 20, maxDiscount: 15, category: '食品', expireAt: new Date(now + 5 * day).toISOString(), claimed: false },
]

const STORAGE_KEY = 'claimedCoupons'

export const readClaimedCoupons = (): number[] => {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') }
  catch { return [] }
}

export const saveClaimedCoupons = (ids: number[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(ids))
}

/** 领取优惠券 */
export const claimCoupon = (couponId: number): boolean => {
  const claimed = readClaimedCoupons()
  if (claimed.includes(couponId)) return false
  claimed.push(couponId)
  saveClaimedCoupons(claimed)
  return true
}

/** 获取用户已领取的优惠券 */
export const getUserCoupons = (): Coupon[] => {
  const claimed = readClaimedCoupons()
  return allCoupons.filter(c => claimed.includes(c.id))
}

/** 计算最优优惠券的折扣金额 */
export const computeBestDiscount = (total: number, category?: string): { coupon: Coupon | null; discountAmount: number } => {
  const available = getUserCoupons().filter(c => {
    if (new Date(c.expireAt) < new Date()) return false // 已过期
    if (c.category && category && c.category !== category) return false // 类目不匹配
    if (total < c.threshold) return false // 未达到门槛
    return true
  })

  let bestCoupon: Coupon | null = null
  let bestAmount = 0

  available.forEach(c => {
    let amount = 0
    if (c.type === 'full_reduction' || c.type === 'fixed') {
      amount = c.discount
    } else if (c.type === 'percentage') {
      amount = Math.floor(total * c.discount / 100)
      if (c.maxDiscount) amount = Math.min(amount, c.maxDiscount)
    }
    if (amount > bestAmount) {
      bestAmount = amount
      bestCoupon = c
    }
  })

  return { coupon: bestCoupon, discountAmount: bestAmount }
}

/** 获取对某商品可用的优惠券 */
export const getProductCoupons = (price: number, category?: string): Coupon[] => {
  return allCoupons.filter(c => {
    if (new Date(c.expireAt) < new Date()) return false
    if (c.category && category && c.category !== category) return false
    if (price < c.threshold) return false
    return true
  })
}
