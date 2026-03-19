"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch, submitVote, submitUnvote } from "@/services/api";
import { supabase } from "@/lib/supabase";

interface PaperDetail {
  id: string;
  title: string;
  author: string;
  abstract: string;
  totalVotes: number;
  userVotes: number;
  date: string;
  original_link?: string;
  pdf_url?: string;
}

export default function ArticleDetail() {
  const params = useParams();
  const paperId = params.id as string;

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [votesLeft, setVotesLeft] = useState(5);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // 获取当前用户
        const { data: { session } } = await supabase.auth.getSession();
        setUser(session?.user || null);

        // 调用单个文章详情接口
        const response = await apiFetch(`/nominees/${paperId}`);
        const paperData = await response.json();
        
        setPaper(paperData);
        
        // 如果响应中包含用户状态，更新票数
        if (paperData.votesLeft !== undefined) {
          setVotesLeft(paperData.votesLeft);
        }
      } catch (err: any) {
        console.error("加载文章失败:", err);
        if (err.message?.includes("404") || err.message?.includes("not found")) {
          setError("Paper not found");
        } else {
          setError("加载文章失败，请稍后重试");
        }
      } finally {
        setLoading(false);
      }
    };

    if (paperId) {
      loadData();
    }
  }, [paperId]);

  const handleVote = async () => {
    if (!user) {
      alert("请先通过顶部导航栏登录！");
      return;
    }
    if (votesLeft <= 0) {
      alert("选票已耗尽！");
      return;
    }
    if (!paper) return;

    // 乐观更新
    setVotesLeft((prev) => prev - 1);
    setPaper((prev) =>
      prev
        ? {
            ...prev,
            totalVotes: prev.totalVotes + 1,
            userVotes: prev.userVotes + 1,
          }
        : null
    );

    try {
      await submitVote(paper.id);
    } catch (e) {
      alert("投票失败，选票已退回。");
      setVotesLeft((prev) => prev + 1);
      setPaper((prev) =>
        prev
          ? {
              ...prev,
              totalVotes: prev.totalVotes - 1,
              userVotes: prev.userVotes - 1,
            }
          : null
      );
    }
  };

  const handleUnvote = async () => {
    if (!paper || paper.userVotes <= 0) return;
    if (!user) {
      alert("请先登录！");
      return;
    }

    // 乐观更新
    setVotesLeft((prev) => prev + 1);
    setPaper((prev) =>
      prev
        ? {
            ...prev,
            totalVotes: prev.totalVotes - 1,
            userVotes: prev.userVotes - 1,
          }
        : null
    );

    try {
      await submitUnvote(paper.id);
    } catch (e) {
      alert("撤回失败");
      setVotesLeft((prev) => prev - 1);
      setPaper((prev) =>
        prev
          ? {
              ...prev,
              totalVotes: prev.totalVotes + 1,
              userVotes: prev.userVotes + 1,
            }
          : null
      );
    }
  };

  // Loading Skeleton
  if (loading) {
    return (
      <main className="min-h-screen bg-white pt-24 pb-24 px-6">
        <div className="max-w-3xl mx-auto">
          {/* 返回按钮骨架 */}
          <div className="w-24 h-5 bg-zinc-200 rounded mb-12 animate-pulse" />
          
          {/* 标题骨架 */}
          <div className="space-y-4 mb-16">
            <div className="w-3/4 h-12 bg-zinc-200 rounded-lg animate-pulse" />
            <div className="w-1/2 h-12 bg-zinc-200 rounded-lg animate-pulse" />
          </div>
          
          {/* 元数据骨架 */}
          <div className="flex items-center gap-4 mb-16">
            <div className="w-32 h-4 bg-zinc-200 rounded animate-pulse" />
            <div className="w-1 h-1 bg-zinc-300 rounded-full" />
            <div className="w-24 h-4 bg-zinc-200 rounded animate-pulse" />
            <div className="w-1 h-1 bg-zinc-300 rounded-full" />
            <div className="w-20 h-4 bg-zinc-200 rounded animate-pulse" />
          </div>
          
          {/* 正文骨架 */}
          <div className="space-y-4 mb-16">
            <div className="w-full h-4 bg-zinc-200 rounded animate-pulse" />
            <div className="w-full h-4 bg-zinc-200 rounded animate-pulse" />
            <div className="w-5/6 h-4 bg-zinc-200 rounded animate-pulse" />
            <div className="w-full h-4 bg-zinc-200 rounded animate-pulse" />
            <div className="w-4/5 h-4 bg-zinc-200 rounded animate-pulse" />
          </div>
          
          {/* 底部骨架 */}
          <div className="border-t border-zinc-200 pt-12">
            <div className="w-full h-12 bg-zinc-200 rounded-full animate-pulse" />
          </div>
        </div>
      </main>
    );
  }

  // Error / 404 State
  if (error || !paper) {
    return (
      <main className="min-h-screen bg-white pt-24 pb-24 px-6">
        <div className="max-w-3xl mx-auto">
          <Link
            href="/vote"
            className="inline-flex items-center text-zinc-500 hover:text-zinc-900 transition-opacity text-sm mb-12 hover:opacity-70"
          >
            <span className="mr-1">←</span> 返回榜单
          </Link>
          <div className="text-center py-20">
            <span className="text-6xl block mb-6 text-zinc-300">📭</span>
            <h2 className="text-2xl font-medium text-zinc-900 mb-2">
              {error === "Paper not found" ? "文章未找到" : "加载失败"}
            </h2>
            <p className="text-zinc-500">
              {error === "Paper not found" 
                ? "这篇论文可能已被移除或编号有误" 
                : error}
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white pt-24 pb-24 px-6">
      <div className="max-w-3xl mx-auto">
        {/* 返回按钮 */}
        <Link
          href="/vote"
          className="inline-flex items-center text-zinc-500 hover:text-zinc-900 transition-opacity text-sm mb-12 hover:opacity-70"
        >
          <span className="mr-1">←</span> 返回榜单
        </Link>

        {/* 文章头部 */}
        <header className="mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-[#1d1d1f] leading-tight mb-8">
            {paper.title}
          </h1>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-zinc-500 text-sm">
            <span>研究员：{paper.author}</span>
            <span className="w-1 h-1 bg-zinc-300 rounded-full hidden sm:block" />
            <span>影响因子：{paper.totalVotes}</span>
            <span className="w-1 h-1 bg-zinc-300 rounded-full hidden sm:block" />
            <span>{paper.date}</span>
          </div>
        </header>

        {/* 文章正文 */}
        <article className="mb-16">
          <div className="text-lg text-zinc-700 leading-loose whitespace-pre-wrap">
            {paper.abstract}
          </div>
        </article>

        {/* 原文链接 / PDF 下载 */}
        {(paper.original_link || paper.pdf_url) && (
          <div className="mb-12">
            <div className="flex flex-wrap gap-4">
              {paper.original_link && (
                <a
                  href={paper.original_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-6 py-3 border border-zinc-300 text-zinc-700 rounded-full hover:bg-zinc-50 transition-colors text-sm font-medium"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  查看原文
                </a>
              )}
              {paper.pdf_url && (
                <a
                  href={paper.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-6 py-3 border border-zinc-300 text-zinc-700 rounded-full hover:bg-zinc-50 transition-colors text-sm font-medium"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  下载 PDF
                </a>
              )}
            </div>
          </div>
        )}

        {/* 底部操作区 */}
        <div className="border-t border-zinc-200 pt-12">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="text-sm text-zinc-500">
              {user ? (
                <span>
                  今日剩余选票：
                  <span className="font-semibold text-[#1d1d1f]">{votesLeft}</span> / 5
                </span>
              ) : (
                <span>登录后可投票</span>
              )}
            </div>

            <div className="flex items-center gap-4">
              {paper.userVotes > 0 && (
                <button
                  onClick={handleUnvote}
                  className="text-sm text-zinc-400 hover:text-red-500 transition-colors"
                >
                  撤回一票
                </button>
              )}
              <button
                onClick={handleVote}
                disabled={!user || votesLeft === 0}
                className="bg-[#1d1d1f] text-white rounded-full px-8 py-3 hover:bg-zinc-800 transition disabled:opacity-40 disabled:cursor-not-allowed font-medium"
              >
                {paper.userVotes > 0 ? `已投 ${paper.userVotes} 票` : "为它投票"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
