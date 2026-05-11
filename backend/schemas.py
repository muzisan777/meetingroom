"""
Pydantic 请求/响应模型
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ==================== 认证相关 ====================

class Token(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user: dict


class PasswordChange(BaseModel):
    """密码修改请求"""
    old_password: str
    new_password: str


# ==================== 用户相关 ====================

class UserCreate(BaseModel):
    """用户创建请求"""
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    org_id: Optional[int] = None
    role_id: Optional[int] = None
    is_admin: Optional[bool] = False
    is_active: Optional[bool] = True


class UserUpdate(BaseModel):
    """用户更新请求"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    org_id: Optional[int] = None
    role_id: Optional[int] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    phone: Optional[str]
    org_id: Optional[int]
    org_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    role_name: Optional[str] = None
    permissions: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True


# ==================== 组织相关 ====================

class OrganizationCreate(BaseModel):
    """组织创建请求"""
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """组织更新请求"""
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(BaseModel):
    """组织响应"""
    id: int
    name: str
    parent_id: Optional[int]
    parent_name: Optional[str] = None
    description: Optional[str]
    is_active: bool
    user_count: int = 0
    
    class Config:
        from_attributes = True


# ==================== 会议室相关 ====================

class MeetingRoomCreate(BaseModel):
    """会议室创建请求"""
    name: str
    capacity: int = 10
    location: Optional[str] = None
    facilities: Optional[str] = None
    description: Optional[str] = None


class MeetingRoomUpdate(BaseModel):
    """会议室更新请求"""
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    facilities: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MeetingRoomResponse(BaseModel):
    """会议室响应"""
    id: int
    name: str
    capacity: int
    location: Optional[str]
    facilities: Optional[str]
    description: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


# ==================== 预约相关 ====================

class BookingCreate(BaseModel):
    """预约创建请求"""
    room_id: int
    start_time: datetime
    end_time: datetime
    purpose: str
    
    class Config:
        from_attributes = True


class BookingUpdate(BaseModel):
    """预约更新请求"""
    status: Optional[str] = None
    purpose: Optional[str] = None


class BookingResponse(BaseModel):
    """预约响应"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_org_name: Optional[str] = None
    room_id: int
    room_name: Optional[str] = None
    start_time: datetime
    end_time: datetime
    purpose: str
    status: str
    org_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 物品相关 ====================

class ItemCreate(BaseModel):
    """物品创建请求"""
    name: str
    category: Optional[str] = None
    quantity: int = 1
    description: Optional[str] = None


class ItemUpdate(BaseModel):
    """物品更新请求"""
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ItemResponse(BaseModel):
    """物品响应"""
    id: int
    name: str
    category: Optional[str]
    quantity: int
    available_quantity: int
    description: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


# ==================== 借用相关 ====================

class BorrowingCreate(BaseModel):
    """借用创建请求"""
    item_id: int
    quantity: int = 1
    return_date: Optional[datetime] = None
    notes: Optional[str] = None


class BorrowingUpdate(BaseModel):
    """借用更新请求"""
    return_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class BorrowingResponse(BaseModel):
    """借用响应"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_org_name: Optional[str] = None
    item_id: int
    item_name: Optional[str] = None
    quantity: int
    borrow_date: datetime
    return_date: Optional[datetime]
    actual_return_date: Optional[datetime]
    status: str
    notes: Optional[str]
    org_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# ==================== 角色权限相关 ====================

class RoleCreate(BaseModel):
    """角色创建请求"""
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    """角色更新请求"""
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    user_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class PermissionCreate(BaseModel):
    """权限创建请求"""
    module: str
    action: str


class PermissionResponse(BaseModel):
    """权限响应"""
    id: int
    role_id: int
    module: str
    action: str
    
    class Config:
        from_attributes = True


class RolePermissionsUpdate(BaseModel):
    """角色权限批量更新请求"""
    permissions: List[PermissionCreate]