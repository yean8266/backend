"""
Bonel Project - 数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ==================== 通用响应模型 ====================

class SuccessResponse(BaseModel):
    """通用成功响应"""
    success: bool = True
    message: Optional[str] = None

# ==================== 用户相关模型 ====================

class UserStatus(BaseModel):
    """用户投票状态"""
    is_logged_in: bool = False
    votes_left: int = 0
    has_shared_today: bool = False
    last_active_date: Optional[str] = None

class VoteStatusResponse(BaseModel):
    """投票状态查询响应"""
    daily_votes_left: int
    has_shared_today: bool
    last_active_date: str

# ==================== 候选人/论文模型 ====================

class NomineeStatus(str, Enum):
    """候选人审核状态"""
    PENDING = "pending"    # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝

class Nominee(BaseModel):
    """候选人/论文模型"""
    id: str
    title: str
    author: str
    abstract: str
    total_votes: int = 0
    user_votes: int = 0  # 当前用户投了多少票
    status: NomineeStatus = NomineeStatus.APPROVED
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Paper(BaseModel):
    """前端兼容的论文模型 (与 Nominee 对应)"""
    id: str
    title: str
    author: str
    abstract: str
    totalVotes: int  # camelCase 为了前端兼容
    userVotes: int
    date: str  # ISO format

# ==================== 投票相关模型 ====================

class VoteRequest(BaseModel):
    """投票请求"""
    paper_id: str = Field(..., alias="paperId")
    
    class Config:
        populate_by_name = True

class VoteResponse(BaseModel):
    """投票响应"""
    success: bool
    votes_left: Optional[int] = None
    total_votes: Optional[int] = None
    message: Optional[str] = None

class UnvoteRequest(BaseModel):
    """撤回投票请求"""
    paper_id: str = Field(..., alias="paperId")
    
    class Config:
        populate_by_name = True

# ==================== 分享相关模型 ====================

class ShareResponse(BaseModel):
    """分享奖励响应"""
    success: bool
    votes_left: Optional[int] = None
    has_shared_today: Optional[bool] = None
    message: Optional[str] = None

# ==================== 排行榜模型 ====================

class LeaderboardItem(BaseModel):
    """排行榜条目"""
    rank: int
    paper: Paper

class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    items: List[LeaderboardItem]
    total: int
    page: int
    page_size: int

# ==================== 统计模型 ====================

class StatsResponse(BaseModel):
    """平台统计数据"""
    total_nominees: int
    total_votes: int
    total_users: int
    today_votes: int

# ==================== 列表查询模型 ====================

class PapersResponse(BaseModel):
    """文章列表响应"""
    user_status: UserStatus
    papers: List[Paper]
    total: int
    page: int
    page_size: int

# ==================== 提交相关模型 ====================

class SubmitResponse(BaseModel):
    """提交论文响应"""
    success: bool
    id: Optional[str] = None
    message: Optional[str] = None

# ==================== 健康检查模型 ====================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    version: str = "1.0.0"

# ==================== 用户角色与档案模型 (新增) ====================

class UserRole(str, Enum):
    """
    用户角色层级枚举
    权限从低到高：user < vip < admin < super_admin
    """
    USER = "user"              # 普通用户
    VIP = "vip"                # 高级会员
    ADMIN = "admin"            # 管理员
    SUPER_ADMIN = "super_admin"  # 超级无敌顶级管理员

class UserProfile(BaseModel):
    """
    用户档案模型
    对应数据库 public.profiles 表
    """
    id: str                    # UUID
    email: Optional[str] = None
    nickname: Optional[str] = None
    wechat_contact: Optional[str] = None
    daily_votes_left: int = 5
    role: UserRole = UserRole.USER
    created_at: Optional[datetime] = None
    last_active_date: Optional[str] = None
    
    class Config:
        from_attributes = True

class CurrentUser(BaseModel):
    """
    当前登录用户完整信息
    包含从 JWT Token 解析的基本信息和从数据库查询的档案信息
    """
    id: str                    # 用户ID (来自 JWT sub)
    email: Optional[str] = None
    nickname: Optional[str] = None
    wechat_contact: Optional[str] = None
    daily_votes_left: int = 5
    role: UserRole = UserRole.USER
    is_authenticated: bool = True
    
    # 权限检查方法
    def is_vip_or_above(self) -> bool:
        """检查是否为 VIP 或更高级别"""
        return self.role in [UserRole.VIP, UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def is_admin_or_above(self) -> bool:
        """检查是否为管理员或更高级别"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def is_super_admin(self) -> bool:
        """检查是否为超级管理员"""
        return self.role == UserRole.SUPER_ADMIN

class UserProfileResponse(BaseModel):
    """获取用户档案响应"""
    id: str
    email: Optional[str]
    nickname: Optional[str]
    wechat_contact: Optional[str]
    daily_votes_left: int
    role: str
    created_at: Optional[datetime]

class UserProfileUpdateRequest(BaseModel):
    """更新用户档案请求"""
    nickname: Optional[str] = Field(None, max_length=255)
    wechat_contact: Optional[str] = Field(None, max_length=255)

class UserProfileUpdateResponse(BaseModel):
    """更新用户档案响应"""
    success: bool
    message: str
    data: Optional[UserProfileResponse] = None
