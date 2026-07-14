<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { sellerService, type SellerOrder, type SellerProduct } from '@/services/sellerService'
import api from '@/services/api'

const router = useRouter()
const userStore = useUserStore()
const orders = ref<SellerOrder[]>([])
const sellerProducts = ref<SellerProduct[]>([])

/** ---- 管理面板 ---- */
type ManageTab = 'products' | 'orders' | 'analytics'
const manageTab = ref<ManageTab>('products')
const showManage = ref(false)
const manageMsg = ref('')

// 商品管理
const editingProduct = ref<SellerProduct | null>(null)
const editStock = ref(0)
const editPrice = ref(0)
const editImageUrls = ref<string[]>([])
const editName = ref('')
const editDescription = ref('')
const editCategory = ref('数码')
const isNewProduct = ref(false)
const uploading = ref(false)

const openProductEdit = (p: SellerProduct) => {
  editingProduct.value = { ...p }
  editStock.value = p.stock
  editPrice.value = p.price
  editImageUrls.value = [...(p.imageUrls || [])]
  editName.value = p.name
  editDescription.value = p.description
  editCategory.value = p.category || '数码'
  isNewProduct.value = false
}

const startNewProduct = () => {
  editingProduct.value = null
  editStock.value = 100
  editPrice.value = 99
  editImageUrls.value = []
  editName.value = ''
  editDescription.value = ''
  editCategory.value = '数码'
  isNewProduct.value = true
}

const uploadImage = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const form = new FormData()
    form.append('file', file)
    form.append('folder', 'products')
    const res = await api.post('/media/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (res.data.code === '0000') {
      editImageUrls.value.push(res.data.data.url)
    }
  } catch (err) { console.error(err) }
  finally { uploading.value = false; (e.target as HTMLInputElement).value = '' }
}

const removeImage = async (idx: number) => {
  const url = editImageUrls.value[idx]
  if (url && url.includes('9002')) {
    const key = url.split('product-images/')[1]
    if (key) {
      try { await api.delete('/media/delete', { params: { object_key: key, folder: 'products' } }) } catch {}
    }
  }
  editImageUrls.value.splice(idx, 1)
}
const moveImageUp = (idx: number) => {
  if (idx > 0) { [editImageUrls.value[idx-1], editImageUrls.value[idx]] = [editImageUrls.value[idx], editImageUrls.value[idx-1]] }
}

const saveProduct = async () => {
  try {
    if (isNewProduct.value) {
      const created = await sellerService.createProduct({
        name: editName.value, description: editDescription.value,
        price: editPrice.value, stock: editStock.value,
        category: editCategory.value, imageUrls: editImageUrls.value,
      })
      sellerProducts.value.unshift(created)
      manageMsg.value = `已创建「${created.name}」`
    } else if (editingProduct.value) {
      const updated = await sellerService.updateProduct(editingProduct.value.productId, {
        stock: editStock.value, price: editPrice.value,
        name: editName.value, description: editDescription.value,
        category: editCategory.value, imageUrls: editImageUrls.value,
      })
      const index = sellerProducts.value.findIndex((p) => p.productId === updated.productId)
      if (index >= 0) sellerProducts.value[index] = updated
      manageMsg.value = `已更新「${updated.name}」`
    }
    editingProduct.value = null; isNewProduct.value = false
    setTimeout(() => { manageMsg.value = '' }, 2000)
  } catch (error) {
    manageMsg.value = error instanceof Error ? error.message : '商品更新失败'
  }
}

// 订单管理
const allSellerOrders = computed(() => {
  return [...orders.value].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const shipOrder = async (orderId: number) => {
  try {
    const updated = await sellerService.shipOrder(orderId)
    const index = orders.value.findIndex((order) => order.orderId === orderId)
    if (index >= 0) orders.value[index] = updated
    manageMsg.value = `订单 ${orderId} 已发货`
    setTimeout(() => { manageMsg.value = '' }, 2000)
  } catch (error) {
    manageMsg.value = error instanceof Error ? error.message : '订单发货失败'
  }
}

const sellerName = computed(() => userStore.currentUser?.shopName || userStore.currentUser?.username || 'Bacon 商家')
const mainCategory = computed(() => userStore.currentUser?.mainCategory || '综合类目')

// 后端已按当前商家过滤订单和商品，前端无需再用类目猜测归属。
const sellerOrders = computed(() => orders.value)

const paidOrders = computed(() => sellerOrders.value.filter((order) => order.status === 'paid'))
const shippedOrders = computed(() => sellerOrders.value.filter((order) => order.status === 'shipped'))
const completedOrders = computed(() => sellerOrders.value.filter((order) => order.status === 'completed'))
const totalSales = computed(() => {
  return sellerOrders.value
    .filter((order) => order.status !== 'pending_payment' && order.status !== 'cancelled')
    .reduce((sum, order) => sum + order.payableAmount, 0)
})

const sellerProductCount = computed(() => sellerProducts.value.length)

const lowStockProducts = computed(() => {
  return sellerProducts.value.filter((product) => product.stock < 30).slice(0, 5)
})

const recentOrders = computed(() => {
  return [...sellerOrders.value]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5)
})

const statusText: Record<string, string> = {
  pending_payment: '待付款',
  paid: '待发货',
  shipped: '待收货',
  completed: '已完成',
  cancelled: '已取消'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  try {
    const [productData, orderData] = await Promise.all([
      sellerService.getProducts(),
      sellerService.getOrders(),
    ])
    sellerProducts.value = productData
    orders.value = orderData
  } catch (error) {
    manageMsg.value = error instanceof Error ? error.message : '商家数据加载失败'
  }
})
</script>

<template>
  <main class="seller-page">
    <section class="seller-hero">
      <div>
        <span>Seller Center</span>
        <h1>{{ sellerName }}</h1>
        <p>主营类目：{{ mainCategory }}。这里用于商家管理商品、订单和经营数据。</p>
      </div>
      <button type="button" @click="router.push('/products')">查看前台店铺</button>
    </section>

    <section class="seller-stats" aria-label="商家经营概览">
      <article>
        <span>商品总数</span>
        <strong>{{ sellerProductCount }}</strong>
      </article>
      <article>
        <span>待发货</span>
        <strong>{{ paidOrders.length }}</strong>
      </article>
      <article>
        <span>配送中</span>
        <strong>{{ shippedOrders.length }}</strong>
      </article>
      <article>
        <span>累计销售额</span>
        <strong>¥{{ totalSales.toFixed(2) }}</strong>
      </article>
    </section>

    <section class="seller-grid">
      <article class="seller-card">
        <div class="card-head">
          <div>
            <span>Orders</span>
            <h2>近期订单</h2>
          </div>
          <button type="button" @click="showManage = true; manageTab = 'orders'">查看全部</button>
        </div>

        <div v-if="recentOrders.length === 0" class="seller-empty">
          暂无订单，买家下单后会出现在这里。
        </div>
        <div v-else class="seller-order-list">
          <div v-for="order in recentOrders" :key="order.orderId">
            <span>订单 {{ order.orderId }}</span>
            <strong>{{ statusText[order.status] }}</strong>
            <em>¥{{ order.payableAmount.toFixed(2) }}</em>
            <time>{{ formatDate(order.createdAt) }}</time>
          </div>
        </div>
      </article>

      <article class="seller-card">
        <div class="card-head">
          <div>
            <span>Inventory</span>
            <h2>库存提醒</h2>
          </div>
        </div>

        <div v-if="lowStockProducts.length === 0" class="seller-empty">
          当前暂无低库存商品。
        </div>
        <div v-else class="stock-list">
          <div v-for="product in lowStockProducts" :key="product.productId">
            <span>{{ product.name }}</span>
            <strong>库存 {{ product.stock }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="seller-actions">
      <button type="button" @click="showManage = true; manageTab = 'products'">商品管理</button>
      <button type="button" @click="showManage = true; manageTab = 'orders'">订单管理</button>
      <button type="button" @click="showManage = true; manageTab = 'analytics'">经营分析</button>
    </section>

    <!-- 管理面板弹窗 -->
    <div v-if="showManage" class="manage-overlay" @click.self="showManage = false">
      <div class="manage-modal">
        <div class="manage-header">
          <div class="manage-tabs">
            <button :class="{ active: manageTab === 'products' }" @click="manageTab = 'products'">商品管理</button>
            <button :class="{ active: manageTab === 'orders' }" @click="manageTab = 'orders'">订单管理</button>
            <button :class="{ active: manageTab === 'analytics' }" @click="manageTab = 'analytics'">经营分析</button>
          </div>
          <button class="manage-close" @click="showManage = false">✕</button>
        </div>

        <p v-if="manageMsg" class="manage-toast">{{ manageMsg }}</p>

        <!-- 商品管理 -->
        <div v-if="manageTab === 'products'" class="manage-body">
          <div v-if="isNewProduct || editingProduct" class="edit-panel">
            <h3>{{ isNewProduct ? '新增商品' : '编辑商品：' + (editingProduct?.name || '') }}</h3>
            <label><span>名称</span><input v-model="editName" /></label>
            <label><span>描述</span><input v-model="editDescription" /></label>
            <label><span>分类</span>
              <select v-model="editCategory">
                <option v-for="c in ['数码','服饰','家居','运动','食品','美妆','图书']" :key="c" :value="c">{{ c }}</option>
              </select></label>
            <label><span>价格 ¥</span><input v-model.number="editPrice" type="number" min="0" step="0.01" /></label>
            <label><span>库存</span><input v-model.number="editStock" type="number" min="0" /></label>
            <label><span>图片</span>
              <input type="file" accept="image/*" @change="uploadImage" :disabled="uploading" />
              <span v-if="uploading">上传中...</span>
            </label>
            <div v-if="editImageUrls.length" class="edit-images">
              <div v-for="(url, i) in editImageUrls" :key="i" class="edit-image-item">
                <img :src="url" style="width:80px;height:80px;object-fit:cover;border-radius:6px" />
                <button @click="moveImageUp(i)" :disabled="i===0">↑</button>
                <button @click="removeImage(i)">✕</button>
              </div>
            </div>
            <div class="edit-actions">
              <button class="btn-save" @click="saveProduct">保存</button>
              <button class="btn-cancel" @click="editingProduct = null; isNewProduct = false">取消</button>
            </div>
          </div>
          <div style="margin-bottom:12px">
            <button class="btn-save" @click="startNewProduct">+ 新增商品</button>
          </div>
          <table v-if="sellerProducts.length" class="manage-table">
            <thead><tr><th>ID</th><th>商品</th><th>价格</th><th>库存</th><th>状态</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="p in sellerProducts" :key="p.productId">
                <td>{{ p.productId }}</td>
                <td class="product-cell">
                  <img :src="p.imageUrls[0]" :alt="p.name" @error="(e: Event) => (e.target as HTMLImageElement).src='https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=100&q=85'" />
                  {{ p.name }}
                </td>
                <td>¥{{ p.price }}</td>
                <td :class="{ low: p.stock < 30 }">{{ p.stock }}</td>
                <td>{{ p.status === 'active' ? '在售' : '下架' }}</td>
                <td><button class="btn-edit" @click="openProductEdit(p)">编辑</button></td>
              </tr>
            </tbody>
          </table>
          <p v-else class="manage-empty">暂无商品数据</p>
        </div>

        <!-- 订单管理 -->
        <div v-if="manageTab === 'orders'" class="manage-body">
          <table v-if="allSellerOrders.length" class="manage-table">
            <thead><tr><th>订单ID</th><th>金额</th><th>状态</th><th>商品</th><th>时间</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="o in allSellerOrders" :key="o.orderId">
                <td>#{{ o.orderId }}</td>
                <td>¥{{ o.payableAmount.toFixed(2) }}</td>
                <td><span :class="'status-tag status-' + o.status">{{ statusText[o.status] }}</span></td>
                <td class="order-items-cell">{{ (o.items || []).map((i) => i.productName).join('、') || '—' }}</td>
                <td>{{ formatDate(o.createdAt) }}</td>
                <td class="action-cell">
                  <button v-if="o.status === 'paid'" class="btn-ship" @click="shipOrder(o.orderId)">发货</button>
                  <span v-else>—</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="manage-empty">暂无订单</p>
        </div>

        <!-- 经营分析 -->
        <div v-if="manageTab === 'analytics'" class="manage-body">
          <div class="analytics-grid">
            <div class="analytic-card">
              <span>总销售额</span>
              <strong>¥{{ totalSales.toFixed(2) }}</strong>
            </div>
            <div class="analytic-card">
              <span>有效订单</span>
              <strong>{{ completedOrders.length + shippedOrders.length + paidOrders.length }}</strong>
            </div>
            <div class="analytic-card">
              <span>待发货</span>
              <strong>{{ paidOrders.length }}</strong>
            </div>
            <div class="analytic-card">
              <span>已完成</span>
              <strong>{{ completedOrders.length }}</strong>
            </div>
          </div>
          <div class="category-breakdown">
            <h3>类目销售占比</h3>
            <p>主营类目：{{ mainCategory }}，商品 {{ sellerProductCount }} 件，其中低库存（&lt;30）{{ lowStockProducts.length }} 件</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style>
.seller-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.seller-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 30px;
  color: #fff;
  background:
    linear-gradient(120deg, rgba(17, 24, 39, 0.9), rgba(14, 165, 233, 0.58)),
    url('https://images.unsplash.com/photo-1556740758-90de374c12ad?auto=format&fit=crop&w=1800&q=85') center/cover;
  border-radius: 16px;
}

.seller-hero span,
.card-head span {
  display: inline-flex;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.seller-hero h1 {
  margin: 0;
  font-size: 34px;
}

.seller-hero p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.82);
}

.seller-hero button,
.card-head button,
.seller-actions button {
  border: 0;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 900;
  cursor: pointer;
}

.seller-hero button {
  color: #111827;
  background: #fff;
}

.card-head button:disabled,
.seller-actions button:disabled {
  color: #9ca3af;
  background: #f5f6f8;
  cursor: not-allowed;
}

.seller-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 18px 0;
}

.seller-stats article,
.seller-card {
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 16px;
  box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
}

.seller-stats article {
  padding: 18px 20px;
}

.seller-stats span {
  color: #6b7280;
  font-size: 14px;
}

.seller-stats strong {
  display: block;
  margin-top: 8px;
  color: #111827;
  font-size: 26px;
}

.seller-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 16px;
}

.seller-card {
  padding: 22px;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.card-head span {
  color: #0ea5e9;
}

.card-head h2 {
  margin: 0;
  color: #111827;
}

.card-head button,
.seller-actions button {
  color: #374151;
  background: #f5f6f8;
}

.seller-order-list,
.stock-list {
  display: grid;
  gap: 10px;
}

.seller-order-list div,
.stock-list div {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto auto;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 12px;
}

.seller-order-list span,
.stock-list span {
  overflow: hidden;
  color: #111827;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.seller-order-list strong,
.stock-list strong {
  color: #0ea5e9;
}

.seller-order-list em {
  color: #fe2c55;
  font-style: normal;
  font-weight: 900;
}

.seller-order-list time {
  color: #9ca3af;
  font-size: 13px;
}

.seller-empty {
  padding: 26px 18px;
  color: #6b7280;
  background: #fafafa;
  border-radius: 14px;
  text-align: center;
}

.seller-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

/* 管理面板弹窗 */
.manage-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(17, 24, 39, 0.5);
  backdrop-filter: blur(4px);
}

.manage-modal {
  width: min(960px, calc(100vw - 40px));
  max-height: 85vh;
  overflow-y: auto;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 20px 60px rgba(17, 24, 39, 0.2);
}

.manage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f2f4;
  position: sticky;
  top: 0;
  background: #fff;
  border-radius: 16px 16px 0 0;
  z-index: 1;
}

.manage-tabs {
  display: flex;
  gap: 4px;
}

.manage-tabs button {
  padding: 8px 18px;
  border: 0;
  border-radius: 999px;
  background: #f5f6f8;
  color: #555;
  font-weight: 900;
  cursor: pointer;
}

.manage-tabs button.active {
  background: #0ea5e9;
  color: #fff;
}

.manage-close {
  border: 0;
  background: transparent;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
}

.manage-close:hover {
  background: #f5f5f5;
  color: #333;
}

.manage-toast {
  margin: 0;
  padding: 10px 20px;
  background: #ecfdf5;
  color: #059669;
  font-size: 14px;
  font-weight: 800;
}

.manage-body {
  padding: 20px;
}

.manage-empty {
  padding: 40px 20px;
  text-align: center;
  color: #999;
}

.edit-panel {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #0ea5e9;
  border-radius: 12px;
  background: #f0f9ff;
}

.edit-panel h3 {
  margin: 0 0 12px;
  color: #111827;
  font-size: 16px;
}

.edit-panel label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #555;
  font-size: 14px;
}

.edit-panel input {
  width: 120px;
  min-height: 36px;
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  outline: none;
}

.edit-panel input:focus {
  border-color: #0ea5e9;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.btn-save,
.btn-ship {
  border: 0;
  padding: 6px 14px;
  border-radius: 8px;
  background: #0ea5e9;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
}

.btn-cancel {
  border: 1px solid #e5e7eb;
  padding: 6px 14px;
  border-radius: 8px;
  background: #fff;
  color: #555;
  font-weight: 900;
  cursor: pointer;
}

.btn-edit {
  border: 0;
  padding: 4px 12px;
  border-radius: 6px;
  background: #f0f9ff;
  color: #0ea5e9;
  font-weight: 800;
  cursor: pointer;
}

.btn-done {
  border: 0;
  padding: 6px 14px;
  border-radius: 8px;
  background: #059669;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
}

.manage-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.manage-table th {
  padding: 10px 8px;
  border-bottom: 2px solid #f1f2f4;
  color: #999;
  font-weight: 800;
  text-align: left;
  font-size: 12px;
  text-transform: uppercase;
}

.manage-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #f5f5f5;
  color: #333;
}

.manage-table td.low {
  color: #fe2c55;
  font-weight: 900;
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-cell img {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  object-fit: cover;
}

.order-items-cell {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-cell {
  white-space: nowrap;
}

.status-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.status-pending_payment { background: #fef3c7; color: #d97706; }
.status-paid { background: #dbeafe; color: #2563eb; }
.status-shipped { background: #e0e7ff; color: #4f46e5; }
.status-completed { background: #d1fae5; color: #059669; }
.status-cancelled { background: #f3f4f6; color: #9ca3af; }

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}

.analytic-card {
  padding: 18px;
  border: 1px solid #f1f2f4;
  border-radius: 12px;
  background: #fafafa;
}

.analytic-card span {
  color: #999;
  font-size: 13px;
}

.analytic-card strong {
  display: block;
  margin-top: 6px;
  color: #111827;
  font-size: 24px;
}

.category-breakdown {
  padding: 16px;
  border: 1px solid #f1f2f4;
  border-radius: 12px;
  background: #fafafa;
}

.category-breakdown h3 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 16px;
}

.category-breakdown p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

@media (max-width: 860px) {
  .seller-page {
    padding: 16px 12px 40px;
  }

  .seller-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .seller-stats,
  .seller-grid,
  .analytics-grid {
    grid-template-columns: 1fr;
  }

  .seller-order-list div {
    grid-template-columns: 1fr;
  }

  .manage-modal {
    width: calc(100vw - 20px);
    max-height: 90vh;
  }
}
</style>
