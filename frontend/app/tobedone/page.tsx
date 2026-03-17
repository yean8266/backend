import Link from "next/link";

export default function UnderConstruction() {
  return (
    <main className="min-h-[85vh] flex flex-col items-center justify-center bg-white px-6 text-center selection:bg-black selection:text-white">

      {/* 极简的视觉占位符：模拟终端报错或警告 */}
      <div className="mb-8 flex items-center justify-center">
        <div className="w-16 h-16 rounded-2xl bg-gray-50 border border-gray-200 flex items-center justify-center shadow-sm">
          <span className="text-2xl font-mono text-gray-400">_</span>
          <span className="text-2xl font-mono text-black animate-pulse">/</span>
        </div>
      </div>

      {/* 核心文案：保持高级且带有一点戏谑 */}
      <h1 className="text-4xl md:text-5xl font-serif font-bold text-[#1d1d1f] tracking-tight mb-6">
        该模块已在测试中烧毁。
      </h1>

      <p className="text-lg md:text-xl text-gray-500 max-w-lg mx-auto font-light leading-relaxed mb-12">
        由于发生不可预见的底层逻辑崩塌，此页面目前正处于灾难重建阶段。我们的工程师正在紧急翻阅《Noture》期刊以寻找修复灵感。
      </p>

      {/* 返回按钮 */}
      <Link
        href="/"
        className="bg-[#1d1d1f] text-white px-8 py-3 rounded-full text-sm font-bold hover:scale-105 transition-transform shadow-lg"
      >
        撤离至安全区域 (返回首页)
      </Link>

      {/* 底部点缀：增加一点极客氛围的错误码 */}
      <div className="absolute bottom-8 text-[10px] font-mono tracking-widest text-gray-400 uppercase">
        Error Log: ERR_ENGINEER_RUNAWAY // ESTIMATED_FIX: UNKNOWN
      </div>

    </main>
  );
}