"""
Bonel Project - Main Application
FastAPI 主入口
"""

# ==================== 最先加载环境变量 ====================
# 必须在导入其他模块之前加载 .env，确保配置能正确读取
from dotenv import load_dotenv
from pathlib import Path

# 使用 pathlib 动态获取项目根目录
# __file__ 是当前文件 (main.py) 的路径
# .resolve() 获取绝对路径
# .parent 获取父目录 (bonel/)
# .parent 再获取父目录 (backend/)，即项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# 显式加载 .env 文件
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print(f"✅ 已加载环境变量: {ENV_PATH}")
else:
    print(f"⚠️  未找到 .env 文件: {ENV_PATH}")
    print(f"   当前 BASE_DIR: {BASE_DIR}")
    # 列出目录内容帮助调试
    if BASE_DIR.exists():
        print(f"   目录内容: {list(BASE_DIR.iterdir())}")

# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from bonel.config import settings
from bonel.api.routes import router as api_router
from bonel.api.user_routes import router as user_router
from bonel.api.routers.nominees import router as nominees_router

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
app.include_router(nominees_router, prefix="/api/v1")  # 候选人/论文提交路由

# 打印所有注册的路由（调试用）
from fastapi.routing import APIRoute
print("\n📋 已注册的路由列表:")
for route in app.routes:
    if isinstance(route, APIRoute):
        methods = ", ".join(route.methods)
        print(f"   {methods} {route.path}")


if __name__ == "__main__":
    uvicorn.run(
        "bonel.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
