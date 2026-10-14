import React from "react";
import { Check, Flame, Trophy, Star, MessageSquare, Newspaper, Monitor, Sparkles, BookOpen, Heart, HelpCircle, Film } from "lucide-react";
import { Template } from "@/types";

interface TemplateMockupCardProps {
  template: Template;
  isSelected: boolean;
  onSelect: () => void;
}

const TEMPLATE_PREVIEWS: Record<string, string> = {
  tesla_fsd_vision: "/templates/tesla_fsd_vision.jpg",
  promo_fitness_gym: "/templates/promo_fitness_gym.jpg",
  vlog_sticker_lifestyle: "/templates/vlog_sticker_lifestyle.jpg",
  vlog_money_salary: "/templates/vlog_money_salary.jpg",
  youth_tips_pick: "/templates/youth_tips_pick.jpg",
  drama_weekly_preview: "/templates/drama_weekly_preview.jpg",
  news_portal: "/templates/news_portal.jpg",
  browser_window: "/templates/browser_window.jpg",
  messenger_chat: "/templates/messenger_chat.jpg",
  ranking_chart: "/templates/ranking_chart.jpg",
  facetime_call: "/templates/facetime_call.jpg",
  instagram_reels: "/templates/instagram_reels.jpg",
  iphone_gallery: "/templates/iphone_gallery.jpg",
  product_review: "/templates/product_review.jpg",
  breaking_news: "/templates/news_portal.jpg",
  tech_review: "/templates/browser_window.jpg",
};

export default function TemplateMockupCard({
  template,
  isSelected,
  onSelect,
}: TemplateMockupCardProps) {
  const tId = template.id;
  const previewImage = `/templates/${tId}.jpg?v=2`;

  return (
    <div
      id={`template-card-${template.id}`}
      onClick={onSelect}
      className={`group relative rounded-2xl p-3.5 border cursor-pointer transition-all duration-300 flex flex-col justify-between ${
        isSelected
          ? "bg-gradient-to-b from-indigo-900/50 via-slate-900/90 to-slate-950 border-indigo-500 shadow-2xl shadow-indigo-500/20 ring-2 ring-indigo-500 scale-[1.02]"
          : "glass-card hover:border-slate-600 hover:scale-[1.01]"
      }`}
    >
      {/* Selection Checkmark Badge */}
      {isSelected && (
        <div className="absolute -top-2.5 -right-2.5 z-20 bg-indigo-600 text-white p-1 rounded-full shadow-lg shadow-indigo-600/50 border border-indigo-400">
          <Check className="w-3.5 h-3.5 stroke-[3]" />
        </div>
      )}

      {/* Visual 9:16 Miniature Screen Mockup (MiriCanvas Style) */}
      <div className="relative aspect-[9/16] w-full rounded-xl overflow-hidden shadow-2xl border border-white/10 mb-3 flex flex-col justify-between p-2 select-none bg-slate-950">
        {previewImage ? (
          <div className="absolute inset-0 bg-slate-950 overflow-hidden group/thumb">
            <img
              src={previewImage}
              alt={template.name}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            {/* Subtle border highlight for aesthetic depth */}
            <div className="absolute inset-0 border border-white/5 pointer-events-none" />

            {/* Top Badge */}
            <div className="absolute top-2 left-2 flex items-center gap-1 z-10">
              <span className="bg-black/60 backdrop-blur-md text-white text-[8px] font-bold px-2 py-0.5 rounded-full border border-white/20 shadow">
                {template.badge_prefix}
              </span>
              {template.category.includes("테슬라") && (
                <span className="bg-red-600/90 backdrop-blur-md text-white text-[7px] font-bold px-1.5 py-0.5 rounded-full border border-red-400/50 shadow">
                  TESLA
                </span>
              )}
            </div>

            {/* Hover Play Button */}
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/20 backdrop-blur-[1px]">
              <div className="w-9 h-9 rounded-full bg-indigo-600/90 text-white flex items-center justify-center shadow-lg shadow-indigo-600/40 scale-90 group-hover:scale-100 transition-transform">
                <div className="w-0 h-0 border-y-[5px] border-y-transparent border-l-[8px] border-l-white ml-0.5" />
              </div>
            </div>
          </div>
        ) : (
          <>
        {/* ========================================================= */}
        {/* 1. NEWS PORTAL */}
        {/* ========================================================= */}
        {tId === "news_portal" && (
          <div className="absolute inset-0 bg-[#f7f8fa] flex flex-col justify-between p-2 text-black">
            {/* Top Red Broadcast Bar */}
            <div className="w-full bg-[#d71923] text-white px-2 py-1 rounded flex items-center justify-between text-[9px] font-black tracking-wider">
              <span>MIRI NEWS</span>
              <span className="flex items-center gap-1 bg-black/60 px-1.5 py-0.5 rounded-full text-[8px]">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping" />
                LIVE
              </span>
              <span>속보 특보</span>
            </div>

            {/* Headline with Red Marker */}
            <div className="space-y-0.5 my-1">
              <span className="text-[8px] bg-red-100 text-red-600 font-bold px-1 rounded">긴급 속보</span>
              <p className="text-[10px] font-black leading-tight text-slate-900">놓치면 후회할 핵심 정보</p>
              <p className="text-[10px] font-black bg-red-600 text-white px-1 inline-block rounded">지금 확인하세요!</p>
            </div>

            {/* Video Box */}
            <div className="relative aspect-video w-full bg-slate-900 rounded-lg flex items-center justify-center border border-slate-700 overflow-hidden shadow-md">
              <span className="absolute top-1 left-1 bg-red-600 text-white text-[7px] font-bold px-1 rounded">HOT 제보</span>
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Bottom News Briefing Card */}
            <div className="bg-white rounded-lg p-1.5 border border-slate-200 shadow-sm mt-1 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-[7px] bg-red-600 text-white px-1 py-0.5 rounded font-bold">MIRI NEWS 속보</span>
                <span className="text-[6px] text-slate-400">실시간 팩트체크</span>
              </div>
              <div className="space-y-0.5 text-[8px] text-slate-800 font-medium">
                <p className="truncate">• 놓치면 후회할 핵심 정보 요약</p>
                <p className="truncate">• 실시간 특종 리포트 브리핑</p>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 2. BROWSER WINDOW */}
        {/* ========================================================= */}
        {tId === "browser_window" && (
          <div className="absolute inset-0 bg-[#161a25] flex flex-col justify-between p-2 text-white">
            {/* Top Attention Tag */}
            <div className="text-center">
              <span className="bg-amber-400 text-black text-[8px] font-black px-2 py-0.5 rounded-full shadow">
                [TIP 01] 필독 꿀팁
              </span>
              <p className="text-[10px] font-black text-amber-300 drop-shadow mt-0.5">반드시 켜야 할 필수 설정</p>
            </div>

            {/* macOS Window Frame */}
            <div className="bg-[#f0f3fa] rounded-xl overflow-hidden shadow-lg border border-white/40 flex-1 my-1 flex flex-col">
              {/* Titlebar */}
              <div className="bg-[#e1e5ee] px-2 py-1 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#ff5f57]" />
                <span className="w-1.5 h-1.5 rounded-full bg-[#febc2e]" />
                <span className="w-1.5 h-1.5 rounded-full bg-[#28c940]" />
                <span className="ml-1 bg-white text-slate-600 text-[6px] px-2 py-0.5 rounded flex-1 truncate font-mono">
                  https://shorts.app/tips
                </span>
              </div>
              {/* Video inside window */}
              <div className="aspect-video bg-slate-900 flex items-center justify-center relative">
                <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
                </div>
              </div>
              {/* Window Content Tip Card */}
              <div className="p-1.5 flex-1 flex flex-col justify-between bg-white text-slate-800">
                <div className="space-y-0.5 text-[7px] font-medium text-slate-700">
                  <p className="truncate">💡 실전 핵심 요약 & 팁</p>
                  <p className="truncate">• 놓치면 손해보는 필수 설정</p>
                </div>
                <div className="flex gap-1 text-[6px] mt-1">
                  <span className="bg-slate-100 text-slate-600 px-1 py-0.5 rounded border border-slate-200">#핵심가이드</span>
                  <span className="bg-slate-100 text-slate-600 px-1 py-0.5 rounded border border-slate-200">#추천팁</span>
                </div>
              </div>
            </div>

            <p className="text-[8px] text-center text-slate-400">좋아요 & 저장 꾹 눌러주세요</p>
          </div>
        )}

        {/* ========================================================= */}
        {/* 3. MESSENGER CHAT (NEW) */}
        {/* ========================================================= */}
        {tId === "messenger_chat" && (
          <div className="absolute inset-0 bg-[#bacce0] flex flex-col justify-between p-2 text-slate-900">
            {/* Top Chat Bar */}
            <div className="bg-white/95 px-2 py-1 rounded-lg flex items-center gap-1.5 shadow-sm">
              <div className="w-4 h-4 rounded-full bg-[#fee500] flex items-center justify-center text-[8px] font-bold">
                💬
              </div>
              <div>
                <p className="text-[8px] font-bold leading-none">익명 제보자 단톡방</p>
                <p className="text-[6px] text-slate-500">참여 1.2만명</p>
              </div>
            </div>

            {/* Chat Bubbles */}
            <div className="space-y-1 my-1">
              <div className="bg-[#fee500] text-black text-[8px] font-bold px-2 py-1 rounded-2xl rounded-tl-sm w-fit shadow-sm">
                이 꿀팁 진짜 실화인가요?!
              </div>
              <div className="bg-white text-black text-[8px] font-medium px-2 py-1 rounded-2xl rounded-tl-sm w-fit shadow-sm">
                직접 써봤는데 대박입니다 👇
              </div>
            </div>

            {/* Video Frame */}
            <div className="aspect-video w-full bg-slate-900 rounded-xl overflow-hidden shadow-md flex items-center justify-center border-2 border-white">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Bottom Fake Input */}
            <div className="bg-white px-2 py-1 rounded-full flex items-center justify-between text-[7px] text-slate-400 mt-1 shadow-sm">
              <span>메시지를 입력하세요...</span>
              <span className="bg-[#fee500] text-black font-bold px-1.5 py-0.5 rounded-full text-[6px]">전송</span>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 4. RANKING CHART (NEW) */}
        {tId === "ranking_chart" && (
          <div className="absolute inset-0 bg-[#12101a] flex flex-col justify-between p-2 text-white">
            <div className="text-center space-y-0.5">
              <span className="bg-gradient-to-r from-amber-500 to-orange-500 text-black text-[8px] font-black px-2 py-0.5 rounded-full inline-flex items-center gap-0.5 shadow">
                <Trophy className="w-2.5 h-2.5" /> TOP RANKING #1
              </span>
              <p className="text-[10px] font-black text-orange-400 drop-shadow">전문가가 뽑은 역대급 1위!</p>
            </div>

            {/* Video with Flame Border */}
            <div className="aspect-video w-full bg-slate-950 rounded-xl overflow-hidden shadow-lg border-2 border-orange-500 flex items-center justify-center my-1 relative">
              <div className="absolute top-1 right-1 bg-orange-600 text-[6px] font-bold px-1 rounded text-white flex items-center gap-0.5">
                <Flame className="w-2 h-2 fill-current" /> BEST
              </div>
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Bottom Chart Specs */}
            <div className="bg-[#1f192b] border border-orange-500/40 rounded-xl p-1.5 text-[8px] space-y-0.5">
              <span className="bg-orange-500 text-black font-bold px-1 rounded text-[7px]">🥇 1위 선정 이유</span>
              <p className="text-slate-300 truncate">• 압도적인 성능과 효율</p>
              <p className="text-slate-400 truncate">• 실시간 추천 랭킹 지수 99점</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 5. PRODUCT REVIEW (NEW) */}
        {tId === "product_review" && (
          <div className="absolute inset-0 bg-[#f5f8fa] flex flex-col justify-between p-2 text-slate-900">
            <div className="text-center space-y-0.5">
              <span className="bg-emerald-400 text-black text-[8px] font-black px-2 py-0.5 rounded-full inline-flex items-center gap-0.5 shadow-sm">
                <Star className="w-2.5 h-2.5 fill-current" /> 평점 4.9 만점
              </span>
              <p className="text-[10px] font-black text-slate-900">내돈내산 솔직 리뷰 대공개</p>
            </div>

            {/* Video Frame */}
            <div className="aspect-video w-full bg-slate-900 rounded-xl overflow-hidden shadow-md flex items-center justify-center my-1 border border-slate-300">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Bottom Pros/Cons */}
            <div className="bg-white rounded-xl p-1.5 border border-slate-200 shadow-sm space-y-1">
              <span className="bg-emerald-500 text-white font-bold text-[7px] px-1 py-0.5 rounded">솔직 평가 요약</span>
              <div className="text-[8px] space-y-0.5 text-slate-700">
                <p className="text-emerald-600 font-semibold truncate">✔ 장점: 가성비 최고 수준</p>
                <p className="text-slate-500 truncate">💡 꿀팁: 구매 전 옵션 필수 확인</p>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 6. MOTIVATION QUOTE (NEW) */}
        {tId === "motivation_quote" && (
          <div className="absolute inset-0 bg-[#0c0c0f] flex flex-col justify-between p-2 text-white">
            <div className="text-center">
              <span className="text-amber-400 text-lg font-serif leading-none">“</span>
              <p className="text-[10px] font-serif text-amber-300 font-bold -mt-2">인생을 바꾸는 단 하나의 습관</p>
            </div>

            {/* Video with Gold Border */}
            <div className="aspect-video w-full bg-slate-950 rounded-xl overflow-hidden shadow-lg border border-amber-400/80 flex items-center justify-center my-1">
              <div className="w-7 h-7 rounded-full bg-amber-400/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-amber-300 ml-0.5" />
              </div>
            </div>

            {/* Bottom Insight Card */}
            <div className="bg-[#14141a] rounded-xl p-1.5 border border-amber-400/30 text-center space-y-0.5">
              <span className="text-[7px] text-amber-400 font-bold">오늘의 인생 인사이트</span>
              <p className="text-[8px] text-slate-300 font-serif italic">&quot;포기하지 않는 자에게 기회가 온다&quot;</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 7. QUIZ BALANCE (NEW) */}
        {tId === "quiz_balance" && (
          <div className="absolute inset-0 bg-[#161420] flex flex-col justify-between p-2 text-white">
            <div className="text-center space-y-0.5">
              <span className="bg-red-500 text-white text-[8px] font-black px-2 py-0.5 rounded-full shadow">
                🔥 당신의 선택은?
              </span>
              <p className="text-[10px] font-black text-amber-300">밸런스 게임 난제 종결!</p>
            </div>

            {/* Video Frame */}
            <div className="aspect-video w-full bg-slate-900 rounded-xl overflow-hidden shadow-md flex items-center justify-center my-1 border-2 border-red-500">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Split Options */}
            <div className="grid grid-cols-2 gap-1 text-[7px] font-bold text-center">
              <div className="bg-blue-600/90 p-1.5 rounded-lg border border-blue-400 shadow">
                <p>옵션 A</p>
                <p className="text-[6px] opacity-80">댓글로 A 투표</p>
              </div>
              <div className="bg-red-600/90 p-1.5 rounded-lg border border-red-400 shadow">
                <p>옵션 B</p>
                <p className="text-[6px] opacity-80">댓글로 B 투표</p>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 8. VLOG POLAROID (NEW) */}
        {tId === "vlog_polaroid" && (
          <div className="absolute inset-0 bg-[#f2eee6] flex flex-col justify-between p-2 text-slate-800">
            {/* Washi Tape */}
            <div className="w-12 h-2.5 bg-amber-200/80 mx-auto rounded-sm -mt-1 shadow-sm" />

            <div className="text-center">
              <span className="text-[8px] text-amber-800 font-mono tracking-wider">DAY LOG • VLOG</span>
              <p className="text-[10px] font-bold text-slate-900">오늘의 소소한 일상 기록</p>
            </div>

            {/* Polaroid Photo Frame */}
            <div className="bg-white p-1 rounded-xl shadow-md border border-stone-200 my-1">
              <div className="aspect-video w-full bg-slate-900 rounded-lg flex items-center justify-center overflow-hidden">
                <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
                </div>
              </div>
              <p className="text-[7px] text-stone-500 font-mono mt-1 text-right pr-1">MEMORIES #01</p>
            </div>

            <div className="bg-white/80 p-1.5 rounded-lg border border-stone-200 text-[8px] text-stone-700">
              <p className="truncate">• 힐링 가득 감성 브이로그</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 9. NEON MAGAZINE */}
        {tId === "neon_magazine" && (
          <div className="absolute inset-0 bg-[#0e1018] flex flex-col justify-between p-2 text-white">
            <div className="text-center space-y-0.5">
              <span className="bg-amber-400 text-black text-[8px] font-black px-2 py-0.5 rounded-full shadow">
                [KEY 01] 핵심 요약
              </span>
              <p className="text-[10px] font-black text-cyan-400 drop-shadow">차세대 인포 매거진</p>
            </div>

            {/* Glowing Video Frame */}
            <div className="aspect-video w-full bg-slate-950 rounded-xl overflow-hidden shadow-lg border-2 border-cyan-400 flex items-center justify-center my-1 relative">
              <div className="absolute top-1 right-1 bg-rose-500 text-[6px] font-bold px-1 rounded text-white">
                HOT 필수
              </div>
              <div className="w-7 h-7 rounded-full bg-cyan-400/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-cyan-300 ml-0.5" />
              </div>
            </div>

            <div className="bg-slate-900/90 rounded-xl p-1.5 border border-cyan-400/30 text-[8px] space-y-0.5">
              <span className="text-amber-400 font-bold">[요약] 핵심 가이드</span>
              <p className="text-slate-300 truncate">• 네온 비주얼 브리핑</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 10. MINIMAL EDU */}
        {tId === "minimal_edu" && (
          <div className="absolute inset-0 bg-[#141822] flex flex-col justify-between p-2 text-white">
            <div className="text-center space-y-0.5">
              <span className="bg-slate-800 text-slate-300 border border-slate-700 text-[8px] font-bold px-2 py-0.5 rounded-full">
                [지식] 1분 완성
              </span>
              <p className="text-[10px] font-bold text-slate-100">핵심만 빠르게 배우는 꿀팁</p>
            </div>

            {/* Clean Video */}
            <div className="aspect-video w-full bg-slate-900 rounded-xl overflow-hidden shadow-md flex items-center justify-center my-1 border border-slate-700">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            <div className="bg-slate-900 rounded-xl p-1.5 border border-slate-800 text-[8px] space-y-0.5">
              <span className="text-slate-400 font-semibold">[노트] 지식 정리</span>
              <p className="text-slate-300 truncate">• 프리텐다드 클린 자막</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 11. INTERVIEW TALK */}
        {tId === "interview_talk" && (
          <div className="absolute inset-0 bg-slate-950 flex flex-col justify-between p-2 text-white overflow-hidden">
            <div className="text-center">
              <span className="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-[8px] font-bold px-2 py-0.5 rounded-full backdrop-blur-sm">
                [TALK] 팟캐스트 인터뷰
              </span>
            </div>

            {/* 9:16 Portrait Avatar Simulation */}
            <div className="my-auto flex flex-col items-center justify-center">
              <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg border-2 border-white/20 mb-2">
                <span className="text-xl">🎙️</span>
              </div>
              <div className="bg-black/70 backdrop-blur-md px-2 py-1 rounded-lg border border-white/10 text-center">
                <p className="text-[10px] font-black text-amber-300">호르모지 키네틱 자막</p>
                <p className="text-[8px] text-white">9:16 인물 풀스크린</p>
              </div>
            </div>

            <p className="text-[7px] text-center text-slate-500">얼굴 추적 스마트 크롭</p>
          </div>
        )}

        {/* ========================================================= */}
        {/* 12. SOURCE PURE */}
        {tId === "source_pure" && (
          <div className="absolute inset-0 bg-black flex flex-col justify-between p-2 text-white">
            <div className="text-center">
              <span className="bg-slate-800 text-slate-300 text-[8px] font-bold px-2 py-0.5 rounded-full border border-slate-700">
                [순정] 원본 보존
              </span>
            </div>

            <div className="aspect-video w-full bg-slate-900 rounded-lg flex items-center justify-center border border-slate-800 my-auto">
              <div className="text-center">
                <Film className="w-6 h-6 text-slate-500 mx-auto mb-1" />
                <p className="text-[8px] text-slate-400">자체 자막 및 원본 100% 유지</p>
              </div>
            </div>

            <p className="text-[7px] text-center text-slate-500">추가 자막 없이 깔끔 렌더링</p>
          </div>
        )}

        {/* ========================================================= */}
        {/* 13. FACETIME CALL */}
        {tId === "facetime_call" && (
          <div className="absolute inset-0 bg-[#0f1218] flex flex-col justify-between p-2 text-white">
            <div className="flex items-center justify-between text-[7px] text-slate-300">
              <span>9:41</span>
              <span className="bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded-full border border-emerald-500/40 text-[6px]">
                통화 중 02:45
              </span>
              <span>5G 85%</span>
            </div>

            <div className="flex-1 bg-slate-900 rounded-xl overflow-hidden my-1 flex items-center justify-center relative border border-white/10">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Bottom Call Buttons */}
            <div className="flex items-center justify-center gap-3 py-0.5">
              <div className="w-5 h-5 rounded-full bg-slate-700/80 flex items-center justify-center text-[8px]">🔇</div>
              <div className="w-6 h-6 rounded-full bg-red-600 flex items-center justify-center text-[9px] shadow-md shadow-red-600/40">📞</div>
              <div className="w-5 h-5 rounded-full bg-slate-700/80 flex items-center justify-center text-[8px]">📷</div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 14. INSTAGRAM REELS */}
        {tId === "instagram_reels" && (
          <div className="absolute inset-0 bg-slate-950 flex flex-col justify-between p-2 text-white">
            <div className="flex items-center justify-between text-[8px] font-bold">
              <span>Reels ▾</span>
              <span>📷</span>
            </div>

            <div className="flex-1 bg-slate-900 rounded-lg overflow-hidden my-1 relative flex items-center justify-center border border-white/10">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>

              {/* Right Action Icons */}
              <div className="absolute right-1 bottom-3 flex flex-col items-center gap-1.5 text-[7px]">
                <div className="flex flex-col items-center"><span>❤️</span><span className="text-[5px]">2.5만</span></div>
                <div className="flex flex-col items-center"><span>💬</span><span className="text-[5px]">1,420</span></div>
                <div className="flex flex-col items-center"><span>✈️</span><span className="text-[5px]">공유</span></div>
              </div>
            </div>

            <div className="space-y-0.5">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <span className="text-[7px] font-bold">@shorts_studio</span>
                <span className="text-[5px] border border-white/40 px-1 rounded">팔로우</span>
              </div>
              <p className="text-[6px] text-slate-400 truncate">🎵 원본 오디오 • 인기 릴스 트렌드</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 15. IPHONE GALLERY MEME */}
        {tId === "iphone_gallery" && (
          <div className="absolute inset-0 bg-[#f5f5f7] flex flex-col justify-between p-2 text-slate-900">
            <div className="flex items-center justify-between text-[7px] text-blue-600 font-semibold border-b pb-0.5">
              <span>‹ 앨범</span>
              <span className="text-black font-bold">전체 사진</span>
              <span>선택</span>
            </div>

            <div className="aspect-square bg-slate-900 rounded-lg overflow-hidden my-1 flex items-center justify-center relative shadow-sm border border-slate-200">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* iOS Delete Warning Dialog */}
            <div className="bg-white rounded-lg p-1.5 shadow-md border border-slate-200 text-center space-y-0.5">
              <p className="text-[6px] text-slate-600 font-medium">이 사진이 모든 기기에서 삭제됩니다.</p>
              <div className="border-t pt-0.5">
                <span className="text-[7px] text-red-600 font-bold">사진 삭제</span>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 16. MEME CARTOON */}
        {tId === "meme_cartoon" && (
          <div className="absolute inset-0 bg-[#fbf9f4] flex flex-col justify-between p-2 text-slate-900">
            {/* Comic Speech Bubble */}
            <div className="bg-[#ffe74c] rounded-xl p-1.5 border-2 border-black shadow-[2px_2px_0px_rgba(0,0,0,1)] text-center">
              <p className="text-[8px] font-black leading-tight">"귀하게 자란 내가 이걸 봐도 될까?!"</p>
            </div>

            <div className="aspect-video bg-slate-950 rounded-lg overflow-hidden my-1 flex items-center justify-center border-2 border-black shadow-[2px_2px_0px_rgba(0,0,0,1)]">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            <div className="bg-white rounded-lg p-1 border-2 border-black shadow-[2px_2px_0px_rgba(0,0,0,1)] text-[7px] text-slate-800 font-bold truncate">
              💬 실시간 베댓 1위: "이거 100% 실화 ㅋㅋㅋ"
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 17. CINEMA PREVIEW */}
        {tId === "cinema_preview" && (
          <div className="absolute inset-0 bg-[#0e0f14] flex flex-col justify-between p-2 text-white">
            <div className="border border-amber-300/40 rounded px-1.5 py-0.5 flex items-center justify-between text-[6px] text-amber-200 font-mono">
              <span>CINEMA TICKET #0824</span>
              <span>★ ★ ★ ★ ★ 9.8</span>
            </div>

            <div className="text-center my-0.5">
              <p className="text-[9px] font-black text-amber-300">《 금주 개봉작 프리뷰 》</p>
            </div>

            <div className="aspect-video bg-slate-900 rounded overflow-hidden flex items-center justify-center border border-amber-300/30">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            <div className="bg-slate-900/90 rounded p-1 border border-white/10 text-[7px] space-y-0.5">
              <p className="text-amber-200 font-bold">[화제작 프리뷰]</p>
              <p className="text-slate-300 truncate">• 놓치면 후회할 시네마틱 명장면</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 18. PIE CHART REACTION */}
        {tId === "pie_chart_reaction" && (
          <div className="absolute inset-0 bg-[#12141e] flex flex-col justify-between p-2 text-white">
            <div className="text-center">
              <span className="bg-red-600 text-white text-[7px] font-black px-1.5 py-0.5 rounded-full shadow">
                🔥 현실 팬 반응 통계
              </span>
              <p className="text-[9px] font-black text-amber-300 mt-0.5">분노와 답답함 99%</p>
            </div>

            <div className="aspect-video bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center border-2 border-red-500/80 my-1">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            <div className="bg-slate-900 rounded-lg p-1.5 border border-slate-800 text-[6px] space-y-1">
              <div className="grid grid-cols-2 gap-1 font-bold">
                <span className="bg-red-600/30 text-red-300 px-1 py-0.5 rounded">답답함 45%</span>
                <span className="bg-orange-600/30 text-orange-300 px-1 py-0.5 rounded">분노 35%</span>
                <span className="bg-amber-600/30 text-amber-300 px-1 py-0.5 rounded">화병 19%</span>
                <span className="bg-emerald-600/30 text-emerald-300 px-1 py-0.5 rounded">이성 1%</span>
              </div>
              <p className="text-slate-400 truncate">"100% 실화... 내 모습인 줄 알았다"</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 19. CHALLENGE FITNESS */}
        {tId === "challenge_fitness" && (
          <div className="absolute inset-0 bg-[#120e14] flex flex-col justify-between p-2 text-white">
            <div className="text-center">
              <span className="bg-red-600 text-white text-[7px] font-black px-1.5 py-0.5 rounded-full shadow">
                🔥 [D-DAY] 오운완 챌린지
              </span>
              <p className="text-[9px] font-black text-red-400 mt-0.5">오늘의 1분 루틴 완성</p>
            </div>

            <div className="aspect-video bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center border-2 border-red-600 my-1">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            <div className="bg-slate-900 rounded-lg p-1.5 border border-red-950 text-[7px] space-y-0.5">
              <p className="text-red-400 font-bold">✔ 오늘의 루틴 미션 체크</p>
              <p className="text-slate-300 truncate">• 매일 꾸준히 반복하는 필수 동작</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 20. VLOG STICKER LIFESTYLE (감성 습관 & 3D 스티커) */}
        {/* ========================================================= */}
        {tId === "vlog_sticker_lifestyle" && (
          <div className="absolute inset-0 bg-gradient-to-b from-stone-900/80 via-stone-800/40 to-stone-900/90 flex flex-col justify-between p-2 text-white">
            {/* Top Wave Tag */}
            <div className="text-center pt-1">
              <span className="bg-[#e8ff82] text-stone-900 text-[7px] font-black px-2 py-0.5 rounded-full shadow border border-white/60">
                〰️ SELF TALK 〰️
              </span>
              <p className="text-[8px] font-bold text-white mt-1 drop-shadow">★ 나를 바꾼 ★</p>
              <p className="text-[11px] font-black text-[#e8ff82] leading-tight drop-shadow">습관 3가지</p>
            </div>

            {/* Cute 3D Stickers Floating */}
            <div className="relative flex-1 my-1 flex items-center justify-center">
              {/* Coffee Cup Sticker Left */}
              <div className="absolute left-1 top-2 bg-white text-[12px] p-1 rounded-full shadow-lg border border-stone-200">
                ☕
              </div>
              {/* Yoga Speech Bubble Right */}
              <div className="absolute right-1 top-4 bg-white text-[12px] p-1.5 rounded-2xl shadow-lg border border-pink-100 flex items-center gap-0.5">
                🧘‍♀️
              </div>
              {/* Center Play Button */}
              <div className="w-8 h-8 rounded-full bg-white/25 backdrop-blur-md flex items-center justify-center border border-white/40 shadow-xl">
                <div className="w-0 h-0 border-y-[5px] border-y-transparent border-l-[8px] border-l-white ml-0.5" />
              </div>
              {/* Plant Sticker */}
              <div className="absolute right-3 bottom-1 bg-white/90 text-[10px] p-1 rounded-full shadow">
                🌱
              </div>
            </div>

            {/* Subtitle Bar */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg px-2 py-1 text-center">
              <p className="text-[7px] font-medium text-stone-200 truncate">
                "작은 습관 하나가 하루를 완전히 바꿔요"
              </p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 21. VLOG MONEY SALARY (프리랜서 평균 수입 & 테이프 스티커) */}
        {/* ========================================================= */}
        {tId === "vlog_money_salary" && (
          <div className="absolute inset-0 bg-gradient-to-b from-slate-900/80 via-slate-800/40 to-slate-950/90 flex flex-col justify-between p-2 text-white">
            {/* Top Pink Capsule */}
            <div className="text-center pt-1">
              <span className="bg-pink-100 text-pink-700 text-[7px] font-black px-2 py-0.5 rounded-full border border-pink-300">
                &#123; FREELANCER VLOG &#125;
              </span>
              <p className="text-[10px] font-black text-white mt-1 drop-shadow tracking-tight">프리랜서 평균 수입</p>
            </div>

            {/* Diagonal Washi Tapes & Flying Money */}
            <div className="relative flex-1 my-1 flex flex-col items-center justify-center gap-1.5">
              <div className="absolute right-1 top-0 text-[12px] animate-bounce">💸</div>
              <div className="absolute left-1 bottom-1 text-[12px]">💸</div>

              {/* Mint Tape */}
              <div className="-rotate-3 bg-[#b4f5e6] text-[#0f5046] text-[8px] font-black px-2 py-0.5 rounded shadow border border-[#82dcc8]">
                진짜 월 1000만원?
              </div>
              {/* Center Play Button */}
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/30 my-0.5 shadow">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
              {/* Yellow Tape */}
              <div className="rotate-2 bg-[#fff5b4] text-[#5f4b0a] text-[8px] font-black px-2 py-0.5 rounded shadow border border-[#ebd782]">
                꾸준히 일 받는 법
              </div>
            </div>

            {/* Bottom Watermark */}
            <div className="text-center pb-0.5">
              <p className="text-[6px] text-slate-300">@designer.miri • 실시간 VLOG</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 22. PROMO FITNESS GYM (미리짐 오운완 챌린지 & 이벤트 CTA) */}
        {/* ========================================================= */}
        {tId === "promo_fitness_gym" && (
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent flex flex-col justify-between p-2 text-white">
            {/* Top MIRIGYM Bar */}
            <div className="flex items-center justify-between pt-0.5">
              <span className="text-[#eb192d] font-black text-[10px] tracking-wider">MIRIGYM</span>
              <div className="flex items-center gap-1 text-[8px] text-white/80">
                <span className="w-3.5 h-3.5 rounded-full border border-white/60 flex items-center justify-center">+</span>
                <span className="w-3.5 h-3.5 rounded-full border border-white/60 flex items-center justify-center text-[7px]">♡</span>
              </div>
            </div>

            {/* Center Play Button */}
            <div className="flex items-center justify-center my-auto">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/40 shadow">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Lower Middle Huge Headline & Red CTA Button */}
            <div className="space-y-1">
              <div className="leading-tight">
                <p className="text-[9px] font-black text-white">미리짐</p>
                <p className="text-[12px] font-black text-white leading-tight">오운완 챌린지</p>
                <p className="text-[11px] font-black text-white">이벤트</p>
              </div>

              {/* Red CTA Button */}
              <div className="flex items-center gap-1 bg-[#eb192d] px-2 py-1 rounded text-white text-[7px] font-bold w-fit shadow">
                <span>▶ 참여방법</span>
                <span className="text-[6px] opacity-80 font-normal">한 달간 특별 혜택</span>
              </div>

              <p className="text-[6px] text-amber-300 font-bold">#오운완 태그하고 쉐이크 1잔 바로 증정!</p>

              {/* Bottom Progress Bar */}
              <div className="w-full bg-slate-700 h-1 rounded-full overflow-hidden mt-1">
                <div className="bg-[#eb192d] h-full w-2/5" />
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 23. YOUTH TIPS PICK (모르면 손해보는 청년혜택 총정리) */}
        {/* ========================================================= */}
        {tId === "youth_tips_pick" && (
          <div className="absolute inset-0 bg-gradient-to-b from-stone-900/80 via-transparent to-stone-950/80 flex flex-col justify-between p-2 text-white">
            {/* Top Headline Deck */}
            <div className="space-y-0.5 pt-1">
              <p className="text-[7px] text-white/90 font-medium italic drop-shadow">놓치면 진짜 아까워요!</p>
              <p className="text-[9px] font-black text-white drop-shadow">모르면 손해보는</p>
              <div className="flex items-center gap-1">
                <span className="bg-[#ebff1e] text-slate-900 font-black text-[10px] px-1 py-0.2 rounded shadow">
                  청년혜택
                </span>
                <span className="text-[10px] font-black text-white drop-shadow">총정리</span>
              </div>
            </div>

            {/* Center Play Button */}
            <div className="flex items-center justify-center my-auto">
              <div className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border border-white/30 shadow">
                <div className="w-0 h-0 border-y-[5px] border-y-transparent border-l-[8px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Bottom Floating PICK! Sticker */}
            <div className="flex items-end justify-between pb-1">
              <div className="flex flex-col items-center">
                <div className="bg-[#ebff1e] text-slate-900 font-black text-[9px] px-2 py-0.5 rounded-full shadow-md">
                  PICK
                </div>
                <span className="text-[6px] text-white drop-shadow font-bold mt-0.5">저장하고 써보세요!</span>
              </div>
              <span className="text-[5px] text-white/70">* 2026 정부지원 기준</span>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 24. DRAMA WEEKLY PREVIEW (이번 주 가장 많이 본 명장면 다시보기) */}
        {/* ========================================================= */}
        {tId === "drama_weekly_preview" && (
          <div className="absolute inset-0 bg-[#0d0d12] flex flex-col justify-between p-2 text-white">
            {/* Top Red Pill */}
            <div className="text-center pt-1">
              <span className="bg-[#e11928] text-white text-[7px] font-black px-2 py-0.5 rounded-full shadow">
                ▶ 이번 주 짧은 드라마
              </span>
              <p className="text-[9px] font-black text-white mt-1 drop-shadow">'가장 많이 본 장면'</p>
              <p className="text-[10px] font-black text-white drop-shadow">다시 보기!</p>
            </div>

            {/* Center Grid Look with Play Button */}
            <div className="aspect-video bg-red-950/40 rounded-lg overflow-hidden flex items-center justify-center border border-red-700/60 my-1 shadow">
              <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-white ml-0.5" />
              </div>
            </div>

            {/* Bottom Red Card */}
            <div className="bg-[#e11928] rounded-lg p-1.5 text-white shadow-md space-y-0.5">
              <div className="flex items-center justify-between">
                <span className="text-[8px] font-black tracking-wide">WEEKLY PREVIEW</span>
                <span className="text-[6px] bg-black/40 px-1 py-0.2 rounded">TODAY PICK! ✔</span>
              </div>
              <p className="text-[6px] opacity-90 truncate">풀버전은 고정 댓글 확인하실 수 있습니다.</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* 25. TESLA FSD VISION (테슬라 FSD 자율주행 HUD 대시보드) */}
        {/* ========================================================= */}
        {tId === "tesla_fsd_vision" && (
          <div className="absolute inset-0 bg-[#0b0e14] flex flex-col justify-between p-2 text-white font-mono">
            {/* Top Tesla HUD Status Bar */}
            <div className="bg-slate-900/90 rounded-lg p-1 border border-slate-700/80 space-y-0.5">
              <div className="flex items-center justify-between text-[7px]">
                <div className="flex items-center gap-1">
                  <span className="text-[#eb192d] font-black">T</span>
                  <span className="font-bold tracking-wider text-slate-200">TESLA</span>
                </div>
                <div className="text-emerald-400 font-bold text-[6px] bg-emerald-950/80 px-1 py-0.2 rounded border border-emerald-500/40">
                  🟢 FSD ACTIVE
                </div>
                <div className="text-right">
                  <span className="font-bold text-white text-[8px]">105</span>
                  <span className="text-[5px] text-slate-400"> km/h</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-[6px] text-slate-400">
                <span>P R N <strong className="text-white">D*</strong></span>
                <span className="text-emerald-300">88% ⚡ 432km</span>
              </div>
            </div>

            {/* Center Autopilot Vision Area with Play Button */}
            <div className="relative flex-1 my-1 flex items-center justify-center">
              {/* Cyan Guidance Lines */}
              <div className="absolute inset-0 flex items-center justify-center opacity-40 pointer-events-none">
                <div className="w-16 h-20 border-x-2 border-cyan-400 transform -skew-x-12" />
              </div>
              <div className="w-7 h-7 rounded-full bg-slate-900/80 backdrop-blur-md flex items-center justify-center border border-cyan-400/60 shadow-lg shadow-cyan-500/20 z-10">
                <div className="w-0 h-0 border-y-[4px] border-y-transparent border-l-[7px] border-l-cyan-300 ml-0.5" />
              </div>
              <span className="absolute bottom-0 text-[6px] text-cyan-300/80 tracking-widest font-sans">
                ▲ FSD 차선 감지 중
              </span>
            </div>

            {/* Bottom Tesla Control Dock */}
            <div className="bg-slate-900/95 rounded-lg px-2 py-1 border border-slate-800 text-[6px] flex items-center justify-between text-slate-300">
              <span>21.5°C 💨</span>
              <span className="text-slate-100 font-bold truncate max-w-[80px]">🎵 Spotify: Media</span>
              <span className="text-emerald-400 font-bold">AUTO</span>
            </div>
          </div>
        )}
          </>
        )}
      </div>

      {/* Card Footer Info */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800/90 text-slate-300 border border-slate-700/80">
            {template.category}
          </span>
          <span className="text-[10px] font-mono text-slate-500">
            {template.badge_prefix}
          </span>
        </div>

        <h3 className="font-bold text-xs text-white leading-snug line-clamp-1 group-hover:text-indigo-300 transition">
          {template.name}
        </h3>
        <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
          {template.description}
        </p>
      </div>
    </div>
  );
}
