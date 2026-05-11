"""
权限检查模块
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, RolePermission
from auth import get_current_user

# 定义系统中所有模块和可用操作
MODULE_ACTIONS = {
    "users": ["create", "read", "update", "delete"],
    "organizations": ["create", "read", "update", "delete"],
    "rooms": ["create", "read", "update", "delete"],
    "bookings": ["create", "read", "update", "delete"],
    "items": ["create", "read", "update", "delete"],
    "borrowings": ["create", "read", "update", "delete"],
    "logs": ["read"],
    "roles": ["read"],
}


def check_user_permission(db: Session, user: User, module: str, action: str) -> bool:
    """检查用户是否有指定模块的指定操作权限"""
    # 超管拥有全部权限
    if user.is_admin:
        return True

    # 验证模块和操作是否合法
    if module not in MODULE_ACTIONS:
        return False
    if action not in MODULE_ACTIONS[module]:
        return False

    # 没有角色 → 无权限
    if not user.role_id:
        return False

    # 查询角色权限
    perm = db.query(RolePermission).filter(
        RolePermission.role_id == user.role_id,
        RolePermission.module == module,
        RolePermission.action == action
    ).first()

    return perm is not None


def require_permission(module: str, action: str):
    """
    FastAPI 依赖项工厂：生成权限检查依赖
    
    用法:
        @app.get("/api/users")
        async def list_users(
            current_user: User = Depends(require_permission("users", "read"))
        ):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not check_user_permission(db, current_user, module, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有 '{module}:{action}' 权限"
            )
        return current_user

    return permission_checker