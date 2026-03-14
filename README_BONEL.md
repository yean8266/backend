# Bonel Project - MVP 快速启动指南

## 项目结构

```
backend/
├── bonel/                    # Bonel Project 主包
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── auth.py              # JWT 鉴权依赖
│   ├── database.py          # Supabase 数据库操作
│   ├── models.py            # Pydantic 数据模型
│   └── api/
│       ├── __init__.py
│       └── routes.py        # API 路由 (4个接口)
├── supabase_schema.sql      # 数据库表结构
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量模板
└── README.md
```

## 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 Supabase 配置
```

### 3. 初始化数据库

在 Supabase SQL Editor 中执行 `supabase_schema.sql`

### 4. 启动服务

```bash
python -m bonel.main
```

服务启动后访问: http://127.0.0.1:8000/docs

## API 端点

### 已实现的接口

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/v1/health` | 健康检查 | 否 |
| GET | `/api/v1/stats` | 平台统计 | 否 |
| GET | `/api/v1/votes/status` | 查询投票状态 | 是 |
| GET | `/api/v1/leaderboard` | 获取排行榜 | 否 |
| GET | `/api/v1/papers` | 获取文章列表 | 可选 |

### 认证方式

所有需要认证的接口，在 Header 中携带:
```
Authorization: Bearer <JWT_TOKEN>
```

## 数据库表结构

### users (用户表)
- `id`: UUID (主键)
- `email`: 邮箱
- `daily_votes_left`: 今日剩余票数
- `has_shared_today`: 今日是否已分享
- `last_active_date`: 最后活跃日期

### nominees (候选人表)
- `id`: 候选人ID (BNL-YYMM-NN)
- `title`: 标题
- `author`: 作者
- `abstract`: 摘要
- `total_votes`: 总票数
- `status`: 状态 (pending/approved/rejected)

### vote_logs (投票记录表)
- `id`: 自增ID
- `user_id`: 用户ID
- `nominee_id`: 候选人ID
- `vote_count`: 投票次数

## 与前端集成

前端 `services/api.ts` 已更新:
- 使用 `/api/v1` 路由前缀
- 自动携带 JWT Token
- 支持所有4个新接口

## 待办事项

- [ ] 合伙人实现投票/撤回投票接口
- [ ] 合伙人实现分享奖励接口
- [ ] 合伙人实现提交论文接口
- [ ] 并发控制优化 (行锁)
- [ ] 单元测试
