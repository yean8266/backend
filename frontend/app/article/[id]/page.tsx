"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { fetchPapers, submitVote } from "@/services/api";
import { supabase } from "@/lib/supabase";

interface Paper {
  id: string;
  title: string;
  author: string;
  abstract: string;
  totalVotes: number;
  userVotes: number;
  date: string;
}

export default function ArticleDetail() {
  const params = useParams();
  const paperId = params.id as string;
  
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [votesLeft, setVotesLeft] = useState(5);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // 获取当前用户
        const { data: { session } } = await supabase.auth.getSession();
        setUser(session?.user || null);

        // 由于没有单个文章接口，从列表中筛选
        const data = await fetchPapers("hot", 1, "");
        const foundPaper = data.papers.find((p: Paper) => p.id === paperId);
        
        if (foundPaper) {
          setPaper(foundPaper);
          if (data.userStatus) {
            setVotesLeft(data.userStatus.votesLeft);
          }
        } else {
          setError("文章未找到");
        }
      } catch (err) {
        console.error("加载文章失败:", err);
        setError("加载文章失败");
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

  if (loading) {
    return (
      <main className="min-h-screen bg-white pt-24 pb-24 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center py-20 text-zinc-400">加载中...</div>
        </div>
      </main>
    );
  }

  if (error || !paper) {
    return (
      <main className="min-h-screen bg-white pt-24 pb-24 px-6">
        <div className="max-w-3xl mx-auto">
          <Link
            href="/vote"
            className="text-zinc-500 hover:text-zinc-900 transition-colors text-sm mb-12 block"
          >
            ← 返回榜单
          </Link>
          <div className="text-center py-20 text-zinc-400">
            <span className="text-4xl block mb-4">📭</span>
            {error || "文章未找到"}
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-50 pt-24 pb-24 px-6">
      <div className="max-w-3xl mx-auto">
        {/* 返回按钮 */}
        <Link
          href="/vote"
          className="text-zinc-500 hover:text-zinc-900 transition-colors text-sm mb-12 block"
        >
          ← 返回榜单
        </Link>

        {/* 文章头部 */}
        <header className="mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-zinc-900 leading-tight mb-6">
            {paper.title}
          </h1>
          
          <div className="flex items-center gap-6 text-zinc-500 text-sm">
            <span>研究员：{paper.author}</span>
            <span className="w-1 h-1 bg-zinc-300 rounded-full"></span>
            <span>影响因子：{paper.totalVotes}</span>
            <span className="w-1 h-1 bg-zinc-300 rounded-full"></span>
            <span>{paper.date}</span>
          </div>
        </header>

        {/* 文章正文 */}
        <article className="mb-16">
          <div className="text-lg text-zinc-700 leading-loose space-y-6">
            <p>{paper.abstract}</p>
          </div>
        </article>

        {/* 底部操作区 */}
        <div className="border-t border-zinc-200 pt-12">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="text-sm text-zinc-500">
              {user ? (
                <span>
                  今日剩余选票：
                  <span className="font-bold text-zinc-900">{votesLeft}</span> / 5
                </span>
              ) : (
                <span>登录后可投票</span>
              )}
            </div>

            <button
              onClick={handleVote}
              disabled={!user || votesLeft === 0}
              className="bg-zinc-900 text-white rounded-full px-8 py-3 hover:bg-zinc-800 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {paper.userVotes > 0 ? `已投 ${paper.userVotes} 票` : "为它投票"}
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
