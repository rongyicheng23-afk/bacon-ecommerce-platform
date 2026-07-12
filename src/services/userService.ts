import api from './api'
import type { AuthResponse, LoginRequest, RegisterRequest } from '../types/user'

const TOKEN_KEY = 'token'
const CURRENT_USER_KEY = 'currentUser'

export const userService = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/user/login', data)
    return response.data
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/user/register', data)
    return response.data
  },

  async logout(): Promise<void> {
    try {
      await api.post('/user/logout')
    } finally {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(CURRENT_USER_KEY)
    }
  }
}
