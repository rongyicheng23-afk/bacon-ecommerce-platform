<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import type { Product } from '@/types'
import { addProductToCart } from '@/utils/cart'
import { readFavoriteIds, toggleFavoriteId } from '@/utils/favorites'

const router = useRouter()
const productStore = useProductStore()
const loading = ref(true)
const error = ref<string | null>(null)
const actionMessage = ref('')
const favoriteIds = ref<number[]>([])
const subscribeEmail = ref('')
const subscribed = ref(false)
const activeNav = ref('all')

const products = computed(() => productStore.products)

const digitalProducts = computed(() => products.value.filter((p) => p.category === '数码').slice(0, 5))
const homeProducts = computed(() => products.value.filter((p) => p.category === '家居').slice(0, 4))
const fashionProducts = computed(() => products.value.filter((p) => p.category === '服饰').slice(0, 3))
const curatedProducts = computed(() => products.value.slice(0, 8))
const newCount = computed(() => products.value.filter((p) => p.productId % 7 === 0 || p.stock > 30).length)
const categoryCount = computed(() => new Set(products.value.map((p) => p.category).filter(Boolean)).size)

const sectionNav = [
  { key: 'all', label: '全部新品' }, { key: 'digital', label: '数码新品' },
  { key: 'home', label: '家居新品' }, { key: 'fashion', label: '服饰新品' },
  { key: 'commute', label: '通勤精选' }, { key: 'weekly', label: '本周关注' },
]

const isFavorite = (id: number) => favoriteIds.value.includes(id)
const toggleFavorite = (p: Product) => { favoriteIds.value = toggleFavoriteId(p.productId); actionMessage.value = isFavorite(p.productId) ? `已收藏` : `已取消收藏`; setTimeout(() => actionMessage.value = '', 1500) }
const addToCart = (p: Product) => { addProductToCart(p); actionMessage.value = `已加购《${p.name}》`; setTimeout(() => actionMessage.value = '', 1500) }
const goDetail = (p: Product) => router.push(`/product/${p.productId}`)
const goCategory = (cat: string) => router.push({ path: '/products', query: { category: cat } })
const handleImageError = (e: Event) => { (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85' }
const subscribe = () => { if (!subscribeEmail.value.trim()) return; subscribed.value = true; subscribeEmail.value = ''; setTimeout(() => subscribed.value = false, 3000) }

onMounted(async () => {
  favoriteIds.value = readFavoriteIds()
  try { if (products.value.length === 0) await productStore.fetchProducts() } catch (err) { error.value = err instanceof Error ? err.message : '加载失败' } finally { loading.value = false }
  const obs = new IntersectionObserver((entries) => { entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('revealed') }) }, { threshold: 0.1 })
  document.querySelectorAll('.reveal').forEach((el) => obs.observe(el))
})
</script>

<template>
  <div class="np-page">
    <p v-if="actionMessage" class="np-toast">{{ actionMessage }}</p>
    <div v-if="loading" class="np-state">加载中...</div>
    <div v-else-if="error" class="np-state err">{{ error }}</div>
    <template v-else>
      <!-- 1. Hero -->
      <section class="np-hero">
        <div class="np-hero-bg"><img src="https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1600&q=85" alt="lifestyle" @error="handleImageError" /></div>
        <div class="np-hero-overlay"></div>
        <div class="np-hero-body">
          <div class="np-hero-tags"><span class="np-htag">NEW</span><span class="np-htag yellow">2026 首发</span><span class="np-htag">本季精选</span></div>
          <span class="np-hero-en">NEW ARRIVALS 2026</span>
          <h1>新品首发</h1>
          <p class="np-hero-sub">焕新日常的每一种可能</p>
          <p class="np-hero-desc">精选数码、家居与穿搭新品，为你的生活带来新的选择。</p>
          <button class="np-btn" @click="router.push('/new-arrivals')">探索新品</button>
        </div>
      </section>

      <!-- 2. Intro -->
      <section class="np-intro reveal">
        <span class="np-kicker">BACON MALL NEW SEASON</span>
        <h2>不止是上新</h2><p class="np-intro-lead">也是生活方式的一次更新</p>
        <p class="np-intro-desc">从高效办公、品质居家到日常穿搭，本季新品围绕真实生活场景，为不同用户提供更合适的选择。</p>
        <div class="np-intro-stats">
          <div class="np-istat"><strong>{{ newCount }}</strong><span>本季新品</span></div>
          <div class="np-istat"><strong>{{ categoryCount }}</strong><span>覆盖分类</span></div>
          <div class="np-istat"><strong>2,680+</strong><span>用户关注</span></div>
        </div>
      </section>

      <!-- 3. Digital -->
      <section class="np-feature reveal" id="digital">
        <div class="np-feat-img"><img src="https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=1200&q=85" alt="数码" @error="handleImageError" /></div>
        <div class="np-feat-card">
          <span class="np-feat-kicker">DIGITAL ESSENTIALS</span><h3>高效连接每一天</h3>
          <p>从无线耳机、机械键盘到移动电源，以更轻便、更稳定的方式提升学习、办公与出行体验。</p>
          <span class="np-feat-count">本季数码新品 {{ digitalProducts.length }} 件</span>
          <button class="np-btn" @click="goCategory('数码')">探索数码新品 →</button>
        </div>
      </section>

      <!-- 4. Home -->
      <section class="np-feature reverse reveal" id="home">
        <div class="np-feat-card">
          <span class="np-feat-kicker">HOME REFRESH</span><h3>让日常空间更舒适</h3>
          <p>从保温杯、氛围灯到香薰加湿器，用更柔和、更实用的设计重新整理生活空间。</p>
          <span class="np-feat-count">本季家居新品 {{ homeProducts.length }} 件</span>
          <button class="np-btn" @click="goCategory('家居')">探索家居新品 →</button>
        </div>
        <div class="np-feat-img"><img src="https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=1200&q=85" alt="家居" @error="handleImageError" /></div>
      </section>

      <!-- 5. Fashion -->
      <section class="np-feature reveal" id="fashion">
        <div class="np-feat-img"><img src="https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=1200&q=85" alt="服饰" @error="handleImageError" /></div>
        <div class="np-feat-card">
          <span class="np-feat-kicker">DAILY STYLE</span><h3>轻松适应不同日常</h3>
          <p>适合通勤、学习、出行和休闲场景的新品，在容量、舒适度和实用性之间取得平衡。</p>
          <span class="np-feat-count">本季服饰新品 {{ fashionProducts.length }} 件</span>
          <button class="np-btn" @click="goCategory('服饰')">探索服饰新品 →</button>
        </div>
      </section>

      <!-- 6. Story -->
      <section class="np-story reveal">
        <div class="np-story-img"><img src="https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1600&q=85" alt="story" @error="handleImageError" /></div>
        <div class="np-story-overlay"></div>
        <div class="np-story-body">
          <span class="np-story-kicker">NEW SEASON STORY</span><h3>每一次上新<br>都从真实需求开始</h3>
          <button class="np-btn-play" @click="() => {}">▶ 观看新品故事</button>
        </div>
      </section>

      <!-- 7. Category Nav -->
      <div class="np-cnav reveal">
        <button v-for="s in sectionNav" :key="s.key" :class="{ active: activeNav === s.key }" @click="activeNav = s.key; s.key === 'digital' ? goCategory('数码') : s.key === 'home' ? goCategory('家居') : s.key === 'fashion' ? goCategory('服饰') : s.key === 'all' ? router.push('/products') : void 0">{{ s.label }}</button>
      </div>

      <!-- 8. Curated -->
      <section class="np-curated reveal">
        <h3>本季精选新品</h3><p class="np-curated-sub">从本季新品中，为你挑选值得关注的商品。</p>
        <div class="np-grid">
          <article v-for="p in curatedProducts" :key="p.productId" class="np-card" @click="goDetail(p)">
            <div class="np-card-img"><img :src="p.imageUrls[0]" :alt="p.name" @error="handleImageError" /><span class="np-card-tag">NEW</span></div>
            <div class="np-card-body">
              <span class="np-card-cat">{{ p.category || '精选' }}</span><h4>{{ p.name }}</h4>
              <p class="np-card-desc">{{ p.description }}</p>
              <div class="np-card-footer">
                <strong>¥{{ p.price }}</strong>
                <div class="np-card-btns" @click.stop>
                  <button :class="{ active: isFavorite(p.productId) }" @click="toggleFavorite(p)"><svg viewBox="0 0 24 24" :fill="isFavorite(p.productId) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>
                  <button class="np-card-cart" @click="addToCart(p)">加购</button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- 9. Values -->
      <section class="np-values reveal">
        <div class="np-val"><span class="np-val-icon">🤖</span><h4>智能推荐</h4><p>根据用户浏览、收藏、加购和购买行为，推荐更符合兴趣的新品。</p></div>
        <div class="np-val"><span class="np-val-icon">📸</span><h4>真实场景</h4><p>新品通过学习、办公、通勤和居家等真实场景进行展示。</p></div>
        <div class="np-val"><span class="np-val-icon">🔄</span><h4>持续更新</h4><p>新品专题和推荐结果会随商品与用户偏好持续更新。</p></div>
      </section>

      <!-- 10. Subscribe -->
      <section class="np-sub reveal">
        <h3>不要错过下一次上新</h3><p>订阅新品通知，第一时间了解最新商品与专题推荐。</p>
        <form v-if="!subscribed" class="np-sub-form" @submit.prevent="subscribe">
          <input v-model="subscribeEmail" type="email" placeholder="输入您的邮箱" /><button type="submit">订阅</button>
        </form>
        <p v-else class="np-sub-ok">✓ 订阅成功！新品上线时我们将第一时间通知您。</p>
      </section>
    </template>
  </div>
</template>

<style scoped>
.np-page { max-width: 1360px; margin: 0 auto; }
.np-toast { position: fixed; z-index: 120; right: 2rem; top: 5rem; padding: 0.65rem 1.1rem; border-radius: 999px; background: rgba(36,27,47,0.92); color: #fff; font-size: 0.84rem; font-weight: 700; }
.np-state { padding: 4rem 1rem; text-align: center; color: #756D7E; } .np-state.err { color: #ff2f68; }
.np-btn { display: inline-flex; align-items: center; gap: 6px; min-height: 44px; padding: 0 1.5rem; border: 0; border-radius: 999px; background: linear-gradient(135deg, #5A0B72 0%, #7B189F 55%, #9226B3 100%); color: #fff; cursor: pointer; font-size: 0.9rem; font-weight: 700; transition: transform 0.2s, box-shadow 0.2s; }
.np-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 26px rgba(90,11,114,0.26); }
.reveal { transition: opacity 0.55s ease, transform 0.55s ease; }
.reveal.revealed { opacity: 1; transform: translateY(0); }

/* Hero */
.np-hero { position: relative; overflow: hidden; min-height: 520px; border-radius: 24px; margin: 2rem 0 0; display: flex; align-items: center; }
.np-hero-bg { position: absolute; inset: 0; } .np-hero-bg img { width: 100%; height: 100%; object-fit: cover; }
.np-hero-overlay { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(15,5,25,0.72) 0%, rgba(15,5,25,0.35) 50%, rgba(15,5,25,0.15) 100%); }
.np-hero-body { position: relative; z-index: 2; max-width: 560px; padding: 3rem; }
.np-hero-tags { display: flex; gap: 8px; margin-bottom: 1rem; }
.np-htag { padding: 4px 12px; border: 1px solid rgba(255,255,255,0.35); border-radius: 999px; color: #fff; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.5px; }
.np-htag.yellow { background: #F4D35E; border-color: #F4D35E; color: #5A4300; }
.np-hero-en { display: block; color: #F4D35E; font-size: 0.78rem; font-weight: 900; letter-spacing: 2px; margin-bottom: 0.25rem; }
.np-hero-body h1 { margin: 0; color: #fff; font-size: 3rem; font-weight: 900; line-height: 1.1; }
.np-hero-sub { margin: 0.5rem 0 0; color: rgba(255,255,255,0.9); font-size: 1.15rem; font-weight: 600; }
.np-hero-desc { margin: 0.4rem 0 0; color: rgba(255,255,255,0.7); font-size: 0.9rem; line-height: 1.6; }
.np-hero-body .np-btn { margin-top: 1.25rem; }

/* Intro */
.np-intro { text-align: center; max-width: 660px; margin: 6rem auto; }
.np-kicker { color: #7B189F; font-size: 0.72rem; font-weight: 900; letter-spacing: 2px; }
.np-intro h2 { margin: 0.3rem 0 0; color: #241B2F; font-size: 2rem; font-weight: 900; }
.np-intro-lead { margin: 0.4rem 0 0; color: #756D7E; font-size: 1.05rem; font-weight: 600; }
.np-intro-desc { margin: 0.8rem 0 0; color: #948B9D; font-size: 0.9rem; line-height: 1.7; max-width: 520px; margin-left: auto; margin-right: auto; }
.np-intro-stats { display: flex; justify-content: center; gap: 3rem; margin-top: 2rem; }
.np-istat strong { display: block; color: #7B189F; font-size: 1.8rem; font-weight: 900; }
.np-istat span { color: #756D7E; font-size: 0.78rem; font-weight: 700; }

/* Feature */
.np-feature { display: grid; grid-template-columns: 65fr 35fr; gap: 0; align-items: center; margin-bottom: 6rem; }
.np-feature.reverse { grid-template-columns: 35fr 65fr; }
.np-feat-img { border-radius: 22px; overflow: hidden; aspect-ratio: 4/3; }
.np-feat-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
.np-feat-img img:hover { transform: scale(1.025); }
.np-feat-card { position: relative; z-index: 2; padding: 2.5rem; margin-left: -3rem; background: rgba(255,255,255,0.96); border-radius: 20px; box-shadow: 0 18px 45px rgba(55,35,75,0.10); }
.np-feature.reverse .np-feat-card { margin-left: 0; margin-right: -3rem; }
.np-feat-kicker { display: inline-block; padding: 3px 10px; border-radius: 4px; background: #F3EAF8; color: #7B189F; font-size: 0.68rem; font-weight: 900; letter-spacing: 1px; margin-bottom: 0.5rem; }
.np-feat-card h3 { margin: 0.3rem 0 0.6rem; color: #241B2F; font-size: 1.5rem; font-weight: 900; }
.np-feat-card p { color: #756D7E; font-size: 0.9rem; line-height: 1.7; margin: 0; }
.np-feat-count { display: block; margin: 0.8rem 0; color: #980B32; font-size: 0.82rem; font-weight: 800; }

/* Story */
.np-story { position: relative; border-radius: 22px; overflow: hidden; min-height: 400px; display: flex; align-items: center; margin-bottom: 6rem; }
.np-story-img { position: absolute; inset: 0; } .np-story-img img { width: 100%; height: 100%; object-fit: cover; }
.np-story-overlay { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(15,5,25,0.65) 0%, rgba(15,5,25,0.25) 60%, rgba(15,5,25,0.1) 100%); }
.np-story-body { position: relative; z-index: 2; padding: 3rem; }
.np-story-kicker { color: #F4D35E; font-size: 0.7rem; font-weight: 900; letter-spacing: 2px; }
.np-story-body h3 { margin: 0.4rem 0 1rem; color: #fff; font-size: 2rem; font-weight: 900; line-height: 1.25; }
.np-btn-play { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; border: 1.5px solid rgba(255,255,255,0.5); border-radius: 999px; background: rgba(255,255,255,0.12); color: #fff; cursor: pointer; font-size: 0.9rem; font-weight: 700; transition: background 0.2s; }
.np-btn-play:hover { background: rgba(255,255,255,0.2); }

/* Category Nav */
.np-cnav { display: flex; justify-content: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 3rem; }
.np-cnav button { min-height: 36px; padding: 0 1.1rem; border: 1px solid #e5e7eb; border-radius: 999px; background: #fff; color: #241B2F; cursor: pointer; font-size: 0.84rem; font-weight: 700; transition: all 0.15s; }
.np-cnav button.active { background: #7B189F; color: #fff; border-color: #7B189F; }

/* Curated */
.np-curated { margin-bottom: 6rem; }
.np-curated h3 { margin: 0 0 0.3rem; text-align: center; color: #241B2F; font-size: 1.6rem; font-weight: 900; }
.np-curated-sub { text-align: center; color: #756D7E; font-size: 0.9rem; margin: 0 0 1.5rem; }
.np-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.25rem; }
.np-card { border-radius: 14px; background: #fff; overflow: hidden; cursor: pointer; box-shadow: 0 2px 12px rgba(15,23,42,0.04); transition: transform 0.25s, box-shadow 0.25s; }
.np-card:hover { transform: translateY(-4px); box-shadow: 0 14px 34px rgba(64,36,78,0.12); }
.np-card-img { position: relative; aspect-ratio: 4/5; overflow: hidden; background: #f8fafc; }
.np-card-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
.np-card:hover .np-card-img img { transform: scale(1.03); }
.np-card-tag { position: absolute; top: 8px; left: 8px; padding: 3px 10px; border-radius: 4px; background: #F4D35E; color: #5A4300; font-size: 10px; font-weight: 900; }
.np-card-body { padding: 0.9rem; }
.np-card-cat { color: #7B189F; font-size: 0.7rem; font-weight: 800; }
.np-card-body h4 { margin: 0.15rem 0 0.2rem; color: #241B2F; font-size: 0.88rem; font-weight: 800; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.np-card-desc { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0 0 0.5rem; color: #948B9D; font-size: 0.75rem; line-height: 1.5; }
.np-card-footer { display: flex; justify-content: space-between; align-items: center; }
.np-card-footer strong { color: #980B32; font-size: 0.95rem; font-weight: 800; }
.np-card-btns { display: flex; gap: 4px; }
.np-card-btns button { display: grid; width: 30px; height: 30px; place-items: center; border-radius: 50%; cursor: pointer; transition: all 0.15s; }
.np-card-btns button:first-child { border: 1.5px solid #980B32; background: #fff; color: #980B32; }
.np-card-btns button:first-child svg { width: 14px; height: 14px; }
.np-card-btns button:first-child.active, .np-card-btns button:first-child:hover { background: #F8EDF1; }
.np-card-cart { border: 0; background: #7B189F; color: #fff; font-size: 0.68rem; font-weight: 700; width: auto !important; padding: 0 12px; border-radius: 999px !important; }
.np-card-cart:hover { background: #5A0B72; }

/* Values */
.np-values { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.5rem; margin-bottom: 6rem; }
.np-val { text-align: center; padding: 2rem 1.5rem; }
.np-val-icon { font-size: 2rem; }
.np-val h4 { margin: 0.5rem 0 0.3rem; color: #241B2F; font-size: 1rem; font-weight: 900; }
.np-val p { color: #756D7E; font-size: 0.85rem; line-height: 1.6; margin: 0; }

/* Subscribe */
.np-sub { text-align: center; padding: 3rem 2rem; border-radius: 22px; background: linear-gradient(135deg, #351044 0%, #5A0B72 50%, #7B189F 100%); color: #fff; margin-bottom: 2rem; }
.np-sub h3 { margin: 0; font-size: 1.4rem; font-weight: 900; }
.np-sub > p { margin: 0.4rem 0 1.25rem; color: rgba(255,255,255,0.75); font-size: 0.9rem; }
.np-sub-form { display: flex; justify-content: center; gap: 0.65rem; max-width: 420px; margin: 0 auto; }
.np-sub-form input { flex: 1; min-height: 46px; padding: 0 1.1rem; border: 1.5px solid rgba(255,255,255,0.3); border-radius: 999px; background: rgba(255,255,255,0.1); color: #fff; font-size: 0.9rem; outline: none; min-width: 0; }
.np-sub-form input::placeholder { color: rgba(255,255,255,0.5); }
.np-sub-form input:focus { border-color: #F4D35E; }
.np-sub-form button { min-height: 46px; padding: 0 1.5rem; border: 0; border-radius: 999px; background: #F4D35E; color: #4C3900; cursor: pointer; font-size: 0.9rem; font-weight: 800; transition: transform 0.2s; }
.np-sub-form button:hover { transform: translateY(-2px); }
.np-sub-ok { color: #F4D35E; font-size: 0.9rem; font-weight: 700; }

@media (max-width: 1100px) {
  .np-feature, .np-feature.reverse { grid-template-columns: 1fr; }
  .np-feat-card { margin: -2rem 1.5rem 0 !important; }
  .np-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 767px) {
  .np-hero { min-height: 400px; } .np-hero-body { padding: 1.5rem; }
  .np-hero-body h1 { font-size: 2rem; }
  .np-intro { margin: 3rem auto; } .np-intro-stats { gap: 1.5rem; }
  .np-feat-card { margin: -1.5rem 1rem 0 !important; padding: 1.5rem; }
  .np-story { min-height: 300px; } .np-story-body h3 { font-size: 1.3rem; }
  .np-grid { gap: 0.65rem; } .np-values { grid-template-columns: 1fr; }
}
</style>
