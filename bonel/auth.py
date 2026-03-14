"""
Bonel Project - Supabase 鉴权依赖
解析前端传来的 JWT Token，获取用户身份
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from typing import Optional
from datetime import datetime
import logging

from bonel.config import settings

logger = logging.getLogger(__name__)

# 安全方案
security = HTTPBearer(auto_error=False)

# Supabase 客户端 (用于验证 JWT)
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """获取 Supabase 客户端 (单例)"""
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase 配置缺失"
            )
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    return _supabase_client


class UserAuth:
    """用户认证信息"""
    def __init__(
        self,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        is_authenticated: bool = False,
        token: Optional[str] = None
    ):
        self.user_id = user_id
        self.email = email
        self.is_authenticated = is_authenticated
        self.token = token
    
    def __repr__(self):
        return f"UserAuth(user_id={self.user_id}, is_authenticated={self.is_authenticated})"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserAuth:
    """
    解析 JWT Token，获取当前用户
    
    使用方式:
        @router.get("/protected")
        async def protected_route(user: UserAuth = Depends(get_current_user)):
            if not user.is_authenticated:
                raise HTTPException(status_code=401, detail="未登录")
            return {"user_id": user.user_id}
    
    返回:
        UserAuth: 包含 user_id, email, is_authenticated 等信息
        如果未提供 Token，返回 is_authenticated=False 的匿名用户
    """
    # 如果没有提供 Token，返回匿名用户
    if credentials is None:
        return UserAuth(is_authenticated=False)
    
    token = credentials.credentials
    
    # 验证 Token 格式
    if not token or token == "null" or token == "undefined":
        return UserAuth(is_authenticated=False)
    
    try:
        # 使用 Supabase 验证 JWT Token
        supabase = get_supabase_client()
        
        # 设置 session
        supabase.auth.set_session(token, "")
        
        # 获取用户信息
        user_response = supabase.auth.get_user()
        
        if user_response and user_response.user:
            user = user_response.user
            return UserAuth(
                user_id=user.id,
                email=user.email,
                is_authenticated=True,
                token=token
            )
        else:
            # Token 无效
            return UserAuth(is_authenticated=False)
            
    except Exception as e:
        logger.warning(f"Token 验证失败: {e}")
        # Token 验证失败，返回匿名用户
        return UserAuth(is_authenticated=False)


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserAuth:
    """
    要求必须登录的依赖
    
    使用方式:
        @router.post("/vote")
        async def vote(user: UserAuth = Depends(require_auth)):
            # 这里一定能拿到 user.user_id
            pass
    
    如果未登录，会抛出 401 错误
    """
    user = await get_current_user(credentials)
    
    if not user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ==================== 辅助函数 ====================

def get_today_date() -> str:
    """获取今天的日期字符串 (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")


def is_same_day(date1: str, date2: str) -> bool:
    """判断两个日期是否是同一天"""
    return date1 == date2
