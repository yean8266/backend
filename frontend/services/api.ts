// services/api.ts
// Bonel Project - API Client
// 适配后端 /api/v1 路由规范，自动携带 Supabase JWT Token

import { createClient } from '@supabase/supabase-js';

// Supabase 配置
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// API 基础路径 - 对齐后端 /api/v1 规范
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * 获取当前用户的 JWT Token
 * 每次请求前调用，确保 Token 最新
 */
async function getAuthToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
}

/**
 * 通用的 fetch 封装
 * 自动添加 Authorization Header 和 Content-Type
 */
export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = await getAuthToken();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };
  
  // 如果有 token，添加到 Authorization header
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `请求失败: ${response.status}`);
  }
  
  return response;
}

// ==================== 接口 A: 获取文章列表 (支持分页、排序和搜索) + 用户状态 ====================

export interface Paper {
  id: string;
  title: string;
  author: string;
  abstract: string;
  totalVotes: number;
  userVotes: number;
  date: string;
}

export interface UserStatus {
  isLoggedIn: boolean;
  votesLeft: number;
  hasSharedToday: boolean;
}

export interface PapersResponse {
  userStatus: UserStatus;
  papers: Paper[];
  total: number;
  page: number;
  pageSize: number;
}

/**
 * 获取文章列表 (对应后端 GET /nominees)
 * 
 * 支持排序、分页和搜索
 * - sort: 'hot' 按票数降序, 'new' 按时间降序
 */
export async function fetchPapers(
  sort: 'hot' | 'new' = 'hot',
  page: number = 1,
  search: string = ''
): Promise<PapersResponse> {
  const queryParams = new URLSearchParams({
    sort,
    page: page.toString(),
  });
  if (search) queryParams.append('search', search);
  
  const response = await apiFetch(`/nominees?${queryParams.toString()}`);
  return response.json();
}

/**
 * 获取用户档案信息
 * 用于获取用户剩余票数等详细信息
 */
export async function fetchUserProfile(): Promise<{
  id: string;
  email?: string;
  nickname?: string;
  dailyVotesLeft: number;
  hasSharedToday: boolean;
}> {
  const response = await apiFetch('/user/profile');
  return response.json();
}

// ==================== 接口 B: 投一票 ====================

export interface VoteResponse {
  success: boolean;
  votesLeft?: number;
  totalVotes?: number;
}

/**
 * 投一票 (对应后端 POST /votes)
 * 
 * 注意：根据后端实际路由调整
 * 如果后端用 /votes，请改为 '/votes'
 */
export async function submitVote(paperId: string): Promise<VoteResponse> {
  // TODO: 确认后端路由是 /vote 还是 /votes
  const response = await apiFetch('/vote', {
    method: 'POST',
    body: JSON.stringify({ paperId }),
  });
  return response.json();
}

// ==================== 接口 C: 撤回一票 ====================

/**
 * 撤回一票 (对应后端 POST /votes/unvote 或 DELETE /votes)
 * 
 * 注意：根据后端实际路由调整
 */
export async function submitUnvote(paperId: string): Promise<VoteResponse> {
  // TODO: 确认后端路由
  const response = await apiFetch('/unvote', {
    method: 'POST',
    body: JSON.stringify({ paperId }),
  });
  return response.json();
}

// ==================== 接口 D: 上报分享成功 ====================

export interface ShareResponse {
  success: boolean;
  votesLeft?: number;
  hasSharedToday?: boolean;
}

/**
 * 上报分享成功 (对应后端 POST /share)
 */
export async function reportShareSuccess(): Promise<ShareResponse> {
  const response = await apiFetch('/share', {
    method: 'POST',
    body: JSON.stringify({}),
  });
  return response.json();
}

// ==================== 新增接口: 获取投票状态 ====================

export interface VoteStatusResponse {
  dailyVotesLeft: number;
  hasSharedToday: boolean;
  lastActiveDate: string;
}

/**
 * 获取用户今日投票状态
 * 用于页面初始化时获取剩余票数
 */
export async function fetchVoteStatus(): Promise<VoteStatusResponse> {
  const response = await apiFetch('/votes/status');
  return response.json();
}

// ==================== 新增接口: 获取排行榜 ====================

export interface LeaderboardItem {
  rank: number;
  paper: Paper;
}

export interface LeaderboardResponse {
  items: LeaderboardItem[];
  total: number;
  page: number;
  pageSize: number;
}

/**
 * 获取排行榜 (热度榜单)
 */
export async function fetchLeaderboard(
  page: number = 1,
  pageSize: number = 20
): Promise<LeaderboardResponse> {
  const queryParams = new URLSearchParams({
    page: page.toString(),
    pageSize: pageSize.toString(),
  });
  
  const response = await apiFetch(`/leaderboard?${queryParams.toString()}`);
  return response.json();
}

// ==================== 新增接口: 获取平台统计 ====================

export interface StatsResponse {
  totalNominees: number;
  totalVotes: number;
  totalUsers: number;
  todayVotes: number;
}

/**
 * 获取平台全局统计数据
 */
export async function fetchStats(): Promise<StatsResponse> {
  const response = await apiFetch('/stats');
  return response.json();
}

// ==================== 新增接口: 健康检查 ====================

export interface HealthResponse {
  status: string;
  timestamp: string;
  version?: string;
}

/**
 * 健康检查
 * 用于前端探测服务器状态
 */
export async function checkHealth(): Promise<HealthResponse> {
  // 健康检查不需要认证
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('服务器无响应');
  }
  return response.json();
}

// ==================== 接口 E: 提交论文 (支持 PDF 附件) ====================

/**
 * 提交抽象论文 (对应后端 POST /submit)
 * 
 * 注意：FormData 请求不自动添加 Content-Type，让浏览器自动设置
 */
export async function submitPaper(formData: FormData): Promise<{ success: boolean; id?: string }> {
  const token = await getAuthToken();
  
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}/nominees`, {
    method: 'POST',
    headers,
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || '提交失败');
  }
  
  return response.json();
}

// ==================== 接口 F: 获取单篇文章详情 ====================

export interface PaperDetail extends Paper {
  original_link?: string;
  pdf_url?: string;
}

/**
 * 获取单篇文章详情 (对应后端 GET /nominees/{id})
 * 
 * 包含原文链接和 PDF 下载链接
 */
export async function fetchPaperDetail(paperId: string): Promise<PaperDetail> {
  const response = await apiFetch(`/nominees/${paperId}`);
  return response.json();
}

// ==================== Supabase 客户端已导出 ====================
