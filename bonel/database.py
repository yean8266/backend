"""
Bonel Project - Mock 数据库 (用于 MVP 测试)
无需真实 Supabase 连接，使用内存数据
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from bonel.config import settings

logger = logging.getLogger(__name__)

# 内存数据库
_mock_users: Dict[str, Dict[str, Any]] = {}
_mock_nominees: Dict[str, Dict[str, Any]] = {}
_mock_vote_logs: Dict[str, Dict[str, Any]] = {}  # key: "user_id:nominee_id"

def get_today_date() -> str:
    """获取今天的日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")


def _init_mock_data():
    """初始化测试数据"""
    global _mock_nominees
    
    if not _mock_nominees:
        _mock_nominees = {
            "BNL-2603-01": {
                "id": "BNL-2603-01",
                "title": "基于 YOLOv5 的垃圾分类系统",
                "author": "张三",
                "abstract": "这是一个使用 YOLOv5 实现的垃圾分类系统，准确率惊人地低...",
                "total_votes": 128,
                "status": "approved",
                "created_at": "2026-03-01T10:00:00",
                "updated_at": "2026-03-01T10:00:00",
            },
            "BNL-2603-02": {
                "id": "BNL-2603-02",
                "title": "用 Excel 做神经网络",
                "author": "李四",
                "abstract": "证明了 Excel 可以做任何事情，包括深度学习...",
                "total_votes": 256,
                "status": "approved",
                "created_at": "2026-03-02T11:00:00",
                "updated_at": "2026-03-02T11:00:00",
            },
            "BNL-2603-03": {
                "id": "BNL-2603-03",
                "title": "Hello World 企业级架构",
                "author": "王五",
                "abstract": "包含 50 个微服务的 Hello World 项目，每个服务只有一行代码...",
                "total_votes": 89,
                "status": "approved",
                "created_at": "2026-03-03T12:00:00",
                "updated_at": "2026-03-03T12:00:00",
            },
        }
        logger.info("✅ Mock 数据已初始化")


class Database:
    """Mock 数据库 - 用于测试"""
    
    def __init__(self):
        _init_mock_data()
    
    @property
    def users(self) -> Dict[str, Dict[str, Any]]:
        """访问 users 字典（用于微信登录模块）"""
        return _mock_users
    
    # ==================== 用户相关操作 ====================
    
    async def get_or_create_user(self, user_id: str, email: str) -> Dict[str, Any]:
        """获取或创建用户"""
        if user_id not in _mock_users:
            today = get_today_date()
            _mock_users[user_id] = {
                "id": user_id,
                "email": email,
                "daily_votes_left": settings.DEFAULT_DAILY_VOTES,
                "has_shared_today": False,
                "last_active_date": today,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            logger.info(f"✅ 创建新用户: {user_id}")
        else:
            # 检查跨天重置
            user = _mock_users[user_id]
            today = get_today_date()
            if user.get("last_active_date") != today:
                user["daily_votes_left"] = settings.DEFAULT_DAILY_VOTES
                user["has_shared_today"] = False
                user["last_active_date"] = today
                user["updated_at"] = datetime.now().isoformat()
                logger.info(f"🔄 用户跨天重置: {user_id}")
        
        return _mock_users[user_id]
    
    async def get_user_vote_status(self, user_id: str) -> Dict[str, Any]:
        """获取用户投票状态"""
        if user_id in _mock_users:
            user = _mock_users[user_id]
            return {
                "daily_votes_left": user.get("daily_votes_left", settings.DEFAULT_DAILY_VOTES),
                "has_shared_today": user.get("has_shared_today", False),
                "last_active_date": user.get("last_active_date", get_today_date()),
            }
        return {
            "daily_votes_left": settings.DEFAULT_DAILY_VOTES,
            "has_shared_today": False,
            "last_active_date": get_today_date(),
        }
    
    # ==================== 候选人相关操作 ====================
    
    async def get_nominees(
        self,
        status: str = "approved",
        sort_by: str = "hot",
        page: int = 1,
        page_size: int = 20,
        search: str = ""
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取候选人列表"""
        nominees = list(_mock_nominees.values())
        
        # 状态筛选
        if status:
            nominees = [n for n in nominees if n.get("status") == status]
        
        # 搜索
        if search:
            search_lower = search.lower()
            nominees = [
                n for n in nominees
                if search_lower in n.get("title", "").lower()
                or search_lower in n.get("author", "").lower()
                or search_lower in n.get("id", "").lower()
            ]
        
        # 排序
        if sort_by == "hot":
            nominees.sort(key=lambda x: (-x.get("total_votes", 0), x.get("created_at", "")))
        else:  # new
            nominees.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # 分页
        total = len(nominees)
        offset = (page - 1) * page_size
        nominees = nominees[offset:offset + page_size]
        
        return nominees, total
    
    async def get_user_votes_for_nominee(self, user_id: str, nominee_id: str) -> int:
        """获取用户对某个候选人的投票数"""
        key = f"{user_id}:{nominee_id}"
        log = _mock_vote_logs.get(key)
        return log.get("vote_count", 0) if log else 0
    
    # ==================== 统计相关操作 ====================
    
    async def get_stats(self) -> Dict[str, int]:
        """获取平台统计数据"""
        total_nominees = len(_mock_nominees)
        total_votes = sum(n.get("total_votes", 0) for n in _mock_nominees.values())
        total_users = len(_mock_users)
        today_votes = total_votes  # MVP 简化
        
        return {
            "total_nominees": total_nominees,
            "total_votes": total_votes,
            "total_users": total_users,
            "today_votes": today_votes,
        }


# 全局数据库实例
db = Database()
