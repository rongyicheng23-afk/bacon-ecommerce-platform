import api, { extractErrorMessage } from './api'
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '../types/user'

const TOKEN_KEY = 'token'
const CURRENT_USER_KEY = 'currentUser'

export const userService = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await api.post<AuthResponse>('/user/login', data)
      return response.data
    } catch (error) {
      throw new Error(extractErrorMessage(error, '登录失败'))
    }
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      // 去除 confirmPassword（仅前端校验用，后端不需要）
      const { confirmPassword: _, ...payload } = data as any
      const response = await api.post<AuthResponse>('/user/register', payload)
      return response.data
    } catch (error) {
      throw new Error(extractErrorMessage(error, '注册失败'))
    }
  },

  async logout(): Promise<void> {
    try {
      await api.post('/user/logout')
    } finally {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(CURRENT_USER_KEY)
    }
  },

  /** 用本地 token 向服务端验证会话是否仍然有效 */
  async fetchMe(): Promise<User | null> {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return null
    try {
      const response = await api.get<{ code: string; data: User }>('/user/me')
      if (response.data.code === '0000' && response.data.data) {
        return response.data.data
      }
      return null
    } catch {
      // token 过期 / 服务端不可用 → 清除本地残留
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(CURRENT_USER_KEY)
      return null
    }
  }
}
