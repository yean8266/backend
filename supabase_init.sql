-- ============================================================================
-- Bonel Project - 数据库初始化脚本
-- 包含：用户角色枚举、业务表、触发器、RLS 策略
-- 在 Supabase SQL Editor 中执行此脚本
-- ============================================================================

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. 创建用户角色枚举类型
-- ============================================================================
DROP TYPE IF EXISTS user_role CASCADE;
CREATE TYPE user_role AS ENUM (
    'user',         -- 普通用户
    'vip',          -- 高级会员
    'admin',        -- 管理员
    'super_admin'   -- 超级无敌顶级管理员
);

COMMENT ON TYPE user_role IS '用户角色层级：user < vip < admin < super_admin';

-- ============================================================================
-- 2. 创建用户档案表 (profiles)
-- ============================================================================
DROP TABLE IF EXISTS public.profiles CASCADE;
CREATE TABLE public.profiles (
    -- 主键：关联到 Supabase Auth 的 users 表
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- 用户邮箱（从 auth.users 同步）
    email VARCHAR(255),
    
    -- 用户自拟代号
    nickname VARCHAR(255),
    
    -- 微信号（领奖用，敏感信息）
    wechat_contact VARCHAR(255),
    
    -- 每日剩余票数，默认5，不能为负数
    daily_votes_left INTEGER DEFAULT 5 CHECK (daily_votes_left >= 0),
    
    -- 用户角色层级，默认为普通用户
    role user_role DEFAULT 'user',
    
    -- 记录创建时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 最后活跃日期（用于跨天重置票数）
    last_active_date DATE DEFAULT CURRENT_DATE,
    
    -- 更新时间
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 添加表注释
COMMENT ON TABLE public.profiles IS '用户档案表，存储业务属性和角色信息';
COMMENT ON COLUMN public.profiles.id IS '关联 auth.users 的外键';
COMMENT ON COLUMN public.profiles.role IS '用户角色：user/vip/admin/super_admin';
COMMENT ON COLUMN public.profiles.daily_votes_left IS '今日剩余票数，每日0点重置为5';
COMMENT ON COLUMN public.profiles.wechat_contact IS '微信号，用于接收奖金';

-- 创建索引
CREATE INDEX idx_profiles_role ON public.profiles(role);
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_profiles_last_active ON public.profiles(last_active_date);

-- ============================================================================
-- 3. 创建候选文章表 (nominees)
-- ============================================================================
DROP TABLE IF EXISTS public.nominees CASCADE;
CREATE TABLE public.nominees (
    -- 自定义ID格式：BNL-YYMM-NN
    id VARCHAR(20) PRIMARY KEY,
    
    -- 文章标题
    title VARCHAR(500) NOT NULL,
    
    -- 摘要
    abstract TEXT,
    
    -- 证据链接（GitHub、视频等）
    evidence_link TEXT,
    
    -- 总票数
    total_votes INTEGER DEFAULT 0 CHECK (total_votes >= 0),
    
    -- 审核状态
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    
    -- 提交者ID
    submitter_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    
    -- 创建时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 更新时间
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE public.nominees IS '候选文章/灾难提名表';

-- 创建索引
CREATE INDEX idx_nominees_status ON public.nominees(status);
CREATE INDEX idx_nominees_votes ON public.nominees(total_votes DESC);
CREATE INDEX idx_nominees_submitter ON public.nominees(submitter_id);

-- ============================================================================
-- 4. 创建投票流水表 (votes_log)
-- ============================================================================
DROP TABLE IF EXISTS public.votes_log CASCADE;
CREATE TABLE public.votes_log (
    -- UUID 主键
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 投票用户ID
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    
    -- 候选文章ID
    nominee_id VARCHAR(20) NOT NULL REFERENCES public.nominees(id) ON DELETE CASCADE,
    
    -- 投票数量（可多次投票）
    vote_count INTEGER DEFAULT 1 CHECK (vote_count > 0),
    
    -- 投票时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 联合唯一约束：每个用户对每篇文章只能有一条记录
    UNIQUE(user_id, nominee_id)
);

COMMENT ON TABLE public.votes_log IS '投票流水记录表';
COMMENT ON COLUMN public.votes_log.vote_count IS '用户对该文章的累计投票数';

-- 创建索引
CREATE INDEX idx_votes_log_user ON public.votes_log(user_id);
CREATE INDEX idx_votes_log_nominee ON public.votes_log(nominee_id);
CREATE INDEX idx_votes_log_created ON public.votes_log(created_at);

-- ============================================================================
-- 5. 创建触发器函数：自动为新用户创建档案
-- 【实现登录到入库的完美闭环】
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- 当有新用户注册到 auth.users 时，自动创建 profiles 记录
    INSERT INTO public.profiles (
        id,
        email,
        nickname,
        wechat_contact,
        daily_votes_left,
        role,
        created_at,
        last_active_date,
        updated_at
    ) VALUES (
        NEW.id,                           -- 用户ID
        NEW.email,                        -- 邮箱
        NULL,                             -- nickname 待用户填写
        NULL,                             -- wechat_contact 待用户填写
        5,                                -- 初始票数5
        'user',                           -- 默认角色为普通用户
        NOW(),                            -- 创建时间
        CURRENT_DATE,                     -- 最后活跃日期
        NOW()                             -- 更新时间
    );
    
    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- 如果插入失败（如已存在），记录日志但不阻止用户创建
        RAISE WARNING '创建用户档案失败: %', SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建触发器：监听 auth.users 表的 INSERT 事件
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

COMMENT ON FUNCTION public.handle_new_user() IS '新用户注册时自动创建业务档案';

-- ============================================================================
-- 6. 创建跨天重置票数函数
-- ============================================================================
CREATE OR REPLACE FUNCTION public.reset_daily_votes()
RETURNS void AS $$
BEGIN
    UPDATE public.profiles
    SET 
        daily_votes_left = 5,
        last_active_date = CURRENT_DATE,
        updated_at = NOW()
    WHERE last_active_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.reset_daily_votes() IS '跨天重置所有用户的每日票数';

-- ============================================================================
-- 7. 启用 Row Level Security (RLS)
-- ============================================================================

-- profiles 表 RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 用户只能查看和修改自己的档案
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- 允许触发器插入（系统级）
CREATE POLICY "System can insert profiles" ON public.profiles
    FOR INSERT WITH CHECK (true);

-- nominees 表 RLS
ALTER TABLE public.nominees ENABLE ROW LEVEL SECURITY;

-- 所有人可以查看已通过的提名
CREATE POLICY "Anyone can view approved nominees" ON public.nominees
    FOR SELECT USING (status = 'approved');

-- 管理员可以查看所有提名
CREATE POLICY "Admins can view all nominees" ON public.nominees
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'super_admin')
        )
    );

-- 登录用户可以创建提名
CREATE POLICY "Users can create nominees" ON public.nominees
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- votes_log 表 RLS
ALTER TABLE public.votes_log ENABLE ROW LEVEL SECURITY;

-- 用户只能查看自己的投票记录
CREATE POLICY "Users can view own votes" ON public.votes_log
    FOR SELECT USING (auth.uid() = user_id);

-- 用户可以创建投票记录
CREATE POLICY "Users can create votes" ON public.votes_log
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- 8. 创建更新时间自动更新触发器
-- ============================================================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为 profiles 表添加自动更新
DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- 为 nominees 表添加自动更新
DROP TRIGGER IF EXISTS update_nominees_updated_at ON public.nominees;
CREATE TRIGGER update_nominees_updated_at
    BEFORE UPDATE ON public.nominees
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- 完成！
-- ============================================================================
SELECT '数据库初始化完成！' AS status;
