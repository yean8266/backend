"use client";

import { useState } from "react";
import AuthModal from "@/components/AuthModal";

export default function LoginPage() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(true);

  return (
    <div className="min-h-screen bg-[#fafafa] flex items-center justify-center">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-b from-gray-100 to-transparent rounded-full opacity-50" />
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-t from-gray-100 to-transparent rounded-full opacity-50" />
      </div>

      {/* 登录弹窗 */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />

      {/* 提示文字 */}
      <div className="absolute bottom-12 text-center">
        <p className="text-xs text-gray-400 tracking-widest uppercase">
          The Bonel Project © 2026
        </p>
      </div>
    </div>
  );
}
