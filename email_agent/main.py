# Email Agent Backend
# Multi-Agent Email Processing System

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from email_agent.config import settings
from email_agent.api.routes import router as api_router, set_orchestrator
from email_agent.websocket.handler import websocket_endpoint
from email_agent.orchestrator.engine import AgentOrchestrator

# 全局编排引擎实例
orchestrator: AgentOrchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global orchestrator
    # 启动时初始化
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    # 将 orchestrator 传递给路由模块
    set_orchestrator(orchestrator)
    
    print("[STARTED] Email Agent Backend Started")
    print(f"[API Docs] http://{settings.HOST}:{settings.PORT}/docs")
    yield
    # 关闭时清理
    await orchestrator.shutdown()
    print("[STOPPED] Email Agent Backend Stopped")

app = FastAPI(
    title="Email Agent API",
    description="Multi-Agent Email Processing System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

# WebSocket 端点
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket_endpoint(websocket, orchestrator)

if __name__ == "__main__":
    uvicorn.run(
        "email_agent.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
