import request from './request'

// 公共接口（无需认证）
export const getPublicTodayBookings = () => request.get('/public/today-bookings')
export const getPublicRooms = () => request.get('/public/rooms')
export const getPublicStats = () => request.get('/public/stats')
export const getPublicItems = () => request.get('/public/items')

// 认证相关
export const login = (username, password) => {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)
  return request.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const register = (data) => request.post('/auth/register', data)
export const getMe = () => request.get('/auth/me')
export const changePassword = (oldPassword, newPassword) => 
  request.put('/auth/password', {
    old_password: oldPassword,
    new_password: newPassword
  })

// 用户管理
export const getUsers = (params) => request.get('/users', { params })
export const getUser = (id) => request.get(`/users/${id}`)
export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.put(`/users/${id}`, data)
export const deleteUser = (id) => request.delete(`/users/${id}`)

// 组织管理
export const getOrganizations = (params) => request.get('/organizations', { params })
export const createOrganization = (data) => request.post('/organizations', data)
export const updateOrganization = (id, data) => request.put(`/organizations/${id}`, data)
export const deleteOrganization = (id) => request.delete(`/organizations/${id}`)

// 会议室管理
export const getRooms = (params) => request.get('/rooms', { params })
export const getAllRooms = (params) => request.get('/rooms/all', { params })
export const getRoom = (id) => request.get(`/rooms/${id}`)
export const createRoom = (data) => request.post('/rooms', data)
export const updateRoom = (id, data) => request.put(`/rooms/${id}`, data)
export const deleteRoom = (id) => request.delete(`/rooms/${id}`)

// 预约管理
export const getBookings = (params) => request.get('/bookings', { params })
export const getBooking = (id) => request.get(`/bookings/${id}`)
export const getTodayBookings = () => request.get('/bookings/today')  // 今日所有预约（不限制权限）
export const createBooking = (data) => {
  console.log('[API] createBooking 调用:', data)
  return request.post('/bookings', data)
    .then(response => {
      console.log('[API] createBooking 成功:', response)
      return response
    })
    .catch(error => {
      console.error('[API] createBooking 失败:', error)
      // 错误由拦截器处理，这里只记录日志
      throw error
    })
}
export const updateBooking = (id, data) => request.put(`/bookings/${id}`, data)
export const deleteBooking = (id) => request.delete(`/bookings/${id}`)

// 物品管理
export const getItems = (params) => request.get('/items', { params })
export const getAllItems = (params) => request.get('/items/all', { params })
export const getItem = (id) => request.get(`/items/${id}`)
export const createItem = (data) => request.post('/items', data)
export const updateItem = (id, data) => request.put(`/items/${id}`, data)
export const deleteItem = (id) => request.delete(`/items/${id}`)

// 借用管理
export const getBorrowings = (params) => request.get('/borrowings', { params })
export const getBorrowing = (id) => request.get(`/borrowings/${id}`)
export const createBorrowing = (data) => request.post('/borrowings', data)
export const returnItem = (id) => request.put(`/borrowings/${id}/return`)

// 日志管理
export const getLogTypes = () => request.get('/logs/types')
export const getLogs = (params) => request.get('/logs', { params })
