"""
Bonel Project - API 路由
包含: /health, /stats, /votes/status, /leaderboard
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional
import logging

from bonel.auth.dependencies import get_current_user
from bonel.database import db
from datetime import datetime

def get_today_date() -> str:
    """获取今天的日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")

from bonel.models import (
    HealthResponse,
    StatsResponse,
    VoteStatusResponse,
    LeaderboardResponse,
    LeaderboardItem,
    Paper,
    NomineeStatus,
    CurrentUser,
)
from bonel.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 1. 健康检查 ====================

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    健康检查端点
    用于服务器监控和前端探测网络状态
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


# ==================== 2. 平台统计 ====================

@router.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats():
    """
    获取平台全局统计数据
    
    返回:
    - total_nominees: 总候选人数
    - total_votes: 全站累计投票数
    - total_users: 总用户数
    - today_votes: 今日投票数 (MVP 阶段简化)
    """
    try:
        stats = await db.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


# ==================== 3. 投票状态查询 ====================

@router.get("/votes/status", response_model=VoteStatusResponse, tags=["Votes"])
async def get_vote_status(user: CurrentUser = Depends(get_current_user)):
    """
    查询用户今日投票状态
    
    需要登录 (JWT Token)
    
    业务逻辑:
    1. 解析 JWT Token 获取 user_id
    2. 检查 last_active_date，如果早于今天则重置 daily_votes_left = 5
    3. 返回剩余票数和分享状态
    
    返回:
    - daily_votes_left: 今日剩余票数
    - has_shared_today: 今日是否已分享
    - last_active_date: 最后活跃日期
    """
    try:
        # 获取或创建用户 (会自动处理跨天重置)
        user_data = await db.get_or_create_user(user.id or "", user.email or "")
        
        return VoteStatusResponse(
            daily_votes_left=user_data.get("daily_votes_left", settings.DEFAULT_DAILY_VOTES),
            has_shared_today=user_data.get("has_shared_today", False),
            last_active_date=user_data.get("last_active_date", get_today_date())
        )
        
    except Exception as e:
        logger.error(f"获取投票状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取投票状态失败: {str(e)}"
        )


# ==================== 4. 排行榜 ====================

@router.get("/leaderboard", response_model=LeaderboardResponse, tags=["Leaderboard"])
async def get_leaderboard(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE, description="每页数量"),
    user: CurrentUser = Depends(get_current_user)
):
    """
    获取排行榜 (热度榜单)
    
    查询所有通过审核的候选人，按 total_votes 倒序排列
    
    参数:
    - page: 页码 (默认1)
    - page_size: 每页数量 (默认20，最大100)
    
    返回:
    - items: 排行榜条目列表 (包含排名)
    - total: 总数量
    - page: 当前页码
    - page_size: 每页数量
    """
    try:
        # 获取候选人列表
        nominees, total = await db.get_nominees(
            status=NomineeStatus.APPROVED.value,
            sort_by="hot",
            page=page,
            page_size=page_size
        )
        
        # 构建排行榜条目
        items = []
        offset = (page - 1) * page_size
        
        for idx, nominee in enumerate(nominees):
            # 如果用户已登录，查询用户对该候选人的投票数
            user_votes = 0
            if user.is_authenticated and user.id:
                user_votes = await db.get_user_votes_for_nominee(
                    user.id, nominee["id"]
                )

            # 转换为前端格式
            paper = Paper(
                id=nominee["id"],
                title=nominee["title"],
                author=nominee["author"],
                abstract=nominee.get("abstract", ""),
                totalVotes=nominee.get("total_votes", 0),
                userVotes=user_votes,
                date=nominee.get("created_at", datetime.now().isoformat())
            )

            items.append(LeaderboardItem(
                rank=offset + idx + 1,
                paper=paper
            ))
        
        return LeaderboardResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"获取排行榜失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取排行榜失败: {str(e)}"
        )


# ==================== 额外的辅助接口 ====================

@router.get("/papers", tags=["Papers"])
async def get_papers(
    sort: str = Query("hot", regex="^(hot|new)$", description="排序方式: hot/new"),
    page: int = Query(1, ge=1, description="页码"),
    search: str = Query("", description="搜索关键词"),
    user: CurrentUser = Depends(get_current_user)
):
    """
    获取文章列表 (兼容前端接口)
    
    与 /leaderboard 类似，但返回格式与前端 api.ts 中的 PapersResponse 一致
    """
    try:
        # 获取用户状态
        user_status = {
            "is_logged_in": user.is_authenticated,
            "votes_left": 0,
            "has_shared_today": False
        }
        
        if user.is_authenticated and user.id:
            user_data = await db.get_or_create_user(user.id, user.email or "")
            user_status["votes_left"] = user_data.get("daily_votes_left", 0)
            user_status["has_shared_today"] = user_data.get("has_shared_today", False)

        # 获取文章列表
        nominees, total = await db.get_nominees(
            status=NomineeStatus.APPROVED.value,
            sort_by=sort,
            page=page,
            page_size=settings.DEFAULT_PAGE_SIZE,
            search=search
        )

        # 转换为前端格式
        papers = []
        for nominee in nominees:
            user_votes = 0
            if user.is_authenticated and user.id:
                user_votes = await db.get_user_votes_for_nominee(
                    user.id, nominee["id"]
                )
            
            papers.append({
                "id": nominee["id"],
                "title": nominee["title"],
                "author": nominee["author"],
                "abstract": nominee.get("abstract", ""),
                "totalVotes": nominee.get("total_votes", 0),
                "userVotes": user_votes,
                "date": nominee.get("created_at", datetime.now().isoformat())
            })
        
        return {
            "user_status": user_status,
            "papers": papers,
            "total": total,
            "page": page,
            "page_size": settings.DEFAULT_PAGE_SIZE
        }
        
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文章列表失败: {str(e)}"
        )
