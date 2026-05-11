"""
SQLAlchemy 数据模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    organization = relationship("Organization", back_populates="users")
    role = relationship("Role", back_populates="users")
    bookings = relationship("Booking", back_populates="user")
    borrowings = relationship("Borrowing", back_populates="user")


class Organization(Base):
    """组织/部门模型"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    parent = relationship("Organization", remote_side=[id], backref="children")
    users = relationship("User", back_populates="organization")


class MeetingRoom(Base):
    """会议室模型"""
    __tablename__ = "meeting_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    capacity = Column(Integer, default=10)
    location = Column(String(200))
    facilities = Column(Text)  # 设施，JSON 格式
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    bookings = relationship("Booking", back_populates="room")


class Booking(Base):
    """预约记录模型"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("meeting_rooms.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    purpose = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")  # pending, confirmed, cancelled, completed
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="bookings")
    room = relationship("MeetingRoom", back_populates="bookings")


class Item(Base):
    """物品模型"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    quantity = Column(Integer, default=1)
    available_quantity = Column(Integer, default=1)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    borrowings = relationship("Borrowing", back_populates="item")


class Borrowing(Base):
    """借用记录模型"""
    __tablename__ = "borrowings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    borrow_date = Column(DateTime, default=datetime.now)
    return_date = Column(DateTime)
    actual_return_date = Column(DateTime)
    status = Column(String(20), default="borrowed")  # borrowed, returned, overdue
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="borrowings")
    item = relationship("Item", back_populates="borrowings")


class Role(Base):
    """角色模型"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


class RolePermission(Base):
    """角色权限模型"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    module = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)
    
    # 关系
    role = relationship("Role", back_populates="permissions")