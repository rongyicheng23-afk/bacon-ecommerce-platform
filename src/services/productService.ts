import api, { extractErrorMessage } from './api'
import type { Product } from '@/types'

export interface ProductListParams {
  category?: string
  subcategory?: string
  keyword?: string
  sort?: 'price-asc' | 'price-desc' | 'stock-desc'
  page?: number
  pageSize?: number
}

export interface ProductListData {
  items: Product[]
  total: number
  page: number
  pageSize: number
}

export interface ApiResponse<T> {
  code: string
  info: string
  data: T
}

export const productService = {
  async getProducts(params: ProductListParams = {}): Promise<ApiResponse<ProductListData>> {
    try {
      const response = await api.get<ApiResponse<ProductListData>>('/product/list', { params })
      return response.data
    } catch (error) {
      throw new Error(extractErrorMessage(error, '获取商品列表失败'))
    }
  },

  async getProduct(id: number): Promise<Product> {
    try {
      const response = await api.get<ApiResponse<Product>>('/product/get', {
        params: { productId: id }
      })
      if (response.data.code !== '0000' || !response.data.data) {
        throw new Error(response.data.info || '商品不存在')
      }
      return response.data.data as Product
    } catch (error) {
      throw new Error(extractErrorMessage(error, '获取商品详情失败'))
    }
  },

  async getCategoryTree(): Promise<any[]> {
    try {
      const response = await api.get<ApiResponse<any[]>>('/categories/tree')
      if (response.data.code === '0000' && response.data.data) {
        return response.data.data as any[]
      }
      return []
    } catch (error) {
      throw new Error(extractErrorMessage(error, '获取分类失败'))
    }
  }
}
