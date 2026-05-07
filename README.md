# 会议室预约系统

> 极简风格 · 用户管理 · 权限系统 · 物品借用

## 📊 项目结构

```
meeting-room-system/
├── backend/              # FastAPI 后端
│   ├── main.py          # 主程序 (完整 API)
│   └── requirements.txt # Python 依赖
├── frontend/            # Vue 3 前端
│   ├── src/
│   │   ├── api/        # API 接口
│   │   ├── router/     # 路由配置
│   │   ├── stores/     # 状态管理
│   │   └── views/      # 页面组件
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🚀 快速启动

### 1. 启动后端

```bash
cd meeting-room-system/backend

# 创建虚拟环境（可选）
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端运行在：http://localhost:8000
API 文档：http://localhost:8000/docs

### 2. 启动前端

```bash
cd meeting-room-system/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在：http://localhost:3000

## 👤 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin@123（首次登录后请修改） |

**⚠️ 首次登录后请立即修改密码！**

## 📋 功能清单

### ✅ 已完成

#### 后端 (FastAPI)
- [x] 用户认证系统 (JWT)
- [x] 权限管理 (管理员/普通用户)
- [x] 会议室管理 (CRUD)
- [x] 预约管理 (冲突检测)
- [x] 物品管理 (库存追踪)
- [x] 借用管理 (归还提醒)
- [x] SQLite 数据库
- [x] 密码哈希加密
- [x] CORS 跨域支持

#### 前端 (Vue 3 + Element Plus)
- [x] 登录页面 (极简渐变风格)
- [x] 主布局 (侧边栏导航)
- [x] 首页数据看板
- [x] 会议室管理
- [x] 预约管理
- [x] 物品管理
- [x] 借用管理
- [x] 用户管理 (管理员)
- [x] 个人中心

## 🎨 设计特点

### 极简风格
- 清爽的渐变登录页
- 卡片式数据展示
- 直观的图标导航
- 响应式布局

### 用户体验
- 预约时间冲突自动检测
- 物品库存实时追踪
- 借用状态一目了然
- 权限分级清晰

## 🔧 技术栈

### 后端
- **框架**: FastAPI 0.109
- **数据库**: SQLite + SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **密码**: bcrypt (passlib)
- **验证**: Pydantic 2.5

### 前端
- **框架**: Vue 3.4
- **UI 库**: Element Plus 2.5
- **状态**: Pinia 2.1
- **路由**: Vue Router 4.2
- **HTTP**: Axios 1.6
- **构建**: Vite 5.0
- **时间**: Day.js 1.11

## 📖 API 接口

### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户
- `POST /api/auth/password` - 修改密码

### 用户管理 (管理员)
- `GET /api/users` - 用户列表
- `GET /api/users/{id}` - 用户详情
- `PUT /api/users/{id}` - 更新用户
- `DELETE /api/users/{id}` - 删除用户

### 会议室
- `GET /api/rooms` - 会议室列表
- `POST /api/rooms` - 创建会议室
- `PUT /api/rooms/{id}` - 更新会议室
- `DELETE /api/rooms/{id}` - 删除会议室

### 预约
- `GET /api/bookings` - 预约列表
- `POST /api/bookings` - 创建预约
- `PUT /api/bookings/{id}` - 更新预约
- `DELETE /api/bookings/{id}` - 取消预约

### 物品
- `GET /api/items` - 物品列表
- `POST /api/items` - 创建物品
- `PUT /api/items/{id}` - 更新物品
- `DELETE /api/items/{id}` - 删除物品

### 借用
- `GET /api/borrowings` - 借用列表
- `POST /api/borrowings` - 创建借用
- `PUT /api/borrowings/{id}/return` - 归还物品

## 🔒 权限说明

| 功能 | 普通用户 | 管理员 |
|------|---------|--------|
| 预约会议室 | ✅ | ✅ |
| 查看预约 | 仅自己 | 全部 |
| 借用物品 | ✅ | ✅ |
| 查看借用 | 仅自己 | 全部 |
| 管理会议室 | ❌ | ✅ |
| 管理物品 | ❌ | ✅ |
| 管理用户 | ❌ | ✅ |

## 📝 使用流程

### 预约会议室
1. 登录系统
2. 进入「会议室管理」
3. 点击「预约」按钮
4. 选择日期和时间段
5. 填写预约事由
6. 提交预约

### 借用物品
1. 进入「物品管理」
2. 找到需要借用的物品
3. 点击「借用」按钮
4. 填写借用数量和预计归还日期
5. 提交借用申请

### 归还物品
1. 进入「借用管理」
2. 找到借用中的记录
3. 点击「归还」按钮
4. 完成归还

## ⚠️ 注意事项

1. **首次使用**请先修改默认管理员密码
2. **生产环境**请更换 `SECRET_KEY`
3. **数据库备份**定期备份 `meeting_room.db`
4. **时间格式**使用 24 小时制
5. **预约冲突**系统自动检测，无法重复预约

## 🐛 常见问题

### 后端启动失败
```bash
# 检查 Python 版本 (需要 3.8+)
python --version

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 前端启动失败
```bash
# 清除 node_modules
rm -rf node_modules
npm install
```

### 数据库重置
```bash
# 删除数据库文件
rm backend/meeting_room.db

# 重启后端会自动创建
python backend/main.py
```

## 📄 License

MIT License

---

**开发时间**: 2026-03-13
**开发者**: 全栈工程师 💻🏗️
