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
    meta: { requiresAuth: true, module: 'rooms', title: '会议室管理' }
  },
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('@/views/bookings/Index.vue'),
    meta: { requiresAuth: true, module: 'bookings', title: '预约管理' }
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
    meta: { requiresAuth: true, module: 'items', title: '物品管理' }
  },
  {
    path: '/borrowings',
    name: 'Borrowings',
    component: () => import('@/views/borrowings/Index.vue'),
    meta: { requiresAuth: true, module: 'borrowings', title: '借用管理' }
  },
  {
    path: '/organizations',
    name: 'Organizations',
    component: () => import('@/views/organizations/Index.vue'),
    meta: { requiresAuth: true, module: 'organizations', title: '组织管理' }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/users/Index.vue'),
    meta: { requiresAuth: true, module: 'users', title: '用户管理' }
  },
  {
    path: '/roles',
    name: 'Roles',
    component: () => import('@/views/admin/Roles.vue'),
    meta: { requiresAuth: true, module: 'roles', title: '角色管理' }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/admin/Logs.vue'),
    meta: { requiresAuth: true, module: 'logs', title: '系统日志' }
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
    return
  }

  // 模块权限检查
  if (to.meta.module && !userStore.hasPermission(to.meta.module, 'read')) {
    next('/dashboard')
    return
  }

  next()
})

export default router