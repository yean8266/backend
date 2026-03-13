"""
WebSocket 处理
支持实时推送 Agent 处理进度
"""

import json
import asyncio
from typing import Dict, Set
import logging

from email_agent.models import StreamResponse, AnalyzeRequest
from email_agent.orchestrator.engine import AgentOrchestrator

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set] = {}  # task_id -> {websockets}
    
    async def connect(self, websocket, task_id: str = None):
        """建立连接"""
        await websocket.accept()
        if task_id:
            if task_id not in self.active_connections:
                self.active_connections[task_id] = set()
            self.active_connections[task_id].add(websocket)
        logger.info(f"WebSocket connected: {task_id}")
    
    def disconnect(self, websocket, task_id: str = None):
        """断开连接"""
        if task_id and task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
        logger.info(f"WebSocket disconnected: {task_id}")
    
    async def send_progress(self, task_id: str, step: str, progress: float):
        """发送进度更新"""
        if task_id not in self.active_connections:
            return
        
        message = StreamResponse(
            type="progress",
            task_id=task_id,
            data={
                "step": step,
                "progress": progress,
                "status": "running"
            }
        )
        
        disconnected = set()
        for ws in self.active_connections[task_id]:
            try:
                await ws.send_json(message.dict())
            except:
                disconnected.add(ws)
        
        # 清理断开的连接
        for ws in disconnected:
            self.active_connections[task_id].discard(ws)
    
    async def send_result(self, task_id: str, result: dict):
        """发送结果"""
        if task_id not in self.active_connections:
            return
        
        message = StreamResponse(
            type="result",
            task_id=task_id,
            data=result
        )
        
        for ws in list(self.active_connections[task_id]):
            try:
                await ws.send_json(message.dict())
            except:
                pass

# 全局管理器实例
manager = WebSocketManager()

async def websocket_endpoint(websocket, orchestrator: AgentOrchestrator):
    """
    WebSocket 处理函数
    
    客户端可以：
    1. 订阅任务进度
    2. 实时发送邮件分析请求
    """
    task_id = None
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "subscribe":
                # 订阅任务进度
                task_id = message.get("task_id")
                await manager.connect(websocket, task_id)
                await websocket.send_json({
                    "type": "status",
                    "message": f"Subscribed to task: {task_id}"
                })
            
            elif action == "analyze":
                # 实时分析请求
                from app.models import AnalyzeRequest, AgentInput, Email
                
                email_data = message.get("email")
                email = Email(**email_data)
                
                request = AnalyzeRequest(
                    email=email,
                    workflow_id=message.get("workflow_id", "default")
                )
                
                # 创建任务并订阅
                task = await orchestrator.execute_workflow(
                    workflow_id=request.workflow_id,
                    input_data=request
                )
                
                task_id = task.task_id
                await manager.connect(websocket, task_id)
                
                # 发送任务创建通知
                await websocket.send_json({
                    "type": "status",
                    "task_id": task_id,
                    "status": "started"
                })
                
                # 模拟进度推送（实际应用中，编排引擎应支持回调）
                asyncio.create_task(
                    simulate_progress(manager, task_id, orchestrator)
                )
            
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
        manager.disconnect(websocket, task_id)

async def simulate_progress(manager: WebSocketManager, task_id: str, orchestrator: AgentOrchestrator):
    """模拟进度推送（示例）"""
    steps = [
        ("summarizer", 0.25),
        ("classifier", 0.5),
        ("priority", 0.75),
        ("complete", 1.0)
    ]
    
    for step, progress in steps:
        await asyncio.sleep(1)  # 模拟处理时间
        await manager.send_progress(task_id, step, progress)
    
    # 发送最终结果
    task = await orchestrator.get_task_status(task_id)
    if task:
        await manager.send_result(task_id, {
            "status": task.status,
            "results": {k: v.dict() for k, v in task.steps_results.items()}
        })

class WebSocketDisconnect(Exception):
    pass
