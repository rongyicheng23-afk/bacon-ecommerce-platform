import axios from 'axios'
import type { Product, ProductSku, ProductResponse } from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
const now = new Date().toISOString()

interface SeedProduct {
  name: string
  description: string
  price: number
  imageUrls: string[]
  category: string
}

const productSeeds: SeedProduct[] = [
  {
    name: '智能降噪耳机',
    description: '通勤、运动和学习都适合的无线蓝牙耳机，支持主动降噪与通透模式。',
    price: 188,
    imageUrls: [
      'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '轻薄机械键盘',
    description: '适合办公、学习和编程的轻薄机械键盘，红轴静音设计。',
    price: 269,
    imageUrls: [
      'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '保温咖啡杯',
    description: '简洁耐用的日常保温杯，适合办公桌和通勤，12 小时保温。',
    price: 79,
    imageUrls: [
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1577937927133-6c9a5c1c5c9f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1563297320-b6a2c95cd396?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '运动休闲背包',
    description: '轻便大容量，适合上课、出行和日常通勤，防泼水面料。',
    price: 159,
    imageUrls: [
      'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '护眼台灯',
    description: '柔和照明，适合夜间学习和居家办公，多档亮度和色温调节。',
    price: 129,
    imageUrls: [
      'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '便携移动电源',
    description: '20000mAh 大容量，小巧便携，满足手机、耳机等设备日常充电。',
    price: 109,
    imageUrls: [
      'https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1585336261022-680e530ce2d7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '无线充电底座',
    description: '桌面无线快充，支持手机和耳机同时补电，兼容 Qi 协议。',
    price: 99,
    imageUrls: [
      'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1622045246592-7b3b8b3b3b3b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '简约双肩包',
    description: '适合通勤和短途出行的轻量背包，多隔层设计，背负舒适。',
    price: 139,
    imageUrls: [
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '人体工学鼠标',
    description: '长时间办公更舒适，减少手腕压力，支持蓝牙和 2.4G 双模连接。',
    price: 119,
    imageUrls: [
      'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1605773527852-c546a8584ea3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '香薰加湿器',
    description: '适合宿舍和卧室的小型桌面加湿器，搭配精油使用更放松。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1585342289952-2ef11c70c5c5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  }
]

const colorOptions = ['深空灰', '珍珠白', '午夜蓝']
const versionOptions = [
  { suffix: '标准版', priceDelta: 0, stockDelta: 0 },
  { suffix: 'Pro 版', priceDelta: 60, stockDelta: -15 },
  { suffix: '旗舰版', priceDelta: 130, stockDelta: -30 }
]

/** 为种子商品生成 SKU 列表 */
const generateSkus = (productId: number, basePrice: number, imageUrls: string[]): ProductSku[] => {
  const skus: ProductSku[] = []
  let skuCounter = productId * 100

  colorOptions.forEach((color, colorIndex) => {
    versionOptions.forEach((version, versionIndex) => {
      skus.push({
        skuId: skuCounter++,
        productId,
        name: `${color} · ${version.suffix}`,
        price: basePrice + version.priceDelta,
        stock: Math.max(5, 40 - colorIndex * 8 - version.stockDelta),
        imageUrl: imageUrls[colorIndex % imageUrls.length],
        attributes: { 颜色: color, 版本: version.suffix }
      })
    })
  })

  return skus
}

/** 计算所有 SKU 中的最低价 */
const minSkuPrice = (skus: ProductSku[]): number =>
  Math.min(...skus.map((s) => s.price))

/** 计算所有 SKU 的库存总和 */
const totalSkuStock = (skus: ProductSku[]): number =>
  skus.reduce((sum, s) => sum + s.stock, 0)

const mockProducts: Product[] = productSeeds.map((seed, groupIndex) => {
  const productId = 1001 + groupIndex
  const skus = generateSkus(productId, seed.price, seed.imageUrls)

  return {
    productId,
    name: seed.name,
    description: seed.description,
    price: minSkuPrice(skus),
    stock: totalSkuStock(skus),
    status: 'active' as const,
    imageUrls: seed.imageUrls,
    category: seed.category,
    skus,
    createdAt: now,
    updatedAt: now
  }
})

const mockResponse = (data: Product[] | Product): ProductResponse => ({
  code: '0000',
  info: 'mock data',
  data
})

export const productService = {
  async getProducts() {
    try {
      const response = await axios.get<ProductResponse>(`${BASE_URL}/product/list`)
      return response.data
    } catch {
      return mockResponse(mockProducts)
    }
  },

  async getProduct(id: number) {
    try {
      const response = await axios.get<ProductResponse>(`${BASE_URL}/product/get`, {
        params: { productId: id }
      })
      return response.data
    } catch {
      const product = mockProducts.find((item) => item.productId === id)
      return mockResponse(product || mockProducts[0])
    }
  }
}
