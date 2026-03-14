"""
Bonel Project - 用户档案路由
包含：获取用户信息、更新用户档案
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
import logging

from bonel.auth.dependencies import get_current_user, get_supabase_service_client
from bonel.models import (
    CurrentUser,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserProfileUpdateResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user: CurrentUser = Depends(get_current_user)
):
    """
    获取当前登录用户的档案信息
    
    用于前端 /user 页面展示
    
    返回:
    - id: 用户ID
    - email: 邮箱
    - nickname: 昵称
    - wechat_contact: 微信号
    - daily_votes_left: 今日剩余票数
    - role: 用户角色
    - created_at: 创建时间
    """
    try:
        # 使用服务角色客户端查询最新数据
        supabase = get_supabase_service_client()
        
        result = supabase.from_("profiles").select("*").eq("id", user.id).single().execute()
        
        if result.data:
            profile = result.data
            return UserProfileResponse(
                id=user.id,
                email=profile.get("email") or user.email,
                nickname=profile.get("nickname"),
                wechat_contact=profile.get("wechat_contact"),
                daily_votes_left=profile.get("daily_votes_left", 5),
                role=profile.get("role", "user"),
                created_at=profile.get("created_at")
            )
        else:
            # 如果数据库中没有，返回当前用户对象的基本信息
            return UserProfileResponse(
                id=user.id,
                email=user.email,
                nickname=user.nickname,
                wechat_contact=user.wechat_contact,
                daily_votes_left=user.daily_votes_left,
                role=user.role.value,
                created_at=None
            )
            
    except Exception as e:
        logger.error(f"获取用户档案失败: {e}")
        # 即使查询失败，也返回当前用户对象，保证接口可用
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            wechat_contact=user.wechat_contact,
            daily_votes_left=user.daily_votes_left,
            role=user.role.value,
            created_at=None
        )


@router.put("/profile", response_model=UserProfileUpdateResponse)
async def update_user_profile(
    request: UserProfileUpdateRequest,
    user: CurrentUser = Depends(get_current_user)
):
    """
    更新当前登录用户的档案信息
    
    允许更新的字段:
    - nickname: 昵称/研究员代号
    - wechat_contact: 微信号（用于接收奖金）
    
    注意:
    - 不能修改 role（角色）
    - 不能修改 daily_votes_left（票数）
    - 不能修改 id、email 等系统字段
    """
    try:
        # 构建更新数据
        update_data = {}
        
        if request.nickname is not None:
            update_data["nickname"] = request.nickname.strip() or None
        
        if request.wechat_contact is not None:
            update_data["wechat_contact"] = request.wechat_contact.strip() or None
        
        # 如果没有要更新的字段
        if not update_data:
            return UserProfileUpdateResponse(
                success=False,
                message="没有提供要更新的字段"
            )
        
        # 添加更新时间
        update_data["updated_at"] = "now()"
        
        # 使用服务角色客户端更新
        supabase = get_supabase_service_client()
        
        result = supabase.from_("profiles").update(update_data).eq("id", user.id).execute()
        
        if result.data:
            # 更新成功，返回更新后的数据
            profile = result.data[0]
            return UserProfileUpdateResponse(
                success=True,
                message="档案更新成功",
                data=UserProfileResponse(
                    id=user.id,
                    email=profile.get("email") or user.email,
                    nickname=profile.get("nickname"),
                    wechat_contact=profile.get("wechat_contact"),
                    daily_votes_left=profile.get("daily_votes_left", 5),
                    role=profile.get("role", "user"),
                    created_at=profile.get("created_at")
                )
            )
        else:
            # 可能是新用户，档案还不存在，尝试创建
            logger.info(f"用户 {user.id} 档案不存在，尝试创建")
            
            insert_data = {
                "id": user.id,
                "email": user.email,
                "nickname": request.nickname.strip() if request.nickname else None,
                "wechat_contact": request.wechat_contact.strip() if request.wechat_contact else None,
                "daily_votes_left": 5,
                "role": "user"
            }
            
            insert_result = supabase.from_("profiles").insert(insert_data).execute()
            
            if insert_result.data:
                profile = insert_result.data[0]
                return UserProfileUpdateResponse(
                    success=True,
                    message="档案创建成功",
                    data=UserProfileResponse(
                        id=user.id,
                        email=profile.get("email"),
                        nickname=profile.get("nickname"),
                        wechat_contact=profile.get("wechat_contact"),
                        daily_votes_left=profile.get("daily_votes_left", 5),
                        role=profile.get("role", "user"),
                        created_at=profile.get("created_at")
                    )
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="档案创建失败"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户档案失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )
