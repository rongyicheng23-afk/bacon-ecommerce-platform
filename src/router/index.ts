import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import ProductDetail from '@/views/ProductDetail.vue'
import ProductCatalog from '@/views/ProductCatalog.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import CartView from '@/views/CartView.vue'
import CheckoutView from '@/views/CheckoutView.vue'
import OrderList from '@/views/OrderList.vue'
import OrderDetail from '@/views/OrderDetail.vue'
import ProfileView from '@/views/ProfileView.vue'
import PaymentPage from '@/components/PaymentPage.vue'
import PaymentSuccess from '@/views/PaymentSuccess.vue'
import SellerDashboard from '@/views/SellerDashboard.vue'
import BrowsingHistory from '@/views/BrowsingHistory.vue'
import MessageCenter from '@/views/MessageCenter.vue'
import CustomerService from '@/views/CustomerService.vue'
import NewArrivals from '@/views/NewArrivals.vue'
import HotSales from '@/views/HotSales.vue'
import CategoryPage from '@/views/CategoryPage.vue'
import { useUserStore } from '@/stores/userStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/products',
      name: 'products',
      component: ProductCatalog
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: ProductDetail
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartView,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: CheckoutView,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/orders',
      name: 'orders',
      component: OrderList,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/history',
      name: 'browsing-history',
      component: BrowsingHistory,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/order/:id',
      name: 'order-detail',
      component: OrderDetail,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/payment/:orderId',
      name: 'payment',
      component: PaymentPage,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/payment-success/:orderId',
      name: 'payment-success',
      component: PaymentSuccess,
      meta: { requiresAuth: true, role: 'buyer' }
    },
    {
      path: '/seller',
      name: 'seller-dashboard',
      component: SellerDashboard,
      meta: { requiresAuth: true, role: 'seller' }
    },
    {
      path: '/messages',
      name: 'messages',
      component: MessageCenter
    },
    {
      path: '/customer-service',
      name: 'customer-service',
      component: CustomerService
    },
    {
      path: '/new-arrivals',
      name: 'new-arrivals',
      component: NewArrivals
    },
    {
      path: '/hot-sales',
      name: 'hot-sales',
      component: HotSales
    },
    { path: '/category/:category', name: 'category', component: CategoryPage },
  ]
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) return true

  const userStore = useUserStore()

  // 本地无 token → 直接拦截
  if (!localStorage.getItem('token')) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 尚未向服务端验证过 → 先验证
  if (!userStore.authChecked) {
    await userStore.initAuth()
  }

  // 验证后仍未登录 → 拦截
  if (!userStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 角色校验
  const requiredRole = to.meta.role as 'buyer' | 'seller' | undefined
  if (requiredRole && userStore.currentUser?.role !== requiredRole) {
    return userStore.currentUser?.role === 'seller' ? { name: 'seller-dashboard' } : { name: 'home' }
  }

  return true
})

export default router
