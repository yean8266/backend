"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { submitPaper } from "@/services/api";

export default function SubmitPaper() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 表单状态管理
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [contact, setContact] = useState(""); // 新增：通讯作者联系方式
  const [abstract, setAbstract] = useState("");
  const [link, setLink] = useState("");
  const [file, setFile] = useState<File | null>(null); // 新增：PDF 文件状态

  // UI 交互状态
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        alert("为了维持顶刊的尊严，目前仅支持 PDF 格式的文件！");
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) { // 限制 10MB
        alert("文件太大了！学术垃圾请压缩在 10MB 以内。");
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 1. 简单的表单校验
    if (!title.trim() || !abstract.trim() || !contact.trim()) {
      alert("标题、摘要和联系方式是必填项！否则发奖金的时候找不到你人。");
      return;
    }

    // 2. 检查用户是否登录
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) {
      alert("请先在顶部导航栏登录，我们不接收完全的匿名信件！");
      return;
    }

    setIsSubmitting(true);

    try {
      // 3. 构建 FormData 对象 (支持文本 + 文件混合上传)
      const formData = new FormData();
      formData.append("title", title.trim());
      formData.append("author", author.trim() || "佚名研究员");
      formData.append("contact", contact.trim());
      formData.append("abstract", abstract.trim());
      formData.append("link", link.trim());
      if (file) {
        formData.append("file", file); // 附加 PDF 文件
      }

      // 4. 调用 API 提交数据
      await submitPaper(formData);

      // 5. 提交成功反馈
      alert("✅ 灾难档案已成功递交！正在等待学术委员会（后端）审核。");
      router.push("/vote");

    } catch (error) {
      console.error(error);
      alert("提交失败，学术炼金炉好像炸了，请稍后再试。");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#fafafa] pt-24 pb-24 px-6">
      <div className="max-w-2xl mx-auto">

        <header className="mb-12 text-center">
          <h1 className="text-4xl font-serif font-bold text-[#1d1d1f] mb-4">递交你的抽象档案。</h1>
          <p className="text-gray-500 text-lg">每一场伟大的思想，都值得被全网铭记。请在此申请 2026 年度贝诺尔奖提名。</p>
        </header>

        <form onSubmit={handleSubmit}
              className="space-y-10 bg-white p-8 md:p-12 rounded-[2rem] shadow-sm border border-gray-100">

          {/* Title */}
          <div className="group">
            <label className="block text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Paper Title / 论文标题
              (必填)</label>
            <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="例如：论一台无人机是如何学会在水下呼吸的..."
                className="w-full text-xl md:text-2xl font-serif text-[#1d1d1f] border-b border-gray-200 focus:border-blue-600 outline-none py-2 bg-transparent transition-colors placeholder:text-gray-300"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Author */}
            {/* 新增了 flex flex-col justify-end 让输入框强制底部对齐 */}
            <div className="group flex flex-col justify-end">
              <label className="block text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Authors / 第一背锅侠
                (支持匿名)</label>
              <input
                  type="text"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  placeholder="例如：某不知名全栈工程师"
                  className="w-full text-lg font-serif text-[#1d1d1f] border-b border-gray-200 focus:border-blue-600 outline-none py-2 bg-transparent transition-colors placeholder:text-gray-300"
              />
            </div>

            {/* Contact */}
            {/* 同样新增了 flex flex-col justify-end */}
            <div className="group flex flex-col justify-end">
              <label className="block text-xs font-bold tracking-widest text-orange-400 uppercase mb-2">Contact /
                通讯作者微信号 (发奖金用)</label>
              <input
                  type="text"
                  required
                  value={contact}
                  onChange={(e) => setContact(e.target.value)}
                  placeholder="微信号或手机号"
                  className="w-full text-lg font-serif text-[#1d1d1f] border-b border-gray-200 focus:border-orange-500 outline-none py-2 bg-transparent transition-colors placeholder:text-gray-300"
              />
            </div>
          </div>

          {/* Abstract */}
          <div className="group">
            <label className="block text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Abstract / 灾难复盘
              (必填)</label>
            <textarea
                rows={5}
                required
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                placeholder="请严肃地描述一下你原本想干嘛，以及最后它炸得有多么壮观..."
                className="w-full text-base text-[#1d1d1f] border-b border-gray-200 focus:border-blue-600 outline-none py-2 bg-transparent transition-colors placeholder:text-gray-300 resize-none leading-relaxed"
            />
          </div>

          {/* Original Link & File Upload */}
          <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100 space-y-6">
            <h3 className="text-sm font-bold text-[#1d1d1f] mb-2">附加材料，原文链接 (提供其一即可)</h3>

            <div className="group">
              <label className="block text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Evidence Link /
                事故现场链接</label>
              <input
                  type="url"
                  value={link}
                  onChange={(e) => setLink(e.target.value)}
                  placeholder="https://github.com/... 或 原文链接"
                  className="w-full text-sm font-mono text-blue-600 border-b border-gray-300 focus:border-blue-600 outline-none py-2 bg-transparent transition-colors placeholder:text-gray-400"
              />
            </div>

            <div className="relative">
              <label className="block text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Upload PDF / 上传源文件
                (.pdf)</label>
              <input
                  type="file"
                  accept=".pdf"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
              />
              <div
                  onClick={() => fileInputRef.current?.click()}
                  className={`w-full py-4 px-6 border-2 border-dashed rounded-xl cursor-pointer transition-all flex items-center justify-center gap-2 text-sm font-medium
                  ${file ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-300 hover:border-gray-400 text-gray-500 hover:bg-white'}
                `}
              >
                {file ? (
                    <><span>📄</span> {file.name} (已选择)</>
                ) : (
                    <><span>📎</span> 点击此处选择 PDF 文件上传 (最大 10MB)</>
                )}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-4 text-center">
            <button
                type="submit"
                disabled={isSubmitting}
                className={`bg-[#1d1d1f] text-white px-12 py-4 rounded-full text-base font-bold transition-all shadow-xl w-full md:w-auto
                ${isSubmitting ? "opacity-70 cursor-not-allowed" : "hover:scale-105 active:scale-95"}
              `}
            >
              {isSubmitting ? "🚀 正在推送至学术委员会..." : "提交同行评审 (Submit)"}
            </button>
            <p className="mt-4 text-xs text-gray-400 font-mono">
              *点击提交即代表您同意我们在《Noture》期刊上公开嘲笑您的工程痛楚。
            </p>
          </div>
        </form>

      </div>
    </main>
  );
}