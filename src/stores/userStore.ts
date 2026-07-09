import { defineStore } from 'pinia'
import type { User, LoginRequest, RegisterRequest } from '../types/user'

interface MockUser extends User {
  password: string
}

const userStorageKey = 'mockUsers'
const currentUserKey = 'currentUser'

const createUser = (data: {
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

const normalizeUser = (user: MockUser): MockUser => ({
  ...user,
  role: user.role || 'buyer'
})

const getMockUsers = (): MockUser[] => {
  const users = (JSON.parse(localStorage.getItem(userStorageKey) || '[]') as MockUser[]).map(normalizeUser)

  const hasBuyerDemo = users.some((user) => user.email === 'student@example.com')
  const hasSellerDemo = users.some((user) => user.email === 'seller@example.com')

  const demoUsers = [...users]

  if (!hasBuyerDemo) {
    demoUsers.push(createUser({
      username: '荣同学',
      email: 'student@example.com',
      password: '123456',
      phone: '13800002026',
      role: 'buyer'
    }))
  }

  if (!hasSellerDemo) {
    demoUsers.push(createUser({
      username: 'Bacon 数码旗舰店',
      email: 'seller@example.com',
      password: '123456',
      phone: '13900002026',
      role: 'seller',
      shopName: 'Bacon 数码旗舰店',
      mainCategory: '数码'
    }))
  }

  localStorage.setItem(userStorageKey, JSON.stringify(demoUsers))
  return demoUsers
}

const readCurrentUser = () => {
  try {
    const user = JSON.parse(localStorage.getItem(currentUserKey) || 'null') as User | null
    return user ? { ...user, role: user.role || 'buyer' } : null
  } catch {
    return null
  }
}

const getUserLandingPath = (user: User | null) => {
  return user?.role === 'seller' ? '/seller' : '/'
}

const saveCurrentUser = (user: User, token: string) => {
  localStorage.setItem('token', token)
  localStorage.setItem(currentUserKey, JSON.stringify({ ...user, role: user.role || 'buyer' }))
}

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: readCurrentUser(),
    token: localStorage.getItem('token'),
    loading: false,
    error: null as string | null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.currentUser,
    isActive: (state) => state.currentUser?.status === 'active',
    isSeller: (state) => state.currentUser?.role === 'seller',
    isBuyer: (state) => !state.currentUser || state.currentUser.role === 'buyer',
    landingPath: (state) => getUserLandingPath(state.currentUser)
  },

  actions: {
    async login(credentials: LoginRequest) {
      this.loading = true
      this.error = null
      try {
        const users = getMockUsers()
        const user = users.find((item) => item.email === credentials.email)

        if (!user || user.password !== credentials.password) {
          throw new Error('邮箱或密码不正确。测试账号：student@example.com / 123456')
        }

        const { password, ...publicUser } = user
        const token = `mock-token-${user.userId}`

        this.token = token
        this.currentUser = publicUser
        saveCurrentUser(publicUser, token)
      } catch (error) {
        this.error = error instanceof Error ? error.message : '登录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async register(data: RegisterRequest) {
      this.loading = true
      this.error = null
      try {
        const users = getMockUsers()

        if (users.some((user) => user.email === data.email)) {
          throw new Error('该邮箱已经注册，请直接登录')
        }

        const user = createUser(data)
        const { password, ...publicUser } = user
        const token = `mock-token-${user.userId}`

        localStorage.setItem(userStorageKey, JSON.stringify([user, ...users]))
        this.token = token
        this.currentUser = publicUser
        saveCurrentUser(publicUser, token)
      } catch (error) {
        this.error = error instanceof Error ? error.message : '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.token = null
      this.currentUser = null
      localStorage.removeItem('token')
      localStorage.removeItem(currentUserKey)
    }
  }
})
