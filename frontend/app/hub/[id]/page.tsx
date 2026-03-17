"use client"; // 需要交互，必须是 client component

import { useState } from "react";
import Link from "next/link";

// 同样使用假数据（真实开发中，这里会根据 URL 的 id 去数据库拉取）
const paper = {
  title: "The Aerodynamics of a Falling Slice of Toast: A Butter-First Approach",
  author: "Dr. Anonymous & The Breakfast Club",
  abstract: "In this groundbreaking paper, we intentionally dropped 10,000 slices of buttered toast to prove definitively that the universe hates us. The results show a 99.8% butter-down correlation when wearing a clean white shirt.",
  content: "Here is the full methodology. First, we procured 10,000 slices of standard white bread. We applied exactly 5 grams of salted butter to one side. We then recruited 50 engineers wearing pristine white lab coats. The drops were conducted from a standard dining table height of 0.75 meters. The findings were statistically significant and emotionally devastating... (This is a placeholder for the full tragic log).",
  initialUpvotes: 8902,
  initialDownvotes: 12,
};

export default function PaperDetail() {
  const [upvotes, setUpvotes] = useState(paper.initialUpvotes);
  const [downvotes, setDownvotes] = useState(paper.initialDownvotes);

  // 动画状态控制
  const [upvoteAnim, setUpvoteAnim] = useState(false);
  const [downvoteAnim, setDownvoteAnim] = useState(false);

  const handleUpvote = () => {
    setUpvotes(prev => prev + 1);
    setUpvoteAnim(true);
    setTimeout(() => setUpvoteAnim(false), 300); // 300ms 后移除动画类
  };

  const handleDownvote = () => {
    setDownvotes(prev => prev + 1);
    setDownvoteAnim(true);
    setTimeout(() => setDownvoteAnim(false), 300);
  };

  return (
    <main className="min-h-screen bg-[#fcfcfc] pt-24 pb-32 px-6 selection:bg-black selection:text-white">
      <div className="max-w-3xl mx-auto">

        {/* 返回按钮 */}
        <Link href="/hub" className="text-sm font-medium text-gray-400 hover:text-black transition-colors mb-12 block">
          ← Back to Leaderboard
        </Link>

        {/* 论文头部 */}
        <header className="mb-16 text-center">
          <p className="text-[10px] font-bold tracking-[0.3em] text-gray-400 uppercase mb-6">
            Jocker Journal of Engineering Failures
          </p>
          <h1 className="text-4xl md:text-6xl font-serif font-bold text-[#1d1d1f] leading-tight mb-8">
            {paper.title}
          </h1>
          <div className="w-16 h-1 bg-black mx-auto mb-8"></div>
          <p className="text-lg text-gray-600 font-medium italic">
            {paper.author}
          </p>
        </header>

        {/* 论文正文阅读区 */}
        <article className="prose prose-lg max-w-none text-gray-800 font-serif leading-relaxed mb-24">
          <h3 className="text-2xl font-bold mb-4 font-sans">Abstract</h3>
          <p className="mb-8 p-6 bg-gray-100 rounded-xl text-gray-600">{paper.abstract}</p>

          <h3 className="text-2xl font-bold mb-4 font-sans">Methodology & Tragedy</h3>
          <p>{paper.content}</p>
        </article>

        {/* 底部巨大的互动按钮区 (戏谑感的核心) */}
        <div className="border-t-2 border-gray-200 pt-16 text-center">
          <h3 className="text-sm font-bold tracking-widest text-gray-400 uppercase mb-8">Peer Review Decision</h3>

          <div className="flex flex-col md:flex-row gap-6 justify-center items-center">
            {/* 授予贝诺尔奖 按钮 */}
            <button
              onClick={handleUpvote}
              className="group relative flex flex-col items-center justify-center w-full md:w-72 p-6 border-2 border-[#1d1d1f] bg-white hover:bg-[#1d1d1f] hover:text-white transition-all duration-300 rounded-2xl"
            >
              <span className="text-3xl mb-2">🏆</span>
              <span className="text-lg font-bold mb-1">授予贝诺尔奖</span>
              <span className="text-xs text-gray-500 group-hover:text-gray-300 mb-4">(This is a masterpiece)</span>

              <div className={`text-4xl font-black font-mono transition-transform duration-300 ${upvoteAnim ? 'scale-150 text-orange-500' : ''}`}>
                {upvotes.toLocaleString()}
              </div>
            </button>

            {/* 纯纯依托答辩 按钮 */}
            <button
              onClick={handleDownvote}
              className="group relative flex flex-col items-center justify-center w-full md:w-72 p-6 border-2 border-gray-200 bg-gray-50 hover:bg-red-50 hover:border-red-200 transition-all duration-300 rounded-2xl"
            >
              <span className="text-3xl mb-2">💩</span>
              <span className="text-lg font-bold mb-1 text-gray-700">纯纯依托答辩</span>
              <span className="text-xs text-gray-400 mb-4">(Absolute Garbage)</span>

              <div className={`text-4xl font-black font-mono text-gray-500 transition-transform duration-300 ${downvoteAnim ? 'scale-150 text-red-500' : ''}`}>
                {downvotes.toLocaleString()}
              </div>
            </button>
          </div>
        </div>

      </div>
    </main>
  );
}