import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 环境变量配置（构建时注入）
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://pwmeoxvixmltsyqlqmnj.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_Hu24pmWYbPi3NJJyfuXv5A_DEl21ye0',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
  
  // 图片优化配置
  images: {
    unoptimized: true,
  },
  
  // ESLint 构建时忽略（可选）
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
