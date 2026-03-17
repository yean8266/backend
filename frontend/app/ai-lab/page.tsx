import Link from "next/link";

export default function AILab() {
  return (
    <main className="flex flex-col items-center w-full overflow-x-hidden pb-24 bg-white min-h-screen">
      
      {/* =====================================
          SECTION 1: 页面头部 (Header)
          ===================================== */}
      <section className="w-full flex flex-col items-center text-center pt-20 pb-12 px-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-semibold tracking-widest uppercase mb-6 border border-blue-100">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          抽象大模型加载中
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 max-w-4xl text-[#1d1d1f]">
          Bonel 学术升华 <span className="text-blue-600 font-serif-academic italic pr-2">AI.</span>
        </h1>
        <p className="text-xl md:text-2xl text-gray-500 max-w-2xl font-light leading-relaxed">
          你的专属“思想废料”提炼专家。只需丢进你洗澡时蹦出的离谱脑洞或深夜备忘录里的碎碎念，我们将为你无缝重构为足以震惊评委的抽象学术巨著。
        </p>
      </section>

      {/* =====================================
          SECTION 2: 核心上传区 (处于锁定状态)
          ===================================== */}
      <section className="w-full max-w-5xl px-6 mb-16">
        {/* Apple 风格的拟物化上传框 */}
        <div className="w-full bg-[#f5f5f7] rounded-[2rem] p-8 md:p-24 flex flex-col items-center justify-center text-center relative overflow-hidden border border-gray-200">

          {/* 内部虚线框 */}
          <div className="w-full h-full border-2 border-dashed border-gray-300 rounded-[1.5rem] flex flex-col items-center justify-center py-20 px-4 bg-white/50 backdrop-blur-sm">
             <span className="text-7xl mb-6 opacity-80">🧠</span>
             <h2 className="text-2xl font-bold text-[#1d1d1f] mb-3">将野生脑洞拖拽至此</h2>
             <p className="text-gray-500 mb-8 max-w-md leading-relaxed">
               支持 .txt, .md, 聊天记录截图以及语无伦次的随笔。AI 将自动提取其中的“抽象因子”，并为其披上严谨的学术外衣。
             </p>

             {/* 锁定的按钮 */}
             <div className="px-8 py-4 bg-gray-200 text-gray-400 rounded-full text-sm font-semibold tracking-widest uppercase cursor-not-allowed flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                学术炼金炉暂未开放
             </div>
          </div>
        </div>
      </section>

      {/* =====================================
          SECTION 3: 功能预告区 (Bento Grid)
          ===================================== */}
      <section className="w-full max-w-5xl px-6 grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* 功能卡片 1 */}
        <div className="bg-[#f5f5f7] rounded-3xl p-8 flex flex-col items-start border border-gray-100">
          <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center text-xl mb-6 shadow-sm">
            🎩
          </div>
          <h3 className="text-lg font-bold text-[#1d1d1f] mb-2">深度黑话赋能</h3>
          <p className="text-gray-500 text-sm leading-relaxed">
            自动捕捉你碎片化想法中的荒诞内核，并强行接入“后现代解构主义”与“量子纠缠”等高级词汇，让你的胡言乱语高深莫测。
          </p>
        </div>

        {/* 功能卡片 2 */}
        <div className="bg-[#f5f5f7] rounded-3xl p-8 flex flex-col items-start border border-gray-100">
          <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xl mb-6 shadow-sm">
            📝
          </div>
          <h3 className="text-lg font-bold text-[#1d1d1f] mb-2">一键学术伪装</h3>
          <p className="text-gray-500 text-sm leading-relaxed">
            将不成句的随笔，无情拆解为“摘要、引言、方法论、结论”的标准八股文结构，完美契合顶级期刊极其做作的排版规范。
          </p>
        </div>

        {/* 功能卡片 3 */}
        <div className="bg-[#f5f5f7] rounded-3xl p-8 flex flex-col items-start border border-gray-100">
          <div className="w-12 h-12 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-xl mb-6 shadow-sm">
            🚀
          </div>
          <h3 className="text-lg font-bold text-[#1d1d1f] mb-2">全自动推送打榜</h3>
          <p className="text-gray-500 text-sm leading-relaxed">
            将生成完毕的抽象巨著直接推送到「贝诺尔奖」评选大厅，立刻开始接受全网评委的顶礼膜拜与疯狂吐槽。
          </p>
        </div>

      </section>

      {/* 返回主页的优雅链接 */}
      <div className="mt-16">
        <Link href="/" className="text-gray-400 hover:text-[#1d1d1f] transition-colors text-sm font-medium flex items-center gap-1">
          ‹ 撤退至安全区 (返回主页)
        </Link>
      </div>

    </main>
  );
}