# Bonel Project - 登录闭环测试指南

## ✅ 后端状态

**构建状态**: ✅ 成功
**导入测试**: ✅ 通过
**API 路由**: ✅ 已挂载

## 🚀 启动后端服务

### 1. 确保依赖已安装
```bash
cd D:\work\hku\创业\backend\backend
pip install supabase pyjwt
```

### 2. 启动后端
```bash
python -m bonel.main
```

**预期输出**:
```
🚀 Bonel Project API Starting...
📚 API Docs: http://127.0.0.1:8000/docs
```

### 3. 验证 API 文档
浏览器访问: http://localhost:8000/docs

应该能看到 Swagger UI，包含以下接口：
- GET /api/v1/health
- GET /api/v1/stats
- GET /api/v1/votes/status
- GET /api/v1/leaderboard
- GET /api/v1/papers
- GET /api/v1/user/profile
- PUT /api/v1/user/profile

## 🧪 测试登录闭环

### 测试 1: 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

**预期响应**:
```json
{
  "status": "ok",
  "timestamp": "2026-03-13T...",
  "version": "1.0.0"
}
```

### 测试 2: 获取用户档案（未登录）
```bash
curl http://localhost:8000/api/v1/user/profile
```

**预期响应**: 401 Unauthorized
```json
{
  "detail": "未提供认证 Token"
}
```

### 测试 3: 使用模拟 Token 测试
由于 Supabase 配置可能不完整，我们可以使用一个模拟的 JWT Token 来测试接口：

**步骤**:
1. 在前端项目 (`bonel-project`) 中启动开发服务器
2. 访问 http://localhost:3000/login
3. 使用 GitHub 或 Magic Link 登录
4. 登录成功后，打开浏览器开发者工具 (F12)
5. 在 Console 中执行：
   ```javascript
   // 获取当前 session
   const { data: { session } } = await supabase.auth.getSession();
   console.log('Token:', session.access_token);
   ```
6. 复制 access_token

**测试用户档案接口**:
```bash
# 替换 YOUR_TOKEN 为实际获取的 token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/user/profile
```

**预期响应**:
```json
{
  "id": "用户的UUID",
  "email": "user@example.com",
  "nickname": null,
  "wechat_contact": null,
  "daily_votes_left": 5,
  "role": "user",
  "created_at": "2026-03-13T..."
}
```

### 测试 4: 更新用户档案
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname": "Dr. Disaster", "wechat_contact": "wechat123"}' \
  http://localhost:8000/api/v1/user/profile
```

**预期响应**:
```json
{
  "success": true,
  "message": "档案更新成功",
  "data": {
    "id": "用户的UUID",
    "email": "user@example.com",
    "nickname": "Dr. Disaster",
    "wechat_contact": "wechat123",
    "daily_votes_left": 5,
    "role": "user",
    "created_at": "2026-03-13T..."
  }
}
```

## 🔍 验证数据库自动建档

### 方法 1: Supabase Dashboard
1. 登录 Supabase Dashboard
2. 进入 Table Editor
3. 查看 `profiles` 表
4. 应该能看到新登录的用户记录

### 方法 2: SQL 查询
在 Supabase SQL Editor 中执行：
```sql
SELECT * FROM public.profiles ORDER BY created_at DESC LIMIT 5;
```

**预期**: 能看到刚登录的用户，role 为 'user'，daily_votes_left 为 5

## 🐛 常见问题

### 问题 1: 后端启动报错 "SUPABASE_JWT_SECRET 未配置"
**解决**: 检查 `.env` 文件是否存在且包含 `SUPABASE_JWT_SECRET`

### 问题 2: 前端登录成功但后端鉴权失败
**解决**:
1. 确认前后端使用的是同一个 Supabase 项目
2. 检查 `SUPABASE_JWT_SECRET` 是否正确
3. 查看后端日志获取详细错误

### 问题 3: 新用户登录后 profiles 表没有记录
**解决**:
1. 检查 SQL 触发器是否正确创建
2. 在 Supabase Logs 中查看触发器执行日志
3. 手动执行 SQL 测试触发器：
   ```sql
   -- 手动创建测试用户（会触发自动建档）
   INSERT INTO auth.users (id, email) 
   VALUES (gen_random_uuid(), 'test@example.com');
   
   -- 检查是否自动创建了档案
   SELECT * FROM public.profiles WHERE email = 'test@example.com';
   ```

## 📋 完整测试流程

```
1. 启动后端 (python -m bonel.main)
   ↓
2. 访问 http://localhost:8000/docs 确认 API 正常
   ↓
3. 启动前端 (npm run dev)
   ↓
4. 访问 http://localhost:3000/login
   ↓
5. 使用 GitHub 或 Magic Link 登录
   ↓
6. 登录成功后自动跳转到 /user
   ↓
7. 前端调用 GET /api/v1/user/profile 获取用户信息
   ↓
8. 后端验证 JWT Token
   ↓
9. 后端查询 Supabase profiles 表
   ↓
10. 返回用户信息给前端展示
   ↓
11. 用户在 /user 页面完善信息
   ↓
12. 前端调用 PUT /api/v1/user/profile 更新信息
   ↓
13. 后端更新数据库
   ↓
14. 登录闭环完成！
```

## ✅ 验证清单

- [ ] 后端启动成功，无报错
- [ ] 访问 /docs 能看到 API 文档
- [ ] 未登录访问 /user/profile 返回 401
- [ ] 前端能正常登录（GitHub/Magic Link）
- [ ] 登录后访问 /user/profile 能返回用户信息
- [ ] 新用户登录后自动在 profiles 表中创建记录
- [ ] 能成功更新 nickname 和 wechat_contact

## 🎉 成功标志

当你能在前端 `/user` 页面看到：
- 正确的邮箱地址
- role 显示为 "user"
- 今日剩余选票为 5
- 能成功保存 nickname 和 wechat_contact

说明登录闭环已成功建立！
