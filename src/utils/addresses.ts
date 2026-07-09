export interface Address {
  id: number
  name: string
  phone: string
  detail: string
  isDefault?: boolean
}

const STORAGE_KEY = 'mockAddresses'

const DEFAULT_ADDRESSES: Address[] = [
  {
    id: 1,
    name: '荣同学',
    phone: '13800002026',
    detail: '广东省广州市 天河区 默认收货地址',
    isDefault: true
  },
  {
    id: 2,
    name: '实习项目测试用户',
    phone: '13900000709',
    detail: '广东省深圳市 南山区 电商平台测试地址'
  }
]

export const readAddresses = (): Address[] => {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    if (Array.isArray(data) && data.length > 0) return data
  } catch { /* ignore */ }
  // 首次初始化
  localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_ADDRESSES))
  return [...DEFAULT_ADDRESSES]
}

export const saveAddresses = (list: Address[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

export const createAddress = (data: Omit<Address, 'id'>): Address => {
  const list = readAddresses()
  const item: Address = { ...data, id: Date.now() }
  if (data.isDefault) {
    list.forEach((a) => (a.isDefault = false))
  }
  saveAddresses([...list, item])
  return item
}

export const updateAddress = (id: number, data: Partial<Omit<Address, 'id'>>) => {
  const list = readAddresses()
  const next = list.map((a) => {
    if (a.id !== id) return a
    return { ...a, ...data }
  })
  if (data.isDefault) {
    next.forEach((a) => { if (a.id !== id) a.isDefault = false })
  }
  saveAddresses(next)
}

export const deleteAddress = (id: number) => {
  const list = readAddresses().filter((a) => a.id !== id)
  saveAddresses(list)
}
