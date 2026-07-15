import axios from 'axios'

// FastAPI 默认运行在 8001；部署时可通过 VITE_API_BASE_URL 覆盖。
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 5000,
})

// 请求拦截器：自动携带 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 仅非登录接口的 401 才清除登录态（登录失败不应踢掉已登录用户）
    const isLoginRequest = error.config?.url?.includes('/user/login')
    if (error.response?.status === 401 && !isLoginRequest) {
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
    }
    return Promise.reject(error)
  }
)

/** 从后端错误响应中提取可读消息 */
export function extractErrorMessage(error: unknown, fallback = '请求失败'): string {
  if (error && typeof error === 'object') {
    const resp = (error as any).response?.data
    if (resp) {
      // FastAPI HTTPException → { detail: "..." }
      if (typeof resp.detail === 'string') return resp.detail
      // 业务层统一响应 → { info: "..." }
      if (typeof resp.info === 'string') return resp.info
      // 校验错误 → { detail: [{ msg: "..." }] }
      if (Array.isArray(resp.detail) && resp.detail[0]?.msg) return resp.detail[0].msg
    }
    if ((error as any).message && typeof (error as any).message === 'string') {
      return (error as any).message
    }
  }
  return fallback
}

export default api
