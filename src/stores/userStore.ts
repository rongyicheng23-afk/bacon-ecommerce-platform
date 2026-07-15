import { defineStore } from 'pinia'
import type { User, LoginRequest, RegisterRequest } from '../types/user'
import { userService } from '@/services/userService'

const CURRENT_USER_KEY = 'currentUser'
const TOKEN_KEY = 'token'

const readCurrentUser = (): User | null => {
  try {
    const user = JSON.parse(localStorage.getItem(CURRENT_USER_KEY) || 'null') as User | null
    return user ? { ...user, role: user.role || 'buyer' } : null
  } catch {
    return null
  }
}

const getUserLandingPath = (user: User | null) => {
  return user?.role === 'seller' ? '/seller' : '/'
}

const saveCurrentUser = (user: User, token: string) => {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify({ ...user, role: user.role || 'buyer' }))
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
    token: localStorage.getItem(TOKEN_KEY),
    loading: false,
    error: null as string | null,
    /** 是否已向服务端验证过当前 token（防止刷新后直接用 localStorage 旧数据放行） */
    authChecked: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.currentUser,
    isActive: (state) => state.currentUser?.status === 'active',
    isSeller: (state) => state.currentUser?.role === 'seller',
    isBuyer: (state) => !state.currentUser || state.currentUser.role === 'buyer',
    landingPath: (state) => getUserLandingPath(state.currentUser)
  },

  actions: {
    /** 页面刷新后验证本地 token 是否仍有效 */
    async initAuth() {
      const token = localStorage.getItem(TOKEN_KEY)
      if (!token) {
        this.authChecked = true
        return
      }
      try {
        const user = await userService.fetchMe()
        if (user) {
          this.token = token
          this.currentUser = user
          saveCurrentUser(user, token)
        } else {
          // 服务端返回 401 / token 无效 → 清空 Pinia 状态
          this.token = null
          this.currentUser = null
        }
      } catch {
        // 网络错误等 → 保守清除
        this.token = null
        this.currentUser = null
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(CURRENT_USER_KEY)
      } finally {
        this.authChecked = true
      }
    },

    async login(credentials: LoginRequest) {
      this.loading = true
      this.error = null
      try {
        const response = await userService.login(credentials)
        if (response.code !== '0000') throw new Error(response.info || '登录失败')
        this.token = response.data.token
        this.currentUser = response.data.user
        this.authChecked = true
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
        const response = await userService.register(data)
        if (response.code !== '0000') throw new Error(response.info || '注册失败')
        this.token = response.data.token
        this.currentUser = response.data.user
        this.authChecked = true
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
      this.authChecked = false
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(CURRENT_USER_KEY)
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
