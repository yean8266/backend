"""
编排引擎测试
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.orchestrator.engine import AgentOrchestrator
from app.models import (
    AgentInput, AgentOutput, Email, WorkflowDefinition, 
    WorkflowStep, WorkflowType, TaskStatus, AgentType
)

@pytest.mark.asyncio
class TestAgentOrchestrator:
    """测试编排引擎"""
    
    @pytest.fixture
    async def orchestrator(self):
        """创建编排引擎实例"""
        orch = AgentOrchestrator()
        await orch.initialize()
        yield orch
        await orch.shutdown()
    
    @pytest.fixture
    def mock_agents(self):
        """创建模拟 Agent"""
        agents = {}
        for agent_type in [AgentType.SUMMARIZER, AgentType.CLASSIFIER, AgentType.PRIORITY]:
            mock_agent = AsyncMock()
            mock_agent.execute = AsyncMock(return_value=AgentOutput(
                agent_type=agent_type,
                success=True,
                result={"test": f"{agent_type.value}_result"},
                processing_time=0.1
            ))
            agents[agent_type] = mock_agent
        return agents
    
    async def test_initialization(self, orchestrator):
        """测试初始化"""
        assert len(orchestrator.workflows) == 3  # 默认工作流
        assert "default" in orchestrator.workflows
        assert "parallel" in orchestrator.workflows
        assert "full" in orchestrator.workflows
    
    async def test_register_workflow(self, orchestrator):
        """测试注册工作流"""
        workflow = WorkflowDefinition(
            workflow_id="test_workflow",
            name="Test Workflow",
            type=WorkflowType.SEQUENTIAL,
            steps=[
                WorkflowStep(step_id="step_1", agent_type=AgentType.SUMMARIZER)
            ]
        )
        
        orchestrator.register_workflow(workflow)
        
        assert "test_workflow" in orchestrator.workflows
        assert orchestrator.workflows["test_workflow"].name == "Test Workflow"
    
    async def test_execute_sequential_workflow(self, orchestrator, sample_email_data, mock_agents):
        """测试顺序工作流执行"""
        # Mock 注册表
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: mock_agents[x]
            
            email = Email(**sample_email_data)
            input_data = AgentInput(email=email)
            
            task = await orchestrator.execute_workflow("default", input_data)
            
            assert task.status == TaskStatus.COMPLETED
            assert len(task.steps_results) == 3
            assert task.workflow_id == "default"
            assert task.completed_at is not None
    
    async def test_execute_parallel_workflow(self, orchestrator, sample_email_data, mock_agents):
        """测试并行工作流执行"""
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: mock_agents[x]
            
            email = Email(**sample_email_data)
            input_data = AgentInput(email=email)
            
            # 记录开始时间
            start = asyncio.get_event_loop().time()
            task = await orchestrator.execute_workflow("parallel", input_data)
            elapsed = asyncio.get_event_loop().time() - start
            
            assert task.status == TaskStatus.COMPLETED
            assert len(task.steps_results) == 3
            # 并行执行应该更快 (3个0.1s的agent并行应该 < 0.3s)
            assert elapsed < 0.3
    
    async def test_execute_workflow_not_found(self, orchestrator, sample_email_data):
        """测试执行不存在的工作流"""
        email = Email(**sample_email_data)
        input_data = AgentInput(email=email)
        
        with pytest.raises(ValueError, match="not found"):
            await orchestrator.execute_workflow("nonexistent", input_data)
    
    async def test_workflow_step_failure(self, orchestrator, sample_email_data):
        """测试工作流步骤失败"""
        # 创建一个会失败的 mock agent
        failing_agent = AsyncMock()
        failing_agent.execute = AsyncMock(return_value=AgentOutput(
            agent_type=AgentType.SUMMARIZER,
            success=False,
            result={},
            processing_time=0.1,
            error_message="Processing failed"
        ))
        
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: failing_agent
            
            email = Email(**sample_email_data)
            input_data = AgentInput(email=email)
            
            task = await orchestrator.execute_workflow("default", input_data)
            
            # 工作流应该继续执行，但记录失败
            assert task.status == TaskStatus.COMPLETED
            assert not task.steps_results["step_1"].success
    
    async def test_get_task_status(self, orchestrator, sample_email_data, mock_agents):
        """测试获取任务状态"""
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: mock_agents[x]
            
            email = Email(**sample_email_data)
            input_data = AgentInput(email=email)
            
            task = await orchestrator.execute_workflow("default", input_data)
            retrieved_task = await orchestrator.get_task_status(task.task_id)
            
            assert retrieved_task is not None
            assert retrieved_task.task_id == task.task_id
    
    async def test_get_nonexistent_task(self, orchestrator):
        """测试获取不存在的任务"""
        task = await orchestrator.get_task_status("nonexistent")
        assert task is None
    
    async def test_context_passing(self, orchestrator, sample_email_data):
        """测试上下文传递"""
        results = []
        
        async def mock_process(input_data):
            results.append(input_data.context.copy())
            return AgentOutput(
                agent_type=AgentType.SUMMARIZER,
                success=True,
                result={"key": f"value_{len(results)}"},
                processing_time=0.1
            )
        
        mock_agent = AsyncMock()
        mock_agent.execute = mock_process
        
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: mock_agent
            
            email = Email(**sample_email_data)
            input_data = AgentInput(email=email, context={"initial": "data"})
            
            await orchestrator.execute_workflow("default", input_data)
            
            # 验证上下文在步骤间传递
            assert len(results) == 3
            # 后面的步骤应该包含前面步骤的结果
            assert "summarizer_result" in results[1]
    
    async def test_generate_task_id(self, orchestrator):
        """测试任务ID生成"""
        task_id = orchestrator._generate_task_id()
        
        assert task_id.startswith("task_")
        assert len(task_id) == 17  # task_ + 12位十六进制
    
    async def test_evaluate_condition(self, orchestrator):
        """测试条件表达式求值"""
        context = {"priority": "high", "category": "work"}
        
        # 测试相等条件
        assert orchestrator._evaluate_condition("priority == 'high'", context) is True
        assert orchestrator._evaluate_condition("priority == 'low'", context) is False
        
        # 测试无效条件（应该返回True继续执行）
        assert orchestrator._evaluate_condition("invalid", context) is True
