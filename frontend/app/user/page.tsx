"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { createClient } from "@supabase/supabase-js";
import {
  User,
  Mail,
  MessageCircle,
  Cpu,
  Save,
  Loader2,
  Ticket,
  FileText,
  Crown,
  AlertCircle,
} from "lucide-react";

// 初始化 Supabase 客户端
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

// 创建单例客户端，避免重复创建
let supabaseInstance: ReturnType<typeof createClient> | null = null;

const getSupabase = () => {
  if (!supabaseInstance && supabaseUrl && supabaseAnonKey) {
    supabaseInstance = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
      },
    });
  }
  return supabaseInstance;
};

// 灾难深水区选项
const DISASTER_DOMAINS = [
  { value: "", label: "选择您的专业领域" },
  { value: "robotics", label: "Robotics / 机器人" },
  { value: "embedded", label: "Embedded Systems / 嵌入式" },
  { value: "fullstack", label: "Full Stack / 全栈开发" },
  { value: "ai-ml", label: "AI / Machine Learning" },
  { value: "hardware", label: "Hardware / 硬件设计" },
  { value: "devops", label: "DevOps / 运维工程" },
  { value: "blockchain", label: "Blockchain / 区块链" },
  { value: "other", label: "Other / 其他灾难" },
];

export default function UserProfilePage() {
  const router = useRouter();
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [supabaseReady, setSupabaseReady] = useState(false);

  // 表单数据
  const [nickname, setNickname] = useState("");
  const [wechatContact, setWechatContact] = useState("");
  const [disasterDomain, setDisasterDomain] = useState("");

  // 用户状态数据
  const [votesLeft, setVotesLeft] = useState(5);
  const [submissionsCount, setSubmissionsCount] = useState(0);

  // 检查登录状态
  useEffect(() => {
    const checkSession = async () => {
      try {
        // 检查 Supabase 配置
        if (!supabaseUrl || !supabaseAnonKey) {
          setError("Supabase 配置缺失，请检查环境变量");
          setLoading(false);
          return;
        }

        const supabase = getSupabase();
        if (!supabase) {
          setError("无法初始化 Supabase 客户端");
          setLoading(false);
          return;
        }

        setSupabaseReady(true);

        // 获取会话
        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession();

        if (sessionError) {
          console.error("获取会话失败:", sessionError);
          setError("获取登录状态失败");
          setLoading(false);
          return;
        }

        if (!session) {
          // 未登录，重定向到登录页
          router.push("/login");
          return;
        }

        setSession(session);

        // 获取用户资料
        try {
          const { data: profile, error: profileError } = await supabase
            .from("profiles")
            .select("*")
            .eq("id", session.user.id)
            .single();

          if (profileError && profileError.code !== "PGRST116") {
            // PGRST116 = 未找到记录，这是正常的（新用户）
            console.error("获取用户资料失败:", profileError);
          }

          if (profile && typeof profile === 'object') {
            setNickname((profile as any).nickname || "");
            setWechatContact((profile as any).wechat_contact || "");
            setDisasterDomain((profile as any).disaster_domain || "");
            setVotesLeft((profile as any).daily_votes_left || 5);
          }
        } catch (err) {
          console.error("获取用户资料异常:", err);
        }

        // 获取提交数量
        try {
          const { count, error: countError } = await supabase
            .from("submissions")
            .select("*", { count: "exact", head: true })
            .eq("user_id", session.user.id);

          if (!countError) {
            setSubmissionsCount(count || 0);
          }
        } catch (err) {
          console.error("获取提交数量异常:", err);
        }

        setLoading(false);
      } catch (err) {
        console.error("检查会话异常:", err);
        setError("系统错误，请刷新页面重试");
        setLoading(false);
      }
    };

    checkSession();

    // 监听认证状态变化
    const supabase = getSupabase();
    if (supabase) {
      const {
        data: { subscription },
      } = supabase.auth.onAuthStateChange((_event, session) => {
        if (!session) {
          router.push("/login");
        }
      });

      return () => subscription.unsubscribe();
    }
  }, [router]);

  // 保存用户资料
  const handleSave = async () => {
    if (!wechatContact.trim()) {
      setError("请填写微信号，用于接收奖金");
      return;
    }

    const supabase = getSupabase();
    if (!supabase || !session) {
      setError("未登录或客户端未初始化");
      return;
    }

    setSaving(true);
    setSaveSuccess(false);
    setError(null);

    try {
      const { error: upsertError } = await supabase.from("profiles").upsert(
        {
          id: session.user.id,
          nickname: nickname.trim() || null,
          wechat_contact: wechatContact.trim(),
          disaster_domain: disasterDomain || null,
          updated_at: new Date().toISOString(),
        } as any,
        { onConflict: "id" }
      );

      if (upsertError) throw upsertError;

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      console.error("保存失败:", err);
      setError(err.message || "保存失败，请重试");
    } finally {
      setSaving(false);
    }
  };

  // 退出登录
  const handleLogout = async () => {
    const supabase = getSupabase();
    if (supabase) {
      await supabase.auth.signOut();
    }
    router.push("/");
  };

  // 重定向到登录页
  const handleGoToLogin = () => {
    router.push("/login");
  };

  // 加载中状态
  if (loading) {
    return (
      <div className="min-h-screen bg-[#fafafa] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400 mx-auto mb-4" />
          <p className="text-sm text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  // 错误状态
  if (error && !supabaseReady) {
    return (
      <div className="min-h-screen bg-[#fafafa] flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white rounded-[2rem] border border-gray-100 p-8 text-center">
          <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="font-serif text-xl text-[#1d1d1f] mb-2">配置错误</h2>
          <p className="text-gray-500 mb-6">{error}</p>
          <p className="text-xs text-gray-400">
            请确保已配置 NEXT_PUBLIC_SUPABASE_URL 和 NEXT_PUBLIC_SUPABASE_ANON_KEY
          </p>
        </div>
      </div>
    );
  }

  // 未登录状态
  if (!session) {
    return (
      <div className="min-h-screen bg-[#fafafa] flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full bg-white rounded-[2rem] border border-gray-100 p-8 text-center"
        >
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="w-8 h-8 text-gray-400" />
          </div>
          <h2 className="font-serif text-xl text-[#1d1d1f] mb-2">
            请先登录
          </h2>
          <p className="text-gray-500 mb-6">
            访问研究员档案需要先验证身份
          </p>
          <button
            onClick={handleGoToLogin}
            className="w-full bg-[#1d1d1f] text-white py-4 px-6 rounded-2xl font-medium transition-all duration-300 hover:bg-black"
          >
            前往登录
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fafafa]">
      {/* 页面标题 */}
      <div className="pt-24 pb-12 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <p className="text-xs text-gray-400 tracking-[0.3em] uppercase mb-3">
              Researcher Profile
            </p>
            <h1 className="font-serif text-4xl md:text-5xl text-[#1d1d1f] mb-4">
              研究员档案
            </h1>
            <p className="text-gray-500 max-w-xl">
              完善您的个人信息，参与年度抽象工程灾难评选
            </p>
          </motion.div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="px-6 pb-24">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* 错误提示 */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-50 border border-red-100 rounded-2xl p-4 flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <p className="text-red-700 text-sm">{error}</p>
            </motion.div>
          )}

          {/* 账号信息卡片 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="bg-white rounded-[2rem] border border-gray-100 p-8"
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-[#1d1d1f] rounded-2xl flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="font-serif text-xl text-[#1d1d1f]">账号信息</h2>
                <p className="text-sm text-gray-400">Account Information</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
                <Mail className="w-5 h-5 text-gray-400" />
                <div className="flex-1">
                  <p className="text-xs text-gray-400 tracking-widest uppercase mb-1">
                    登录邮箱
                  </p>
                  <p className="text-[#1d1d1f]">{session?.user?.email}</p>
                </div>
              </div>

              <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
                <Crown className="w-5 h-5 text-gray-400" />
                <div className="flex-1">
                  <p className="text-xs text-gray-400 tracking-widest uppercase mb-1">
                    登录方式
                  </p>
                  <p className="text-[#1d1d1f]">
                    {session?.user?.app_metadata?.provider === "github"
                      ? "GitHub"
                      : "邮箱验证"}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* 状态统计卡片 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {/* 剩余票数 */}
            <div className="bg-white rounded-[2rem] border border-gray-100 p-8">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center">
                  <Ticket className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-400 tracking-widest uppercase">
                    今日剩余选票
                  </p>
                  <p className="text-3xl font-serif text-[#1d1d1f]">{votesLeft}</p>
                </div>
              </div>
              <p className="text-sm text-gray-400">
                每日 00:00 自动重置为 5 票
              </p>
            </div>

            {/* 提交数量 */}
            <div className="bg-white rounded-[2rem] border border-gray-100 p-8">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-purple-50 rounded-2xl flex items-center justify-center">
                  <FileText className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-400 tracking-widest uppercase">
                    已提交灾难
                  </p>
                  <p className="text-3xl font-serif text-[#1d1d1f]">
                    {submissionsCount}
                  </p>
                </div>
              </div>
              <p className="text-sm text-gray-400">
                每篇被采纳的论文将获得奖励
              </p>
            </div>
          </motion.div>

          {/* 个人信息表单 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="bg-white rounded-[2rem] border border-gray-100 p-8"
          >
            <div className="flex items-center gap-4 mb-8">
              <div className="w-12 h-12 bg-gradient-to-br from-gray-800 to-black rounded-2xl flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="font-serif text-xl text-[#1d1d1f]">完善档案</h2>
                <p className="text-sm text-gray-400">Complete Your Profile</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* 研究员代号 */}
              <div>
                <label className="block text-xs text-gray-400 tracking-widest uppercase mb-2">
                  Nickname / 研究员代号
                </label>
                <input
                  type="text"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  placeholder="例如：Dr. Disaster"
                  className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl text-[#1d1d1f] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#1d1d1f]/10 focus:border-[#1d1d1f]/30 transition-all duration-300"
                />
              </div>

              {/* 微信号 */}
              <div>
                <label className="block text-xs text-gray-400 tracking-widest uppercase mb-2">
                  <span className="flex items-center gap-2">
                    WeChat Contact / 奖金接收微信号
                    <span className="text-red-500">*</span>
                  </span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={wechatContact}
                    onChange={(e) => setWechatContact(e.target.value)}
                    placeholder="请输入您的微信号"
                    className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl text-[#1d1d1f] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#1d1d1f]/10 focus:border-[#1d1d1f]/30 transition-all duration-300"
                  />
                  <MessageCircle className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                </div>
                <p className="mt-2 text-xs text-amber-600 bg-amber-50 px-3 py-2 rounded-lg">
                  必填：用于接收论文采纳奖金，请确保填写正确
                </p>
              </div>

              {/* 灾难深水区 */}
              <div>
                <label className="block text-xs text-gray-400 tracking-widest uppercase mb-2">
                  Disaster Domain / 灾难深水区
                </label>
                <div className="relative">
                  <select
                    value={disasterDomain}
                    onChange={(e) => setDisasterDomain(e.target.value)}
                    className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl text-[#1d1d1f] focus:outline-none focus:ring-2 focus:ring-[#1d1d1f]/10 focus:border-[#1d1d1f]/30 transition-all duration-300 appearance-none cursor-pointer"
                  >
                    {DISASTER_DOMAINS.map((domain) => (
                      <option key={domain.value} value={domain.value}>
                        {domain.label}
                      </option>
                    ))}
                  </select>
                  <Cpu className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* 保存按钮 */}
              <div className="pt-4">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="w-full md:w-auto flex items-center justify-center gap-2 bg-[#1d1d1f] text-white px-8 py-4 rounded-2xl font-medium transition-all duration-300 hover:bg-black hover:shadow-lg hover:shadow-black/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>保存中...</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5" />
                      <span>保存档案</span>
                    </>
                  )}
                </button>

                {/* 成功提示 */}
                {saveSuccess && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="mt-4 p-4 bg-green-50 border border-green-100 rounded-2xl text-green-700 text-center"
                  >
                    档案保存成功！
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>

          {/* 退出登录 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex justify-center"
          >
            <button
              onClick={handleLogout}
              className="text-sm text-gray-400 hover:text-[#1d1d1f] transition-colors"
            >
              退出登录
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
