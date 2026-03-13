"""
数据模型定义
使用 Pydantic 进行数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    """Agent 类型枚举"""
    SUMMARIZER = "summarizer"
    CLASSIFIER = "classifier"
    PRIORITY = "priority"
    TEMPLATE = "template"
    REPLY_GENERATOR = "reply_generator"
    ACTION_PLANNER = "action_planner"

class WorkflowType(str, Enum):
    """工作流类型"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PriorityLevel(int, Enum):
    """优先级等级"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    IGNORE = 0

# ==================== 邮件相关模型 ====================

class Email(BaseModel):
    """邮件数据模型"""
    id: str
    subject: str
    from_address: str
    to_addresses: List[str]
    cc_addresses: Optional[List[str]] = None
    bcc_addresses: Optional[List[str]] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    date: datetime
    attachments: Optional[List[Dict[str, Any]]] = None
    headers: Optional[Dict[str, str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_12345",
                "subject": "Q4预算审批",
                "from_address": "boss@company.com",
                "to_addresses": ["me@company.com"],
                "body_text": "请尽快审批Q4预算...",
                "date": "2024-01-15T09:30:00"
            }
        }

# ==================== Agent 相关模型 ====================

class AgentInput(BaseModel):
    """Agent 输入"""
    email: Email
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AgentOutput(BaseModel):
    """Agent 输出"""
    agent_type: AgentType
    success: bool
    result: Dict[str, Any]
    processing_time: float  # 秒
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentConfig(BaseModel):
    """Agent 配置"""
    agent_type: AgentType
    enabled: bool = True
    priority: int = 5  # 1-10
    config: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = 30

# ==================== 工作流相关模型 ====================

class WorkflowStep(BaseModel):
    """工作流步骤"""
    step_id: str
    agent_type: AgentType
    depends_on: Optional[List[str]] = None  # 依赖的步骤ID
    condition: Optional[str] = None  # 条件表达式 (conditional workflow)
    config: Optional[Dict[str, Any]] = None

class WorkflowDefinition(BaseModel):
    """工作流定义"""
    workflow_id: str
    name: str
    description: Optional[str] = None
    type: WorkflowType = WorkflowType.SEQUENTIAL
    steps: List[WorkflowStep]
    created_at: datetime = Field(default_factory=datetime.now)

class WorkflowTask(BaseModel):
    """工作流任务实例"""
    task_id: str
    workflow_id: str
    email_id: str
    status: TaskStatus = TaskStatus.PENDING
    steps_results: Dict[str, AgentOutput] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

# ==================== API 请求/响应模型 ====================

class AnalyzeRequest(BaseModel):
    """分析请求"""
    email: Email
    workflow_id: Optional[str] = "default"
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class AnalyzeResponse(BaseModel):
    """分析响应"""
    task_id: str
    status: TaskStatus
    results: Dict[str, AgentOutput]
    overall_priority: Optional[PriorityLevel] = None
    suggested_actions: Optional[List[Dict[str, Any]]] = None

class GenerateReplyRequest(BaseModel):
    """生成回复请求"""
    email: Email
    tone: Optional[str] = "professional"  # professional/casual/friendly
    template_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class GenerateReplyResponse(BaseModel):
    """生成回复响应"""
    reply_text: str
    reply_html: Optional[str] = None
    subject: Optional[str] = None
    confidence: float
    alternatives: Optional[List[str]] = None

class StreamResponse(BaseModel):
    """流式响应 (WebSocket)"""
    type: Literal["status", "progress", "result", "error"]
    task_id: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
