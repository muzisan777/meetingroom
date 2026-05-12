import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 默认配置（会被数据库中的设置覆盖）
LOG_DIR = "logs"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 10
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(levelname)s - [用户 ID:%(user_id)s | 用户名:%(username)s | 姓名:%(full_name)s] - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 当前生效的配置缓存（避免每次日志都查 DB）
_current_config = {
    "max_bytes": DEFAULT_MAX_BYTES,
    "backup_count": DEFAULT_BACKUP_COUNT,
    "log_level": DEFAULT_LOG_LEVEL,
    "log_format": DEFAULT_LOG_FORMAT,
    "date_format": DEFAULT_DATE_FORMAT,
    "enabled_actions": None,  # None = 全部记录
}

# 所有可记录的操作类型定义
ALL_ACTION_TYPES = {
    "login": "用户登录",
    "register": "用户注册",
    "change_password": "修改密码",
    "create_organization": "创建组织",
    "update_organization": "更新组织",
    "delete_organization": "删除组织",
    "create_user": "创建用户",
    "update_user": "更新用户",
    "delete_user": "删除用户",
    "create_room": "创建会议室",
    "update_room": "更新会议室",
    "delete_room": "删除会议室",
    "create_booking": "创建预约",
    "update_booking": "更新预约",
    "cancel_booking": "取消预约",
    "create_item": "创建物品",
    "update_item": "更新物品",
    "delete_item": "删除物品",
    "create_borrowing": "创建借用",
    "return_item": "归还物品",
    "create_role": "创建角色",
    "update_role": "更新角色",
    "delete_role": "删除角色",
    "update_role_permissions": "更新角色权限",
    "update_settings": "更新系统设置",
    "delete_logs": "删除日志",
}


def is_action_enabled(action):
    """检查指定操作是否启用日志记录"""
    enabled = _current_config.get("enabled_actions")
    if enabled is None:
        return True
    return action in enabled


def get_log_settings_from_db():
    """从数据库读取日志配置（由 main.py 启动时调用）"""
    try:
        from database import SessionLocal
        from models import SystemSetting
        db = SessionLocal()
        try:
            settings = {s.key: s.value for s in db.query(SystemSetting).all()}
            return settings
        finally:
            db.close()
    except Exception:
        return {}


def apply_settings(settings):
    """从设置字典更新日志配置"""
    if "log_max_bytes" in settings:
        try:
            _current_config["max_bytes"] = int(settings["log_max_bytes"])
        except ValueError:
            pass
    if "log_backup_count" in settings:
        try:
            _current_config["backup_count"] = int(settings["log_backup_count"])
        except ValueError:
            pass
    if "log_level" in settings:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        _current_config["log_level"] = level_map.get(settings["log_level"].upper(), logging.INFO)
    if "log_date_format" in settings and settings["log_date_format"]:
        _current_config["date_format"] = settings["log_date_format"]
    if "enabled_log_actions" in settings:
        val = settings["enabled_log_actions"]
        if val == "*" or not val:
            _current_config["enabled_actions"] = None
        else:
            _current_config["enabled_actions"] = [a.strip() for a in val.split(",") if a.strip()]


def setup_logger(name, log_file, level=None):
    """设置日志记录器（使用当前配置）"""
    level = level or _current_config["log_level"]
    fmt_str = _current_config["log_format"]
    date_fmt = _current_config["date_format"]
    max_bytes = _current_config["max_bytes"]
    backup_count = _current_config["backup_count"]

    formatter = logging.Formatter(fmt_str, datefmt=date_fmt)

    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # 清除已有 handler 避免重复
    logger.handlers.clear()
    logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 创建日志记录器
action_logger = setup_logger('action', 'action.log')
error_logger = setup_logger('error', 'error.log', level=logging.ERROR)


def reload_loggers():
    """重新加载日志记录器（配置变更后调用）"""
    global action_logger, error_logger
    action_logger = setup_logger('action', 'action.log')
    error_logger = setup_logger('error', 'error.log', level=logging.ERROR)


class LogContextFilter(logging.Filter):
    def __init__(self, user_id=None, username=None, full_name=None):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.full_name = full_name

    def filter(self, record):
        record.user_id = self.user_id or 'anonymous'
        record.username = self.username or 'anonymous'
        record.full_name = self.full_name or 'anonymous'
        return True


def log_user_action(user_id, username, full_name, action, details=None, ip_address=None):
    """记录用户操作（自动过滤未启用的操作类型）"""
    if not is_action_enabled(action):
        return

    extra = {
        'user_id': user_id,
        'username': username,
        'full_name': full_name,
    }

    action_label = ALL_ACTION_TYPES.get(action, action)
    log_msg = f"Action: {action_label}"
    if details:
        log_msg += f" | Details: {details}"
    if ip_address:
        log_msg += f" | IP: {ip_address}"

    action_logger.info(log_msg, extra=extra)


def log_user_login(user_id, username, full_name, success, ip_address=None, reason=None):
    """记录用户登录（受 login 操作类型开关控制）"""
    if not is_action_enabled("login"):
        return

    extra = {
        'user_id': user_id,
        'username': username,
        'full_name': full_name,
    }

    status = "SUCCESS" if success else "FAILED"
    log_msg = f"Login {status}"
    if ip_address:
        log_msg += f" | IP: {ip_address}"
    if reason:
        log_msg += f" | Reason: {reason}"

    if success:
        action_logger.info(log_msg, extra=extra)
    else:
        error_logger.warning(log_msg, extra=extra)


def log_error(user_id, username, full_name, error_type, error_msg, traceback=None, context=None):
    """记录错误信息"""
    extra = {
        'user_id': user_id or 'system',
        'username': username or 'system',
        'full_name': full_name or 'system',
    }

    log_msg = f"Error: {error_type} | {error_msg}"
    if context:
        log_msg += f" | Context: {context}"
    if traceback:
        log_msg += f"\nTraceback: {traceback}"

    error_logger.error(log_msg, extra=extra)


from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import jwt
from jwt.exceptions import PyJWTError


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """API 请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        user_id = None
        username = None
        full_name = None

        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    user_id = decoded.get("sub")
                    username = decoded.get("username")
                    full_name = decoded.get("full_name")
                except PyJWTError:
                    pass
        except Exception:
            pass

        client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)

            if response.status_code >= 400:
                duration_ms = int((time.time() - start_time) * 1000)
                log_error(
                    user_id=user_id,
                    username=username,
                    full_name=full_name,
                    error_type=f"HTTP {response.status_code}",
                    error_msg=f"{request.method} {request.url.path}",
                    context=f"Duration: {duration_ms}ms"
                )

            return response
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log_error(
                user_id=user_id,
                username=username,
                full_name=full_name,
                error_type=type(e).__name__,
                error_msg=str(e),
                context=f"{request.method} {request.url.path}"
            )
            raise
