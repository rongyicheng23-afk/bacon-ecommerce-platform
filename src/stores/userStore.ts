import { defineStore } from 'pinia'
import type { User, LoginRequest, RegisterRequest } from '../types/user'
import { getMockUsers, saveMockUsers, createMockUser, toPublicUser } from '@/utils/mockUsers'

const currentUserKey = 'currentUser'

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

/** 判断 redirect 路径是否与用户角色兼容 */
const isRedirectCompatible = (user: User, path: string): boolean => {
  const buyerOnly = ['/cart', '/checkout', '/orders', '/order/', '/profile', '/payment', '/payment-success']
  const sellerOnly = ['/seller']
  if (user.role === 'buyer' && sellerOnly.some((p) => path.startsWith(p))) return false
  if (user.role === 'seller' && buyerOnly.some((p) => path.startsWith(p))) return false
  return true
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
          throw new Error('邮箱或密码不正确。测试账号：student@example.com / seller@example.com / 123456')
        }

        const publicUser = toPublicUser(user)
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

        const user = createMockUser(data)
        const publicUser = toPublicUser(user)
        const token = `mock-token-${user.userId}`

        saveMockUsers([user, ...users])
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
    },

    /** 登录后跳转：检查 redirect 与角色是否兼容 */
    getLoginRedirect(redirectPath?: string): string {
      if (!this.currentUser) return '/login'
      if (redirectPath && isRedirectCompatible(this.currentUser, redirectPath)) {
        return redirectPath
      }
      return getUserLandingPath(this.currentUser)
    }
  }
})
