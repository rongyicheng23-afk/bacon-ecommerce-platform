import type { User } from '@/types/user'

export interface MockUser extends User {
  password: string
}

const STORAGE_KEY = 'mockUsers'

const DEMO_USERS: MockUser[] = [
  {
    userId: 1,
    username: '荣同学',
    email: 'student@example.com',
    phone: '13800002026',
    role: 'buyer',
    password: '123456',
    status: 'active',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    userId: 2,
    username: 'Bacon 数码旗舰店',
    email: 'seller@example.com',
    phone: '13900002026',
    role: 'seller',
    shopName: 'Bacon 数码旗舰店',
    mainCategory: '数码',
    password: '123456',
    status: 'active',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
]

/** 创建新用户 */
export const createMockUser = (data: {
  username: string
  email: string
  password: string
  phone?: string
  role?: 'buyer' | 'seller'
  shopName?: string
  mainCategory?: string
}): MockUser => {
  const now = new Date().toISOString()
  return {
    userId: Date.now(),
    username: data.username,
    email: data.email,
    phone: data.phone || '',
    role: data.role || 'buyer',
    shopName: data.shopName,
    mainCategory: data.mainCategory,
    password: data.password,
    status: 'active',
    createdAt: now,
    updatedAt: now
  }
}

/** 读取所有 mock 用户，自动补齐 demo 账号 */
export const getMockUsers = (): MockUser[] => {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') as MockUser[]
    const users = stored.map((u) => ({ ...u, role: u.role || 'buyer' }))

    // 补齐缺失的 demo 账号
    const emails = new Set(users.map((u) => u.email))
    const missing = DEMO_USERS.filter((demo) => !emails.has(demo.email))
    if (missing.length === 0) return users

    const merged = [...users, ...missing]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
    return merged
  } catch {
    return [...DEMO_USERS]
  }
}

/** 持久化用户列表 */
export const saveMockUsers = (users: MockUser[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
}

/** 移除密码字段 */
export const toPublicUser = (user: MockUser): User => {
  const { password, ...publicUser } = user
  return publicUser
}
