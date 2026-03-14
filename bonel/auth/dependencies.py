"""
Bonel Project - FastAPI 鉴权依赖
包含：JWT Token 验证、用户权限检查、角色分级校验
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from typing import Optional
import jwt
import logging

from bonel.config import settings
from bonel.models import CurrentUser, UserRole

logger = logging.getLogger(__name__)

# HTTP Bearer 认证方案
oauth2_scheme = HTTPBearer(auto_error=False)

# ==================== Supabase 客户端（服务角色）====================

_supabase_service_client: Optional[Client] = None

def get_supabase_service_client() -> Client:
    """
    获取具有服务角色权限的 Supabase 客户端
    用于后端管理员操作，可以绕过 RLS
    ⚠️ 严禁将此客户端暴露给前端
    """
    global _supabase_service_client
    
    if _supabase_service_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase 服务角色配置缺失"
            )
        
        _supabase_service_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY  # 使用服务角色密钥
        )
    
    return _supabase_service_client


# ==================== JWT Token 验证 ====================

def verify_jwt_token(token: str) -> Optional[dict]:
    """
    验证 JWT Token 并返回 payload
    
    Args:
        token: 前端传来的 JWT Token
        
    Returns:
        解码后的 payload，验证失败返回 None
    """
    if not settings.SUPABASE_JWT_SECRET:
        logger.error("SUPABASE_JWT_SECRET 未配置")
        return None
    
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token 已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token 验证失败: {e}")
        return None


# ==================== 基础鉴权依赖 ====================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme)
) -> CurrentUser:
    """
    获取当前登录用户
    
    使用方式:
        @router.get("/profile")
        async def get_profile(user: CurrentUser = Depends(get_current_user)):
            return {"user_id": user.id, "role": user.role}
    
    流程:
    1. 从 Header 中提取 Bearer Token
    2. 使用 JWT_SECRET 验证 Token
    3. 从 payload 中提取 user_id (sub)
    4. 查询数据库获取完整用户信息
    5. 返回 CurrentUser 对象
    """
    # 检查是否提供了 Token
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # 验证 Token
    payload = verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户 ID
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 格式错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 使用服务角色客户端查询用户信息
    try:
        supabase = get_supabase_service_client()
        
        # 查询 profiles 表
        result = supabase.from_("profiles").select("*").eq("id", user_id).single().execute()
        
        if not result.data:
            # 用户不存在，可能是刚注册还没触发器创建档案
            # 返回基本信息
            return CurrentUser(
                id=user_id,
                email=payload.get("email"),
                role=UserRole.USER,
                daily_votes_left=5,
                is_authenticated=True
            )
        
        profile = result.data
        
        # 构建 CurrentUser 对象
        return CurrentUser(
            id=user_id,
            email=profile.get("email") or payload.get("email"),
            nickname=profile.get("nickname"),
            wechat_contact=profile.get("wechat_contact"),
            daily_votes_left=profile.get("daily_votes_left", 5),
            role=UserRole(profile.get("role", "user")),
            is_authenticated=True
        )
        
    except Exception as e:
        logger.error(f"查询用户信息失败: {e}")
        # 即使查询失败，也返回基本信息，保证接口可用
        return CurrentUser(
            id=user_id,
            email=payload.get("email"),
            role=UserRole.USER,
            daily_votes_left=5,
            is_authenticated=True
        )


# ==================== 角色权限校验依赖 ====================

async def require_vip(
    user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    要求 VIP 或更高级别权限
    
    使用方式:
        @router.get("/vip-only")
        async def vip_endpoint(user: CurrentUser = Depends(require_vip)):
            # 只有 VIP、admin、super_admin 能访问
            pass
    """
    if not user.is_vip_or_above():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要 VIP 或更高级别权限"
        )
    return user


async def require_admin(
    user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    要求管理员或更高级别权限
    
    使用方式:
        @router.post("/admin-action")
        async def admin_endpoint(user: CurrentUser = Depends(require_admin)):
            # 只有 admin、super_admin 能访问
            pass
    """
    if not user.is_admin_or_above():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return user


async def require_super_admin(
    user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    要求超级管理员权限
    
    使用方式:
        @router.post("/super-admin-action")
        async def super_admin_endpoint(user: CurrentUser = Depends(require_super_admin)):
            # 只有 super_admin 能访问
            # 用于封号、发版等最高权限操作
            pass
    """
    if not user.is_super_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    return user


# ==================== 可选鉴权依赖 ====================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme)
) -> Optional[CurrentUser]:
    """
    获取当前用户（可选，不强制登录）
    
    使用方式:
        @router.get("/public-data")
        async def public_data(user: Optional[CurrentUser] = Depends(get_current_user_optional)):
            if user:
                # 用户已登录，返回个性化数据
                pass
            else:
                # 用户未登录，返回默认数据
                pass
    """
    if not credentials or not credentials.credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
