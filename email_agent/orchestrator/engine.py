"""
Agent 编排引擎
支持顺序、并行、条件分支工作流
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from email_agent.models import (
    AgentInput, AgentOutput, WorkflowDefinition, WorkflowStep,
    WorkflowTask, TaskStatus, WorkflowType
)
from email_agent.agents.base import registry

logger = logging.getLogger(__name__)

@dataclass
class ExecutionContext:
    """执行上下文"""
    task_id: str
    email_id: str
    results: Dict[str, AgentOutput] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)

class AgentOrchestrator:
    """
    Agent 编排引擎
    
    支持的工作流类型：
    1. Sequential: 顺序执行
    2. Parallel: 并行执行
    3. Conditional: 条件分支
    """
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.active_tasks: Dict[str, WorkflowTask] = {}
    
    async def initialize(self):
        """初始化编排引擎"""
        # 注册默认工作流
        await self._register_default_workflows()
        logger.info("Orchestrator initialized")
    
    async def shutdown(self):
        """关闭编排引擎"""
        # 取消所有活动任务
        for task in self.active_tasks.values():
            task.status = TaskStatus.CANCELLED
        logger.info("Orchestrator shutdown")
    
    async def _register_default_workflows(self):
        """注册默认工作流"""
        # 默认顺序工作流
        default_workflow = WorkflowDefinition(
            workflow_id="default",
            name="默认分析工作流",
            description="顺序执行：总结 -> 分类 -> 优先级",
            type=WorkflowType.SEQUENTIAL,
            steps=[
                WorkflowStep(step_id="step_1", agent_type="summarizer"),
                WorkflowStep(step_id="step_2", agent_type="classifier"),
                WorkflowStep(step_id="step_3", agent_type="priority")
            ]
        )
        
        # 并行分析工作流
        parallel_workflow = WorkflowDefinition(
            workflow_id="parallel",
            name="并行分析工作流",
            description="并行执行：总结、分类、优先级同时运行",
            type=WorkflowType.PARALLEL,
            steps=[
                WorkflowStep(step_id="step_1", agent_type="summarizer"),
                WorkflowStep(step_id="step_2", agent_type="classifier"),
                WorkflowStep(step_id="step_3", agent_type="priority")
            ]
        )
        
        # 带模板的完整工作流
        full_workflow = WorkflowDefinition(
            workflow_id="full",
            name="完整工作流",
            description="分析 + 生成回复模板",
            type=WorkflowType.SEQUENTIAL,
            steps=[
                WorkflowStep(step_id="step_1", agent_type="summarizer"),
                WorkflowStep(step_id="step_2", agent_type="classifier"),
                WorkflowStep(step_id="step_3", agent_type="priority"),
                WorkflowStep(step_id="step_4", agent_type="template")
            ]
        )
        
        self.workflows[default_workflow.workflow_id] = default_workflow
        self.workflows[parallel_workflow.workflow_id] = parallel_workflow
        self.workflows[full_workflow.workflow_id] = full_workflow
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """注册自定义工作流"""
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Registered workflow: {workflow.workflow_id}")
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: AgentInput,
        task_id: Optional[str] = None
    ) -> WorkflowTask:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            input_data: 输入数据
            task_id: 可选的任务ID
            
        Returns:
            WorkflowTask 任务结果
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        task = WorkflowTask(
            task_id=task_id or self._generate_task_id(),
            workflow_id=workflow_id,
            email_id=input_data.email.id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.active_tasks[task.task_id] = task
        
        try:
            # 根据工作流类型执行
            if workflow.type == WorkflowType.SEQUENTIAL:
                await self._execute_sequential(workflow, input_data, task)
            elif workflow.type == WorkflowType.PARALLEL:
                await self._execute_parallel(workflow, input_data, task)
            elif workflow.type == WorkflowType.CONDITIONAL:
                await self._execute_conditional(workflow, input_data, task)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            logger.error(f"Workflow {workflow_id} failed: {e}")
        
        return task
    
    async def _execute_sequential(
        self,
        workflow: WorkflowDefinition,
        input_data: AgentInput,
        task: WorkflowTask
    ):
        """顺序执行工作流"""
        context = input_data.context or {}
        
        for step in workflow.steps:
            logger.debug(f"Executing step {step.step_id}: {step.agent_type}")
            
            # 获取 Agent
            agent = registry.get(step.agent_type)
            
            # 构建输入（包含之前步骤的结果）
            step_input = AgentInput(
                email=input_data.email,
                context=context,
                user_preferences=input_data.user_preferences
            )
            
            # 执行 Agent
            result = await agent.execute(step_input)
            
            # 保存结果
            task.steps_results[step.step_id] = result
            
            # 更新上下文，供后续步骤使用
            if result.success:
                context[f"{step.agent_type.value}_result"] = result.result
            else:
                logger.warning(f"Step {step.step_id} failed: {result.error_message}")
    
    async def _execute_parallel(
        self,
        workflow: WorkflowDefinition,
        input_data: AgentInput,
        task: WorkflowTask
    ):
        """并行执行工作流"""
        
        async def execute_step(step: WorkflowStep):
            """执行单个步骤"""
            agent = registry.get(step.agent_type)
            result = await agent.execute(input_data)
            return step.step_id, result
        
        # 并行执行所有步骤
        results = await asyncio.gather(
            *[execute_step(step) for step in workflow.steps],
            return_exceptions=True
        )
        
        # 收集结果
        for step_id, result in results:
            if isinstance(result, Exception):
                task.steps_results[step_id] = AgentOutput(
                    agent_type=None,
                    success=False,
                    result={},
                    error_message=str(result)
                )
            else:
                task.steps_results[step_id] = result
    
    async def _execute_conditional(
        self,
        workflow: WorkflowDefinition,
        input_data: AgentInput,
        task: WorkflowTask
    ):
        """条件执行工作流（简化版）"""
        # 先执行前几个必要步骤获取上下文
        context = input_data.context or {}
        
        for step in workflow.steps:
            # 检查条件
            if step.condition:
                if not self._evaluate_condition(step.condition, context):
                    logger.debug(f"Skipping step {step.step_id}, condition not met")
                    continue
            
            agent = registry.get(step.agent_type)
            step_input = AgentInput(
                email=input_data.email,
                context=context,
                user_preferences=input_data.user_preferences
            )
            
            result = await agent.execute(step_input)
            task.steps_results[step.step_id] = result
            
            if result.success:
                context[f"{step.agent_type.value}_result"] = result.result
    
    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """评估条件表达式（简化实现）"""
        # TODO: 实现完整的条件表达式解析
        # 目前只支持简单的键值检查
        try:
            parts = condition.split("==")
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().strip("'")
                return context.get(key) == value
            return True
        except:
            return True
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        import uuid
        return f"task_{uuid.uuid4().hex[:12]}"
    
    async def get_task_status(self, task_id: str) -> Optional[WorkflowTask]:
        """获取任务状态"""
        return self.active_tasks.get(task_id)
    
    def get_workflow_list(self) -> List[WorkflowDefinition]:
        """获取所有工作流列表"""
        return list(self.workflows.values())
