import { defineStore } from 'pinia'
import type { User, LoginRequest, RegisterRequest } from '../types/user'
import { userService } from '@/services/userService'

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
        const response = await userService.login(credentials)
        if (response.code !== '0000') throw new Error(response.info || '登录失败')
        this.token = response.data.token
        this.currentUser = response.data.user
        saveCurrentUser(response.data.user, response.data.token)
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
        const { confirmPassword: _confirmPassword, ...payload } = data
        const response = await userService.register(payload as RegisterRequest)
        if (response.code !== '0000') throw new Error(response.info || '注册失败')
        this.token = response.data.token
        this.currentUser = response.data.user
        saveCurrentUser(response.data.user, response.data.token)
      } catch (error) {
        this.error = error instanceof Error ? error.message : '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      await userService.logout()
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
