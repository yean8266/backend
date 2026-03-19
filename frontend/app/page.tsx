import Link from "next/link";
import Image from "next/image";
import HeroCarousel from "../components/HeroCarousel";

export default function Home() {
  return (
    <main className="flex flex-col items-center w-full overflow-x-hidden pb-24 bg-white">
      {/* =====================================
          SECTION 1: HERO (超大首屏)
          ===================================== */}
      <section className="w-full flex flex-col items-center text-center pt-24 pb-12">
          <div className="px-6 flex flex-col items-center">
              <h2 className="text-sm font-semibold tracking-widest uppercase text-amber-600 mb-4">
                  重塑抽象学术边界
              </h2>
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 max-w-4xl text-[#1d1d1f]">提名"无用"但有趣的文章
                  <br/> 角逐属于你的“贝诺尔奖”！
              </h1>
              <p className="text-xl md:text-2xl text-gray-500 mb-10 max-w-2xl font-light leading-relaxed">
                  你的幽默或许是另一种科研天赋！
              </p>

              <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 text-lg font-medium mb-12 items-center">
                  {/* 核心功能 1：进入投票大厅 */}
                  <Link href="/vote"
                        className="bg-blue-600 text-white px-8 py-3 rounded-full hover:bg-blue-700 transition-colors shadow-sm w-full sm:w-auto">
                      进入榜单投票
                  </Link>

                  {/* 核心功能 2：新增的提交论文入口 */}
                  <Link href="/submit"
                        className="bg-[#1d1d1f] text-white px-8 py-3 rounded-full hover:bg-gray-800 transition-colors shadow-sm w-full sm:w-auto">
                      递交有趣文章
                  </Link>

                  {/* 次级功能：探索往期档案 */}
                  <Link href="/hub"
                        className="text-gray-500 hover:text-blue-600 flex items-center hover:underline px-4 py-3 transition-colors">
                      探索往期档案 <span className="ml-1">›</span>
                  </Link>
              </div>
          </div>

          {/* 轮播图区域：全宽展示 (Full Bleed) */}
          <div className="w-full border-b border-gray-100 pb-16">
              <HeroCarousel/>
          </div>

      </section>

        {/*/!* =====================================*/}
        {/*    SECTION 2: BENTO GRID (Apple 风格双卡片)*/}
        {/*    ===================================== *!/*/}
        {/*<section className="w-full max-w-6xl px-6 py-16 grid grid-cols-1 md:grid-cols-2 gap-6">*/}

        {/*  /!* 卡片 1：Silence *!/*/}
        {/*  <div className="bg-[#f5f5f7] rounded-[2rem] p-12 flex flex-col items-center text-center min-h-[550px] relative overflow-hidden group hover:shadow-lg transition-shadow cursor-pointer">*/}
        {/*    <h3 className="text-4xl font-bold mb-3 font-serif-academic text-blue-900">Silence.</h3>*/}
        {/*    <p className="text-xl text-gray-500 mb-6">“未被听见的轰鸣，依然是光。”</p>*/}
        {/*    /!* 修改点 *!/*/}
      {/*    <Link href="/tobedone" className="text-blue-600 font-medium hover:underline flex items-center mb-8 z-10">*/}
      {/*      阅读官方期刊 <span className="ml-1">›</span>*/}
      {/*    </Link>*/}

      {/*    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4/5 h-64 bg-white rounded-t-2xl shadow-sm border border-gray-200 flex items-center justify-center translate-y-8 group-hover:translate-y-4 transition-transform duration-500">*/}
      {/*       <span className="text-gray-400 font-mono text-xs text-center px-4 leading-relaxed">*/}
      {/*         [ 影像存档占位: <br/> 因主板烧毁而失去梦想的六足机器人 ]*/}
      {/*       </span>*/}
      {/*    </div>*/}
      {/*    /!* 修改点：隐形全覆盖链接 *!/*/}
      {/*    <Link href="/tobedone" className="absolute inset-0 z-0" aria-label="前往施工页面"></Link>*/}
      {/*  </div>*/}

      {/*  /!* 卡片 2：Noture *!/*/}
      {/*  <div className="bg-[#1d1d1f] text-white rounded-[2rem] p-12 flex flex-col items-center text-center min-h-[550px] relative overflow-hidden group hover:shadow-2xl transition-shadow cursor-pointer">*/}
      {/*    <h3 className="text-4xl font-bold mb-3 font-serif-academic text-orange-500">Noture.</h3>*/}
      {/*    <p className="text-xl text-gray-400 mb-6">灾难性工程事故的深度解剖学。</p>*/}
      {/*    /!* 修改点 *!/*/}
      {/*    <Link href="/tobedone" className="text-orange-500 font-medium hover:underline flex items-center mb-8 z-10">*/}
      {/*      揭露踩坑内幕 <span className="ml-1">›</span>*/}
      {/*    </Link>*/}

      {/*    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4/5 h-64 bg-zinc-800 rounded-t-2xl shadow-2xl border border-zinc-700 flex items-center justify-center translate-y-8 group-hover:translate-y-4 transition-transform duration-500">*/}
      {/*       <span className="text-zinc-500 font-mono text-xs text-center px-4 leading-relaxed">*/}
      {/*         [ 运行日志占位: <br/> 将人体错误识别为单车的 CV 测试画面 ]*/}
      {/*       </span>*/}
      {/*    </div>*/}
      {/*    /!* 修改点：隐形全覆盖链接 *!/*/}
      {/*    <Link href="/tobedone" className="absolute inset-0 z-0" aria-label="前往施工页面"></Link>*/}
      {/*  </div>*/}

      {/*</section>*/}

      {/* =====================================
          SECTION 3: 工具横幅 (全区域可点击更新)
          ===================================== */}
      <section className="w-full max-w-6xl px-6">
        {/* 修改点：整个横幅块的点击跳转 */}
          <Link
              href="/ai-lab"
              className="block bg-[#f5f5f7] rounded-[2rem] p-12 md:p-16 flex flex-col md:flex-row items-center justify-between gap-12 group hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
          >
              <div className="max-w-md text-left">
                  <h3 className="text-3xl font-bold mb-4 text-[#1d1d1f]">Bonel 格式化 AI。</h3>
                  <p className="text-lg text-gray-500 mb-6 leading-relaxed">
                      丢进你那乱七八糟的工程废案或报错日志。见证它被一键重构为符合顶级期刊规范的学术巨著。
                  </p>
                  <span className="text-blue-600 font-medium flex items-center group-hover:underline">
              体验自动化编撰 <span className="ml-1 group-hover:translate-x-1 transition-transform">›</span>
            </span>
              </div>

              <div
                  className="w-full md:w-1/2 aspect-video bg-white rounded-2xl shadow-sm border border-gray-200 flex items-center justify-center group-hover:shadow-md transition-shadow relative overflow-hidden">
                  <Image
                      src="/ailab.jpg"
                      alt="AI 一键生成有趣论文全过程"
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-500 ease-in-out"
                  />
              </div>
          </Link>
      </section>

        {/* =====================================
          SECTION 4: 免责声明 (Footer Disclaimer)
          ===================================== */}
      <section className="w-full max-w-4xl px-6 mt-20 mb-8 text-center">
          <p className="text-xs text-gray-400 font-light leading-relaxed tracking-wide">
              免责声明：本网站所有文章不涉及任何政治、男女对立等敏感话题，切勿上升高度。<br className="hidden sm:block" />
              我们一起留存奇思妙想，谢谢大家！
          </p>
      </section>
    </main>
  );
}