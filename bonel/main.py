"""
Bonel Project - Main Application
FastAPI 主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from bonel.config import settings
from bonel.api.routes import router as api_router
from bonel.api.user_routes import router as user_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("=" * 50)
    logger.info(f"🚀 {settings.APP_NAME} Starting...")
    logger.info(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 50)
    
    # 启动时检查配置
    if not settings.SUPABASE_URL:
        logger.warning("⚠️  SUPABASE_URL 未配置，请检查 .env 文件")
    if not settings.SUPABASE_ANON_KEY:
        logger.warning("⚠️  SUPABASE_ANON_KEY 未配置，请检查 .env 文件")
    
    yield
    
    logger.info("👋  Server stopped")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="Bonel Project - 工程灾难投票平台 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置 - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")  # 用户档案路由


if __name__ == "__main__":
    uvicorn.run(
        "bonel.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
