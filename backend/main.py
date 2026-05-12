"""
会议室预约系统 - FastAPI 后端
极简风格 | 用户管理 | 权限系统 | 物品借用
"""

from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List

# 导入配置模块
from database import get_db, engine, SessionLocal
from models import User, Organization, MeetingRoom, Booking, Item, Borrowing, Role, RolePermission, SystemSetting
from schemas import (
    Token, UserCreate, UserUpdate, UserResponse,
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    MeetingRoomCreate, MeetingRoomUpdate, MeetingRoomResponse,
    BookingCreate, BookingUpdate, BookingResponse,
    ItemCreate, ItemUpdate, ItemResponse,
    BorrowingCreate, BorrowingUpdate, BorrowingResponse,
    PasswordChange,
    RoleCreate, RoleUpdate, RoleResponse,
    PermissionCreate, PermissionResponse, RolePermissionsUpdate,
    SystemSettingResponse, SystemSettingUpdate
)
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, get_current_admin_user
)
from permissions import require_permission

# 导入日志系统
from logger import log_user_action, log_error, apply_settings, reload_loggers

# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="会议室预约系统",
    description="极简风格会议室预约管理系统 | 用户管理 | 权限系统 | 物品借用",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """记录所有未处理的异常"""
    from logger import log_error
    import traceback
    
    # 尝试获取用户信息
    user_id = None
    username = None
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            username = decoded.get("username")
    except Exception:
        pass
    
    # 记录错误
    log_error(
        user_id=user_id,
        username=username,
        error_type=type(exc).__name__,
        error_msg=str(exc),
        traceback=traceback.format_exc(),
        context=f"{request.method} {request.url.path}"
    )
    
    # 返回通用错误响应
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )


# 导入 jwt 用于异常处理
from jose import jwt


# ==================== 初始化数据库 ====================

@app.on_event("startup")
def startup_event():
    from models import Base
    Base.metadata.create_all(bind=engine)
    
    # 创建默认管理员账户和角色
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        
        # 创建默认角色
        admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
        if not admin_role:
            admin_role = Role(name="超级管理员", description="拥有系统全部权限")
            db.add(admin_role)
            db.flush()
            
            # 为超级管理员角色分配所有权限
            all_modules = {
                "users": ["create", "read", "update", "delete"],
                "organizations": ["create", "read", "update", "delete"],
                "rooms": ["create", "read", "update", "delete"],
                "bookings": ["create", "read", "update", "delete"],
                "items": ["create", "read", "update", "delete"],
                "borrowings": ["create", "read", "update", "delete"],
                "logs": ["read", "delete"],
                "roles": ["read"],
                "settings": ["read", "update"],
            }
            for module, actions in all_modules.items():
                for action in actions:
                    db.add(RolePermission(role_id=admin_role.id, module=module, action=action))
        
        user_role = db.query(Role).filter(Role.name == "普通用户").first()
        if not user_role:
            user_role = Role(name="普通用户", description="拥有基础的查看和预约借用权限")
            db.add(user_role)
            db.flush()
            
            # 普通用户可以查看会议室和物品，操作自己的预约和借用
            default_perms = [
                ("rooms", "read"),
                ("items", "read"),
                ("bookings", "read"),
                ("bookings", "create"),
                ("borrowings", "read"),
                ("borrowings", "create"),
            ]
            for module, action in default_perms:
                db.add(RolePermission(role_id=user_role.id, module=module, action=action))
        
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                full_name="System Admin",
                hashed_password=get_password_hash("admin@123"),
                is_admin=True,
                role_id=admin_role.id,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Default admin account created: admin / admin@123")
        else:
            # 给现有 admin 用户关联角色
            if not admin.role_id:
                admin.role_id = admin_role.id
                db.commit()
            print("Admin role assigned to existing admin user")

        # 清理不再使用的设置项
        db.query(SystemSetting).filter(SystemSetting.key == "system_name").delete()
        db.query(SystemSetting).filter(SystemSetting.key == "jwt_secret_key").delete()

        # 初始化默认系统设置
        default_settings = {
            "app_title": "会议室系统",
            "enable_registration": "true",
            "items_per_page": "20",
            "log_max_bytes": "10485760",
            "log_backup_count": "10",
            "log_level": "INFO",
            "log_date_format": "%Y-%m-%d %H:%M:%S",
            "log_retention_days": "0",
            "enabled_log_actions": "*",
        }
        for key, value in default_settings.items():
            existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if not existing:
                desc_map = {
                    "app_title": "前端标题",
                    "enable_registration": "是否开放注册",
                    "items_per_page": "列表默认每页条数",
                    "log_max_bytes": "单日志文件最大字节数",
                    "log_backup_count": "日志备份文件个数",
                    "log_level": "日志级别",
                    "log_date_format": "日志时间戳格式",
                    "log_retention_days": "日志自动清理天数（0=不清理）",
                    "enabled_log_actions": "需要记录的操作类型（* = 全部）",

                }
                group_map = {
                    "app_title": "basic",
                    "enable_registration": "basic",
                    "items_per_page": "basic",
                    "log_max_bytes": "log",
                    "log_backup_count": "log",
                    "log_level": "log",
                    "log_date_format": "log",
                    "log_retention_days": "log",
                    "enabled_log_actions": "log",
                }
                db.add(SystemSetting(
                    key=key,
                    value=value,
                    description=desc_map.get(key, ""),
                    group=group_map.get(key, "basic")
                ))
        db.commit()

        # 将系统设置应用到日志模块
        settings_dict = {s.key: s.value for s in db.query(SystemSetting).all()}
        from logger import apply_settings
        apply_settings(settings_dict)

    finally:
        db.close()


# ==================== 认证接口 ====================

@app.post("/api/auth/login", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        # 记录登录失败
        log_error(
            user_id=user.id if user else None,
            username=username,
            full_name=user.full_name if user else username,
            error_type="登录失败",
            error_msg="用户名或密码错误",
            context="login"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        # 记录登录失败
        log_error(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name or user.username,
            error_type="登录失败",
            error_msg="用户已被禁用",
            context="login"
        )
        raise HTTPException(status_code=400, detail="用户已被禁用")
    
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # 记录登录成功
    log_user_action(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name or user.username,
        action="login",
        details=f"成功登录系统"
    )
    
    # 获取用户权限列表
    permissions = []
    role_name = None
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            role_name = role.name
            perms = db.query(RolePermission).filter(RolePermission.role_id == user.role_id).all()
            permissions = [{"module": p.module, "action": p.action} for p in perms]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "role_id": user.role_id,
            "role_name": role_name,
            "permissions": permissions
        }
    }


@app.post("/api/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            hashed_password=get_password_hash(user_data.password),
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 记录用户注册成功
        log_user_action(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name or user.username,
            action="register",
            details=f"新用户注册成功"
        )
        
        return user
    except HTTPException:
        # 记录注册失败
        log_error(
            user_id=None,
            username=user_data.username,
            full_name=user_data.full_name or user_data.username,
            error_type="用户注册失败",
            error_msg=f"注册用户失败: {user_data.username}",
            context="register"
        )
        raise


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    permissions = []
    role_name = None
    if current_user.role_id:
        role = db.query(Role).filter(Role.id == current_user.role_id).first()
        if role:
            role_name = role.name
            perms = db.query(RolePermission).filter(RolePermission.role_id == current_user.role_id).all()
            permissions = [{"module": p.module, "action": p.action} for p in perms]
    
    user_dict = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "org_id": current_user.org_id,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "role_id": current_user.role_id,
        "role_name": role_name,
        "permissions": permissions
    }
    return user_dict


@app.put("/api/auth/password")
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改密码"""
    if not verify_password(password_data.old_password, current_user.hashed_password):
        # 记录密码修改失败
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="密码修改失败",
            error_msg="原密码错误",
            context="change_password"
        )
        raise HTTPException(status_code=400, detail="原密码错误")
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    # 记录密码修改成功
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="change_password",
        details="成功修改密码"
    )
    
    return {"message": "密码修改成功"}


# ==================== 组织管理接口 ====================

@app.get("/api/organizations", response_model=List[OrganizationResponse])
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organizations", "read"))
):
    """获取组织列表"""
    orgs = db.query(Organization).offset(skip).limit(limit).all()
    
    # 统计每个组织的用户数
    result = []
    for org in orgs:
        user_count = db.query(User).filter(User.org_id == org.id).count()
        parent_name = None
        if org.parent_id:
            parent = db.query(Organization).filter(Organization.id == org.parent_id).first()
            if parent:
                parent_name = parent.name
        
        org_dict = {
            "id": org.id,
            "name": org.name,
            "parent_id": org.parent_id,
            "parent_name": parent_name,
            "description": org.description,
            "is_active": org.is_active,
            "user_count": user_count
        }
        result.append(org_dict)
    
    return result


@app.get("/api/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organizations", "read"))
):
    """获取组织详情"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取组织详情失败",
            error_msg=f"组织不存在: {org_id}",
            context="get_organization"
        )
        raise HTTPException(status_code=404, detail="组织不存在")
    
    # 统计组织的用户数
    user_count = db.query(User).filter(User.org_id == org.id).count()
    parent_name = None
    if org.parent_id:
        parent = db.query(Organization).filter(Organization.id == org.parent_id).first()
        if parent:
            parent_name = parent.name
    
    return {
        "id": org.id,
        "name": org.name,
        "parent_id": org.parent_id,
        "parent_name": parent_name,
        "description": org.description,
        "is_active": org.is_active,
        "user_count": user_count
    }


@app.post("/api/organizations", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organizations", "create"))
):
    """创建组织"""
    try:
        existing_org = db.query(Organization).filter(Organization.name == org_data.name).first()
        if existing_org:
            raise HTTPException(status_code=400, detail="组织名称已存在")
        
        org = Organization(**org_data.dict())
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # 记录管理员操作
        log_user_action(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            action="create_organization",
            details=f"组织ID: {org.id}, 组织名称: {org.name}"
        )
        
        return {
            "id": org.id,
            "name": org.name,
            "parent_id": org.parent_id,
            "parent_name": None,
            "description": org.description,
            "is_active": org.is_active,
            "user_count": 0
        }
    except HTTPException:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="组织创建失败",
            error_msg=f"尝试创建组织: {org_data.name}",
            context="create_organization"
        )
        raise


@app.put("/api/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organizations", "update"))
):
    """更新组织"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="组织更新失败",
            error_msg=f"组织不存在: {org_id}",
            context="update_organization"
        )
        raise HTTPException(status_code=404, detail="组织不存在")
    
    update_data = org_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    db.commit()
    db.refresh(org)
    
    # 重新获取组织信息
    user_count = db.query(User).filter(User.org_id == org.id).count()
    parent_name = None
    if org.parent_id:
        parent = db.query(Organization).filter(Organization.id == org.parent_id).first()
        if parent:
            parent_name = parent.name
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_organization",
        details=f"组织ID: {org.id}, 组织名称: {org.name}"
    )
    
    return {
        "id": org.id,
        "name": org.name,
        "parent_id": org.parent_id,
        "parent_name": parent_name,
        "description": org.description,
        "is_active": org.is_active,
        "user_count": user_count
    }


@app.delete("/api/organizations/{org_id}")
async def delete_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organizations", "delete"))
):
    """删除组织"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="组织删除失败",
            error_msg=f"组织不存在: {org_id}",
            context="delete_organization"
        )
        raise HTTPException(status_code=404, detail="组织不存在")
    
    # 检查是否有用户
    user_count = db.query(User).filter(User.org_id == org_id).count()
    if user_count > 0:
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="组织删除失败",
            error_msg=f"组织下还有{user_count}个用户，无法删除: {org_id}",
            context="delete_organization"
        )
        raise HTTPException(status_code=400, detail=f"组织下还有{user_count}个用户，无法删除")
    
    db.delete(org)
    db.commit()
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="delete_organization",
        details=f"组织ID: {org_id}, 组织名称: {org.name}"
    )
    
    return {"message": "组织已删除"}


# ==================== 用户管理接口 ====================

@app.get("/api/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users", "read"))
):
    """获取用户列表"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    # 关联组织名称
    result = []
    for user in users:
        org_name = None
        if user.org_id:
            org = db.query(Organization).filter(Organization.id == user.org_id).first()
            if org:
                org_name = org.name
        
        role_name = None
        if user.role_id:
            role = db.query(Role).filter(Role.id == user.role_id).first()
            if role:
                role_name = role.name
        
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "org_id": user.org_id,
            "org_name": org_name,
            "role_id": user.role_id,
            "role_name": role_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
        result.append(user_dict)
    
    return result


@app.post("/api/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users", "create"))
):
    """创建用户"""
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            org_id=user_data.org_id,
            role_id=user_data.role_id,
            hashed_password=get_password_hash(user_data.password),
            is_admin=user_data.is_admin if hasattr(user_data, 'is_admin') else False,
            is_active=user_data.is_active if hasattr(user_data, 'is_active') else True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 获取组织名称
        org_name = None
        if user.org_id:
            org = db.query(Organization).filter(Organization.id == user.org_id).first()
            if org:
                org_name = org.name
        
        # 获取角色名称
        role_name = None
        if user.role_id:
            role = db.query(Role).filter(Role.id == user.role_id).first()
            if role:
                role_name = role.name
        
        # 记录管理员操作
        log_user_action(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            action="create_user",
            details=f"用户ID: {user.id}, 用户名: {user.username}, 组织: {org_name or '无'}"
        )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "org_id": user.org_id,
            "org_name": org_name,
            "role_name": role_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
    except HTTPException:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="用户创建失败",
            error_msg=f"尝试创建用户: {user_data.username}",
            context="create_user"
        )
        raise


@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users", "read"))
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取用户详情失败",
            error_msg=f"用户不存在: {user_id}",
            context="get_user"
        )
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user


@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users", "update"))
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="用户更新失败",
            error_msg=f"用户不存在: {user_id}",
            context="update_user"
        )
        raise HTTPException(status_code=404, detail="用户不存在")
    
    original_username = user.username
    if user_data.email:
        user.email = user_data.email
    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.phone:
        user.phone = user_data.phone
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    if user_data.org_id is not None:
        user.org_id = user_data.org_id
    if user_data.role_id is not None:
        user.role_id = user_data.role_id
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    # 获取组织名称
    org_name = None
    if user.org_id:
        org = db.query(Organization).filter(Organization.id == user.org_id).first()
        if org:
            org_name = org.name
    
    # 获取角色名称
    role_name = None
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            role_name = role.name
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_user",
        details=f"用户ID: {user.id}, 用户名: {original_username} -> {user.username}, 组织: {org_name or '无'}"
    )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "org_id": user.org_id,
        "org_name": org_name,
        "role_name": role_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin
    }


@app.delete("/api/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users", "delete"))
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="用户删除失败",
            error_msg=f"用户不存在: {user_id}",
            context="delete_user"
        )
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.username == "admin":
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="用户删除失败",
            error_msg=f"尝试删除管理员账户: {user.username}",
            context="delete_user"
        )
        raise HTTPException(status_code=400, detail="不能删除管理员账户")
    
    db.delete(user)
    db.commit()
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="delete_user",
        details=f"用户ID: {user_id}, 用户名: {user.username}"
    )
    
    return {"message": "用户已删除"}


# ==================== 会议室管理接口 ====================

@app.get("/api/rooms", response_model=List[MeetingRoomResponse])
async def list_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取会议室列表"""
    rooms = db.query(MeetingRoom).filter(MeetingRoom.is_active == True).offset(skip).limit(limit).all()
    return rooms


@app.get("/api/rooms/all", response_model=List[MeetingRoomResponse])
async def list_all_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rooms", "update"))
):
    """获取所有会议室（包括禁用的）"""
    rooms = db.query(MeetingRoom).offset(skip).limit(limit).all()
    
    return rooms


@app.post("/api/rooms", response_model=MeetingRoomResponse)
async def create_room(
    room_data: MeetingRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rooms", "create"))
):
    """创建会议室"""
    try:
        existing_room = db.query(MeetingRoom).filter(MeetingRoom.name == room_data.name).first()
        if existing_room:
            raise HTTPException(status_code=400, detail="会议室名称已存在")
        
        room = MeetingRoom(**room_data.dict())
        db.add(room)
        db.commit()
        db.refresh(room)
        
        # 记录管理员操作
        log_user_action(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            action="create_room",
            details=f"会议室ID: {room.id}, 会议室名称: {room.name}, 位置: {room.location or '未知'}, 容量: {room.capacity}"
        )
        
        return room
    except HTTPException:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="会议室创建失败",
            error_msg=f"尝试创建会议室: {room_data.name}",
            context="create_room"
        )
        raise


@app.get("/api/rooms/{room_id}", response_model=MeetingRoomResponse)
async def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会议室详情"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取会议室详情失败",
            error_msg=f"会议室不存在: {room_id}",
            context="get_room"
        )
        raise HTTPException(status_code=404, detail="会议室不存在")
    
    return room


@app.put("/api/rooms/{room_id}", response_model=MeetingRoomResponse)
async def update_room(
    room_id: int,
    room_data: MeetingRoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rooms", "update"))
):
    """更新会议室"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="会议室更新失败",
            error_msg=f"会议室不存在: {room_id}",
            context="update_room"
        )
        raise HTTPException(status_code=404, detail="会议室不存在")
    
    update_data = room_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)
    
    db.commit()
    db.refresh(room)
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_room",
        details=f"会议室ID: {room.id}, 会议室名称: {room.name}, 更新字段: {list(update_data.keys())}"
    )
    
    return room


@app.delete("/api/rooms/{room_id}")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rooms", "delete"))
):
    """删除会议室"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="会议室删除失败",
            error_msg=f"会议室不存在: {room_id}",
            context="delete_room"
        )
        raise HTTPException(status_code=404, detail="会议室不存在")
    
    room.is_active = False
    db.commit()
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="delete_room",
        details=f"会议室ID: {room_id}, 会议室名称: {room.name}"
    )
    
    return {"message": "会议室已删除"}


# ==================== 预约管理接口 ====================

@app.get("/api/bookings", response_model=List[BookingResponse])
async def list_bookings(
    room_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取预约列表"""
    query = db.query(Booking)
    
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    if start_date:
        query = query.filter(Booking.start_time >= start_date)
    if end_date:
        query = query.filter(Booking.end_time <= end_date)
    
    # 普通用户只能看到自己的预约
    if not current_user.is_admin:
        query = query.filter(Booking.user_id == current_user.id)
    
    bookings = query.offset(skip).limit(limit).all()
    
    # 关联用户名、部门名和会议室名
    result = []
    for booking in bookings:
        user = db.query(User).filter(User.id == booking.user_id).first()
        room = db.query(MeetingRoom).filter(MeetingRoom.id == booking.room_id).first()
        org_name = None
        if user and user.org_id:
            org = db.query(Organization).filter(Organization.id == user.org_id).first()
            if org:
                org_name = org.name
        
        result.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "user_name": user.username if user else None,
            "user_org_name": org_name,
            "room_id": booking.room_id,
            "room_name": room.name if room else None,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "purpose": booking.purpose,
            "status": booking.status,
            "created_at": booking.created_at,
            "org_id": user.org_id if user else None
        })
    
    return result


@app.get("/api/bookings/today", response_model=List[BookingResponse])
async def list_today_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取今日所有预约（不限制权限，所有用户可见）"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    query = db.query(Booking).filter(
        Booking.start_time >= today_start,
        Booking.start_time <= today_end
    )
    
    bookings = query.all()
    
    # 关联用户名、部门名和会议室名
    result = []
    for booking in bookings:
        user = db.query(User).filter(User.id == booking.user_id).first()
        room = db.query(MeetingRoom).filter(MeetingRoom.id == booking.room_id).first()
        org_name = None
        if user and user.org_id:
            org = db.query(Organization).filter(Organization.id == user.org_id).first()
            if org:
                org_name = org.name
        
        result.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "user_name": user.username if user else None,
            "user_org_name": org_name,
            "room_id": booking.room_id,
            "room_name": room.name if room else None,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "purpose": booking.purpose,
            "status": booking.status,
            "created_at": booking.created_at,
            "org_id": user.org_id if user else None
        })
    
    return result


@app.post("/api/bookings", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建预约"""
    try:
        # 检查会议室是否存在
        room = db.query(MeetingRoom).filter(MeetingRoom.id == booking_data.room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="会议室不存在")
        if not room.is_active:
            raise HTTPException(status_code=400, detail="会议室已停用")
        
        # 检查时间是否冲突
        conflict = db.query(Booking).filter(
            Booking.room_id == booking_data.room_id,
            Booking.status != "cancelled",
            Booking.start_time < booking_data.end_time,
            Booking.end_time > booking_data.start_time
        ).first()
        
        if conflict:
            raise HTTPException(status_code=400, detail="该时间段已被预约")
        
        # 检查时间有效性
        if booking_data.start_time >= booking_data.end_time:
            raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
        
        booking = Booking(
            user_id=current_user.id,
            room_id=booking_data.room_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            purpose=booking_data.purpose,
            status="confirmed"
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        # 记录预约操作（所有用户）
        log_user_action(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            action="create_booking",
            details=f"预约ID: {booking.id}, 会议室: {room.name}, 时间: {booking.start_time} - {booking.end_time}, 事由: {booking.purpose}"
        )
        
        return booking
    except HTTPException:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="创建预约失败",
            error_msg=f"会议室ID: {booking_data.room_id}, 时间: {booking_data.start_time} - {booking_data.end_time}",
            context="create_booking"
        )
        raise


@app.get("/api/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取预约详情"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取预约详情失败",
            error_msg=f"预约不存在: {booking_id}",
            context="get_booking"
        )
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 普通用户只能查看自己的预约
    if not current_user.is_admin and booking.user_id != current_user.id:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取预约详情失败",
            error_msg=f"无权查看此预约: {booking_id}",
            context="get_booking"
        )
        raise HTTPException(status_code=403, detail="无权查看此预约")
    
    return booking


@app.put("/api/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新预约"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="更新预约失败",
            error_msg=f"预约不存在: {booking_id}",
            context="update_booking"
        )
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 普通用户只能取消自己的预约
    if not current_user.is_admin and booking.user_id != current_user.id:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="更新预约失败",
            error_msg=f"无权修改此预约: {booking_id}",
            context="update_booking"
        )
        raise HTTPException(status_code=403, detail="无权修改此预约")
    
    update_data = booking_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_booking",
        details=f"预约ID: {booking_id}, 更新字段: {list(update_data.keys())}"
    )
    
    return booking


@app.delete("/api/bookings/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消预约"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="取消预约失败",
            error_msg=f"预约不存在: {booking_id}",
            context="delete_booking"
        )
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 普通用户只能取消自己的预约
    if not current_user.is_admin and booking.user_id != current_user.id:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="取消预约失败",
            error_msg=f"无权取消此预约: {booking_id}",
            context="delete_booking"
        )
        raise HTTPException(status_code=403, detail="无权取消此预约")
    
    booking.status = "cancelled"
    db.commit()
    
    # 记录取消预约操作（所有用户）
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="cancel_booking",
        details=f"预约ID: {booking_id}, 会议室: {booking.room_id}, 时间: {booking.start_time} - {booking.end_time}"
    )
    
    return {"message": "预约已取消"}


# ==================== 物品管理接口 ====================

@app.get("/api/items", response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取物品列表"""
    items = db.query(Item).filter(Item.is_active == True).offset(skip).limit(limit).all()
    return items


@app.get("/api/items/all", response_model=List[ItemResponse])
async def list_all_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("items", "update"))
):
    """获取所有物品（包括禁用的）"""
    items = db.query(Item).offset(skip).limit(limit).all()
    
    return items


@app.post("/api/items", response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("items", "create"))
):
    """创建物品"""
    try:
        item = Item(**item_data.dict(), available_quantity=item_data.quantity)
        db.add(item)
        db.commit()
        db.refresh(item)
        
        # 记录管理员操作
        log_user_action(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            action="create_item",
            details=f"物品ID: {item.id}, 物品名称: {item.name}, 分类: {item.category or '无'}, 数量: {item.quantity}"
        )
        
        return item
    except Exception as e:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="物品创建失败",
            error_msg=str(e),
            context="create_item"
        )
        raise


@app.get("/api/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取物品详情"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取物品详情失败",
            error_msg=f"物品不存在: {item_id}",
            context="get_item"
        )
        raise HTTPException(status_code=404, detail="物品不存在")
    
    return item


@app.put("/api/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("items", "update"))
):
    """更新物品"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="物品更新失败",
            error_msg=f"物品不存在: {item_id}",
            context="update_item"
        )
        raise HTTPException(status_code=404, detail="物品不存在")
    
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_item",
        details=f"物品ID: {item.id}, 物品名称: {item.name}, 更新字段: {list(update_data.keys())}"
    )
    
    return item


@app.delete("/api/items/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("items", "delete"))
):
    """删除物品"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="物品删除失败",
            error_msg=f"物品不存在: {item_id}",
            context="delete_item"
        )
        raise HTTPException(status_code=404, detail="物品不存在")
    
    item.is_active = False
    db.commit()
    
    # 记录管理员操作
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="delete_item",
        details=f"物品ID: {item_id}, 物品名称: {item.name}"
    )
    
    return {"message": "物品已删除"}


# ==================== 借用管理接口 ====================

@app.get("/api/borrowings", response_model=List[BorrowingResponse])
async def list_borrowings(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取借用列表"""
    query = db.query(Borrowing)
    
    if status:
        query = query.filter(Borrowing.status == status)
    
    # 普通用户只能看到自己的借用
    if not current_user.is_admin:
        query = query.filter(Borrowing.user_id == current_user.id)
    
    borrowings = query.offset(skip).limit(limit).all()
    
    # 关联用户名、部门名和物品名
    result = []
    for borrowing in borrowings:
        user = db.query(User).filter(User.id == borrowing.user_id).first()
        item = db.query(Item).filter(Item.id == borrowing.item_id).first()
        org_name = None
        if user and user.org_id:
            org = db.query(Organization).filter(Organization.id == user.org_id).first()
            if org:
                org_name = org.name
        
        result.append({
            "id": borrowing.id,
            "user_id": borrowing.user_id,
            "user_name": user.username if user else None,
            "user_org_name": org_name,
            "item_id": borrowing.item_id,
            "item_name": item.name if item else None,
            "quantity": borrowing.quantity,
            "borrow_date": borrowing.borrow_date,
            "return_date": borrowing.return_date,
            "actual_return_date": borrowing.actual_return_date,
            "status": borrowing.status,
            "notes": borrowing.notes,
            "org_id": user.org_id if (user and user.org_id) else None
        })
    
    return result


@app.post("/api/borrowings", response_model=BorrowingResponse)
async def create_borrowing(
    borrowing_data: BorrowingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建借用"""
    try:
        # 检查物品是否存在
        item = db.query(Item).filter(Item.id == borrowing_data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="物品不存在")
        if not item.is_active:
            raise HTTPException(status_code=400, detail="物品已停用")
        
        # 检查库存
        if item.available_quantity < borrowing_data.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        
        # 创建借用记录
        borrowing = Borrowing(
            user_id=current_user.id,
            item_id=borrowing_data.item_id,
            quantity=borrowing_data.quantity,
            return_date=borrowing_data.return_date,
            notes=borrowing_data.notes,
            status="borrowed"
        )
        db.add(borrowing)
        
        # 更新库存
        item.available_quantity -= borrowing_data.quantity
        db.commit()
        db.refresh(borrowing)
        
        # 记录借用操作（所有用户）
        log_user_action(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            action="create_borrowing",
            details=f"借用ID: {borrowing.id}, 物品: {item.name}, 数量: {borrowing_data.quantity}, 归还日期: {borrowing_data.return_date}"
        )
        
        return borrowing
    except HTTPException:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="创建借用失败",
            error_msg=f"物品ID: {borrowing_data.item_id}, 数量: {borrowing_data.quantity}",
            context="create_borrowing"
        )
        raise


@app.get("/api/borrowings/{borrowing_id}", response_model=BorrowingResponse)
async def get_borrowing(
    borrowing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取借用详情"""
    borrowing = db.query(Borrowing).filter(Borrowing.id == borrowing_id).first()
    if not borrowing:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取借用详情失败",
            error_msg=f"借用记录不存在: {borrowing_id}",
            context="get_borrowing"
        )
        raise HTTPException(status_code=404, detail="借用记录不存在")
    
    # 普通用户只能查看自己的借用
    if not current_user.is_admin and borrowing.user_id != current_user.id:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取借用详情失败",
            error_msg=f"无权查看此借用: {borrowing_id}",
            context="get_borrowing"
        )
        raise HTTPException(status_code=403, detail="无权查看此借用")
    
    return borrowing


@app.put("/api/borrowings/{borrowing_id}/return", response_model=BorrowingResponse)
async def return_item(
    borrowing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """归还物品"""
    borrowing = db.query(Borrowing).filter(Borrowing.id == borrowing_id).first()
    if not borrowing:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="归还物品失败",
            error_msg=f"借用记录不存在: {borrowing_id}",
            context="return_item"
        )
        raise HTTPException(status_code=404, detail="借用记录不存在")
    
    # 普通用户只能归还自己的物品
    if not current_user.is_admin and borrowing.user_id != current_user.id:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="归还物品失败",
            error_msg=f"无权归还此物品: {borrowing_id}",
            context="return_item"
        )
        raise HTTPException(status_code=403, detail="无权归还此物品")
    
    if borrowing.status == "returned":
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="归还物品失败",
            error_msg=f"物品已归还: {borrowing_id}",
            context="return_item"
        )
        raise HTTPException(status_code=400, detail="物品已归还")
    
    # 更新借用记录
    borrowing.status = "returned"
    borrowing.actual_return_date = datetime.now()
    
    # 恢复库存
    item = db.query(Item).filter(Item.id == borrowing.item_id).first()
    if item:
        item.available_quantity += borrowing.quantity
    
    db.commit()
    db.refresh(borrowing)
    
    # 记录归还操作（所有用户）
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="return_item",
        details=f"借用ID: {borrowing_id}, 物品: {borrowing.item_id}, 数量: {borrowing.quantity}"
    )
    
    return borrowing


# ==================== 系统设置接口 (管理员) ====================

@app.get("/api/settings", response_model=List[SystemSettingResponse])
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings", "read"))
):
    """获取所有系统设置"""
    settings = db.query(SystemSetting).all()
    return settings


@app.put("/api/settings")
async def update_settings(
    setting_data: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings", "update"))
):
    """批量更新系统设置"""
    updated_keys = []
    for key, value in setting_data.settings.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.now()
            updated_keys.append(key)
    db.commit()

    # 将设置应用到日志模块
    settings_dict = {s.key: s.value for s in db.query(SystemSetting).all()}
    apply_settings(settings_dict)
    reload_loggers()

    # 记录操作日志
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_settings",
        details=f"更新系统设置: {', '.join(updated_keys)}"
    )

    return {"message": "设置已更新", "updated_keys": updated_keys}


# ==================== 日志管理接口 (管理员) ====================

import os
from typing import Optional

@app.get("/api/logs")
async def get_logs(
    log_type: str = "action",
    page: int = 0,
    page_size: int = 50,
    keyword: Optional[str] = None,
    current_user: User = Depends(require_permission("logs", "read"))
):
    """获取日志"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return {"logs": [], "total": 0, "page": page, "page_size": page_size}
    
    log_file_map = {
        "action": "action.log",
        "error": "error.log",
    }
    
    if log_type not in log_file_map:
        raise HTTPException(status_code=400, detail="无效的日志类型")
    
    log_file = os.path.join(log_dir, log_file_map[log_type])
    if not os.path.exists(log_file):
        return {"logs": [], "total": 0, "page": page, "page_size": page_size}
    
    # 读取日志文件
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 过滤关键词
        if keyword:
            lines = [line for line in lines if keyword.lower() in line.lower()]
        
        total = len(lines)
        
        # 分页
        start_idx = page * page_size
        end_idx = start_idx + page_size
        paginated_lines = lines[start_idx:end_idx]
        
        return {
            "logs": [line.strip() for line in paginated_lines],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        # 记录错误操作
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="获取日志失败",
            error_msg=str(e),
            context="get_logs"
        )
        raise HTTPException(status_code=500, detail="读取日志文件失败")


@app.get("/api/logs/types")
async def get_log_types(current_user: User = Depends(require_permission("logs", "read"))):
    """获取日志类型列表"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return {"types": []}
    
    available_types = []
    log_files = {
        "action": "action.log",
        "error": "error.log", 
    }
    
    for log_type, filename in log_files.items():
        if os.path.exists(os.path.join(log_dir, filename)):
            available_types.append(log_type)
    
    return {"types": available_types}


@app.delete("/api/logs")
async def delete_logs(
    log_type: str = "action",
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("logs", "delete"))
):
    """按时间段删除日志"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        raise HTTPException(status_code=404, detail="日志目录不存在")

    log_file_map = {
        "action": "action.log",
        "error": "error.log",
    }

    if log_type not in log_file_map:
        raise HTTPException(status_code=400, detail="无效的日志类型")

    log_file = os.path.join(log_dir, log_file_map[log_type])
    if not os.path.exists(log_file):
        return {"message": "没有日志可删除", "deleted_lines": 0}

    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="请提供 start_date 和 end_date 参数")

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        kept_lines = []
        deleted_count = 0

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                kept_lines.append(line)
                continue
            # 尝试从行首解析日期 (YYYY-MM-DD)
            try:
                line_date_str = line_stripped[:10]
                line_date = datetime.strptime(line_date_str, "%Y-%m-%d")
                if start_dt <= line_date <= end_dt:
                    deleted_count += 1
                    continue
            except ValueError:
                pass
            kept_lines.append(line)

        with open(log_file, 'w', encoding='utf-8') as f:
            f.writelines(kept_lines)

        # 记录操作日志
        log_user_action(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            action="delete_logs",
            details=f"日志类型: {log_type}, 时间范围: {start_date} ~ {end_date}, 删除行数: {deleted_count}"
        )

        return {
            "message": f"已删除 {deleted_count} 行日志",
            "deleted_lines": deleted_count
        }
    except Exception as e:
        log_error(
            user_id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or current_user.username,
            error_type="删除日志失败",
            error_msg=str(e),
            context="delete_logs"
        )
        raise HTTPException(status_code=500, detail="删除日志文件失败")


# ==================== 公共接口（无需认证） ====================

@app.get("/api/public/today-bookings")
async def public_today_bookings(db: Session = Depends(get_db)):
    """获取今日未取消的预约（公开接口）"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    query = db.query(Booking).filter(
        Booking.start_time >= today_start,
        Booking.start_time <= today_end,
        Booking.status != "cancelled"
    )

    bookings = query.all()

    result = []
    for booking in bookings:
        user = db.query(User).filter(User.id == booking.user_id).first()
        room = db.query(MeetingRoom).filter(MeetingRoom.id == booking.room_id).first()
        org_name = None
        if user and user.org_id:
            org = db.query(Organization).filter(Organization.id == user.org_id).first()
            if org:
                org_name = org.name

        result.append({
            "id": booking.id,
            "room_id": booking.room_id,
            "user_id": booking.user_id,
            "user_name": user.username if user else None,
            "user_full_name": user.full_name if user else None,
            "user_org_name": org_name,
            "room_name": room.name if room else None,
            "room_location": room.location if room else None,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "purpose": booking.purpose,
            "status": booking.status,
        })

    return result


@app.get("/api/public/rooms")
async def public_rooms(db: Session = Depends(get_db)):
    """获取所有可用会议室（公开接口）"""
    rooms = db.query(MeetingRoom).filter(MeetingRoom.is_active == True).all()
    return [
        {
            "id": room.id,
            "name": room.name,
            "location": room.location,
            "capacity": room.capacity,
            "description": room.description,
        }
        for room in rooms
    ]


@app.get("/api/public/stats")
async def public_stats(db: Session = Depends(get_db)):
    """获取系统统计数据（公开接口）"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    total_rooms = db.query(MeetingRoom).filter(MeetingRoom.is_active == True).count()
    today_bookings = db.query(Booking).filter(
        Booking.start_time >= today_start,
        Booking.start_time <= today_end,
        Booking.status != "cancelled"
    ).count()
    in_use_rooms = db.query(Booking.room_id).filter(
        Booking.start_time <= now,
        Booking.end_time >= now,
        Booking.status != "cancelled"
    ).distinct().count()
    available_rooms = total_rooms - in_use_rooms

    total_items = db.query(func.sum(Item.available_quantity)).filter(Item.is_active == True).scalar() or 0

    return {
        "totalRooms": total_rooms,
        "todayBookings": today_bookings,
        "inUseRooms": in_use_rooms,
        "availableRooms": available_rooms,
        "totalItems": total_items,
    }


@app.get("/api/public/app-config")
async def public_app_config(db: Session = Depends(get_db)):
    """获取前端公开配置（无认证）"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "app_title").first()
    return {"app_title": setting.value if setting else "会议室系统"}


@app.get("/api/public/items")
async def public_items(db: Session = Depends(get_db)):
    """公共接口：获取可借物品列表（无需登录）"""
    items = db.query(Item).filter(Item.is_active == True).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "category": i.category,
            "quantity": i.quantity,
            "available_quantity": i.available_quantity,
            "description": i.description,
        }
        for i in items
    ]


# ==================== 角色管理接口 ====================

@app.get("/api/roles", response_model=List[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("roles", "read"))
):
    """获取角色列表"""
    roles = db.query(Role).offset(skip).limit(limit).all()
    
    result = []
    for role in roles:
        user_count = db.query(User).filter(User.role_id == role.id).count()
        result.append({
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
            "user_count": user_count,
            "created_at": role.created_at
        })
    
    return result


@app.get("/api/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("roles", "read"))
):
    """获取角色详情"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    user_count = db.query(User).filter(User.role_id == role.id).count()
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_active": role.is_active,
        "user_count": user_count,
        "created_at": role.created_at
    }


@app.post("/api/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建角色（仅管理员）"""
    existing = db.query(Role).filter(Role.name == role_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    
    role = Role(name=role_data.name, description=role_data.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="create_role",
        details=f"角色ID: {role.id}, 角色名称: {role.name}"
    )
    
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_active": role.is_active,
        "user_count": 0,
        "created_at": role.created_at
    }


@app.put("/api/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新角色信息（仅管理员）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if role_data.name is not None:
        existing = db.query(Role).filter(Role.name == role_data.name, Role.id != role_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="角色名称已存在")
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    
    db.commit()
    db.refresh(role)
    
    user_count = db.query(User).filter(User.role_id == role.id).count()
    
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_role",
        details=f"角色ID: {role.id}, 角色名称: {role.name}"
    )
    
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_active": role.is_active,
        "user_count": user_count,
        "created_at": role.created_at
    }


@app.delete("/api/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除角色（仅管理员）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if role.name == "超级管理员":
        raise HTTPException(status_code=400, detail="不能删除超级管理员角色")
    
    user_count = db.query(User).filter(User.role_id == role.id).count()
    if user_count > 0:
        raise HTTPException(status_code=400, detail=f"该角色下还有 {user_count} 个用户，无法删除")
    
    db.delete(role)
    db.commit()
    
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="delete_role",
        details=f"角色ID: {role_id}, 角色名称: {role.name}"
    )
    
    return {"message": "角色已删除"}


@app.get("/api/roles/{role_id}/permissions", response_model=List[PermissionResponse])
async def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取角色的权限列表（仅管理员）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    permissions = db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
    return permissions


@app.put("/api/roles/{role_id}/permissions")
async def update_role_permissions(
    role_id: int,
    perm_data: RolePermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """批量更新角色权限（仅管理员）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 删除旧权限
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    
    # 添加新权限
    for p in perm_data.permissions:
        db.add(RolePermission(role_id=role_id, module=p.module, action=p.action))
    
    db.commit()
    
    log_user_action(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or current_user.username,
        action="update_role_permissions",
        details=f"角色ID: {role_id}, 角色名称: {role.name}, 权限数: {len(perm_data.permissions)}"
    )
    
    return {"message": "权限已更新"}


# ==================== 健康检查 ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "会议室预约系统运行中"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)