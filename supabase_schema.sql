-- Bonel Project - Supabase 数据库表结构
-- 用于支持 GitHub 登录和邮箱免密登录

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== profiles 表 (用户档案) ====================
-- 这个表与 Supabase Auth 的 users 表关联，存储额外的用户信息
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nickname VARCHAR(255),
    wechat_contact VARCHAR(255) NOT NULL,
    disaster_domain VARCHAR(100),
    daily_votes_left INTEGER DEFAULT 5,
    has_shared_today BOOLEAN DEFAULT FALSE,
    last_active_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_profiles_wechat ON profiles(wechat_contact);
CREATE INDEX IF NOT EXISTS idx_profiles_domain ON profiles(disaster_domain);

-- ==================== submissions 表 (论文提交) ====================
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    abstract TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    pdf_url TEXT,
    total_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);

-- ==================== vote_logs 表 (投票记录) ====================
CREATE TABLE IF NOT EXISTS vote_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    submission_id UUID REFERENCES submissions(id) ON DELETE CASCADE,
    vote_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, submission_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_vote_logs_user ON vote_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_vote_logs_submission ON vote_logs(submission_id);

-- ==================== RLS (Row Level Security) 配置 ====================
-- 启用 RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE vote_logs ENABLE ROW LEVEL SECURITY;

-- profiles 表策略
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- submissions 表策略
CREATE POLICY "Anyone can view approved submissions" ON submissions
    FOR SELECT USING (status = 'approved');

CREATE POLICY "Users can view own submissions" ON submissions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create submissions" ON submissions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- vote_logs 表策略
CREATE POLICY "Users can view own votes" ON vote_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create votes" ON vote_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ==================== 触发器：自动创建用户档案 ====================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, wechat_contact, daily_votes_left)
    VALUES (NEW.id, '', 5);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 当新用户注册时自动创建档案
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ==================== 跨天重置函数 ====================
CREATE OR REPLACE FUNCTION reset_daily_votes()
RETURNS void AS $$
BEGIN
    UPDATE profiles
    SET daily_votes_left = 5,
        has_shared_today = FALSE,
        last_active_date = CURRENT_DATE,
        updated_at = NOW()
    WHERE last_active_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;
