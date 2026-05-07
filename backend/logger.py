import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 创建日志目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志配置
def setup_logger(name, log_file, level=logging.INFO):
    """设置日志记录器"""
    
    # 创建 formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [用户 ID:%(user_id)s | 用户名:%(username)s | 姓名:%(full_name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建 handler - 按大小轮转，每个文件最大 10MB，保留 10 个文件
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        maxBytes=10*1024*1024,
        backupCount=10,
        encoding='utf-8'
    )
    handler.setFormatter(formatter)
    
    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    # 同时输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# 创建操作日志记录器
action_logger = setup_logger('action', 'action.log')

# 创建错误日志记录器
error_logger = setup_logger('error', 'error.log', level=logging.ERROR)


class LogContextFilter(logging.Filter):
    """日志上下文过滤器，添加用户信息"""
    
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
    """记录用户操作"""
    extra = {
        'user_id': user_id,
        'username': username,
        'full_name': full_name
    }
    
    log_msg = f"Action: {action}"
    if details:
        log_msg += f" | Details: {details}"
    if ip_address:
        log_msg += f" | IP: {ip_address}"
    
    action_logger.info(log_msg, extra=extra)


def log_user_login(user_id, username, full_name, success, ip_address=None, reason=None):
    """记录用户登录"""
    extra = {
        'user_id': user_id,
        'username': username,
        'full_name': full_name
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
        'full_name': full_name or 'system'
    }
    
    log_msg = f"Error: {error_type} | {error_msg}"
    if context:
        log_msg += f" | Context: {context}"
    if traceback:
        log_msg += f"\nTraceback: {traceback}"
    
    error_logger.error(log_msg, extra=extra)


# 中间件：记录所有 API 请求
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import jwt
from jwt.exceptions import PyJWTError

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """API 请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录开始时间
        start_time = time.time()
        
        # 尝试获取用户信息
        user_id = None
        username = None
        full_name = None
        
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                # 解码 token 获取用户信息（不验证，只读取）
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    user_id = decoded.get("sub")
                    username = decoded.get("username")
                    full_name = decoded.get("full_name")
                except PyJWTError:
                    pass
        except Exception:
            pass
        
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 仅记录错误请求
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
            # 记录错误
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



