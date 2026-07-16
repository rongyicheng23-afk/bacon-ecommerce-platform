import { defineStore } from 'pinia'
import { productService, type ProductListParams } from '../services/productService'
import type { Product } from '../types'

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [] as Product[],
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    error: null as string | null,
    categories: [] as any[],
    categoryTree: [] as any[]
  }),

  actions: {
    async fetchProducts(params: ProductListParams = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await productService.getProducts({
          page: this.page,
          pageSize: this.pageSize,
          ...params
        })

        if (response.code === '0000' && response.data) {
          this.products = response.data.items || []
          this.total = response.data.total || 0
          this.page = response.data.page || 1
          this.pageSize = response.data.pageSize || 20
        } else {
          throw new Error(response.info || '获取商品列表失败')
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : '获取商品列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchCategoryTree() {
      try {
        const data = await productService.getCategoryTree()
        this.categoryTree = data
        // 提取一级分类名列表
        this.categories = data.map((c: any) => c.name)
      } catch {
        // 静默失败
      }
    }
  }
})
