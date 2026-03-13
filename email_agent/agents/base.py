"""
Agent 基类定义
所有 Agent 必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import time
import logging

from email_agent.models import AgentInput, AgentOutput, AgentType

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agent_type: AgentType = None
        self.initialized = False
    
    async def initialize(self):
        """初始化 Agent"""
        if not self.initialized:
            await self._setup()
            self.initialized = True
            logger.info(f"Agent {self.agent_type.value} initialized")
    
    @abstractmethod
    async def _setup(self):
        """子类实现具体初始化逻辑"""
        pass
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        处理输入数据
        
        Args:
            input_data: AgentInput 包含邮件和上下文
            
        Returns:
            AgentOutput 处理结果
        """
        pass
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        执行 Agent（包装 process，添加通用逻辑）
        
        包括：
        - 初始化检查
        - 执行计时
        - 错误处理
        """
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            result = await self.process(input_data)
            result.processing_time = time.time() - start_time
            result.agent_type = self.agent_type
            result.success = True
            
            logger.debug(f"Agent {self.agent_type.value} completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Agent {self.agent_type.value} failed: {str(e)}")
            
            return AgentOutput(
                agent_type=self.agent_type,
                success=False,
                result={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def health_check(self) -> bool:
        """健康检查"""
        return True

class AgentRegistry:
    """Agent 注册表 - 管理所有 Agent"""
    
    _instance = None
    _agents: Dict[AgentType, BaseAgent] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, agent_type: AgentType, agent: BaseAgent):
        """注册 Agent"""
        self._agents[agent_type] = agent
        logger.info(f"Registered agent: {agent_type.value}")
    
    def get(self, agent_type: AgentType) -> BaseAgent:
        """获取 Agent"""
        if agent_type not in self._agents:
            raise ValueError(f"Agent {agent_type.value} not registered")
        return self._agents[agent_type]
    
    def list_agents(self) -> Dict[AgentType, BaseAgent]:
        """列出所有 Agent"""
        return self._agents.copy()
    
    async def initialize_all(self):
        """初始化所有 Agent"""
        for agent_type, agent in self._agents.items():
            try:
                await agent.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize {agent_type.value}: {e}")
    
    async def shutdown_all(self):
        """关闭所有 Agent"""
        for agent in self._agents.values():
            try:
                if hasattr(agent, 'shutdown'):
                    await agent.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down agent: {e}")

# 全局注册表实例
registry = AgentRegistry()
