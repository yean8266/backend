-- Bonel Project - Supabase 数据库表结构
-- 在 Supabase SQL Editor 中执行

-- ==================== 用户表 ====================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    daily_votes_left INTEGER DEFAULT 5,
    has_shared_today BOOLEAN DEFAULT FALSE,
    last_active_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active_date);

-- ==================== 候选人/论文表 ====================
CREATE TABLE IF NOT EXISTS nominees (
    id TEXT PRIMARY KEY,  -- 格式: BNL-YYMM-NN
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    abstract TEXT,
    total_votes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'approved',  -- pending, approved, rejected
    pdf_url TEXT,
    contact_email TEXT,
    submitted_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_nominees_status ON nominees(status);
CREATE INDEX IF NOT EXISTS idx_nominees_votes ON nominees(total_votes DESC);
CREATE INDEX IF NOT EXISTS idx_nominees_created ON nominees(created_at DESC);

-- 全文搜索索引 (可选)
CREATE INDEX IF NOT EXISTS idx_nominees_search ON nominees 
USING gin(to_tsvector('english', title || ' ' || author || ' ' || COALESCE(abstract, '')));

-- ==================== 投票记录表 ====================
CREATE TABLE IF NOT EXISTS vote_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    nominee_id TEXT REFERENCES nominees(id) ON DELETE CASCADE,
    vote_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, nominee_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_vote_logs_user ON vote_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_vote_logs_nominee ON vote_logs(nominee_id);

-- ==================== 存储过程: 原子增加票数 ====================
-- 用于防止并发刷票
CREATE OR REPLACE FUNCTION increment_nominee_votes(nominee_id TEXT)
RETURNS void AS $$
BEGIN
    UPDATE nominees 
    SET total_votes = total_votes + 1,
        updated_at = NOW()
    WHERE id = nominee_id;
END;
$$ LANGUAGE plpgsql;

-- ==================== RLS (Row Level Security) 配置 ====================
-- 启用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE nominees ENABLE ROW LEVEL SECURITY;
ALTER TABLE vote_logs ENABLE ROW LEVEL SECURITY;

-- 用户表策略: 用户只能查看和修改自己的数据
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- 候选人表策略: 所有人可以查看已通过的候选人
CREATE POLICY "Anyone can view approved nominees" ON nominees
    FOR SELECT USING (status = 'approved');

-- 投票记录表策略: 用户只能查看自己的投票记录
CREATE POLICY "Users can view own votes" ON vote_logs
    FOR SELECT USING (auth.uid() = user_id);

-- ==================== 示例数据 (可选) ====================
-- 插入一些测试数据
INSERT INTO nominees (id, title, author, abstract, total_votes, status) VALUES
('BNL-2603-01', '基于 YOLOv5 的垃圾分类系统', '张三', '这是一个使用 YOLOv5 实现的垃圾分类系统...', 128, 'approved'),
('BNL-2603-02', '用 Excel 做神经网络', '李四', '证明了 Excel 可以做任何事情...', 256, 'approved'),
('BNL-2603-03', 'Hello World 企业级架构', '王五', '包含 50 个微服务的 Hello World...', 89, 'approved')
ON CONFLICT (id) DO NOTHING;
