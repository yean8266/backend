"use client";

import Link from "next/link";
import { useState } from "react";

// 伪造的测试数据（已翻译并注入本土化抽象灵魂）
const mockPapers = [
  {
    id: "1",
    title: "《跌落吐司的空气动力学：一种“黄油优先”的接触假说》",
    author: "佚名博士 & 早餐俱乐部",
    abstract: "在这项突破性研究中，我们故意丢下了一万片涂满黄油的吐司，以确凿地证明宇宙对人类怀有纯粹的恶意。数据表明，当研究员穿着洁白衬衫时，黄油面朝下的概率高达 99.8%。",
    upvotes: 8902,
    downvotes: 12,
    date: "2026-03-01",
  },
  {
    id: "4", // 模拟一篇刚刚发布、还没什么赞的新文章
    title: "《基于 YOLOv5 与树莓派 5 的目标追踪：论模型为何将室友识别为不可回收垃圾》",
    author: "某通信工程在读研究生",
    abstract: "在尝试使用带 Ubuntu 桌面的开发板追踪越界物体时，我们发现视觉算法对碳基生物的分类存在深层次的哲学偏见。该模型在高达 99% 的置信度下，坚定地认定正在打游戏的室友属于需要被立刻清理的静止障碍物。",
    upvotes: 42,
    downvotes: 3,
    date: "2026-03-07",
  },
  {
    id: "2",
    title: "《耳机线缆中的量子纠缠：论口袋内局部空间的拓扑混沌现象》",
    author: "404 实验室",
    abstract: "我们假设耳机线同时存在于多个维度中。当处于局部黑暗环境（即裤兜）时，它们会自发坍缩成混沌的拓扑死结。该项目的经费申请已被苹果公司无情拒绝。",
    upvotes: 4521,
    downvotes: 450,
    date: "2026-03-02",
  },
  {
    id: "3",
    title: "《关于“重启试试”疗效的综合性现象学研究》",
    author: "IT 救助中心",
    abstract: "在为期 5 年的观察期内，我们追踪了服务器主机、人际关系危机以及存在主义困境。研究表明，重启系统能解决 85% 的硬件故障，但会显著恶化人类的情绪稳定性。",
    upvotes: 3100,
    downvotes: 2100,
    date: "2026-02-28",
  }
];

export default function HubLeaderboard() {
  // 状态管理：当前选中的排序模式，默认为 'hot'
  const [activeTab, setActiveTab] = useState<'hot' | 'new'>('hot');

  // 核心算法：根据当前选中的 Tab 动态排序展示数据
  const sortedPapers = [...mockPapers].sort((a, b) => {
    if (activeTab === 'hot') {
      // 净得分从高到低
      return (b.upvotes - b.downvotes) - (a.upvotes - a.downvotes);
    } else {
      // 日期从新到旧
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    }
  });

  return (
    <main className="min-h-screen bg-white pt-24 pb-24 px-6">
      <div className="max-w-4xl mx-auto">

        {/* Header 区域：极致严肃 */}
        <div className="border-b-2 border-black pb-8 mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-6">
          <div>
            <h2 className="text-xs font-bold tracking-[0.3em] text-gray-400 uppercase mb-3">Official Leaderboard</h2>
            <h1 className="text-5xl font-serif font-bold text-[#1d1d1f]">贝诺尔工程抽象论文。</h1>
          </div>
          <Link href="/submit" className="bg-[#1d1d1f] text-white px-6 py-3 rounded-full text-sm font-medium hover:bg-gray-800 transition-colors whitespace-nowrap">
            + 递交你的抽象档案
          </Link>
        </div>

        {/* 动态切换 Tab UI (苹果风格的 Segmented Control) */}
        <div className="flex bg-gray-100 p-1 rounded-full w-fit mb-12">
          <button
            onClick={() => setActiveTab('hot')}
            className={`px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-300 ${
              activeTab === 'hot' 
                ? 'bg-white shadow-sm text-black' 
                : 'text-gray-500 hover:text-black'
            }`}
          >
            🔥 殿堂级神作
          </button>
          <button
            onClick={() => setActiveTab('new')}
            className={`px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-300 ${
              activeTab === 'new' 
                ? 'bg-white shadow-sm text-black' 
                : 'text-gray-500 hover:text-black'
            }`}
          >
            ✨ 最新野生脑洞
          </button>
        </div>

        {/* 列表区域 */}
        <div className="flex flex-col gap-10">
          {sortedPapers.map((paper) => {
            const netScore = paper.upvotes - paper.downvotes;
            return (
              <Link href={`/hub/${paper.id}`} key={paper.id} className="group block border-b border-gray-100 pb-10 hover:bg-gray-50 transition-colors -mx-6 px-6 rounded-2xl">
                <div className="flex items-start gap-8">

                  {/* 左侧：净得分 (Impact Factor) */}
                  <div className="flex flex-col items-center justify-center min-w-[80px]">
                    <span className="text-[10px] uppercase tracking-widest text-gray-400 font-bold mb-1 border-b border-gray-300 pb-1">影响因子</span>
                    <span className="text-3xl font-bold font-serif text-[#1d1d1f] group-hover:scale-110 transition-transform">
                      {netScore}
                    </span>
                  </div>

                  {/* 右侧：论文信息 */}
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-2xl font-bold font-serif text-[#1d1d1f] group-hover:text-blue-600 transition-colors pr-4">
                        {paper.title}
                      </h3>
                      {/* 如果是最新模式，可以在右侧显示一下日期标签 */}
                      {activeTab === 'new' && (
                        <span className="text-xs text-blue-500 font-mono bg-blue-50 px-2 py-1 rounded whitespace-nowrap mt-1">
                          首发
                        </span>
                      )}
                    </div>

                    <p className="text-sm font-medium text-gray-500 mb-4 tracking-wide">
                      作者：{paper.author}
                    </p>
                    <p className="text-gray-600 leading-relaxed font-light line-clamp-2">
                      {paper.abstract}
                    </p>
                  </div>

                </div>
              </Link>
            );
          })}
        </div>

      </div>
    </main>
  );
}