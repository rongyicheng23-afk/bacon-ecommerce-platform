<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Product, ProductSku } from '@/types'
import { productService } from '@/services/productService'
import { useProductStore } from '@/stores/productStore'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'
import { behaviorService } from '@/services/behaviorService'
import { commerceService } from '@/services/commerceService'
import MagnifiableImage from '@/components/MagnifiableImage.vue'

type BehaviorAction = 'view' | 'favorite' | 'unfavorite' | 'cart' | 'buy'
type DetailTab = 'detail' | 'reviews' | 'recommend' | 'qa'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const product = ref<Product | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const selectedSkuId = ref<number>(0)
const mainImageIndex = ref(0)
const quantity = ref(1)
const activeTab = ref<DetailTab>('detail')
const actionMessage = ref('')
const favoriteIds = ref<number[]>([])

const serviceItems = ['正品保障', '极速配送', '7天无理由', '售后无忧']

/** ---- 评价系统 ---- */
interface ReviewItem { user: string; rating: number; content: string; date: string; sku: string }
const allReviews: ReviewItem[] = [
  { user: '数码控小王', rating: 5, date: '2026-06-28', sku: '深空灰 · Pro 版', content: '质感超棒，做工精细，超出预期！物流隔天就到，包装也非常严实。' },
  { user: '居家达人', rating: 5, date: '2026-06-25', sku: '珍珠白 · 标准版', content: '包装完整，价格合适，日常使用很方便。卖家还送了小赠品，很贴心。' },
  { user: '学生党小张', rating: 4, date: '2026-06-22', sku: '午夜蓝 · 旗舰版', content: '功能比较实用，性价比很高。用了一周没什么问题，后续还会继续关注。' },
  { user: '办公族老李', rating: 5, date: '2026-06-20', sku: '深空灰 · 标准版', content: '买来办公用，同事们都说好看。手感舒适，推荐购买。' },
  { user: '跑步爱好者', rating: 4, date: '2026-06-18', sku: '珍珠白 · Pro 版', content: '整体满意，细节还有提升空间。不过就这个价位来说已经非常值了。' },
  { user: '程序猿阿明', rating: 5, date: '2026-06-15', sku: '午夜蓝 · Pro 版', content: '第二次回购了，送朋友的生日礼物，朋友非常喜欢！颜值在线。' },
  { user: '美妆博主CC', rating: 3, date: '2026-06-12', sku: '珍珠白 · 标准版', content: '中规中矩吧，没有宣传的那么好，但也不差。物流有点慢，等了一周才到。' },
  { user: '大学生小王', rating: 5, date: '2026-06-10', sku: '深空灰 · 旗舰版', content: '攒了很久的钱一次性买了旗舰版，果然没让我失望！各方面都很优秀。' },
  { user: '退休老教师', rating: 4, date: '2026-06-08', sku: '午夜蓝 · 标准版', content: '女儿帮我网购的，操作简单易上手。做工不错，希望能用得久一点。' },
  { user: '摄影爱好者', rating: 5, date: '2026-06-05', sku: '深空灰 · Pro 版', content: '拍了几张照片发朋友圈，好多人问链接。颜值和实用性都很棒！' },
  { user: '宝妈小芳', rating: 4, date: '2026-06-02', sku: '珍珠白 · Pro 版', content: '带娃没时间去店里逛，网上买到的意外惊喜。颜色很正，没色差。' },
  { user: '健身教练阿强', rating: 5, date: '2026-05-30', sku: '午夜蓝 · 旗舰版', content: '第三次在这个店铺买东西了，一如既往的好品质。客服回复也很快。' },
  { user: '设计师Lisa', rating: 4, date: '2026-05-28', sku: '珍珠白 · 旗舰版', content: '外观设计很有品味，放在桌上就是一道风景。功能也完全够用。' },
  { user: '外卖小哥', rating: 3, date: '2026-05-25', sku: '深空灰 · 标准版', content: '还行吧，对得起这个价格。就是说明书有点简略，一开始不太会用。' },
  { user: '高三学生', rating: 5, date: '2026-05-22', sku: '午夜蓝 · 标准版', content: '高考完奖励自己的，超级满意！比同学买的同类产品好太多了。' },
  { user: '自由职业者', rating: 4, date: '2026-05-20', sku: '深空灰 · Pro 版', content: '在家办公的好帮手。用了一个月没什么问题，充电也很快。' },
  { user: '旅行达人', rating: 5, date: '2026-05-18', sku: '珍珠白 · 标准版', content: '出门旅行带着很方便，小巧不占地方。续航也够用，好评！' },
  { user: '游戏玩家', rating: 5, date: '2026-05-15', sku: '午夜蓝 · Pro 版', content: 'RGB灯效很酷，手感也很好。打游戏时延迟很低，竞技利器。' },
  { user: '考研党', rating: 4, date: '2026-05-12', sku: '深空灰 · 标准版', content: '图书馆自习用，很安静不会打扰别人。希望能陪我度过考研时光。' },
  { user: '美食博主', rating: 5, date: '2026-05-10', sku: '珍珠白 · Pro 版', content: '拍美食视频时用这个当道具，画面质感瞬间提升。功能颜值都在线。' },
  { user: 'IT男小李', rating: 2, date: '2026-05-08', sku: '午夜蓝 · 标准版', content: '收到时盒子有点压坏了，虽然东西没坏但体验不太好。包装可以再加固。' },
  { user: '音乐老师', rating: 5, date: '2026-05-05', sku: '深空灰 · 旗舰版', content: '音质出乎意料的好，上课用来放音乐很清晰。同事也跟着买了同款。' },
  { user: '健身新手', rating: 4, date: '2026-05-02', sku: '珍珠白 · 标准版', content: '朋友推荐的，果然好用。刚开始健身，这个帮我记录了很多数据。' },
  { user: '律师张先生', rating: 5, date: '2026-04-28', sku: '午夜蓝 · 旗舰版', content: '商务场合使用很有档次，客户都夸好看。稳定性和续航都很满意。' },
  { user: '插画师小林', rating: 4, date: '2026-04-25', sku: '珍珠白 · Pro 版', content: '用来画画手感很好，压感灵敏。如果能再多几个快捷键就更完美了。' },
  { user: '退休工程师', rating: 5, date: '2026-04-22', sku: '深空灰 · Pro 版', content: '做工扎实，用料讲究，一看就是好产品。操作逻辑也很清晰，上手快。' },
  { user: '大学老师', rating: 3, date: '2026-04-20', sku: '午夜蓝 · 标准版', content: '功能还可以，但是价格波动有点大，买完没几天就降价了，有点心疼。' },
  { user: '自媒体运营', rating: 5, date: '2026-04-18', sku: '珍珠白 · 旗舰版', content: '工作效率提升明显！剪视频和处理图片都很流畅，强烈推荐给同行。' },
  { user: '初中生小明', rating: 4, date: '2026-04-15', sku: '深空灰 · 标准版', content: '爸妈给买的生日礼物，很喜欢！同学们都很羡慕，嘿嘿。' },
  { user: '咖啡店老板', rating: 5, date: '2026-04-12', sku: '午夜蓝 · Pro 版', content: '放在店里做背景音乐播放器，客人经常问在哪买的。颜值和音质都在线。' },
  { user: '医生赵姐', rating: 4, date: '2026-04-10', sku: '珍珠白 · 标准版', content: '夜班时用着很方便，光线柔和不会打扰同事休息。推荐给医护人员。' },
  { user: '快递员小刘', rating: 5, date: '2026-04-08', sku: '深空灰 · 旗舰版', content: '每天配送路上用，信号稳定续航长，工作好帮手。摔了一次也没坏。' },
]

const REVIEWS_PER_PAGE = 5
const reviewPage = ref(1)
const reviewFilter = ref(0) // 0=all, 5=5星, 4=4星, etc.

const filteredReviews = computed(() => {
  let list = allReviews
  if (reviewFilter.value > 0) list = list.filter(r => r.rating === reviewFilter.value)
  return list
})

const pagedReviews = computed(() => {
  const start = (reviewPage.value - 1) * REVIEWS_PER_PAGE
  return filteredReviews.value.slice(start, start + REVIEWS_PER_PAGE)
})

const reviewTotalPages = computed(() => Math.ceil(filteredReviews.value.length / REVIEWS_PER_PAGE))

const ratingDistribution = computed(() => {
  const dist: Record<number, number> = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }
  allReviews.forEach(r => { dist[r.rating]++ })
  return dist
})

const avgRating = computed(() => {
  const total = allReviews.reduce((s, r) => s + r.rating, 0)
  return (total / allReviews.length).toFixed(1)
})

const setReviewFilter = (rating: number) => {
  reviewFilter.value = rating
  reviewPage.value = 1
}

/** ---- Q&A 问答系统 ---- */
interface QAItem { id: number; question: string; answer: string | null; user: string; date: string }
const qaList = ref<QAItem[]>([
  { id: 1, user: '新用户小王', question: '请问这款商品支持7天无理由退货吗？', answer: '支持！本店所有商品均支持7天无理由退货，请放心购买。', date: '2026-06-20' },
  { id: 2, user: '学生党', question: '学生有优惠吗？可以分期付款吗？', answer: '目前暂不支持分期，但经常有限时折扣活动，关注店铺首页即可获取最新优惠信息。', date: '2026-06-15' },
  { id: 3, user: '数码控', question: 'Pro版和旗舰版的主要区别是什么？', answer: 'Pro版在标准版基础上升级了核心配置，旗舰版则额外增加了高端材质和更长的续航，具体可查看规格参数对比。', date: '2026-06-10' },
  { id: 4, user: '宝妈小李', question: '这款商品安全吗？有没有什么有害物质？', answer: '产品通过了3C认证和RoHS检测，不含任何有害物质，请放心使用。', date: '2026-06-05' },
  { id: 5, user: '户外爱好者', question: '防水性能怎么样？下雨天能正常使用吗？', answer: '日常防泼溅是没有问题的，但不建议长时间浸泡在水中。雨天正常使用请放心。', date: '2026-05-28' },
])
const newQuestion = ref('')
const qaSubmitMsg = ref('')

const submitQuestion = () => {
  const q = newQuestion.value.trim()
  if (!q) return
  qaList.value.unshift({ id: Date.now(), user: '我', question: q, answer: null, date: new Date().toISOString().slice(0, 10) })
  newQuestion.value = ''
  qaSubmitMsg.value = '问题已提交，客服将在24小时内回复'
  setTimeout(() => { qaSubmitMsg.value = '' }, 3000)
}

/** 当前选中的 SKU */
const selectedSku = computed<ProductSku | null>(() => {
  if (!product.value) return null
  const skus = product.value.skus
  if (skus.length === 0) return null
  return skus.find((s) => s.skuId === selectedSkuId.value) || skus[0]
})

/** 当前展示价格（选中 SKU 的价格，无 SKU 则用商品最低价） */
const currentPrice = computed(() => {
  return selectedSku.value?.price ?? product.value?.price ?? 0
})

/** 当前可用库存（选中 SKU 的库存，无 SKU 则用总库存） */
const currentStock = computed(() => {
  return selectedSku.value?.stock ?? product.value?.stock ?? 0
})

/** 按属性分组 SKU，用于渲染规格选择面板 */
const skuGroups = computed(() => {
  if (!product.value) return []
  const skus = product.value.skus
  const attrKeys = skus.length > 0 ? Object.keys(skus[0].attributes) : []
  return attrKeys.map((key) => ({
    label: key,
    values: [...new Set(skus.map((s) => s.attributes[key] as string))].map(
      (value) => ({
        value,
        available: skus.some((s) => s.attributes[key] === value)
      })
    )
  }))
})

/** 选中某个规格值 */
const selectSkuAttribute = (attrLabel: string, attrValue: string) => {
  if (!product.value) return
  const { skus } = product.value
  // 尝试找到完全匹配当前所有已选属性的 SKU
  let targetSku: ProductSku | undefined

  if (selectedSku.value) {
    const currentAttrs = { ...selectedSku.value.attributes, [attrLabel]: attrValue }
    targetSku = skus.find((s) =>
      Object.entries(currentAttrs).every(([k, v]) => s.attributes[k] === v)
    )
  }

  if (!targetSku) {
    targetSku = skus.find((s) => s.attributes[attrLabel] === attrValue)
  }

  if (targetSku) {
    selectedSkuId.value = targetSku.skuId
    // 切换 SKU 时更新主图为该 SKU 对应的图片
    const skuImageIndex = product.value.imageUrls.indexOf(targetSku.imageUrl)
    if (skuImageIndex >= 0) {
      mainImageIndex.value = skuImageIndex
    }
    // 数量不能超过 SKU 库存
    quantity.value = Math.max(1, Math.min(quantity.value, targetSku.stock))
  }
}

const relatedProducts = computed(() => {
  if (!product.value) return []
  return productStore.products
    .filter((item) => item.productId !== product.value?.productId && item.category === product.value?.category)
    .slice(0, 6)
})

const canBuy = computed(() => {
  return Boolean(product.value && product.value.status === 'active' && currentStock.value > 0)
})

const recordBehavior = (target: Product, action: BehaviorAction) => {
  behaviorService.send({
    productId: target.productId,
    productName: target.name,
    action,
    category: target.category,
    quantity: quantity.value,
    skuId: selectedSkuId.value,
    skuName: selectedSku.value?.name || '',
    source: 'product_detail',
  })
}

const fetchProduct = async () => {
  const productId = Number(route.params.id)
  if (Number.isNaN(productId)) {
    error.value = '无效的商品ID'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null
    product.value = await productService.getProduct(productId)
    if (product.value) {
      selectedSkuId.value = product.value.skus[0]?.skuId || 0
      mainImageIndex.value = 0
      quantity.value = 1
      recordBehavior(product.value, 'view')
    }
    // 预热商品列表供关联商品展示
    if (productStore.products.length === 0) {
      productStore.fetchProducts()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '商品不存在或已下架'
  } finally {
    loading.value = false
  }
}

const setQuantity = (value: number) => {
  quantity.value = Math.max(1, Math.min(value, currentStock.value || 1))
}

const handleAction = (action: Exclude<BehaviorAction, 'view' | 'view_recommendation'>) => {
  if (!product.value || !canBuy.value) return
  recordBehavior(product.value, action)
  const actionText = action === 'favorite' ? '收藏' : action === 'unfavorite' ? '取消收藏' : action === 'cart' ? '加入购物车' : '立即购买'
  actionMessage.value = `已${actionText}《${product.value.name}》`
}

const isFavorite = computed(() => {
  return Boolean(product.value && favoriteIds.value.includes(product.value.productId))
})

const toggleFavorite = async () => {
  if (!product.value || !canBuy.value) return
  const wasFavorite = isFavorite.value
  try {
    if (localStorage.getItem('token')) {
      favoriteIds.value = await commerceService.toggleFavorite(product.value.productId, wasFavorite)
    } else {
      favoriteIds.value = toggleFavoriteId(product.value.productId)
    }
    handleAction(wasFavorite ? 'unfavorite' : 'favorite')
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '收藏操作失败'
  }
}

const addToCart = async () => {
  if (!product.value || !canBuy.value) return
  if (!localStorage.getItem('token')) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  try {
    await commerceService.addToCart(product.value, selectedSku.value, quantity.value)
    handleAction('cart')
  } catch (error) {
    actionMessage.value = error instanceof Error ? error.message : '加入购物车失败'
  }
}

const buyNow = async () => {
  if (!product.value || !canBuy.value) return
  await addToCart()
  if (localStorage.getItem('token')) router.push('/cart')
}

const openRelatedProduct = (target: Product) => {
  recordBehavior(target, 'view')
  router.push(`/product/${target.productId}`)
}

// ---- 主图悬停放大 ----
const mainImageRef = ref<HTMLImageElement | null>(null)
const imageZoomStyle = ref('')
const isZooming = ref(false)

const onImageHover = (e: MouseEvent) => {
  const img = mainImageRef.value
  if (!img) return
  const rect = img.getBoundingClientRect()
  const x = ((e.clientX - rect.left) / rect.width) * 100
  const y = ((e.clientY - rect.top) / rect.height) * 100
  isZooming.value = true
  imageZoomStyle.value = `transform-origin: ${x}% ${y}%; transform: scale(2); cursor: zoom-out;`
}

const onImageLeave = () => {
  isZooming.value = false
  imageZoomStyle.value = ''
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
}

watch(() => route.params.id, fetchProduct)

onMounted(async () => {
  if (localStorage.getItem('token')) {
    try { favoriteIds.value = await commerceService.favorites() } catch { favoriteIds.value = [] }
  } else {
    favoriteIds.value = readFavoriteIds()
  }
  fetchProduct()
})
</script>

<template>
  <main class="detail-page">
    <p v-if="actionMessage" class="action-toast">{{ actionMessage }}</p>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <div class="error-actions">
        <button class="retry-btn" @click="fetchProduct()">重新加载</button>
        <button class="ghost-btn" @click="router.push('/products')">返回商品列表</button>
      </div>
    </div>

    <template v-else-if="product">
      <section class="product-shell">
        <div class="gallery-panel">
          <div class="main-image">
            <MagnifiableImage
              :src="product.imageUrls[mainImageIndex] || product.imageUrls[0]"
              :alt="product.name"
              :zoom-scale="2.5"
            />
          </div>
          <div v-if="product.imageUrls.length > 1" class="thumb-row">
            <button
              v-for="(img, index) in product.imageUrls"
              :key="index"
              type="button"
              :class="['thumb-button', { active: mainImageIndex === index }]"
              @click="mainImageIndex = index"
            >
              <img :src="img" :alt="`${product.name} 图 ${index + 1}`" @error="handleImageError" />
            </button>
          </div>
        </div>

        <section class="purchase-panel">
          <div class="title-row">
            <span class="category">{{ product.category || '精选' }}</span>
            <h1>{{ product.name }}</h1>
            <p>{{ product.description }}</p>
          </div>

          <div class="price-box">
            <span>平台价</span>
            <strong>¥{{ currentPrice }}</strong>
            <small v-if="selectedSku">已选：{{ selectedSku.name }}</small>
            <small>累计评价 {{ allReviews.length * 128 }}+</small>
          </div>

          <div class="meta-grid">
            <div>
              <span>库存</span>
              <strong>{{ currentStock }}</strong>
            </div>
            <div>
              <span>销量</span>
              <strong>{{ 300 + product.productId }}</strong>
            </div>
            <div>
              <span>评分</span>
              <strong>4.8</strong>
            </div>
          </div>

          <div
            v-for="group in skuGroups"
            :key="group.label"
            class="option-block"
          >
            <span class="option-label">{{ group.label }}</span>
            <div class="spec-row">
              <button
                v-for="option in group.values"
                :key="option.value"
                type="button"
                :class="{
                  active: selectedSku?.attributes[group.label] === option.value,
                  disabled: !option.available
                }"
                :disabled="!option.available"
                @click="selectSkuAttribute(group.label, option.value)"
              >
                {{ option.value }}
              </button>
            </div>
          </div>

          <div class="option-block">
            <span class="option-label">配送</span>
            <p class="delivery-text">广东广州 至 默认地址，预计 48 小时内发货</p>
          </div>

          <div class="option-block">
            <span class="option-label">数量</span>
            <div class="quantity-stepper">
              <button type="button" @click="setQuantity(quantity - 1)">-</button>
              <input :value="quantity" type="number" min="1" :max="product.stock" @input="setQuantity(Number(($event.target as HTMLInputElement).value))" />
              <button type="button" @click="setQuantity(quantity + 1)">+</button>
            </div>
          </div>

          <div class="service-row">
            <span v-for="item in serviceItems" :key="item">{{ item }}</span>
          </div>

          <div class="action-buttons">
            <button
              type="button"
              :class="['ghost-button', { active: isFavorite }]"
              :disabled="!canBuy"
              @click="toggleFavorite"
            >
              {{ isFavorite ? '已收藏' : '收藏' }}
            </button>
            <button type="button" class="cart-button" :disabled="!canBuy" @click="addToCart">加入购物车</button>
            <button type="button" class="buy-button" :disabled="!canBuy" @click="buyNow">立即购买</button>
          </div>
        </section>
      </section>

      <section class="detail-tabs">
        <div class="tab-header">
          <button type="button" :class="{ active: activeTab === 'detail' }" @click="activeTab = 'detail'">商品详情</button>
          <button type="button" :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">用户评价 ({{ allReviews.length }})</button>
          <button type="button" :class="{ active: activeTab === 'recommend' }" @click="activeTab = 'recommend'">相关推荐</button>
          <button type="button" :class="{ active: activeTab === 'qa' }" @click="activeTab = 'qa'">商品问答 ({{ qaList.length }})</button>
        </div>

        <div v-if="activeTab === 'detail'" class="tab-body detail-copy">
          <h2>{{ product.name }}</h2>
          <p>{{ product.description }}</p>
          <div class="detail-grid">
            <span>分类：{{ product.category || '精选' }}</span>
            <span>规格：{{ selectedSku?.name || '默认' }}</span>
            <span>库存：{{ currentStock }}</span>
            <span>状态：{{ product.status === 'active' ? '在售' : '下架' }}</span>
          </div>
        </div>

        <div v-else-if="activeTab === 'reviews'" class="tab-body">
          <!-- 评分概览 -->
          <div class="review-summary">
            <div class="review-score">
              <strong>{{ avgRating }}</strong>
              <span>{{ '★'.repeat(Math.round(Number(avgRating))) }}</span>
              <small>共 {{ allReviews.length }} 条评价</small>
            </div>
            <div class="review-bars">
              <button v-for="r in [5,4,3,2,1]" :key="r" type="button"
                :class="['review-filter-btn', { active: reviewFilter === r }]"
                @click="setReviewFilter(r === reviewFilter ? 0 : r)">
                <span>{{ r }} 星</span>
                <span class="bar-track"><span class="bar-fill" :style="{ width: (ratingDistribution[r] / allReviews.length * 100) + '%' }"></span></span>
                <span>{{ ratingDistribution[r] }}</span>
              </button>
            </div>
          </div>

          <div v-if="pagedReviews.length === 0" class="review-empty">暂无该星级评价</div>
          <article v-for="review in pagedReviews" :key="review.user + review.date" class="review-card">
            <div class="review-card-head">
              <strong>{{ review.user }}</strong>
              <span>{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</span>
              <time>{{ review.date }}</time>
            </div>
            <small class="review-sku">{{ review.sku }}</small>
            <p>{{ review.content }}</p>
          </article>

          <div v-if="reviewTotalPages > 1" class="review-pagination">
            <button type="button" :disabled="reviewPage <= 1" @click="reviewPage--">上一页</button>
            <span v-for="p in reviewTotalPages" :key="p"
              :class="{ active: reviewPage === p }"
              @click="reviewPage = p">{{ p }}</span>
            <button type="button" :disabled="reviewPage >= reviewTotalPages" @click="reviewPage++">下一页</button>
          </div>
        </div>

        <div v-else-if="activeTab === 'qa'" class="tab-body">
          <p v-if="qaSubmitMsg" class="qa-toast">{{ qaSubmitMsg }}</p>
          <div class="qa-input-row">
            <input v-model="newQuestion" type="text" placeholder="有什么问题想问？输入后按回车提交..." @keyup.enter="submitQuestion" />
            <button type="button" @click="submitQuestion">提问</button>
          </div>
          <div class="qa-list">
            <article v-for="qa in qaList" :key="qa.id" :class="['qa-card', { answered: qa.answer }]">
              <div class="qa-q">
                <span class="qa-badge">问</span>
                <div>
                  <strong>{{ qa.question }}</strong>
                  <small>{{ qa.user }} · {{ qa.date }}</small>
                </div>
              </div>
              <div v-if="qa.answer" class="qa-a">
                <span class="qa-badge answer">答</span>
                <div>
                  <p>{{ qa.answer }}</p>
                  <small>商家客服</small>
                </div>
              </div>
              <div v-else class="qa-pending">客服处理中，请耐心等待...</div>
            </article>
          </div>
        </div>

        <div v-else class="tab-body related-grid">
          <article
            v-for="item in relatedProducts"
            :key="item.productId"
            class="related-card"
            @click="openRelatedProduct(item)"
          >
            <img :src="item.imageUrls[0]" :alt="item.name" @error="handleImageError" />
            <div>
              <span>{{ item.category || '精选' }}</span>
              <h3>{{ item.name }}</h3>
              <strong>¥{{ item.price }}</strong>
            </div>
          </article>
          <p v-if="relatedProducts.length === 0" class="empty-related">暂无相关推荐</p>
        </div>
      </section>
    </template>

    <div v-else class="state error">商品不存在</div>
  </main>
</template>

<style>
.detail-page {
  width: 100%;
}

.action-toast {
  position: fixed;
  z-index: 120;
  right: 2rem;
  top: 5.5rem;
  max-width: min(360px, calc(100vw - 2rem));
  padding: 0.75rem 1rem;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.92);
  color: #fff;
  font-size: 0.875rem;
  box-shadow: 0 12px 30px rgba(17, 24, 39, 0.2);
}

.product-shell {
  display: grid;
  grid-template-columns: minmax(360px, 480px) minmax(0, 1fr);
  gap: 1.5rem;
  align-items: start;
}

.gallery-panel,
.purchase-panel,
.detail-tabs {
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.gallery-panel {
  padding: 1rem;
  overflow: visible;
}

.main-image {
  overflow: visible;
  aspect-ratio: 1;
  border-radius: 14px;
  background: #f5f6f8;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.15s ease-out;
  cursor: zoom-in;
}

.thumb-button img,
.related-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.thumb-button {
  overflow: hidden;
  aspect-ratio: 1;
  padding: 0;
  border: 2px solid #E9E4EE;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
}

.thumb-button.active {
  border-color: #980B32;
}

.purchase-panel {
  padding: 1.25rem;
}

.title-row {
  padding-bottom: 1rem;
  border-bottom: 1px solid #E9E4EE;
}

.category {
  color: #980B32;
  font-size: 0.82rem;
  font-weight: 900;
}

.title-row h1 {
  margin: 0.35rem 0 0.5rem;
  color: #241B2F;
  font-size: 1.7rem;
  line-height: 1.25;
}

.title-row p {
  margin: 0;
  color: #756D7E;
  line-height: 1.6;
}

.price-box {
  display: flex;
  gap: 0.9rem;
  align-items: baseline;
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 12px;
  background: #F4EFF7;
}

.price-box span {
  color: #756D7E;
  font-size: 0.9rem;
}

.price-box strong {
  color: #980B32;
  font-size: 2.2rem;
  line-height: 1;
}

.price-box small {
  margin-left: auto;
  color: #999;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.meta-grid div {
  padding: 0.75rem;
  border-radius: 10px;
  background: #F7F6FA;
}

.meta-grid span,
.meta-grid strong {
  display: block;
}

.meta-grid span {
  color: #777;
  font-size: 0.8rem;
}

.meta-grid strong {
  color: #241B2F;
  font-size: 1rem;
}

.option-block {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 1rem;
  align-items: center;
  margin: 1rem 0;
}

.option-label {
  color: #756D7E;
  font-weight: 800;
}

.spec-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.spec-row button {
  min-height: 36px;
  padding: 0 0.9rem;
  border: 1px solid #948B9D;
  border-radius: 999px;
  background: #fff;
  color: #333;
  cursor: pointer;
  font-weight: 700;
}

.spec-row button.active {
  border-color: #980B32;
  background: #F4EFF7;
  color: #980B32;
}

.spec-row button.disabled {
  border-color: #E9E4EE;
  color: #ccc;
  cursor: not-allowed;
  opacity: 0.5;
}

.delivery-text {
  margin: 0;
  color: #555;
}

.quantity-stepper {
  display: inline-grid;
  grid-template-columns: 36px 56px 36px;
  overflow: hidden;
  width: max-content;
  border: 1px solid #948B9D;
  border-radius: 8px;
}

.quantity-stepper button,
.quantity-stepper input {
  min-height: 36px;
  border: 0;
  background: #fff;
  text-align: center;
}

.quantity-stepper button {
  cursor: pointer;
  font-weight: 900;
}

.quantity-stepper input {
  border-right: 1px solid #948B9D;
  border-left: 1px solid #948B9D;
  outline: none;
}

.service-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1.25rem 0;
  color: #756D7E;
  font-size: 0.88rem;
}

.service-row span::before {
  margin-right: 0.25rem;
  color: #980B32;
  content: '✓';
  font-weight: 900;
}

.action-buttons {
  display: grid;
  grid-template-columns: 0.8fr 1fr 1fr;
  gap: 0.75rem;
}

.action-buttons button {
  min-height: 46px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 900;
}

.ghost-button {
  border: 1px solid #948B9D;
  background: #fff;
  color: #333;
}

.ghost-button.active {
  border-color: #980B32;
  background: #F4EFF7;
  color: #980B32;
}

.cart-button {
  border: 1px solid #5A0B72;
  background: #F4EFF7;
  color: #980B32;
}

.buy-button {
  border: 1px solid #5A0B72;
  background: #980B32;
  color: #fff;
}

.action-buttons button:disabled {
  border-color: #ddd;
  background: #f5f5f5;
  color: #aaa;
  cursor: not-allowed;
}

.detail-tabs {
  margin-top: 1.5rem;
  overflow: hidden;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #E9E4EE;
}

.tab-header button {
  min-height: 48px;
  padding: 0 1.25rem;
  border: 0;
  background: #fff;
  color: #555;
  cursor: pointer;
  font-weight: 900;
}

.tab-header button.active {
  color: #980B32;
  box-shadow: inset 0 -3px 0 #5A0B72;
}

.tab-body {
  padding: 1.25rem;
}

.detail-copy h2 {
  margin: 0 0 0.75rem;
  color: #241B2F;
}

.detail-copy p {
  margin: 0 0 1rem;
  color: #756D7E;
  line-height: 1.8;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

.detail-grid span {
  padding: 0.75rem;
  border-radius: 10px;
  background: #F7F6FA;
  color: #555;
}

.review-list {
  display: grid;
  gap: 0.75rem;
}

.review-summary {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 24px;
  margin-bottom: 20px;
  padding: 16px;
  border-radius: 12px;
  background: #fafafa;
}

.review-score {
  text-align: center;
}

.review-score strong {
  display: block;
  color: #fe2c55;
  font-size: 42px;
  line-height: 1;
}

.review-score span {
  display: block;
  margin: 4px 0;
  color: #fe2c55;
  font-size: 18px;
}

.review-score small {
  color: #999;
  font-size: 13px;
}

.review-bars {
  display: grid;
  gap: 6px;
}

.review-filter-btn {
  display: grid;
  grid-template-columns: 36px 1fr 24px;
  gap: 10px;
  align-items: center;
  border: 0;
  background: transparent;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
  color: #666;
  font-size: 13px;
  text-align: left;
}

.review-filter-btn:hover,
.review-filter-btn.active {
  background: #fff1f2;
  color: #fe2c55;
}

.bar-track {
  display: block;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  overflow: hidden;
}

.bar-fill {
  display: block;
  height: 100%;
  border-radius: 3px;
  background: #fe2c55;
  transition: width 0.3s;
}

.review-empty {
  padding: 24px;
  text-align: center;
  color: #999;
}

.review-card {
  padding: 1rem;
  border-radius: 12px;
  background: #F7F6FA;
}

.review-card strong {
  margin-right: 0.75rem;
}

.review-card span {
  color: #980B32;
}

.review-card p {
  margin: 0.5rem 0 0;
  color: #756D7E;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 1rem;
}

.related-card {
  overflow: hidden;
  border: 1px solid #E9E4EE;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
}

.related-card img {
  aspect-ratio: 1;
}

.related-card div {
  padding: 0.75rem;
}

.related-card span {
  color: #980B32;
  font-size: 0.76rem;
  font-weight: 900;
}

.related-card h3 {
  display: -webkit-box;
  min-height: 2.5rem;
  margin: 0.25rem 0 0.4rem;
  overflow: hidden;
  color: #241B2F;
  font-size: 0.9rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.related-card strong {
  color: #980B32;
}

.empty-related {
  grid-column: 1 / -1;
  margin: 0;
  color: #756D7E;
}

.state {
  padding: 3rem;
  color: #756D7E;
  text-align: center;
}

.state.error {
  color: #ff4d4f;
}

.state.error p { margin: 0 0 1rem; }

.error-actions {
  display: flex; justify-content: center; gap: 0.6rem; margin-top: 0.5rem;
}

.retry-btn {
  min-height: 34px; padding: 0 1.2rem; border: 0; border-radius: 999px;
  background: #7B189F; color: #fff; cursor: pointer; font-size: 0.84rem; font-weight: 800;
}

.ghost-btn {
  min-height: 34px; padding: 0 1rem; border: 1px solid #e5e7eb; border-radius: 999px;
  background: #fff; color: #756D7E; cursor: pointer; font-size: 0.84rem; font-weight: 700;
}

@media (min-width: 768px) and (max-width: 1100px) {
  .product-shell {
    grid-template-columns: 360px minmax(0, 1fr);
  }

  .related-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .product-shell {
    grid-template-columns: 1fr;
  }

  .option-block,
  .action-buttons {
    grid-template-columns: 1fr;
  }

  .price-box {
    align-items: flex-start;
    flex-direction: column;
  }

  .price-box small {
    margin-left: 0;
  }

  .detail-grid,
  .related-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
