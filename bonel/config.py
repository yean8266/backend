"""
Bonel Project - 配置管理
包含 Supabase 和 JWT 配置
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Bonel Project API"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # ==================== Supabase 配置 ====================
    # 数据库地址
    SUPABASE_URL: str = ""
    
    # JWT 解密密钥（用于验证前端 Token）
    SUPABASE_JWT_SECRET: str = ""
    
    # 服务角色密钥（后端管理员操作，⚠️ 严禁泄露）
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Anon Key（公开）
    SUPABASE_ANON_KEY: str = ""
    
    # JWT 算法
    JWT_ALGORITHM: str = "HS256"
    
    # ==================== 投票配置 ====================
    DEFAULT_DAILY_VOTES: int = 5
    SHARE_BONUS_VOTES: int = 1
    
    # ==================== 分页配置 ====================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
