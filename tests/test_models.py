"""
模型验证测试
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models import (
    Email, AgentInput, AgentOutput, WorkflowDefinition, WorkflowStep,
    AgentType, WorkflowType, PriorityLevel
)

class TestEmailModel:
    """测试邮件模型"""
    
    def test_email_creation(self):
        """测试创建邮件"""
        email = Email(
            id="msg_123",
            subject="Test Subject",
            from_address="from@test.com",
            to_addresses=["to@test.com"],
            body_text="Test body",
            date=datetime(2024, 1, 15, 9, 30, 0)
        )
        
        assert email.id == "msg_123"
        assert email.subject == "Test Subject"
        assert email.body_html is None  # 可选字段
    
    def test_email_validation_missing_required(self):
        """测试缺少必填字段"""
        with pytest.raises(ValidationError):
            Email(
                subject="Test",  # 缺少 id, from_address 等
                date=datetime.now()
            )
    
    def test_email_with_optional_fields(self):
        """测试带可选字段的邮件"""
        email = Email(
            id="msg_123",
            subject="Test",
            from_address="from@test.com",
            to_addresses=["to@test.com"],
            cc_addresses=["cc@test.com"],
            bcc_addresses=["bcc@test.com"],
            body_text="Text",
            body_html="<p>HTML</p>",
            attachments=[{"filename": "test.pdf"}],
            date=datetime.now()
        )
        
        assert len(email.cc_addresses) == 1
        assert len(email.attachments) == 1

class TestWorkflowModel:
    """测试工作流模型"""
    
    def test_workflow_definition(self):
        """测试工作流定义"""
        workflow = WorkflowDefinition(
            workflow_id="test_flow",
            name="Test Workflow",
            type=WorkflowType.SEQUENTIAL,
            steps=[
                WorkflowStep(step_id="s1", agent_type=AgentType.SUMMARIZER),
                WorkflowStep(step_id="s2", agent_type=AgentType.CLASSIFIER)
            ]
        )
        
        assert workflow.workflow_id == "test_flow"
        assert len(workflow.steps) == 2
        assert workflow.type == WorkflowType.SEQUENTIAL
    
    def test_workflow_step_with_condition(self):
        """测试带条件的工作流步骤"""
        step = WorkflowStep(
            step_id="s1",
            agent_type=AgentType.PRIORITY,
            condition="priority == 'high'",
            depends_on=["s0"]
        )
        
        assert step.condition == "priority == 'high'"
        assert step.depends_on == ["s0"]

class TestAgentModels:
    """测试 Agent 相关模型"""
    
    def test_agent_input(self):
        """测试 Agent 输入"""
        email = Email(
            id="msg_123",
            subject="Test",
            from_address="from@test.com",
            to_addresses=["to@test.com"],
            body_text="Test",
            date=datetime.now()
        )
        
        agent_input = AgentInput(
            email=email,
            context={"key": "value"},
            user_preferences={"timezone": "UTC"}
        )
        
        assert agent_input.email.id == "msg_123"
        assert agent_input.context["key"] == "value"
    
    def test_agent_output(self):
        """测试 Agent 输出"""
        output = AgentOutput(
            agent_type=AgentType.SUMMARIZER,
            success=True,
            result={"summary": "test"},
            processing_time=0.5,
            metadata={"tokens": 100}
        )
        
        assert output.agent_type == AgentType.SUMMARIZER
        assert output.success is True
        assert output.processing_time == 0.5

class TestEnumValidation:
    """测试枚举验证"""
    
    def test_agent_type_enum(self):
        """测试 Agent 类型枚举"""
        assert AgentType.SUMMARIZER.value == "summarizer"
        assert AgentType.CLASSIFIER.value == "classifier"
        
        # 验证无效值
        with pytest.raises(ValueError):
            AgentType("invalid")
    
    def test_workflow_type_enum(self):
        """测试工作流类型枚举"""
        assert WorkflowType.SEQUENTIAL.value == "sequential"
        assert WorkflowType.PARALLEL.value == "parallel"
    
    def test_priority_level_enum(self):
        """测试优先级枚举"""
        assert PriorityLevel.CRITICAL.value == 4
        assert PriorityLevel.HIGH.value == 3
        assert PriorityLevel.LOW.value == 1
