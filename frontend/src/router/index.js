import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: () => import('@/views/HomePage.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true, title: '首页' }
  },
  {
    path: '/rooms',
    name: 'Rooms',
    component: () => import('@/views/rooms/Index.vue'),
    meta: { requiresAuth: true, title: '会议室管理' }
  },
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('@/views/bookings/Index.vue'),
    meta: { requiresAuth: true, title: '预约管理' }
  },
  {
    path: '/bookings/today',
    name: 'TodayBookings',
    component: () => import('@/views/bookings/TodayBookings.vue'),
    meta: { requiresAuth: true, title: '今日预约' }
  },
  {
    path: '/items',
    name: 'Items',
    component: () => import('@/views/items/Index.vue'),
    meta: { requiresAuth: true, title: '物品管理' }
  },
  {
    path: '/borrowings',
    name: 'Borrowings',
    component: () => import('@/views/borrowings/Index.vue'),
    meta: { requiresAuth: true, title: '借用管理' }
  },
  {
    path: '/organizations',
    name: 'Organizations',
    component: () => import('@/views/organizations/Index.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '组织管理' }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/users/Index.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '用户管理' }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/admin/Logs.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '系统日志' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true, title: '个人中心' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
