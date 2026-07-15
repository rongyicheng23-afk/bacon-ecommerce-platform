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
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
    }
    return Promise.reject(error)
  }
)

export default api
