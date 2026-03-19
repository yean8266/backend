"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Image from "next/image";
import Link from "next/link";

// 原始数据
const originalSlides = [
    {
    id: 0,
    tag: "我们的愿景",
    title: "写在前面，我们想做的网站不止......",
    desc: "我的初衷是和搞笑诺贝尔奖一样，让大家思考一些看似无用实则有趣的问题，例如“意大利面为什么只能掰成三段？”",
    image: "",
    bgColor: "bg-gradient-to-br from-orange-100 to-amber-50",
    link: "/silence",
    textColor: "text-[#1d1d1f]"
  },
  {
    id: 1,
    tag: "最新消息",
    title: "BoNel Prize 2026提名",
    desc: "寻找最有趣的文章和奇思妙想？",
    image: "/bonelprize.jpg",
    bgColor: "bg-[#f5f5f7]",
    link: "/vote",
    textColor: "text-[#1d1d1f]"
  },
  {
    id: 2,
    tag: "幽默文章推荐",
    title: "甲沟炎vs痔疮，哪个更痛？",
    desc: "关注痛觉信号传递上的峰值强度，在感官维度上进行对比",
    image: "", 
    bgColor: "bg-gradient-to-br from-blue-100 to-blue-50",
    link: "/vote",
    textColor: "text-[#1d1d1f]"
  },
  {
    id: 3,
    tag: "即将到来",
    title: "AI格式化生成有趣文章",
    desc: "将你碎片零散的随笔，一键转化为标准的论述文章",
    image: "/ailab.jpg",
    bgColor: "bg-gradient-to-br from-orange-100 to-amber-50",
    link: "/ai-lab",
    textColor: "text-[#1d1d1f]"
  },
  {
    id: 4,
    tag: "社区",
    title: "往期有趣文章档案",
    desc: "灵机一动和奇思妙想将在我们这里被存档，被看见，被认可。",
    image: "",
    bgColor: "bg-[#1d1d1f]",
    link: "/hub",
    textColor: "text-white"
  }
];

// 【核心算法】：克隆最后一张放前面，克隆第一张放后面
const CLONE_COUNT = 2;
const slides = [
  ...originalSlides.slice(-CLONE_COUNT), // 把最后两张克隆到最前面
  ...originalSlides,                     // 真实的原始数组
  ...originalSlides.slice(0, CLONE_COUNT) // 把最前两张克隆到最后面
];

const TRANSITION_DURATION = 700; // 动画时长必须与 CSS 保持绝对一致

export default function HeroCarousel() {
  // 初始索引从 1 开始，因为 0 是我们克隆的假幻灯片
  const [currentIndex, setCurrentIndex] = useState(1); 
  const [isTransitioning, setIsTransitioning] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const isAnimatingRef = useRef(false);

  // 计算用于底部圆点显示的“真实索引” (0 到 originalSlides.length - 1)
  const realIndex = currentIndex === 0 
    ? originalSlides.length - 1 
    : currentIndex === originalSlides.length + 1 
    ? 0 
    : currentIndex - 1;

  const goToSlide = useCallback((index: number) => {
    if (isAnimatingRef.current) return;
    isAnimatingRef.current = true;
    setIsTransitioning(true);
    setCurrentIndex(index);

    // 动画结束后释放锁
    setTimeout(() => {
      isAnimatingRef.current = false;
    }, TRANSITION_DURATION);
  }, []);

  const nextSlide = useCallback(() => {
    goToSlide(currentIndex + 1);
  }, [currentIndex, goToSlide]);

  const prevSlide = useCallback(() => {
    goToSlide(currentIndex - 1);
  }, [currentIndex, goToSlide]);

  // 【核心算法】：监听边界越界，执行瞬间“无缝重置”
  useEffect(() => {
    if (currentIndex === 0) {
      const timer = setTimeout(() => {
        setIsTransitioning(false); // 关掉动画
        setCurrentIndex(originalSlides.length); // 瞬间跳回倒数第二张（真实的最后一张）
      }, TRANSITION_DURATION);
      return () => clearTimeout(timer);
    }
    
    if (currentIndex === originalSlides.length + 1) {
      const timer = setTimeout(() => {
        setIsTransitioning(false); // 关掉动画
        setCurrentIndex(1); // 瞬间跳回第二张（真实的第一张）
      }, TRANSITION_DURATION);
      return () => clearTimeout(timer);
    }
  }, [currentIndex]);

  // 自动播放
  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(nextSlide, 5000);
    return () => clearInterval(interval);
  }, [isPaused, nextSlide]);

  return (
    <div 
      className="w-full relative py-8 md:py-16 overflow-hidden group"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div 
        // 根据 isTransitioning 动态开关 CSS 动画
        className={`flex ${isTransitioning ? 'transition-transform ease-[cubic-bezier(0.25,1,0.5,1)]' : 'transition-none'}`}
        style={{
          transitionDuration: isTransitioning ? `${TRANSITION_DURATION}ms` : '0ms',
          transform: `translateX(calc(50vw - var(--slide-half) - (${currentIndex} * (var(--slide-full) + var(--gap)))))`
        } as any}
      >
        {/* CSS 变量作用域 */}
        <div className="contents" style={{
            "--gap": "1rem",
            "--slide-full": "85vw",
            "--slide-half": "42.5vw",
        } as any}></div>
        
        <style jsx>{`
          .flex {
            --slide-full: 85vw;
            --slide-half: 42.5vw;
            --gap: 1rem;
          }
          @media (min-width: 768px) {
            .flex {
              --slide-full: 60vw;
              --slide-half: 30vw;
              --gap: 2rem;
            }
          }
        `}</style>

        {slides.map((slide, index) => {
          const isActive = index === currentIndex;
          // 克隆节点需要有唯一的 key 避免 React 报错
          const uniqueKey = `${slide.id}-${index}`; 

          return (
            <div 
              key={uniqueKey} 
              className={`
                shrink-0 w-[85vw] md:w-[60vw] 
                aspect-[4/3] md:aspect-[21/9] 
                rounded-[2rem] overflow-hidden relative 
                ${isTransitioning ? "transition-all ease-out" : "transition-none"}
                ${isActive ? "scale-100 opacity-100 shadow-xl" : "scale-95 opacity-50 cursor-pointer hover:opacity-80"}
                mr-[1rem] md:mr-[2rem]
                last:mr-0
              `}
              style={{ transitionDuration: isTransitioning ? `${TRANSITION_DURATION}ms` : '0ms' }}
              onClick={() => {
                if (!isActive) goToSlide(index);
              }}
            >
              <div className={`absolute inset-0 ${slide.bgColor}`}>
                {slide.image && (
                  <Image 
                    src={slide.image} 
                    alt={slide.title}
                    fill
                    className="object-cover"
                    priority={true}
                  />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
              </div>

              <div className={`absolute bottom-0 left-0 right-0 p-6 md:p-12 flex flex-col items-start justify-end h-full transition-opacity duration-500 ${isActive ? 'opacity-100' : 'opacity-0'}`}>
                <span className={`text-[10px] md:text-xs font-bold tracking-[0.2em] uppercase mb-2 md:mb-4 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md ${slide.textColor}`}>
                  {slide.tag}
                </span>
                <h2 className={`text-2xl md:text-5xl font-bold mb-2 md:mb-4 tracking-tight leading-tight ${slide.textColor}`}>
                  {slide.title}
                </h2>
                <p className={`text-sm md:text-lg mb-6 md:mb-8 font-medium max-w-lg line-clamp-2 ${slide.textColor}`}>
                  {slide.desc}
                </p>
                <Link 
                  href={slide.link}
                  className="bg-white text-black px-6 py-2 md:px-8 md:py-3 rounded-full text-xs md:text-sm font-bold hover:scale-105 transition-transform shadow-lg"
                  onClick={(e) => e.stopPropagation()} 
                >
                  View Detail
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* 左右导航箭头 */}
      <button 
        onClick={prevSlide}
        className="absolute left-4 md:left-12 top-1/2 -translate-y-1/2 w-10 h-10 md:w-14 md:h-14 bg-white/80 backdrop-blur-xl rounded-full flex items-center justify-center text-black hover:scale-110 transition-all shadow-lg z-20 opacity-0 group-hover:opacity-100"
      >
        ‹
      </button>
      <button 
        onClick={nextSlide}
        className="absolute right-4 md:right-12 top-1/2 -translate-y-1/2 w-10 h-10 md:w-14 md:h-14 bg-white/80 backdrop-blur-xl rounded-full flex items-center justify-center text-black hover:scale-110 transition-all shadow-lg z-20 opacity-0 group-hover:opacity-100"
      >
        ›
      </button>

      {/* 底部指示器 */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 md:gap-3 z-20">
        {originalSlides.map((_, idx) => (
          <button
            key={idx}
            onClick={() => goToSlide(idx + 1)} // 映射回真实的数组索引
            className={`h-1.5 md:h-2 rounded-full transition-all duration-300 ${
              realIndex === idx 
                ? "bg-[#1d1d1f] w-6 md:w-8" 
                : "bg-gray-300 w-1.5 md:w-2 hover:bg-gray-400"
            }`}
          />
        ))}
      </div>
    </div>
  );
}