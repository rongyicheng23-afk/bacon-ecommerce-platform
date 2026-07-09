import axios from 'axios'
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '../types/user'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
const USER_STORAGE_KEY = 'mockUsers'
const CURRENT_USER_KEY = 'currentUser'
const TOKEN_KEY = 'token'

interface MockUser extends User {
  password: string
}

const getMockUsers = (): MockUser[] => {
  try {
    const users = (JSON.parse(localStorage.getItem(USER_STORAGE_KEY) || '[]') as MockUser[])
      .map((user) => ({ ...user, role: user.role || 'buyer' }))
    if (users.length > 0) return users

    // 初始化 demo 用户
    const now = new Date().toISOString()
    const demoUsers: MockUser[] = [
      {
        userId: 1,
        username: '荣同学',
        email: 'student@example.com',
        phone: '13800002026',
        role: 'buyer',
        password: '123456',
        status: 'active',
        createdAt: now,
        updatedAt: now
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
        createdAt: now,
        updatedAt: now
      }
    ]
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(demoUsers))
    return demoUsers
  } catch {
    return []
  }
}

const mockAuthResponse = (user: MockUser): AuthResponse => {
  const { password, ...publicUser } = user
  const token = `mock-token-${user.userId}-${Date.now()}`
  return {
    code: '0000',
    info: 'success',
    data: { token, user: publicUser }
  }
}

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
      return mockAuthResponse(user)
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

      const now = new Date().toISOString()
      const newUser: MockUser = {
        userId: Date.now(),
        username: data.username,
        email: data.email,
        phone: data.phone || '',
        role: data.role,
        shopName: data.shopName,
        mainCategory: data.mainCategory,
        password: data.password,
        status: 'active',
        createdAt: now,
        updatedAt: now
      }

      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify([newUser, ...users]))
      return mockAuthResponse(newUser)
    }
  },

  async logout(): Promise<void> {
    try {
      await axios.post(`${BASE_URL}/user/logout`)
    } catch {
      // mock 登出：清除本地状态
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(CURRENT_USER_KEY)
    }
  }
}
