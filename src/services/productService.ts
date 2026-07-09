import axios from 'axios'
import type { Product, ProductResponse } from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
const now = new Date().toISOString()

const productSeeds = [
  {
    name: '智能降噪耳机',
    description: '通勤、运动和学习都适合的无线蓝牙耳机。',
    price: 188,
    imageUrl: 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85',
    category: '数码',
  },
  {
    name: '轻薄机械键盘',
    description: '适合办公、学习和编程的轻薄机械键盘。',
    price: 269,
    imageUrl: 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85',
    category: '数码',
  },
  {
    name: '保温咖啡杯',
    description: '简洁耐用的日常保温杯，适合办公桌和通勤。',
    price: 79,
    imageUrl: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85',
    category: '家居',
  },
  {
    name: '运动休闲背包',
    description: '轻便大容量，适合上课、出行和日常通勤。',
    price: 159,
    imageUrl: 'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
    category: '服饰',
  },
  {
    name: '护眼台灯',
    description: '柔和照明，适合夜间学习和居家办公。',
    price: 129,
    imageUrl: 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85',
    category: '家居',
  },
  {
    name: '便携移动电源',
    description: '小巧便携，满足手机、耳机等设备日常充电。',
    price: 109,
    imageUrl: 'https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85',
    category: '数码',
  },
  {
    name: '无线充电底座',
    description: '桌面无线快充，适合手机和耳机同时补电。',
    price: 99,
    imageUrl: 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85',
    category: '数码',
  },
  {
    name: '简约双肩包',
    description: '适合通勤和短途出行的轻量背包。',
    price: 139,
    imageUrl: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
    category: '服饰',
  },
  {
    name: '人体工学鼠标',
    description: '长时间办公更舒适，减少手腕压力。',
    price: 119,
    imageUrl: 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85',
    category: '数码',
  },
  {
    name: '香薰加湿器',
    description: '适合宿舍和卧室的小型桌面加湿器。',
    price: 89,
    imageUrl: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85',
    category: '家居',
  },
  {
    name: '运动水杯',
    description: '大容量防漏设计，适合健身和户外。',
    price: 59,
    imageUrl: 'https://images.unsplash.com/photo-1523362628745-0c100150b504?auto=format&fit=crop&w=900&q=85',
    category: '运动',
  },
  {
    name: '纯棉基础T恤',
    description: '简洁百搭，适合日常穿搭。',
    price: 69,
    imageUrl: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=85',
    category: '服饰',
  },
  {
    name: '桌面收纳架',
    description: '整理键盘、书本和小物件，让桌面更清爽。',
    price: 49,
    imageUrl: 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=85',
    category: '家居',
  },
  {
    name: '蓝牙音箱',
    description: '小体积大音量，适合宿舍和露营。',
    price: 169,
    imageUrl: 'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=900&q=85',
    category: '数码',
  },
  {
    name: '速干运动外套',
    description: '轻薄透气，适合晨跑和日常出行。',
    price: 199,
    imageUrl: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=85',
    category: '运动',
  },
  {
    name: '便携阅读灯',
    description: '夹式设计，适合夜间阅读和自习。',
    price: 39,
    imageUrl: 'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85',
    category: '家居',
  },
  {
    name: '电脑支架',
    description: '抬高屏幕视角，改善桌面办公姿势。',
    price: 89,
    imageUrl: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=85',
    category: '数码',
  },
  {
    name: '帆布托特包',
    description: '轻便大容量，适合上课和购物。',
    price: 49,
    imageUrl: 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=900&q=85',
    category: '服饰',
  }
]

const variantNames = ['', ' Pro', ' Max', ' 青春版', ' 旗舰版', ' 限定款']

const mockProducts: Product[] = productSeeds.flatMap((seed, groupIndex) =>
  variantNames.map((suffix, variantIndex) => {
    const productId = 1001 + groupIndex * variantNames.length + variantIndex
    return {
      productId,
      name: `${seed.name}${suffix}`,
      description: seed.description,
      price: seed.price + variantIndex * 18,
      stock: 40 + ((groupIndex + 1) * 13 + variantIndex * 7) % 160,
      status: 'active' as const,
      imageUrl: seed.imageUrl,
      category: seed.category,
      createdAt: now,
      updatedAt: now
    }
  })
)

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
