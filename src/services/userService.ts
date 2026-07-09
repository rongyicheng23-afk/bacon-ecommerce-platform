import axios from 'axios'
import type { AuthResponse, LoginRequest, RegisterRequest } from '../types/user'
import { getMockUsers, saveMockUsers, createMockUser, toPublicUser } from '@/utils/mockUsers'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
const TOKEN_KEY = 'token'
const CURRENT_USER_KEY = 'currentUser'

export const userService = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(`${BASE_URL}/user/login`, data)
      return response.data
    } catch {
      const users = getMockUsers()
      const user = users.find((u) => u.email === data.email)
      if (!user || user.password !== data.password) {
        throw new Error('邮箱或密码不正确')
      }
      const token = `mock-token-${user.userId}-${Date.now()}`
      return {
        code: '0000',
        info: 'success',
        data: { token, user: toPublicUser(user) }
      }
    }
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(`${BASE_URL}/user/register`, data)
      return response.data
    } catch {
      const users = getMockUsers()
      if (users.some((u) => u.email === data.email)) {
        throw new Error('该邮箱已经注册')
      }

      const newUser = createMockUser(data)
      saveMockUsers([newUser, ...users])

      const token = `mock-token-${newUser.userId}-${Date.now()}`
      return {
        code: '0000',
        info: 'success',
        data: { token, user: toPublicUser(newUser) }
      }
    }
  },

  async logout(): Promise<void> {
    try {
      await axios.post(`${BASE_URL}/user/logout`)
    } catch {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(CURRENT_USER_KEY)
    }
  }
}
