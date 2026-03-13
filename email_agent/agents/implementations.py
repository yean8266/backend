"""
Summarizer Agent - 邮件总结 Agent
"""

import json
from typing import Dict, Any
import logging

from openai import AsyncOpenAI

from email_agent.agents.base import BaseAgent, registry
from email_agent.models import AgentInput, AgentOutput, AgentType
from email_agent.config import settings

logger = logging.getLogger(__name__)

class SummarizerAgent(BaseAgent):
    """
    邮件总结 Agent
    
    功能：
    - 生成邮件摘要
    - 提取关键信息
    - 识别行动项
    - 情感分析
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.agent_type = AgentType.SUMMARIZER
        self.client: AsyncOpenAI = None
    
    async def _setup(self):
        """初始化 OpenAI 客户端"""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """处理邮件并生成总结"""
        email = input_data.email
        
        # 构建 prompt
        system_prompt = """你是一个专业的邮件分析助手。请分析以下邮件并提供结构化总结。

请提供以下信息（JSON格式）：
{
    "summary": "邮件一句话总结",
    "key_points": ["要点1", "要点2", "要点3"],
    "action_items": ["行动项1", "行动项2"],
    "deadline": "截止日期（如果有）",
    "sentiment": "positive/negative/neutral",
    "category": "work/personal/newsletter/notification/promotional",
    "confidence": 0.95
}"""

        user_prompt = f"""Subject: {email.subject}
From: {email.from_address}
Date: {email.date}

Content:
{email.body_text or email.body_html}
"""
        
        # 调用 LLM
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000
        )
        
        # 解析结果
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        return AgentOutput(
            agent_type=self.agent_type,
            success=True,
            result=result,
            processing_time=0,
            metadata={
                "model": settings.OPENAI_MODEL,
                "tokens": response.usage.total_tokens if response.usage else 0
            }
        )

class ClassifierAgent(BaseAgent):
    """
    分类 Agent
    
    功能：
    - 邮件分类（工作/个人/新闻/通知等）
    - 子类别识别
    - 标签建议
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.agent_type = AgentType.CLASSIFIER
        self.client: AsyncOpenAI = None
        
        # 预定义分类
        self.categories = {
            "work": ["meeting", "task", "report", "approval", "collaboration"],
            "personal": ["family", "friend", "hobby", "health"],
            "newsletter": ["tech", "business", "marketing", "update"],
            "notification": ["alert", "reminder", "system"],
            "promotional": ["sales", "discount", "product"]
        }
    
    async def _setup(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """分类邮件"""
        email = input_data.email
        
        system_prompt = f"""对邮件进行分类。可选类别：{list(self.categories.keys())}

请提供（JSON格式）：
{{
    "primary_category": "主要类别",
    "sub_category": "子类别",
    "tags": ["标签1", "标签2"],
    "confidence": 0.95,
    "reasoning": "分类理由"
}}"""

        user_prompt = f"Subject: {email.subject}\nFrom: {email.from_address}\n\nContent:\n{email.body_text[:1000]}"
        
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return AgentOutput(
            agent_type=self.agent_type,
            success=True,
            result=result,
            processing_time=0
        )

class PriorityAgent(BaseAgent):
    """
    优先级 Agent
    
    功能：
    - 计算邮件优先级
    - 识别紧急程度
    - 建议处理时间
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.agent_type = AgentType.PRIORITY
        self.client: AsyncOpenAI = None
    
    async def _setup(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """计算优先级"""
        email = input_data.email
        preferences = input_data.user_preferences or {}
        
        # 获取重要发件人列表
        important_senders = preferences.get("important_senders", [])
        
        system_prompt = """评估邮件优先级。请提供（JSON格式）：
{
    "priority_score": 85,
    "priority_level": "high",
    "urgency_indicators": ["deadline", "boss_request"],
    "suggested_action_time": "today",
    "reasoning": "理由说明"
}"""

        user_prompt = f"""Subject: {email.subject}
From: {email.from_address}
Important senders: {important_senders}

Content:
{email.body_text[:800]}"""
        
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return AgentOutput(
            agent_type=self.agent_type,
            success=True,
            result=result,
            processing_time=0
        )

class TemplateAgent(BaseAgent):
    """
    模板 Agent
    
    功能：
    - 生成回复模板
    - 匹配预定义模板
    - 变量替换
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.agent_type = AgentType.TEMPLATE
        self.client: AsyncOpenAI = None
        
        # 预定义模板
        self.templates = {
            "meeting_request": {
                "subject": "Re: {original_subject}",
                "body": "Hi {sender_name},\n\nI'd be happy to meet. How about {suggested_time}?\n\nBest"
            },
            "acknowledgment": {
                "subject": "Re: {original_subject}",
                "body": "Hi {sender_name},\n\nThank you for your email. I'll get back to you soon.\n\nBest"
            },
            "follow_up": {
                "subject": "Follow-up: {original_subject}",
                "body": "Hi {sender_name},\n\nJust following up on {topic}. Any updates?\n\nBest"
            }
        }
    
    async def _setup(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """生成回复建议"""
        email = input_data.email
        context = input_data.context
        
        tone = context.get("tone", "professional")
        
        system_prompt = f"""根据邮件内容生成3个不同风格的回复建议。
语气：{tone}

请提供（JSON格式）：
{{
    "suggestions": [
        {{
            "style": "简洁版",
            "subject": "回复主题",
            "body": "回复内容",
            "confidence": 0.95
        }}
    ],
    "recommended_template": "template_id"
}}"""

        user_prompt = f"""Original Subject: {email.subject}
From: {email.from_address}

Original Content:
{email.body_text[:600]}"""
        
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return AgentOutput(
            agent_type=self.agent_type,
            success=True,
            result=result,
            processing_time=0
        )

# 注册所有 Agent
async def register_all_agents():
    """注册所有 Agent 到全局注册表"""
    agents = [
        SummarizerAgent(),
        ClassifierAgent(),
        PriorityAgent(),
        TemplateAgent()
    ]
    
    for agent in agents:
        registry.register(agent.agent_type, agent)
    
    # 初始化所有 Agent
    await registry.initialize_all()
    
    logger.info(f"Registered {len(agents)} agents")
