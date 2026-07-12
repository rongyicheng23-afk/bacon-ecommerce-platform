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
          // 后端返回 { items, total, page, pageSize } 分页对象
          if (response.data.items) {
            this.products = response.data.items
            this.total = response.data.total
          } else if (Array.isArray(response.data)) {
            this.products = response.data
            this.total = response.data.length
          } else {
            this.products = [response.data]
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
