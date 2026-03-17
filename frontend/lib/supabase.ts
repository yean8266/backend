import { createClient } from '@supabase/supabase-js';

// 环境变量配置（带默认值，防止构建时出错）
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://pwmeoxvixmltsyqlqmnj.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_Hu24pmWYbPi3NJJyfuXv5A_DEl21ye0';

// 运行时检查
if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials not found. Please check your .env.local file.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
