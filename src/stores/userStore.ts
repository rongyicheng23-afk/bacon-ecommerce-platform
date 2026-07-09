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
}): MockUser => {
  const now = new Date().toISOString()

  return {
    user_id: Date.now(),
    username: data.username,
    email: data.email,
    phone: data.phone || '',
    password: data.password,
    status: 'active',
    created_at: now,
    updated_at: now
  }
}

const getMockUsers = (): MockUser[] => {
  const users = JSON.parse(localStorage.getItem(userStorageKey) || '[]') as MockUser[]

  if (users.length > 0) return users

  const demoUser = createUser({
    username: '荣同学',
    email: 'student@example.com',
    password: '123456',
    phone: '13800002026'
  })
  localStorage.setItem(userStorageKey, JSON.stringify([demoUser]))
  return [demoUser]
}

const saveCurrentUser = (user: User, token: string) => {
  localStorage.setItem('token', token)
  localStorage.setItem(currentUserKey, JSON.stringify(user))
}

const readCurrentUser = () => {
  try {
    return JSON.parse(localStorage.getItem(currentUserKey) || 'null') as User | null
  } catch {
    return null
  }
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
    isActive: (state) => state.currentUser?.status === 'active'
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
        const token = `mock-token-${user.user_id}`

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
        const token = `mock-token-${user.user_id}`

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
