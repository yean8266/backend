"""
测试配置和 fixtures
"""

import pytest
import pytest_asyncio
from datetime import datetime
from typing import Generator
import asyncio

# 设置事件循环策略
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_email_data():
    """示例邮件数据"""
    return {
        "id": "test_msg_001",
        "subject": "Q4预算审批需要立即确认",
        "from_address": "boss@company.com",
        "to_addresses": ["employee@company.com"],
        "cc_addresses": [],
        "body_text": """Hi,

Please review and approve the Q4 budget plan by today 5pm.

Key points:
- Total budget: 5M RMB
- 3 major projects
- Deadline: Jan 20, 2024

Let me know if you have any questions.

Best,
Boss""",
        "body_html": None,
        "date": datetime(2024, 1, 15, 9, 30, 0),
        "attachments": [],
        "headers": {}
    }

@pytest.fixture
def sample_newsletter_email():
    """示例新闻通讯邮件"""
    return {
        "id": "test_msg_002",
        "subject": "Weekly Tech Newsletter #234",
        "from_address": "newsletter@tech.com",
        "to_addresses": ["user@gmail.com"],
        "body_text": """Hi Subscriber,

This week's top stories:
1. AI breakthrough in natural language
2. New framework released
3. Cloud computing trends

Unsubscribe: click here

Best,
Tech Team""",
        "date": datetime(2024, 1, 15, 10, 0, 0)
    }

@pytest.fixture
def sample_personal_email():
    """示例个人邮件"""
    return {
        "id": "test_msg_003",
        "subject": "周末聚会安排",
        "from_address": "friend@personal.com",
        "to_addresses": ["user@gmail.com"],
        "body_text": "Hey, are you free this Saturday? Let's grab dinner!",
        "date": datetime(2024, 1, 15, 14, 0, 0)
    }

@pytest.fixture
def mock_llm_response():
    """模拟 LLM 响应"""
    return {
        "summary": "This is a test summary",
        "key_points": ["Point 1", "Point 2"],
        "action_items": ["Action 1"],
        "sentiment": "neutral",
        "category": "work"
    }
