# Email Agent Backend

Multi-Agent Email Processing System

## 快速开始

### 1. 安装依赖

```bash
cd email-agent-backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key
```

### 3. 启动服务

```bash
python -m app.main
```

服务启动后访问: http://localhost:8000/docs

## 核心组件

### Agents

- **SummarizerAgent**: 邮件总结
- **ClassifierAgent**: 邮件分类
- **PriorityAgent**: 优先级计算
- **TemplateAgent**: 模板生成

### Orchestrator

支持的工作流类型:
- **Sequential**: 顺序执行
- **Parallel**: 并行执行
- **Conditional**: 条件分支

### API

REST API 端点:
- `POST /api/v1/analyze` - 分析邮件
- `POST /api/v1/generate-reply` - 生成回复
- `GET /api/v1/agents` - 列出 Agent
- `GET /api/v1/workflows` - 列出工作流

WebSocket:
- `/ws` - 实时进度推送

## 使用示例

```python
import requests

# 分析邮件
response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "email": {
        "id": "msg_123",
        "subject": "Q4预算审批",
        "from_address": "boss@company.com",
        "body_text": "请尽快审批Q4预算方案...",
        "date": "2024-01-15T09:30:00"
    }
})

result = response.json()
print(result["overall_priority"])  # high
print(result["suggested_actions"])  # [{"type": "mark_important", ...}]
```

## 架构图

见项目文档
