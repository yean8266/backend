"""
API 路由定义
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional

from email_agent.models import (
    AnalyzeRequest, AnalyzeResponse,
    GenerateReplyRequest, GenerateReplyResponse,
    WorkflowDefinition, WorkflowTask, TaskStatus,
    AgentInput
)
from email_agent.orchestrator.engine import AgentOrchestrator
from email_agent.agents.base import registry
from email_agent.agents.implementations import register_all_agents

router = APIRouter()

# 全局 orchestrator 实例，在 main.py 中设置
orchestrator: AgentOrchestrator = None

def set_orchestrator(orch: AgentOrchestrator):
    """设置 orchestrator 实例"""
    global orchestrator
    orchestrator = orch

@router.on_event("startup")
async def startup_event():
    """启动时注册所有 Agent"""
    await register_all_agents()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_email(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    分析邮件
    
    使用指定的工作流分析邮件，返回 AI 分析结果
    """
    try:
        workflow_id = request.workflow_id or "default"
        
        # 转换请求为 AgentInput
        agent_input = AgentInput(
            email=request.email,
            context=request.preferences or {},
            user_preferences=request.preferences or {}
        )
        
        # 执行工作流
        task = await orchestrator.execute_workflow(
            workflow_id=workflow_id,
            input_data=agent_input
        )
        
        # 聚合结果
        results = task.steps_results
        
        # 计算整体优先级
        priority_result = results.get("step_3")  # priority agent
        overall_priority = None
        if priority_result and priority_result.success:
            overall_priority = priority_result.result.get("priority_level")
        
        # 生成建议动作
        suggested_actions = generate_suggested_actions(results)
        
        return AnalyzeResponse(
            task_id=task.task_id,
            status=task.status,
            results=results,
            overall_priority=overall_priority,
            suggested_actions=suggested_actions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/async")
async def analyze_email_async(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    异步分析邮件
    
    返回 task_id，通过 /task/{task_id} 查询结果
    """
    try:
        workflow_id = request.workflow_id or "default"
        
        # 转换请求为 AgentInput
        agent_input = AgentInput(
            email=request.email,
            context=request.preferences or {},
            user_preferences=request.preferences or {}
        )
        
        # 在后台执行
        task = await orchestrator.execute_workflow(
            workflow_id=workflow_id,
            input_data=agent_input
        )
        
        return {
            "task_id": task.task_id,
            "status": task.status,
            "message": "Task started, use /task/{task_id} to check status"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态和结果"""
    task = await orchestrator.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "workflow_id": task.workflow_id,
        "results": task.steps_results,
        "error_message": task.error_message,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }

@router.post("/generate-reply", response_model=GenerateReplyResponse)
async def generate_reply(request: GenerateReplyRequest):
    """
    生成回复建议
    
    根据邮件内容生成智能回复
    """
    try:
        from email_agent.agents.base import registry
        from email_agent.models import AgentInput, AgentType
        
        # 获取 Template Agent
        agent = registry.get(AgentType.TEMPLATE)
        
        # 构建输入
        agent_input = AgentInput(
            email=request.email,
            context={
                "tone": request.tone,
                "template_id": request.template_id,
                **(request.context or {})
            }
        )
        
        # 执行
        result = await agent.execute(agent_input)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error_message)
        
        suggestions = result.result.get("suggestions", [])
        if not suggestions:
            raise HTTPException(status_code=500, detail="No suggestions generated")
        
        # 返回第一个建议
        primary = suggestions[0]
        
        return GenerateReplyResponse(
            reply_text=primary.get("body", ""),
            reply_html=primary.get("body_html"),
            subject=primary.get("subject"),
            confidence=primary.get("confidence", 0.8),
            alternatives=[s.get("body", "") for s in suggestions[1:]] if len(suggestions) > 1 else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows", response_model=List[WorkflowDefinition])
async def list_workflows():
    """列出所有可用工作流"""
    return orchestrator.get_workflow_list()

@router.get("/agents")
async def list_agents():
    """列出所有已注册的 Agent"""
    agents = registry.list_agents()
    return {
        "agents": [
            {
                "type": agent_type.value,
                "initialized": agent.initialized
            }
            for agent_type, agent in agents.items()
        ]
    }

@router.post("/workflows")
async def create_workflow(workflow: WorkflowDefinition):
    """创建自定义工作流"""
    orchestrator.register_workflow(workflow)
    return {"message": "Workflow created", "workflow_id": workflow.workflow_id}

@router.get("/health")
async def health_check():
    """健康检查"""
    agents = registry.list_agents()
    agent_status = {}
    
    for agent_type, agent in agents.items():
        try:
            healthy = await agent.health_check()
            agent_status[agent_type.value] = "healthy" if healthy else "unhealthy"
        except:
            agent_status[agent_type.value] = "error"
    
    return {
        "status": "healthy",
        "agents": agent_status,
        "workflows": len(orchestrator.workflows)
    }

def generate_suggested_actions(results: dict) -> List[dict]:
    """基于 Agent 结果生成建议动作"""
    actions = []
    
    # 检查优先级
    priority_result = results.get("step_3")
    if priority_result and priority_result.success:
        priority_level = priority_result.result.get("priority_level")
        if priority_level in ["critical", "high"]:
            actions.append({
                "type": "mark_important",
                "label": "标记为重要",
                "icon": "🔴"
            })
    
    # 检查是否需要回复
    summary_result = results.get("step_1")
    if summary_result and summary_result.success:
        action_items = summary_result.result.get("action_items", [])
        if action_items:
            actions.append({
                "type": "generate_reply",
                "label": "生成回复",
                "icon": "📝"
            })
    
    # 检查分类
    classifier_result = results.get("step_2")
    if classifier_result and classifier_result.success:
        category = classifier_result.result.get("primary_category")
        if category == "newsletter":
            actions.append({
                "type": "archive",
                "label": "归档",
                "icon": "📦"
            })
    
    return actions
