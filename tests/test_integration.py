"""
集成测试
测试完整的邮件处理流程
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.orchestrator.engine import AgentOrchestrator
from app.models import (
    AgentInput, Email, WorkflowType, TaskStatus, AgentType, AgentOutput
)

@pytest.mark.asyncio
class TestEmailProcessingIntegration:
    """邮件处理集成测试"""
    
    @pytest.fixture
    async def orchestrator(self):
        """创建编排引擎"""
        orch = AgentOrchestrator()
        await orch.initialize()
        yield orch
        await orch.shutdown()
    
    @pytest.fixture
    def work_email(self):
        """工作邮件"""
        return Email(
            id="work_001",
            subject="Urgent: Q4 Budget Approval Needed",
            from_address="boss@company.com",
            to_addresses=["employee@company.com"],
            body_text="""Hi,

Please review and approve the Q4 budget plan by today 5pm.
This is urgent as we need to submit to finance tomorrow.

Key points:
- Total budget: 5M RMB
- 3 major projects: AI platform, Mobile app, Cloud migration
- Expected ROI: 150%

Please let me know if you have any questions.

Best regards,
Director""",
            date=datetime(2024, 1, 15, 9, 30, 0)
        )
    
    @pytest.fixture
    def newsletter_email(self):
        """新闻通讯邮件"""
        return Email(
            id="news_001",
            subject="Weekly Tech Newsletter #234",
            from_address="newsletter@tech.com",
            to_addresses=["user@gmail.com"],
            body_text="""Hi Subscriber,

This week's top stories:
1. New AI breakthrough in natural language processing
2. Framework updates and releases
3. Cloud computing cost optimization tips

Click here to unsubscribe: [unsubscribe link]

Best,
Tech Team""",
            date=datetime(2024, 1, 15, 10, 0, 0)
        )
    
    async def test_work_email_processing(self, orchestrator, work_email):
        """测试工作邮件处理流程"""
        
        # Mock 所有 Agent
        mock_results = {
            AgentType.SUMMARIZER: AgentOutput(
                agent_type=AgentType.SUMMARIZER,
                success=True,
                result={
                    "summary": "Urgent budget approval request",
                    "key_points": ["5M budget", "3 projects", "Due today"],
                    "action_items": ["Review budget", "Send approval"],
                    "sentiment": "neutral"
                },
                processing_time=0.5
            ),
            AgentType.CLASSIFIER: AgentOutput(
                agent_type=AgentType.CLASSIFIER,
                success=True,
                result={
                    "primary_category": "work",
                    "sub_category": "finance",
                    "tags": ["budget", "approval", "urgent"]
                },
                processing_time=0.3
            ),
            AgentType.PRIORITY: AgentOutput(
                agent_type=AgentType.PRIORITY,
                success=True,
                result={
                    "priority_score": 95,
                    "priority_level": "high",
                    "urgency_indicators": ["deadline", "boss_request"]
                },
                processing_time=0.2
            )
        }
        
        with patch('app.orchestrator.engine.registry') as mock_registry:
            def mock_get(agent_type):
                agent = AsyncMock()
                agent.execute = AsyncMock(return_value=mock_results[agent_type])
                return agent
            
            mock_registry.get = mock_get
            
            # 执行工作流
            input_data = AgentInput(email=work_email)
            task = await orchestrator.execute_workflow("default", input_data)
            
            # 验证结果
            assert task.status == TaskStatus.COMPLETED
            assert len(task.steps_results) == 3
            
            # 验证优先级
            priority_result = task.steps_results["step_3"]
            assert priority_result.result["priority_level"] == "high"
            assert priority_result.result["priority_score"] == 95
            
            # 验证分类
            classifier_result = task.steps_results["step_2"]
            assert classifier_result.result["primary_category"] == "work"
    
    async def test_newsletter_email_processing(self, orchestrator, newsletter_email):
        """测试新闻通讯邮件处理"""
        
        mock_results = {
            AgentType.SUMMARIZER: AgentOutput(
                agent_type=AgentType.SUMMARIZER,
                success=True,
                result={
                    "summary": "Weekly tech newsletter",
                    "key_points": ["AI news", "Framework updates"],
                    "sentiment": "positive"
                },
                processing_time=0.5
            ),
            AgentType.CLASSIFIER: AgentOutput(
                agent_type=AgentType.CLASSIFIER,
                success=True,
                result={
                    "primary_category": "newsletter",
                    "sub_category": "tech",
                    "tags": ["news", "tech"]
                },
                processing_time=0.3
            ),
            AgentType.PRIORITY: AgentOutput(
                agent_type=AgentType.PRIORITY,
                success=True,
                result={
                    "priority_score": 20,
                    "priority_level": "low"
                },
                processing_time=0.2
            )
        }
        
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: AsyncMock(
                execute=AsyncMock(return_value=mock_results[x])
            )
            
            input_data = AgentInput(email=newsletter_email)
            task = await orchestrator.execute_workflow("default", input_data)
            
            assert task.status == TaskStatus.COMPLETED
            
            # 新闻通讯应该是低优先级
            priority_result = task.steps_results["step_3"]
            assert priority_result.result["priority_level"] == "low"
            
            # 分类应该是 newsletter
            classifier_result = task.steps_results["step_2"]
            assert classifier_result.result["primary_category"] == "newsletter"
    
    async def test_parallel_workflow_performance(self, orchestrator, work_email):
        """测试并行工作流性能"""
        
        async def slow_execute(*args, **kwargs):
            await asyncio.sleep(0.1)
            return AgentOutput(
                agent_type=AgentType.SUMMARIZER,
                success=True,
                result={},
                processing_time=0.1
            )
        
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: AsyncMock(execute=slow_execute)
            
            input_data = AgentInput(email=work_email)
            
            # 测量执行时间
            start = asyncio.get_event_loop().time()
            task = await orchestrator.execute_workflow("parallel", input_data)
            elapsed = asyncio.get_event_loop().time() - start
            
            assert task.status == TaskStatus.COMPLETED
            # 并行执行 3 个 0.1s 的任务应该 < 0.2s
            assert elapsed < 0.2

@pytest.mark.asyncio
class TestErrorHandlingIntegration:
    """错误处理集成测试"""
    
    @pytest.fixture
    async def orchestrator(self):
        orch = AgentOrchestrator()
        await orch.initialize()
        yield orch
        await orch.shutdown()
    
    @pytest.fixture
    def sample_email(self):
        return Email(
            id="test_001",
            subject="Test",
            from_address="test@test.com",
            to_addresses=["user@test.com"],
            body_text="Test content",
            date=datetime.now()
        )
    
    async def test_agent_failure_handling(self, orchestrator, sample_email):
        """测试 Agent 失败处理"""
        
        call_count = 0
        
        async def conditional_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # 第一个 Agent 失败
                return AgentOutput(
                    agent_type=AgentType.SUMMARIZER,
                    success=False,
                    result={},
                    processing_time=0.1,
                    error_message="LLM API error"
                )
            return AgentOutput(
                agent_type=AgentType.CLASSIFIER,
                success=True,
                result={},
                processing_time=0.1
            )
        
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: AsyncMock(execute=conditional_execute)
            
            input_data = AgentInput(email=sample_email)
            task = await orchestrator.execute_workflow("default", input_data)
            
            # 工作流应该继续执行
            assert task.status == TaskStatus.COMPLETED
            
            # 第一个步骤应该记录失败
            first_step = task.steps_results.get("step_1")
            assert first_step is not None
            assert not first_step.success
    
    async def test_workflow_not_found(self, orchestrator, sample_email):
        """测试工作流不存在"""
        input_data = AgentInput(email=sample_email)
        
        with pytest.raises(ValueError, match="not found"):
            await orchestrator.execute_workflow("nonexistent", input_data)

@pytest.mark.asyncio
class TestContextPassingIntegration:
    """上下文传递集成测试"""
    
    @pytest.fixture
    async def orchestrator(self):
        orch = AgentOrchestrator()
        await orch.initialize()
        yield orch
        await orch.shutdown()
    
    async def test_context_accumulation(self, orchestrator):
        """测试上下文累积"""
        email = Email(
            id="ctx_test",
            subject="Context Test",
            from_address="test@test.com",
            to_addresses=["user@test.com"],
            body_text="Test",
            date=datetime.now()
        )
        
        contexts = []
        
        async def capture_context(input_data):
            contexts.append(input_data.context.copy())
            return AgentOutput(
                agent_type=AgentType.SUMMARIZER,
                success=True,
                result={"key": f"value_{len(contexts)}"},
                processing_time=0.1
            )
        
        with patch('app.orchestrator.engine.registry') as mock_registry:
            mock_registry.get = lambda x: AsyncMock(execute=capture_context)
            
            input_data = AgentInput(email=email, context={"initial": "data"})
            task = await orchestrator.execute_workflow("default", input_data)
            
            # 验证上下文传递
            assert len(contexts) == 3
            assert contexts[0] == {"initial": "data"}
            assert "summarizer_result" in contexts[1]
