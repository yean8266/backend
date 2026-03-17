# -*- coding: utf-8 -*-
"""
Bonel Project Backend - 登录限制版
FastAPI + Supabase + JWT Auth
"""
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(title="Bonel Project API", version="1.1.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Supabase
supabase: Optional[Client] = None
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase connected")
    else:
        print("⚠️ Supabase not configured")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")

# ========== 认证相关 ==========

async def get_current_user(request: Request) -> Optional[dict]:
    """验证 JWT Token 获取当前用户"""
    if not supabase:
        return None
    
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    
    try:
        # 验证 Token
        user = supabase.auth.get_user(token)
        return user.user if user else None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

async def require_auth(request: Request) -> dict:
    """要求必须登录，否则抛出 401"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return user

async def get_or_create_profile(user_id: str):
    """获取或创建用户档案"""
    if not supabase:
        return None
    
    try:
        # 查询用户档案
        result = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        
        if result.data:
            profile = result.data
            # 检查是否需要重置每日投票
            last_date = profile.get("last_active_date")
            today = date.today().isoformat()
            
            if last_date != today:
                # 重置投票数
                supabase.table("profiles").update({
                    "daily_votes_left": 5,
                    "has_shared_today": False,
                    "last_active_date": today
                }).eq("id", user_id).execute()
                profile["daily_votes_left"] = 5
                profile["has_shared_today"] = False
            
            return profile
        else:
            # 创建新档案
            new_profile = {
                "id": user_id,
                "wechat_contact": "",
                "daily_votes_left": 5,
                "has_shared_today": False,
                "last_active_date": date.today().isoformat()
            }
            supabase.table("profiles").insert(new_profile).execute()
            return new_profile
    except Exception as e:
        print(f"Profile error: {e}")
        return None

# ========== API 路由 ==========

@app.get("/")
def root():
    return {"message": "Bonel Project API", "status": "running", "auth": "required for write ops"}

@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "database": "connected" if supabase else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/nominees")
async def get_papers(
    request: Request,
    sort: str = "hot",
    page: int = 1,
    search: Optional[str] = None
):
    """获取论文列表（公开访问）"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 获取当前用户（可选）
    user = await get_current_user(request)
    user_id = user.id if user else None
    
    try:
        query = supabase.table("submissions").select("*").eq("status", "approved")
        
        if search:
            query = query.or_(f"title.ilike.%{search}%,abstract.ilike.%{search}%")
        
        if sort == "hot":
            query = query.order("total_votes", desc=True)
        else:
            query = query.order("created_at", desc=True)
        
        page_size = 20
        start = (page - 1) * page_size
        result = query.range(start, start + page_size - 1).execute()
        
        # 获取用户投票情况
        user_votes = {}
        if user_id:
            vote_result = supabase.table("vote_logs").select("submission_id, vote_count").eq("user_id", user_id).execute()
            user_votes = {v["submission_id"]: v["vote_count"] for v in vote_result.data}
        
        # 获取用户档案
        user_status = {"isLoggedIn": False, "votesLeft": 5, "hasSharedToday": False}
        if user_id:
            profile = await get_or_create_profile(user_id)
            if profile:
                user_status = {
                    "isLoggedIn": True,
                    "votesLeft": profile.get("daily_votes_left", 5),
                    "hasSharedToday": profile.get("has_shared_today", False)
                }
        
        papers = []
        for item in result.data:
            papers.append({
                "id": str(item["id"]),
                "title": item["title"],
                "author": "匿名",
                "abstract": item.get("abstract", ""),
                "totalVotes": item.get("total_votes", 0),
                "userVotes": user_votes.get(item["id"], 0),
                "date": item["created_at"][:10] if item.get("created_at") else "2024-01-01"
            })
        
        return {
            "papers": papers,
            "total": len(papers),
            "page": page,
            "pageSize": page_size,
            "userStatus": user_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vote")
async def vote(request: Request, data: dict):
    """投票（需要登录）"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证登录
    user = await require_auth(request)
    
    paper_id = data.get("paperId")
    if not paper_id:
        raise HTTPException(status_code=400, detail="Missing paperId")
    
    try:
        # 获取用户档案
        profile = await get_or_create_profile(user.id)
        if not profile:
            raise HTTPException(status_code=500, detail="Failed to get profile")
        
        votes_left = profile.get("daily_votes_left", 0)
        if votes_left <= 0:
            raise HTTPException(status_code=400, detail="今日投票次数已用完")
        
        # 获取论文当前票数
        result = supabase.table("submissions").select("total_votes").eq("id", paper_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        new_total = result.data.get("total_votes", 0) + 1
        
        # 更新论文票数
        supabase.table("submissions").update({
            "total_votes": new_total,
            "updated_at": datetime.now().isoformat()
        }).eq("id", paper_id).execute()
        
        # 记录用户投票
        existing = supabase.table("vote_logs").select("*").eq("user_id", user.id).eq("submission_id", paper_id).execute()
        if existing.data:
            # 更新投票数
            current = existing.data[0].get("vote_count", 0)
            supabase.table("vote_logs").update({
                "vote_count": current + 1,
                "updated_at": datetime.now().isoformat()
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # 创建新记录
            supabase.table("vote_logs").insert({
                "user_id": user.id,
                "submission_id": paper_id,
                "vote_count": 1
            }).execute()
        
        # 减少用户剩余票数
        new_votes_left = votes_left - 1
        supabase.table("profiles").update({
            "daily_votes_left": new_votes_left
        }).eq("id", user.id).execute()
        
        return {"success": True, "totalVotes": new_total, "votesLeft": new_votes_left}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error voting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/unvote")
async def unvote(request: Request, data: dict):
    """撤票（需要登录）"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证登录
    user = await require_auth(request)
    
    paper_id = data.get("paperId")
    if not paper_id:
        raise HTTPException(status_code=400, detail="Missing paperId")
    
    try:
        # 检查用户是否投过票
        existing = supabase.table("vote_logs").select("*").eq("user_id", user.id).eq("submission_id", paper_id).execute()
        if not existing.data:
            raise HTTPException(status_code=400, detail="你还没有给这篇论文投过票")
        
        vote_record = existing.data[0]
        current_votes = vote_record.get("vote_count", 0)
        
        if current_votes <= 0:
            raise HTTPException(status_code=400, detail="没有可撤回的投票")
        
        # 获取论文当前票数
        result = supabase.table("submissions").select("total_votes").eq("id", paper_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        new_total = max(0, result.data.get("total_votes", 0) - 1)
        
        # 更新论文票数
        supabase.table("submissions").update({
            "total_votes": new_total,
            "updated_at": datetime.now().isoformat()
        }).eq("id", paper_id).execute()
        
        # 更新用户投票记录
        new_vote_count = current_votes - 1
        if new_vote_count > 0:
            supabase.table("vote_logs").update({
                "vote_count": new_vote_count,
                "updated_at": datetime.now().isoformat()
            }).eq("id", vote_record["id"]).execute()
        else:
            supabase.table("vote_logs").delete().eq("id", vote_record["id"]).execute()
        
        # 恢复用户票数
        profile = await get_or_create_profile(user.id)
        new_votes_left = min(5, profile.get("daily_votes_left", 0) + 1)
        supabase.table("profiles").update({
            "daily_votes_left": new_votes_left
        }).eq("id", user.id).execute()
        
        return {"success": True, "totalVotes": new_total, "votesLeft": new_votes_left}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error unvoting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/nominees")
async def submit_paper(
    request: Request,
    title: str = Form(...),
    abstract: str = Form(...),
    author: Optional[str] = Form("佚名"),
    contact: Optional[str] = Form("")
):
    """提交论文（需要登录）"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证登录
    user = await require_auth(request)
    
    try:
        # 插入论文
        result = supabase.table("submissions").insert({
            "user_id": user.id,
            "title": title,
            "abstract": abstract,
            "status": "pending",
            "total_votes": 0
        }).execute()
        
        if result.data:
            new_id = result.data[0]["id"]
            
            # 更新用户联系方式
            if contact:
                supabase.table("profiles").update({
                    "wechat_contact": contact
                }).eq("id", user.id).execute()
            
            return {"success": True, "id": str(new_id), "status": "pending"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create submission")
            
    except Exception as e:
        print(f"Error submitting paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/share")
async def report_share(request: Request):
    """分享奖励（需要登录）"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证登录
    user = await require_auth(request)
    
    try:
        profile = await get_or_create_profile(user.id)
        if not profile:
            raise HTTPException(status_code=500, detail="Failed to get profile")
        
        if profile.get("has_shared_today"):
            return {
                "success": True,
                "votesLeft": profile.get("daily_votes_left", 5),
                "hasSharedToday": True
            }
        
        # 增加一票
        new_votes = min(5, profile.get("daily_votes_left", 0) + 1)
        supabase.table("profiles").update({
            "daily_votes_left": new_votes,
            "has_shared_today": True
        }).eq("id", user.id).execute()
        
        return {"success": True, "votesLeft": new_votes, "hasSharedToday": True}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sharing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/leaderboard")
def get_leaderboard(page: int = 1, pageSize: int = 20):
    """获取排行榜（公开访问）"""
    if not supabase:
        return {"items": [], "total": 0, "page": page, "pageSize": pageSize}
    
    try:
        result = supabase.table("submissions").select("*").eq("status", "approved").order("total_votes", desc=True).execute()
        
        items = []
        for i, item in enumerate(result.data, start=1):
            items.append({
                "rank": i,
                "paper": {
                    "id": str(item["id"]),
                    "title": item["title"],
                    "author": "匿名",
                    "abstract": item.get("abstract", ""),
                    "totalVotes": item.get("total_votes", 0),
                    "date": item["created_at"][:10] if item.get("created_at") else "2024-01-01"
                }
            })
        
        return {"items": items, "total": len(items), "page": page, "pageSize": pageSize}
    except Exception as e:
        return {"items": [], "total": 0, "page": page, "pageSize": pageSize}

@app.get("/api/v1/stats")
def get_stats():
    """获取统计（公开访问）"""
    if not supabase:
        return {"totalNominees": 0, "totalVotes": 0, "totalUsers": 0, "todayVotes": 0}
    
    try:
        papers = supabase.table("submissions").select("total_votes").eq("status", "approved").execute()
        total_papers = len(papers.data)
        total_votes = sum(p.get("total_votes", 0) for p in papers.data)
        
        return {"totalNominees": total_papers, "totalVotes": total_votes, "totalUsers": 0, "todayVotes": 0}
    except Exception as e:
        return {"totalNominees": 0, "totalVotes": 0, "totalUsers": 0, "todayVotes": 0}

# 启动
if __name__ == "__main__":
    import uvicorn
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
