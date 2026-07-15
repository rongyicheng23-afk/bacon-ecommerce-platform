import { defineStore } from 'pinia'
import { productService } from '../services/productService'
import type { Product } from '../types'

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [] as Product[],
    total: 0,
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchProducts() {
      this.loading = true
      this.error = null
      try {
        const response = await productService.getProducts()

        if (response.code === '0000' && response.data) {
          const raw = response.data as unknown as Record<string, unknown>
          // 后端返回 { items, total, page, pageSize } 分页对象
          if (raw.items) {
            this.products = raw.items as Product[]
            this.total = (raw.total as number) || 0
          } else if (Array.isArray(raw)) {
            this.products = raw as Product[]
            this.total = (raw as Product[]).length
          } else {
            this.products = [raw as unknown as Product]
            this.total = 1
          }
        } else {
          throw new Error(response.info || '获取商品列表失败')
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : '获取商品列表失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
