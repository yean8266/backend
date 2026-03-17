# Bonel Project - Backend

FastAPI 后端 API

## 🎯 API 功能

- 📊 论文列表（分页、排序、搜索）
- 🗳️ 投票/撤票
- 📝 论文提交
- 🔗 分享奖励
- 📈 排行榜/统计

## 🚀 开发

```bash
# 创建虚拟环境
python -m venv venv

# 激活（Windows）
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

API 文档：http://localhost:8000/docs

## 📁 目录结构

```
main.py              # 主应用入口
requirements.txt     # Python 依赖
.env.example         # 环境变量示例
```

## ⚙️ 环境变量

创建 `.env`：

```env
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# 安全密钥
SECRET_KEY=your-secret-key

# 调试模式
DEBUG=True
```

## 📚 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/nominees` | GET | 论文列表 |
| `/api/v1/nominees` | POST | 提交论文 |
| `/api/v1/vote` | POST | 投票 |
| `/api/v1/unvote` | POST | 撤票 |
| `/api/v1/share` | POST | 分享奖励 |
| `/api/v1/leaderboard` | GET | 排行榜 |
| `/api/v1/stats` | GET | 统计信息 |

## 📦 部署

### Railway

```bash
railway login
railway init
railway up
```

### Render

1. 创建 Web Service
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. 添加环境变量

### Docker

```bash
docker build -t bonel-backend .
docker run -p 8000:8000 --env-file .env bonel-backend
```
