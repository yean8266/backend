"""
配置管理
使用 Pydantic Settings 管理环境变量
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Email Agent Backend"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./email_agent.db"
    
    # Redis (用于缓存和消息队列)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM 配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # 可选：本地模型配置
    LOCAL_LLM_ENABLED: bool = False
    LOCAL_LLM_URL: str = "http://localhost:11434"
    LOCAL_LLM_MODEL: str = "llama3.1:8b"
    
    # Agent 配置
    AGENT_TIMEOUT: int = 30  # 秒
    MAX_CONCURRENT_AGENTS: int = 10
    
    # 日志
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
