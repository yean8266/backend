# Bonel Project - 贝诺尔奖投票平台

一个幽默的"抽象工程论文"评选系统。

## 📁 项目结构

```
bonel-deploy/
├── backend/              # FastAPI 后端
│   ├── main.py          # API 入口
│   ├── requirements.txt # Python 依赖
│   ├── .env             # 环境变量（已配置）
│   └── README.md        # 后端文档
│
├── frontend/             # Next.js 前端
│   ├── app/             # 页面路由
│   ├── components/      # React 组件
│   ├── lib/             # 工具函数
│   ├── services/        # API 服务
│   ├── public/          # 静态资源
│   ├── .env.local       # 环境变量（已配置）
│   └── package.json     # Node 依赖
│
├── docs/                 # 部署文档
│   └── DEPLOYMENT.md    # 部署指南
│
└── supabase_schema.sql   # 数据库表结构
```

## 🚀 快速启动

### 1. 确保数据库已创建

在 Supabase SQL Editor 中执行 `supabase_schema.sql`

### 2. 启动后端

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

后端运行在 http://localhost:8000

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:3000

## 🔧 环境变量

环境变量已配置好，如需修改：

- **后端**: 编辑 `backend/.env`
- **前端**: 编辑 `frontend/.env.local`

## 📚 详细文档

- [后端文档](backend/README.md)
- [前端文档](frontend/README.md)
- [部署指南](docs/DEPLOYMENT.md)

## 🛠️ 技术栈

- **前端**: Next.js 16 + TypeScript + Tailwind CSS
- **后端**: FastAPI + Python 3.10+
- **数据库**: Supabase (PostgreSQL)
- **认证**: Supabase Auth

## 📝 License

MIT
