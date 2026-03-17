# -*- coding: utf-8 -*-
"""
Bonel Project - FastAPI Backend with Supabase
完整功能后端 - 支持用户认证、投票、数据持久化
"""
from fastapi import FastAPI, HTTPException, Query, Request, Header, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="Bonel Project API",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase 客户端
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_KEY", ""))

# 使用不同的变量名避免冲突
supabase_client: Optional[Client] = None

# 检查是否是有效的 Supabase 配置
is_valid_supabase = (
    supabase_url and 
    supabase_key and 
    "your-project" not in supabase_url and
    "supabase.co" in supabase_url
)

if not is_valid_supabase:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not set properly. Using mock mode.")
    print(f"  URL: {supabase_url[:50]}..." if supabase_url else "  URL: (empty)")
    supabase_client = None
else:
    try:
        supabase_client = create_client(supabase_url, supabase_key)
        print(f"Connected to Supabase: {supabase_url}")
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
        print("Falling back to mock mode.")
        supabase_client = None

# Data Models
class Paper(BaseModel):
    id: str
    title: str
    author: str
    abstract: str
    totalVotes: int
    userVotes: int
    date: str

class UserStatus(BaseModel):
    isLoggedIn: bool = False
    votesLeft: int = 5
    hasSharedToday: bool = False

class PapersResponse(BaseModel):
    userStatus: UserStatus
    papers: List[Paper]
    total: int
    page: int
    pageSize: int

class VoteResponse(BaseModel):
    success: bool
    votesLeft: Optional[int] = None
    totalVotes: Optional[int] = None

class ShareResponse(BaseModel):
    success: bool
    votesLeft: int
    hasSharedToday: bool

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "2.0.0"
    database: str = "unknown"

class SubmitPaperRequest(BaseModel):
    title: str
    author: str = "Anonymous Researcher"
    contact: str = ""
    abstract: str
    link: str = ""

# Helper Functions
async def get_current_user(authorization: Optional[str] = Header(None)):
    """从 JWT Token 获取当前用户"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    
    if not supabase_client:
        return None
    
    try:
        # 验证 JWT token
        user = supabase_client.auth.get_user(token)
        return user.user if user else None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

async def get_or_create_profile(user_id: str):
    """获取或创建用户档案"""
    if not supabase_client:
        return None
    
    # 检查是否需要重置每日投票
    try:
        # 获取用户档案
        result = supabase_client.table("profiles").select("*").eq("id", user_id).single().execute()
        
        if result.data:
            profile = result.data
            # 检查是否需要重置每日投票
            last_date = profile.get("last_active_date")
            today = date.today().isoformat()
            
            if last_date != today:
                # 重置每日投票
                supabase_client.table("profiles").update({
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
            supabase_client.table("profiles").insert(new_profile).execute()
            return new_profile
            
    except Exception as e:
        print(f"Profile error: {e}")
        return None

async def get_user_votes_for_papers(user_id: str, paper_ids: List[str]):
    """获取用户对多篇论文的投票情况"""
    if not supabase_client or not paper_ids:
        return {}
    
    try:
        # 获取用户提交的论文ID列表
        submissions = supabase_client.table("submissions").select("id").eq("user_id", user_id).execute()
        user_paper_ids = {s["id"] for s in submissions.data} if submissions.data else set()
        
        # 获取用户投票记录
        result = supabase_client.table("vote_logs").select("submission_id, vote_count").eq("user_id", user_id).in_("submission_id", paper_ids).execute()
        
        votes_map = {}
        if result.data:
            for vote in result.data:
                votes_map[vote["submission_id"]] = vote["vote_count"]
        
        return votes_map, user_paper_ids
    except Exception as e:
        print(f"Get votes error: {e}")
        return {}, set()

# API Routes

@app.get("/")
def root():
    return {
        "message": "Bonel Project API with Supabase",
        "docs": "/docs",
        "database": "connected" if supabase_client else "mock mode"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        database="connected" if supabase_client else "mock"
    )

@app.get("/api/v1/nominees", response_model=PapersResponse)
async def get_nominees(
    request: Request,
    sort: str = Query("hot"),
    page: int = Query(1, ge=1),
    search: str = Query("")
):
    """获取论文列表（支持排序、分页、搜索）"""
    
    # 获取当前用户
    auth_header = request.headers.get("authorization")
    user = await get_current_user(auth_header)
    user_id = user.id if user else None
    
    # Mock data for when database is not available
    MOCK_PAPERS = [
        {
            "id": "mock-001",
            "title": "The Aerodynamics of Falling Toast: A 'Butter-First' Contact Hypothesis",
            "author": "Anonymous PhD",
            "abstract": "In this groundbreaking study, we deliberately dropped ten thousand buttered toast slices to conclusively prove that the universe harbors pure malice toward humanity.",
            "totalVotes": 8902,
            "userVotes": 0,
            "date": "2026-03-01"
        },
        {
            "id": "mock-002",
            "title": "YOLOv5 Object Tracking on Raspberry Pi 5: Why the Model Identified My Roommate as Non-recyclable Garbage",
            "author": "A Graduate Student",
            "abstract": "When attempting to track out-of-bound objects using an Ubuntu desktop development board, we discovered deep philosophical biases in the visual algorithm.",
            "totalVotes": 2042,
            "userVotes": 0,
            "date": "2026-03-07"
        },
        {
            "id": "mock-003",
            "title": "Quantum Entanglement in Headphone Cables: On Topological Chaos in Local Pocket Space",
            "author": "404 Laboratory",
            "abstract": "We hypothesize that headphone cables exist in multiple dimensions simultaneously. When in a locally dark environment, they spontaneously collapse into chaotic topological knots.",
            "totalVotes": 4521,
            "userVotes": 0,
            "date": "2026-03-02"
        },
        {
            "id": "mock-004",
            "title": "A Comprehensive Phenomenological Study on the Efficacy of 'Have You Tried Restarting?'",
            "author": "IT Rescue Center",
            "abstract": "Over a 5-year observation period, we tracked server crashes, relationship crises, and existential dilemmas. Research shows restarting fixes 85% of hardware issues but worsens human emotional stability.",
            "totalVotes": 3100,
            "userVotes": 0,
            "date": "2026-02-28"
        }
    ]
    
    if not supabase_client:
        # Mock mode - return sample data
        papers = MOCK_PAPERS
        if search:
            search_lower = search.lower()
            papers = [p for p in papers if search_lower in p["title"].lower()]
        if sort == "hot":
            papers.sort(key=lambda x: x["totalVotes"], reverse=True)
        
        return PapersResponse(
            userStatus=UserStatus(isLoggedIn=False, votesLeft=5, hasSharedToday=False),
            papers=[Paper(**p) for p in papers],
            total=len(papers),
            page=page,
            pageSize=20
        )
    
    try:
        # 构建查询
        query = supabase_client.table("submissions").select("*", count="exact").eq("status", "approved")
        
        # 搜索过滤
        if search:
            query = query.or_(f"title.ilike.%{search}%,abstract.ilike.%{search}%")
        
        # 排序
        if sort == "hot":
            query = query.order("total_votes", desc=True)
        else:  # new
            query = query.order("created_at", desc=True)
        
        # 分页
        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size - 1
        
        result = query.range(start, end).execute()
        
        papers_data = result.data if result.data else []
        total_count = result.count if hasattr(result, 'count') else len(papers_data)
        
        # 获取用户投票状态
        paper_ids = [p["id"] for p in papers_data]
        user_votes_map, user_paper_ids = await get_user_votes_for_papers(user_id, paper_ids) if user_id else ({}, set())
        
        # 获取用户档案
        user_status = UserStatus(isLoggedIn=bool(user))
        if user_id:
            profile = await get_or_create_profile(user_id)
            if profile:
                user_status.votesLeft = profile.get("daily_votes_left", 5)
                user_status.hasSharedToday = profile.get("has_shared_today", False)
        
        # 构建响应
        papers = []
        for p in papers_data:
            is_author = p["id"] in user_paper_ids
            papers.append(Paper(
                id=str(p["id"]),
                title=p["title"],
                author="Anonymous" if not is_author else "You",
                abstract=p.get("abstract", ""),
                totalVotes=p.get("total_votes", 0),
                userVotes=user_votes_map.get(p["id"], 0),
                date=p["created_at"][:10] if p.get("created_at") else date.today().isoformat()
            ))
        
        return PapersResponse(
            userStatus=user_status,
            papers=papers,
            total=total_count or len(papers),
            page=page,
            pageSize=page_size
        )
        
    except Exception as e:
        print(f"Get nominees error: {e}")
        # Return mock data on database error
        papers = MOCK_PAPERS
        if search:
            search_lower = search.lower()
            papers = [p for p in papers if search_lower in p["title"].lower()]
        if sort == "hot":
            papers.sort(key=lambda x: x["totalVotes"], reverse=True)
        
        return PapersResponse(
            userStatus=UserStatus(isLoggedIn=False, votesLeft=5, hasSharedToday=False),
            papers=[Paper(**p) for p in papers],
            total=len(papers),
            page=page,
            pageSize=20
        )

@app.post("/api/v1/vote", response_model=VoteResponse)
async def submit_vote(request: Request, data: dict):
    """投票（需要登录）"""
    paper_id = data.get("paperId")
    if not paper_id:
        raise HTTPException(status_code=400, detail="Missing paperId")
    
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证用户登录
    auth_header = request.headers.get("authorization")
    user = await get_current_user(auth_header)
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")
    
    try:
        # 获取用户档案
        profile = await get_or_create_profile(user.id)
        if not profile:
            raise HTTPException(status_code=500, detail="Failed to get profile")
        
        votes_left = profile.get("daily_votes_left", 0)
        if votes_left <= 0:
            raise HTTPException(status_code=400, detail="No votes left for today")
        
        # 检查是否已投票
        existing = supabase_client.table("vote_logs").select("*").eq("user_id", user.id).eq("submission_id", paper_id).execute()
        
        if existing.data:
            # 更新投票数
            current_votes = existing.data[0].get("vote_count", 0)
            supabase_client.table("vote_logs").update({
                "vote_count": current_votes + 1,
                "updated_at": datetime.now().isoformat()
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # 创建新投票记录
            supabase_client.table("vote_logs").insert({
                "user_id": user.id,
                "submission_id": paper_id,
                "vote_count": 1
            }).execute()
        
        # 更新论文总票数
        new_total = 0
        submission = supabase_client.table("submissions").select("total_votes").eq("id", paper_id).single().execute()
        if submission.data:
            new_total = (submission.data.get("total_votes") or 0) + 1
            supabase_client.table("submissions").update({
                "total_votes": new_total,
                "updated_at": datetime.now().isoformat()
            }).eq("id", paper_id).execute()
        
        # 更新用户剩余票数
        new_votes_left = votes_left - 1
        supabase_client.table("profiles").update({
            "daily_votes_left": new_votes_left
        }).eq("id", user.id).execute()
        
        return VoteResponse(success=True, votesLeft=new_votes_left, totalVotes=new_total)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Vote error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/unvote", response_model=VoteResponse)
async def submit_unvote(request: Request, data: dict):
    """撤回投票（需要登录）"""
    paper_id = data.get("paperId")
    if not paper_id:
        raise HTTPException(status_code=400, detail="Missing paperId")
    
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证用户登录
    auth_header = request.headers.get("authorization")
    user = await get_current_user(auth_header)
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")
    
    try:
        # 获取投票记录
        existing = supabase_client.table("vote_logs").select("*").eq("user_id", user.id).eq("submission_id", paper_id).execute()
        
        if not existing.data:
            raise HTTPException(status_code=400, detail="You haven't voted for this paper")
        
        vote_record = existing.data[0]
        current_votes = vote_record.get("vote_count", 0)
        
        if current_votes <= 0:
            raise HTTPException(status_code=400, detail="No votes to withdraw")
        
        # 更新投票记录
        new_vote_count = current_votes - 1
        if new_vote_count > 0:
            supabase_client.table("vote_logs").update({
                "vote_count": new_vote_count,
                "updated_at": datetime.now().isoformat()
            }).eq("id", vote_record["id"]).execute()
        else:
            # 删除投票记录
            supabase_client.table("vote_logs").delete().eq("id", vote_record["id"]).execute()
        
        # 更新论文总票数
        new_total = 0
        submission = supabase_client.table("submissions").select("total_votes").eq("id", paper_id).single().execute()
        if submission.data:
            new_total = max(0, (submission.data.get("total_votes") or 0) - 1)
            supabase_client.table("submissions").update({
                "total_votes": new_total,
                "updated_at": datetime.now().isoformat()
            }).eq("id", paper_id).execute()
        
        # 恢复用户票数
        profile = await get_or_create_profile(user.id)
        if profile is None:
            raise HTTPException(status_code=500, detail="Failed to get profile")
        
        new_votes_left = min(5, profile.get("daily_votes_left", 0) + 1)
        supabase_client.table("profiles").update({
            "daily_votes_left": new_votes_left
        }).eq("id", user.id).execute()
        
        return VoteResponse(success=True, votesLeft=new_votes_left, totalVotes=new_total if 'new_total' in locals() else 0)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unvote error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/share", response_model=ShareResponse)
async def report_share(request: Request):
    """分享成功，获得额外票数（需要登录）"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证用户登录
    auth_header = request.headers.get("authorization")
    user = await get_current_user(auth_header)
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")
    
    try:
        profile = await get_or_create_profile(user.id)
        if not profile:
            raise HTTPException(status_code=500, detail="Failed to get profile")
        
        if profile.get("has_shared_today"):
            raise HTTPException(status_code=400, detail="Already shared today")
        
        # 增加票数并标记已分享
        new_votes = min(5, profile.get("daily_votes_left", 0) + 1)
        supabase_client.table("profiles").update({
            "daily_votes_left": new_votes,
            "has_shared_today": True
        }).eq("id", user.id).execute()
        
        return ShareResponse(success=True, votesLeft=new_votes, hasSharedToday=True)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Share error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/nominees")
async def create_paper(
    request: Request,
    title: str = Form(...),
    abstract: str = Form(...),
    author: str = Form("Anonymous"),
    contact: str = Form(""),
    link: str = Form("")
):
    """提交新论文（需要登录）"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # 验证用户登录
    auth_header = request.headers.get("authorization")
    user = await get_current_user(auth_header)
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")
    
    try:
        # 插入新论文
        paper_data = {
            "user_id": user.id,
            "title": title,
            "abstract": abstract,
            "status": "pending",  # 需要审核
            "total_votes": 0
        }
        
        # 更新用户联系方式（如果提供）
        if contact:
            supabase_client.table("profiles").update({
                "wechat_contact": contact
            }).eq("id", user.id).execute()
        
        result = supabase_client.table("submissions").insert(paper_data).execute()
        
        if result.data:
            new_id = result.data[0]["id"]
            return {"success": True, "id": str(new_id), "status": "pending"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create submission")
            
    except Exception as e:
        print(f"Create paper error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/leaderboard")
async def get_leaderboard(page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1)):
    """获取排行榜"""
    if not supabase_client:
        return {"items": [], "total": 0, "page": page, "pageSize": pageSize}
    
    try:
        result = supabase_client.table("submissions").select("*", count="exact").eq("status", "approved").order("total_votes", desc=True).range((page-1)*pageSize, page*pageSize-1).execute()
        
        papers = result.data if result.data else []
        total = result.count if hasattr(result, 'count') else len(papers)
        
        items = []
        for i, p in enumerate(papers, start=(page-1)*pageSize+1):
            items.append({
                "rank": i,
                "paper": {
                    "id": str(p["id"]),
                    "title": p["title"],
                    "author": "Anonymous",
                    "abstract": p.get("abstract", ""),
                    "totalVotes": p.get("total_votes", 0),
                    "userVotes": 0,
                    "date": p["created_at"][:10] if p.get("created_at") else date.today().isoformat()
                }
            })
        
        return {"items": items, "total": total, "page": page, "pageSize": pageSize}
        
    except Exception as e:
        print(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats")
async def get_stats():
    """获取平台统计"""
    if not supabase_client:
        return {
            "totalNominees": 0,
            "totalVotes": 0,
            "totalUsers": 0,
            "todayVotes": 0
        }
    
    try:
        # 获取论文数量
        papers_result = supabase_client.table("submissions").select("*", count="exact").eq("status", "approved").execute()
        total_nominees = papers_result.count if hasattr(papers_result, 'count') else 0
        
        # 获取总票数
        votes_count = 0
        if papers_result.data:
            votes_count = sum(p.get("total_votes", 0) for p in papers_result.data)
        
        # 获取用户数量
        users_result = supabase_client.table("profiles").select("*", count="exact").execute()
        total_users = users_result.count if hasattr(users_result, 'count') else 0
        
        return {
            "totalNominees": total_nominees,
            "totalVotes": votes_count,
            "totalUsers": total_users,
            "todayVotes": 0  # 可以添加更复杂的统计
        }
        
    except Exception as e:
        print(f"Stats error: {e}")
        return {
            "totalNominees": 0,
            "totalVotes": 0,
            "totalUsers": 0,
            "todayVotes": 0
        }

if __name__ == "__main__":
    import uvicorn
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
