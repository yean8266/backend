"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { supabase } from '@/lib/supabase';
import { User } from '@supabase/supabase-js'; // 引入 Supabase 的用户类型
import { fetchPapers, submitVote, submitUnvote, reportShareSuccess, fetchUserProfile } from '@/services/api';

// 定义咱们的论文数据长什么样
interface Paper {
  id: string;
  title: string;
  author: string;
  abstract: string;
  totalVotes: number;
  userVotes: number;
  date: string;
}

// ... 下面的 initialPapers 保持不变 ...

// 注意：所有数据现在从后端 /api/v1/nominees 接口获取
// 移除了静态假数据，使用真实数据库数据

export default function HubLeaderboard() {
  // UI 交互状态
  const [activeTab, setActiveTab] = useState<'hot' | 'new'>('hot');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState(''); // 防抖搜索词

  // 核心数据与分页状态
  const [user, setUser] = useState<User | null>(null);
  const [votesLeft, setVotesLeft] = useState(0);
  const [hasShared, setHasShared] = useState(false);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false); // 是否还有下一页

  // 1. 搜索防抖逻辑：用户停止打字 500ms 后再触发请求
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1); // 搜索词改变时，从第一页重新查
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // 2. 核心加载逻辑：当 tab、page 或 搜索词 改变时向后端发请求
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);

      try {
        // 请求真实数据，把所有的参数都传给后端！
        const data = await fetchPapers(activeTab, page, debouncedSearch);

        // 如果是第一页，直接替换；如果是加载更多，拼接到现有数组后面
        if (page === 1) {
          setPapers(data.papers);
        } else {
          setPapers(prev => [...prev, ...data.papers]);
        }

        // 假设后端每页返回 20 条，如果少于 20 条说明没数据了
        setHasMore(data.papers.length >= 20);

        if (session?.user && data.userStatus) {
          setVotesLeft(data.userStatus.votesLeft);
          setHasShared(data.userStatus.hasSharedToday);
        }
      } catch (error) {
        console.error("获取数据失败:", error);
        // 显示错误状态
        setPapers([]);
        setVotesLeft(5);
        setHasMore(false);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [activeTab, page, debouncedSearch]); // 监听这三个变量

  // 切换 Tab 时重置分页
  const handleTabChange = (tab: 'hot' | 'new') => {
    if (activeTab === tab) return;
    setActiveTab(tab);
    setPage(1);
    setPapers([]); // 清空列表触发骨架屏或直接 loading
  };

  // (以下 handleVote, handleUnvote, handleShare 乐观更新逻辑完全保持不变...)
  const handleVote = async (paperId: string) => {
    if (!user) { alert("请先通过顶部导航栏登录！"); return; }
    if (votesLeft <= 0) { alert("选票已耗尽！"); return; }
    setVotesLeft(prev => prev - 1);
    setPapers(prev => prev.map(p => p.id === paperId ? { ...p, totalVotes: p.totalVotes + 1, userVotes: p.userVotes + 1 } : p));
    try { await submitVote(paperId); } catch (e) {
      alert("投票失败，选票已退回。");
      setVotesLeft(prev => prev + 1);
      setPapers(prev => prev.map(p => p.id === paperId ? { ...p, totalVotes: p.totalVotes - 1, userVotes: p.userVotes - 1 } : p));
    }
  };

  const handleUnvote = async (paperId: string) => {
    const paper = papers.find(p => p.id === paperId);
    if (!paper || paper.userVotes <= 0) return;
    setVotesLeft(prev => prev + 1);
    setPapers(prev => prev.map(p => p.id === paperId ? { ...p, totalVotes: p.totalVotes - 1, userVotes: p.userVotes - 1 } : p));
    try { await submitUnvote(paperId); } catch (e) {
      alert("撤销失败");
      setVotesLeft(prev => prev - 1);
      setPapers(prev => prev.map(p => p.id === paperId ? { ...p, totalVotes: p.totalVotes + 1, userVotes: p.userVotes + 1 } : p));
    }
  };

  const handleShare = async () => {
    if (!user) { alert("请先登录！"); return; }
    if (hasShared) { alert("今天已获取过额外选票！"); return; }
    alert("链接已复制！额外获得 1 票！");
    setVotesLeft(prev => prev + 1);
    setHasShared(true);
    try { await reportShareSuccess(); } catch (e) {}
  };

  return (
    <main className="min-h-screen bg-[#fafafa] pt-24 pb-32 px-4 md:px-6">
      <div className="max-w-4xl mx-auto">
        {/* Banner 保持不变 */}
        <div className="bg-[#1d1d1f] rounded-[2rem] p-8 md:p-12 text-white mb-12 relative overflow-hidden shadow-2xl">
          <div className="relative z-10">
            <h2 className="text-xs font-bold tracking-[0.3em] text-orange-500 uppercase mb-4">Bonel Prize · Monthly Hub</h2>
            <h1 className="text-4xl md:text-5xl font-serif font-bold mb-6 leading-tight">3 月“抽象之巅”提名战。<br />用你的抽象，折现成科研经费。</h1>
            <p className="text-gray-400 mb-8 max-w-xl text-sm md:text-base">本月排名前三的工程灾难/抽象巨著，将晋级年度总决赛并获现金津贴。</p>
            <div className="flex gap-4 md:gap-8">
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 md:p-6 text-center border border-white/10 flex-1"><div className="text-3xl mb-1">🥇</div><div className="text-2xl font-black text-orange-400">¥108</div></div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 md:p-6 text-center border border-white/10 flex-1"><div className="text-3xl mb-1">🥈</div><div className="text-2xl font-black text-gray-300">¥68</div></div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 md:p-6 text-center border border-white/10 flex-1"><div className="text-3xl mb-1">🥉</div><div className="text-2xl font-black text-amber-700">¥58</div></div>
            </div>
          </div>
        </div>

        {/* 控制台与搜索框 */}
        <div className="sticky top-16 z-40 bg-[#fafafa]/80 backdrop-blur-xl py-4 border-b border-gray-200 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="flex items-center gap-4 bg-white px-5 py-3 rounded-full shadow-sm border border-gray-100 w-full md:w-auto">
            <div className="flex flex-col">
              <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">今日可用选票</span>
              <span className="text-xl font-black text-[#1d1d1f] font-mono">{votesLeft} <span className="text-gray-300 text-base">/ 5</span></span>
            </div>
            <div className="w-px h-8 bg-gray-200 mx-2"></div>
            <button onClick={handleShare} className={`text-xs font-bold px-4 py-2 rounded-full flex items-center gap-1 ${hasShared ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-green-100 text-green-700 hover:bg-green-200'}`}>
              {hasShared ? '已获取分享奖励' : '转发获取 +1 票'}
            </button>
          </div>
          <div className="relative w-full md:w-64">
            <input
              type="text"
              placeholder="搜索论文..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-gray-200 text-sm rounded-full px-4 py-3 pl-10 focus:outline-none focus:border-blue-500 transition-all shadow-sm"
            />
          </div>
        </div>

        {/* 排序 Tabs：更改为调用 handleTabChange */}
        <div className="flex gap-2 mb-8">
          <button onClick={() => handleTabChange('hot')} className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${activeTab === 'hot' ? 'bg-[#1d1d1f] text-white' : 'bg-gray-200 text-gray-500'}`}>🔥 热度榜单</button>
          <button onClick={() => handleTabChange('new')} className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${activeTab === 'new' ? 'bg-[#1d1d1f] text-white' : 'bg-gray-200 text-gray-500'}`}>✨ 最新入库</button>
        </div>

        {/* 论文列表 */}
        <div className="flex flex-col gap-6">
          {isLoading && page === 1 && <div className="text-center py-10 text-gray-500">正在从学术垃圾桶中检索...</div>}

          {!isLoading && papers.length === 0 && (
            <div className="text-center py-20 text-gray-400"><span className="text-4xl block mb-4">📭</span>没有找到相关的灾难记录。</div>
          )}

          {papers.map((paper, index) => (
            <Link href={`/article/${paper.id}`} key={`${paper.id}-${index}`} className="bg-white border border-gray-100 p-6 md:p-8 rounded-3xl shadow-sm hover:shadow-xl transition-all flex flex-col md:flex-row gap-8 items-start relative group cursor-pointer">
              {activeTab === 'hot' && page === 1 && index < 3 && !searchQuery && (
                <div className={`absolute top-0 right-0 w-16 h-16 flex items-start justify-end p-3 rounded-bl-full font-black text-xl z-10 ${index === 0 ? 'bg-orange-100 text-orange-600' : index === 1 ? 'bg-gray-100 text-gray-500' : 'bg-amber-50 text-amber-700'}`}>#{index + 1}</div>
              )}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs font-mono font-bold bg-gray-100 text-gray-500 px-2 py-1 rounded">{paper.id}</span>
                  {activeTab === 'new' && <span className="text-xs font-bold bg-blue-50 text-blue-600 px-2 py-1 rounded">NEW</span>}
                </div>
                <h3 className="text-2xl font-bold font-serif text-[#1d1d1f] mb-2 group-hover:text-blue-600 transition-colors">{paper.title}</h3>
                <p className="text-sm font-medium text-gray-500 mb-4">研究员：{paper.author}</p>
                <p className="text-gray-600 font-light line-clamp-2 mb-6">{paper.abstract}</p>
              </div>

              <div className="flex flex-col items-center min-w-[120px] bg-gray-50 rounded-2xl p-4 border border-gray-100 w-full md:w-auto">
                <span className="text-[10px] text-gray-400 font-bold uppercase mb-1">Score</span>
                <span className="text-3xl font-black font-mono text-[#1d1d1f] mb-4">{paper.totalVotes}</span>
                <div className="flex flex-col w-full gap-2">
                  <button onClick={() => handleVote(paper.id)} disabled={votesLeft === 0} className={`w-full py-3 rounded-xl font-bold text-sm flex flex-col items-center gap-1 ${paper.userVotes > 0 ? 'bg-blue-600 text-white' : 'border-2 border-[#1d1d1f] text-[#1d1d1f]'} ${votesLeft === 0 && paper.userVotes === 0 ? 'opacity-50' : ''}`}>
                    <span>投它一票</span>
                    {paper.userVotes > 0 && <span className="text-[10px] font-mono bg-white/20 px-2 rounded-full">已投 {paper.userVotes} 票</span>}
                  </button>
                  {paper.userVotes > 0 && <button onClick={() => handleUnvote(paper.id)} className="w-full py-1.5 rounded-xl text-xs font-medium text-gray-400 hover:text-red-500">撤回一票</button>}
                </div>
              </div>
            </Link>
          ))}

          {/* 加载更多按钮 */}
          {hasMore && (
            <div className="text-center pt-8">
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={isLoading}
                className="bg-white border-2 border-gray-200 text-gray-600 px-8 py-3 rounded-full font-bold hover:border-black hover:text-black transition-colors disabled:opacity-50"
              >
                {isLoading ? '加载中...' : '挖掘更多往期文章 ↓'}
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}