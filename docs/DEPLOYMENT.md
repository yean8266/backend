# 部署指南

## 🎯 架构

```
Frontend (Vercel) → Backend (Railway/Render) → Supabase (Database)
```

## 🚀 部署步骤

### 1. 初始化 Git 仓库

```bash
cd bonel-deploy
git init
git add .
git commit -m "Initial commit"
```

### 2. 创建 GitHub 仓库并推送

```bash
git remote add origin https://github.com/YOUR_USERNAME/bonel-project.git
git push -u origin main
```

### 3. 部署后端（推荐 Railway）

**Option A: Railway (推荐)**

1. 访问 https://railway.app
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择你的仓库
4. 设置：
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. 环境变量已配置在代码中，或手动添加
6. 部署后会获得域名如：`https://bonel-api.up.railway.app`

**Option B: Render**

1. 访问 https://render.com
2. New → Web Service → Connect GitHub
3. 配置：
   - Name: `bonel-api`
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. 部署

### 4. 部署前端（Vercel）

1. 访问 https://vercel.com
2. Import GitHub Repository
3. 配置：
   - Framework: Next.js
   - Root Directory: `frontend`
4. 修改环境变量：
   - 编辑 `frontend/.env.local`
   - 将 `NEXT_PUBLIC_API_URL` 改为后端域名
   - 例如：`https://bonel-api.up.railway.app/api/v1`
5. Deploy

### 5. 更新后端 CORS

在后端环境变量中添加：
```
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

或在 `backend/main.py` 中修改：
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.vercel.app"
]
```

## ✅ 部署后

- **前端**: https://your-project.vercel.app
- **后端**: https://your-api.railway.app
- **数据库**: Supabase (已配置)

## 💰 费用

全部免费额度足够个人项目使用。

## 🔧 故障排除

| 问题 | 解决 |
|------|------|
| CORS 错误 | 检查后端 `allow_origins` 是否包含前端域名 |
| 数据库连接失败 | 检查 Supabase 环境变量 |
| 401 错误 | 正常，需要登录 |
