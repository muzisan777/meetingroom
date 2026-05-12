# 会议室预约系统

极简风格 · 用户管理 · 角色权限 · 物品借用 · 系统设置

## 项目结构

```
meeting-room-system/
├── backend/                  # FastAPI 后端
│   ├── main.py              # 主程序 (全部 API 路由)
│   ├── models.py            # SQLAlchemy 数据模型
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── auth.py              # JWT 认证工具
│   ├── permissions.py       # RBAC 权限检查模块
│   ├── logger.py            # 日志模块（动态配置）
│   ├── database.py          # 数据库引擎配置
│   ├── init_test_data.py    # 测试数据
│   ├── reset_db.py          # 数据库重置
│   ├── logs/                # 日志文件目录
│   │   ├── action.log
│   │   └── error.log
│   └── requirements.txt
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── api/             # API 接口
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   └── views/           # 页面组件
│   │       ├── admin/       # 管理员页面
│   │       ├── rooms/
│   │       ├── bookings/
│   │       ├── items/
│   │       ├── borrowings/
│   │       ├── organizations/
│   │       └── users/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 快速启动

### 1. 启动后端

```bash
cd meeting-room-system/backend

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端运行在：http://localhost:8000
API 文档：http://localhost:8000/docs

### 2. 启动前端

```bash
cd meeting-room-system/frontend
npm install
npm run dev
```

前端运行在：http://localhost:3000

## 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin@123（首次登录后请修改） |

## 功能清单

### 后端

- 用户认证系统 (JWT)
- RBAC 角色权限管理 (细粒度模块+操作)
- 会议室管理 (CRUD)
- 预约管理 (冲突检测)
- 物品管理 (库存追踪)
- 借用管理 (归还提醒)
- 组织/部门管理
- **角色管理**（创建/编辑/删除角色，权限矩阵配置）
- **系统设置**（通过管理页面动态配置）
- **日志模块**（分类型查看、关键词搜索、按时间删除、操作类型可配）
- SQLite 数据库
- 密码哈希加密
- CORS 跨域支持

### 前端

- 登录页面
- 主布局 (侧边栏导航 + 权限控制菜单显示)
- 首页数据看板
- 会议室管理
- 预约管理
- 物品管理
- 借用管理
- 组织管理
- 用户管理
- **角色管理** (权限矩阵编辑)
- **系统设置** (标题、日志参数、操作类型开关)
- **系统日志** (类型筛选、搜索、分页、时间范围删除)
- 个人中心

## 系统设置 (管理员)

| 参数 | 说明 |
|------|------|
| 前端标题 | 页面标题和侧边栏名称，可动态修改 |
| 开放注册 | 是否允许新用户自助注册 |
| 每页默认条数 | 列表分页默认大小 |
| 日志级别 | DEBUG / INFO / WARNING / ERROR |
| 单文件最大字节数 | 日志文件轮转大小 |
| 备份文件个数 | 保留的旧日志文件数 |
| 时间戳格式 | 日志时间显示格式 |
| 自动清理天数 | N 天前的日志自动清理 |
| 记录操作类型 | 24 种操作可精细控制是否写入日志 |

## 日志模块

- **操作日志** (`action.log`) — 记录用户所有操作行为
- **错误日志** (`error.log`) — 记录系统错误和异常
- 支持按时间段删除日志（需要 `logs:delete` 权限）
- 支持配置只记录特定类型的操作（通过系统设置中的操作类型多选）

## 设计特点

### 极简风格
- 清爽的渐变登录页
- 卡片式数据展示
- 直观的导航
- 响应式布局

### 用户体验
- 预约时间冲突自动检测
- 物品库存实时追踪
- 借用状态一目了然
- 权限分级清晰
- 角色权限矩阵可视化编辑

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **密码**: bcrypt (passlib)
- **验证**: Pydantic 2

### 前端
- **框架**: Vue 3 (Composition API)
- **UI 库**: Element Plus
- **状态**: Pinia
- **路由**: Vue Router 4
- **HTTP**: Axios
- **构建**: Vite
- **时间**: Day.js

## API 接口

### 公开接口（无需认证）
- `GET /api/public/today-bookings` - 今日预约
- `GET /api/public/rooms` - 会议室列表
- `GET /api/public/stats` - 系统统计
- `GET /api/public/items` - 可借物品
- `GET /api/public/app-config` - 前端标题配置
- `GET /api/health` - 健康检查

### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户
- `PUT /api/auth/password` - 修改密码

### 用户管理（需要 `users` 权限）
- `GET /api/users` - 用户列表
- `GET /api/users/{id}` - 用户详情
- `POST /api/users` - 创建用户
- `PUT /api/users/{id}` - 更新用户
- `DELETE /api/users/{id}` - 删除用户

### 组织管理（需要 `organizations` 权限）
- `GET /api/organizations` - 组织列表
- `POST /api/organizations` - 创建组织
- `PUT /api/organizations/{id}` - 更新组织
- `DELETE /api/organizations/{id}` - 删除组织

### 会议室（需要 `rooms` 权限）
- `GET /api/rooms` - 会议室列表
- `POST /api/rooms` - 创建会议室
- `PUT /api/rooms/{id}` - 更新会议室
- `DELETE /api/rooms/{id}` - 删除会议室

### 预约（需要 `bookings` 权限）
- `GET /api/bookings` - 预约列表
- `POST /api/bookings` - 创建预约
- `PUT /api/bookings/{id}` - 更新预约
- `DELETE /api/bookings/{id}` - 取消预约
- `GET /api/bookings/today` - 今日预约

### 物品（需要 `items` 权限）
- `GET /api/items` - 物品列表
- `POST /api/items` - 创建物品
- `PUT /api/items/{id}` - 更新物品
- `DELETE /api/items/{id}` - 删除物品

### 借用（需要 `borrowings` 权限）
- `GET /api/borrowings` - 借用列表
- `POST /api/borrowings` - 创建借用
- `PUT /api/borrowings/{id}/return` - 归还物品

### 角色管理（需要 `roles` 权限）
- `GET /api/roles` - 角色列表
- `POST /api/roles` - 创建角色
- `PUT /api/roles/{id}` - 更新角色
- `DELETE /api/roles/{id}` - 删除角色
- `GET /api/roles/{id}/permissions` - 获取角色权限
- `PUT /api/roles/{id}/permissions` - 更新角色权限

### 系统设置（需要 `settings` 权限）
- `GET /api/settings` - 获取所有设置
- `PUT /api/settings` - 批量更新设置

### 日志（需要 `logs` 权限）
- `GET /api/logs` - 获取日志（分页、关键词搜索）
- `GET /api/logs/types` - 获取日志类型
- `DELETE /api/logs` - 按时间段删除日志（需要 `logs:delete`）

## 权限说明

系统使用 RBAC 权限模型，支持 9 个模块，每个模块可独立控制 4 种操作：

| 模块 | 查看 | 新增 | 修改 | 删除 |
|------|------|------|------|------|
| 用户管理 | read | create | update | delete |
| 组织管理 | read | create | update | delete |
| 会议室管理 | read | create | update | delete |
| 预约管理 | read | create | update | delete |
| 物品管理 | read | create | update | delete |
| 借用管理 | read | create | update | delete |
| 系统日志 | read | - | - | delete |
| 角色管理 | read | - | - | - |
| 系统设置 | read | - | update | - |

## 使用流程

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

### 管理角色权限
1. 进入「角色管理」
2. 创建或编辑角色
3. 勾选权限矩阵中的模块/操作
4. 保存后该角色的用户重新登录即可生效

## 注意事项

1. **首次使用**请先修改默认管理员密码
2. **生产环境**请更换 `SECRET_KEY`
3. **数据库备份**定期备份 `meeting_room.db`
4. **日志文件**定期清理，可通过系统设置配置自动清理天数
5. **权限变更**修改角色权限后，对应用户需重新登录才能生效

## 常见问题

### 后端启动失败
```bash
# 检查 Python 版本 (需要 3.8+)
python --version
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 前端启动失败
```bash
rm -rf node_modules
npm install
```

### 数据库重置
```bash
rm backend/meeting_room.db
# 重启后端会自动创建
python backend/main.py
```

## License

MIT License

---

**开发时间**: 2026
