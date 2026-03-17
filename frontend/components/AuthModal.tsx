"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createClient } from "@supabase/supabase-js";
import { Github, Mail, ArrowRight, X, Loader2 } from "lucide-react";

// 初始化 Supabase 客户端
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

// 创建单例客户端
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

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [magicLinkSent, setMagicLinkSent] = useState(false);
  const [error, setError] = useState("");

  // GitHub OAuth 登录
  const handleGithubLogin = async () => {
    const supabase = getSupabase();
    if (!supabase) {
      setError("Supabase 客户端未初始化");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
          redirectTo: `${window.location.origin}/user`,
        },
      });

      if (error) throw error;
    } catch (err: any) {
      setError(err.message || "登录失败，请重试");
      setIsLoading(false);
    }
  };

  // 邮箱免密登录 (Magic Link)
  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault();
    const supabase = getSupabase();
    if (!supabase) {
      setError("Supabase 客户端未初始化");
      return;
    }

    if (!email || !email.includes("@")) {
      setError("请输入有效的邮箱地址");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/user`,
        },
      });

      if (error) throw error;

      setMagicLinkSent(true);
    } catch (err: any) {
      setError(err.message || "发送失败，请重试");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 背景遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-md z-50"
            onClick={onClose}
          />

          {/* 弹窗内容 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md z-50"
          >
            <div className="bg-white/95 backdrop-blur-xl rounded-[2rem] shadow-2xl border border-gray-100/50 p-8 md:p-10">
              {/* 关闭按钮 */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              {/* 标题 */}
              <div className="text-center mb-10">
                <h2 className="font-serif text-2xl md:text-3xl text-[#1d1d1f] mb-2">
                  Access The Bonel Archive
                </h2>
                <p className="text-sm text-gray-500 tracking-widest uppercase">
                  验证研究员身份
                </p>
              </div>

              {/* 错误提示 */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-6 p-3 bg-red-50 border border-red-100 rounded-xl text-sm text-red-600 text-center"
                >
                  {error}
                </motion.div>
              )}

              {/* Magic Link 发送成功提示 */}
              {magicLinkSent ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-8"
                >
                  <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Mail className="w-8 h-8 text-green-600" />
                  </div>
                  <h3 className="font-serif text-xl text-[#1d1d1f] mb-2">
                    验证链接已发送
                  </h3>
                  <p className="text-gray-500 text-sm mb-6">
                    请检查邮箱 {email}，点击链接完成登录
                  </p>
                  <button
                    onClick={() => {
                      setMagicLinkSent(false);
                      setEmail("");
                    }}
                    className="text-sm text-gray-500 hover:text-[#1d1d1f] transition-colors"
                  >
                    使用其他方式登录
                  </button>
                </motion.div>
              ) : (
                <>
                  {/* GitHub 登录按钮 */}
                  <button
                    onClick={handleGithubLogin}
                    disabled={isLoading}
                    className="w-full group relative flex items-center justify-center gap-3 bg-[#1d1d1f] text-white py-4 px-6 rounded-2xl font-medium transition-all duration-300 hover:bg-black hover:shadow-lg hover:shadow-black/20 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        <Github className="w-5 h-5" />
                        <span>Continue with GitHub</span>
                        <ArrowRight className="w-4 h-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
                      </>
                    )}
                  </button>

                  {/* 分隔线 */}
                  <div className="relative my-8">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-200" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-4 bg-white/95 text-gray-400 tracking-widest uppercase text-xs">
                        or
                      </span>
                    </div>
                  </div>

                  {/* 邮箱免密登录 */}
                  <form onSubmit={handleMagicLink} className="space-y-4">
                    <div className="relative">
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="researcher@example.com"
                        className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl text-[#1d1d1f] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#1d1d1f]/10 focus:border-[#1d1d1f]/30 transition-all duration-300"
                        disabled={isLoading}
                      />
                      <Mail className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading || !email}
                      className="w-full flex items-center justify-center gap-2 bg-white border-2 border-gray-200 text-[#1d1d1f] py-4 px-6 rounded-2xl font-medium transition-all duration-300 hover:border-[#1d1d1f] hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <>
                          <span>发送免密验证链接</span>
                          <span className="text-xs text-gray-400 tracking-wider">
                            Send Magic Link
                          </span>
                        </>
                      )}
                    </button>
                  </form>

                  {/* 提示文字 */}
                  <p className="mt-6 text-center text-xs text-gray-400 leading-relaxed">
                    登录即表示您同意我们的服务条款
                    <br />
                    我们仅使用您的邮箱或 GitHub 公开信息用于身份验证
                  </p>
                </>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
