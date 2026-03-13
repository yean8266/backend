"""
Agent 基类测试
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from app.agents.base import BaseAgent, AgentRegistry
from app.models import AgentInput, AgentOutput, AgentType, Email

class TestAgent(BaseAgent):
    """测试用的 Agent"""
    def __init__(self, config=None):
        super().__init__(config)
        self.agent_type = AgentType.SUMMARIZER
    
    async def _setup(self):
        pass
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        return AgentOutput(
            agent_type=self.agent_type,
            success=True,
            result={"test": "data"},
            processing_time=0.5
        )

@pytest.mark.asyncio
class TestBaseAgent:
    """测试 Agent 基类"""
    
    async def test_initialization(self):
        """测试初始化"""
        agent = TestAgent()
        assert not agent.initialized
        
        await agent.initialize()
        assert agent.initialized
    
    async def test_execute_success(self, sample_email_data):
        """测试成功执行"""
        agent = TestAgent()
        email = Email(**sample_email_data)
        input_data = AgentInput(email=email)
        
        result = await agent.execute(input_data)
        
        assert result.success is True
        assert result.agent_type == AgentType.SUMMARIZER
        assert result.result == {"test": "data"}
        assert result.processing_time > 0
        assert result.error_message is None
    
    async def test_execute_failure(self, sample_email_data):
        """测试执行失败"""
        agent = TestAgent()
        
        # Mock process 方法抛出异常
        async def mock_process(*args, **kwargs):
            raise ValueError("Test error")
        
        agent.process = mock_process
        
        email = Email(**sample_email_data)
        input_data = AgentInput(email=email)
        
        result = await agent.execute(input_data)
        
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.processing_time >= 0
    
    async def test_execute_timing(self, sample_email_data):
        """测试执行计时"""
        import asyncio
        
        class SlowAgent(TestAgent):
            async def process(self, input_data):
                await asyncio.sleep(0.1)
                return AgentOutput(
                    agent_type=self.agent_type,
                    success=True,
                    result={},
                    processing_time=0
                )
        
        agent = SlowAgent()
        email = Email(**sample_email_data)
        input_data = AgentInput(email=email)
        
        result = await agent.execute(input_data)
        
        # 验证计时准确性 (允许 ±50ms 误差)
        assert 0.05 <= result.processing_time <= 0.2
    
    async def test_health_check(self):
        """测试健康检查"""
        agent = TestAgent()
        healthy = await agent.health_check()
        assert healthy is True

@pytest.mark.asyncio
class TestAgentRegistry:
    """测试 Agent 注册表"""
    
    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """每个测试前重置注册表"""
        registry = AgentRegistry()
        registry._agents = {}
        yield
    
    async def test_register_agent(self):
        """测试注册 Agent"""
        registry = AgentRegistry()
        agent = TestAgent()
        
        registry.register(AgentType.SUMMARIZER, agent)
        
        assert len(registry._agents) == 1
        assert AgentType.SUMMARIZER in registry._agents
    
    async def test_get_agent(self):
        """测试获取 Agent"""
        registry = AgentRegistry()
        agent = TestAgent()
        registry.register(AgentType.SUMMARIZER, agent)
        
        retrieved = registry.get(AgentType.SUMMARIZER)
        assert retrieved == agent
    
    async def test_get_nonexistent_agent(self):
        """测试获取不存在的 Agent"""
        registry = AgentRegistry()
        
        with pytest.raises(ValueError, match="not registered"):
            registry.get(AgentType.CLASSIFIER)
    
    async def test_list_agents(self):
        """测试列出所有 Agent"""
        registry = AgentRegistry()
        agent1 = TestAgent()
        agent2 = TestAgent()
        agent2.agent_type = AgentType.CLASSIFIER
        
        registry.register(AgentType.SUMMARIZER, agent1)
        registry.register(AgentType.CLASSIFIER, agent2)
        
        agents = registry.list_agents()
        assert len(agents) == 2
        assert AgentType.SUMMARIZER in agents
        assert AgentType.CLASSIFIER in agents
    
    async def test_initialize_all(self, sample_email_data):
        """测试初始化所有 Agent"""
        registry = AgentRegistry()
        agent = TestAgent()
        registry.register(AgentType.SUMMARIZER, agent)
        
        await registry.initialize_all()
        
        assert agent.initialized
    
    async def test_shutdown_all(self):
        """测试关闭所有 Agent"""
        registry = AgentRegistry()
        agent = TestAgent()
        registry.register(AgentType.SUMMARIZER, agent)
        
        await registry.shutdown_all()
        # 验证没有抛出异常
