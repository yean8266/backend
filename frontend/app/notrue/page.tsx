"use client";

import Link from "next/link";

export default function EasterEggPage() {
  return (
    <main className="min-h-screen bg-zinc-50 flex items-center justify-center px-6 py-20">
      {/* 极简内容容器 */}
      <div className="w-full max-w-2xl text-center">
        
        {/* 顶部标题 - 精致小巧 */}
        <div className="mb-20 opacity-0 animate-[fadeIn_0.8s_ease-out_forwards]">
          <span className="text-[11px] font-medium tracking-[0.25em] uppercase text-zinc-400">
            🎉 恭喜您发现了隐藏的小彩蛋
          </span>
        </div>

        {/* 核心价值观 - 字重对比突出 */}
        <div className="mb-20 space-y-3 opacity-0 animate-[fadeIn_0.8s_ease-out_0.2s_forwards]">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-zinc-900">
            鼓励无意义的成功
          </h1>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight">
            <span className="bg-gradient-to-r from-zinc-900 to-zinc-500 bg-clip-text text-transparent">
              致敬有意义的失败
            </span>
          </h1>
        </div>

        {/* 开发者独白 - 优雅引语 */}
        <div className="mb-16 opacity-0 animate-[fadeIn_0.8s_ease-out_0.4s_forwards]">
          <div className="relative px-8 py-12">
            {/* 左侧细线装饰 */}
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-px h-24 bg-gradient-to-b from-transparent via-zinc-200 to-transparent"></div>
            
            <p className="text-zinc-500 leading-[2.2] text-[15px] text-left">
              <span className="text-zinc-900 font-medium">"</span>
              我的初衷是和搞笑诺贝尔奖一样，让大家思考一些看似无用实则有趣的问题，例如：
            </p>
            {/* 意大利面问题 - 独立居中突出 */}
            <p className="text-zinc-700 italic text-[16px] text-center my-6 py-4 px-6 bg-white rounded-lg shadow-sm border border-zinc-100">
              『意大利面为什么只能掰成三段？』
            </p>
            <p className="text-zinc-500 leading-[2.2] text-[15px] text-left">
              作为个人开发者，很难在一周内完成所有宏大的设想。起步阶段，我们先用抽象的论文博君一笑。但请相信，好戏才刚刚开始——
              <span className="text-zinc-900 font-medium">"</span>
            </p>
          </div>
        </div>

        {/* 愿景清单 - 简约卡片式布局 */}
        <div className="mb-20 opacity-0 animate-[fadeIn_0.8s_ease-out_0.6s_forwards]">
          {/* 引导语 */}
          <div className="mb-8">
            <p className="text-zinc-400 text-[12px] tracking-[0.2em] uppercase">
              作为一名工科生，我希望
            </p>
          </div>
          
          {/* 愿景卡片网格 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-6 bg-white rounded-2xl shadow-sm border border-zinc-100 text-left group hover:shadow-md transition-shadow duration-300">
              <div className="text-zinc-900 font-semibold text-[14px] mb-2">
                引发思考
              </div>
              <p className="text-zinc-500 text-[13px] leading-relaxed">
                让大脑保持活跃，在AI时代找到人类自己的方向
              </p>
            </div>
            
            <div className="p-6 bg-white rounded-2xl shadow-sm border border-zinc-100 text-left group hover:shadow-md transition-shadow duration-300">
              <div className="text-zinc-900 font-semibold text-[14px] mb-2">
                收录失败
              </div>
              <p className="text-zinc-500 text-[13px] leading-relaxed">
                记录失败的学术路径，以供后人避坑
              </p>
            </div>
            
            <div className="p-6 bg-white rounded-2xl shadow-sm border border-zinc-100 text-left group hover:shadow-md transition-shadow duration-300 md:col-span-2">
              <div className="text-zinc-900 font-semibold text-[14px] mb-2">
                鼓励探索
              </div>
              <p className="text-zinc-500 text-[13px] leading-relaxed">
                用看似无意义的探索，鼓励孤独的研究
              </p>
            </div>
          </div>
        </div>

        {/* 底部交互 - Apple 风格胶囊按钮 */}
        <div className="opacity-0 animate-[fadeIn_0.8s_ease-out_0.8s_forwards]">
          <Link
              href="/"
              className="inline-flex items-center gap-2 px-8 py-3 bg-zinc-900 text-white text-[13px] font-medium tracking-wide rounded-full hover:bg-zinc-800 transition-colors duration-300"
          >
            <span>返回主会场</span>
            <svg 
              className="w-4 h-4" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={1.5} 
                d="M17 8l4 4m0 0l-4 4m4-4H3" 
              />
            </svg>
          </Link>
        </div>
      </div>

      {/* 自定义动画 */}
      <style jsx global>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </main>
  );
}
