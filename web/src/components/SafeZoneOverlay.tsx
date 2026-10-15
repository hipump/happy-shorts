"use client";

import React from "react";
import {
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Share2,
  Repeat,
  Heart,
  Send,
  MoreVertical,
  Bookmark,
  Search,
  Camera,
  Music2,
  Disc,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

export type SafeZonePlatform = "none" | "youtube" | "reels" | "tiktok";

interface SafeZoneOverlayProps {
  platform: SafeZonePlatform;
  className?: string;
}

export default function SafeZoneOverlay({
  platform,
  className = "",
}: SafeZoneOverlayProps) {
  if (platform === "none") return null;

  return (
    <div
      className={`absolute inset-0 pointer-events-none z-30 select-none flex flex-col justify-between overflow-hidden font-sans ${className}`}
    >
      {/* 1. YOUTUBE SHORTS OVERLAY */}
      {platform === "youtube" && (
        <>
          {/* Top Header Bar */}
          <div className="w-full pt-3 px-3 flex items-center justify-between text-white/80 bg-gradient-to-b from-black/60 via-black/20 to-transparent pb-6">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-black tracking-tight text-white flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
                Shorts
              </span>
            </div>
            <div className="flex items-center gap-3 text-white/90">
              <Search className="w-4 h-4 drop-shadow" />
              <Camera className="w-4 h-4 drop-shadow" />
              <MoreVertical className="w-4 h-4 drop-shadow" />
            </div>
          </div>

          {/* Central Safe Zone Guide Lines */}
          <div className="flex-1 mx-3 my-1 border-2 border-dashed border-cyan-400/70 rounded-2xl relative flex flex-col items-center justify-between p-2">
            <div className="bg-cyan-500/90 text-slate-950 font-black text-[9px] px-2 py-0.5 rounded-full shadow-lg flex items-center gap-1 tracking-wide">
              <ShieldCheck className="w-3 h-3 stroke-[3]" />
              유튜브 쇼츠 세이프존 (자막/얼굴 안전 영역)
            </div>

            <div className="text-[9px] text-cyan-300/80 font-mono text-center bg-black/40 px-2 py-0.5 rounded backdrop-blur-sm">
              우측 버튼 레일 & 하단 자막 영역 여백 확보
            </div>
          </div>

          {/* Right Action Rail & Bottom Metadata */}
          <div className="w-full pb-3 px-3 bg-gradient-to-t from-black/80 via-black/40 to-transparent pt-6 relative flex items-end justify-between">
            {/* Bottom Channel & Title Info */}
            <div className="flex-1 pr-12 text-left space-y-1.5">
              <div className="flex items-center gap-1.5">
                <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-amber-500 to-rose-500 flex items-center justify-center text-[10px] font-bold text-white shadow">
                  H
                </div>
                <span className="text-xs font-bold text-white drop-shadow">@happyshorts</span>
                <span className="text-[10px] font-bold bg-white text-black px-2 py-0.5 rounded-full shadow">
                  구독
                </span>
              </div>
              <p className="text-[11px] text-white/95 line-clamp-2 leading-tight drop-shadow font-medium">
                알고리즘이 선택한 실전 핵심 하이라이트 #Shorts #꿀팁
              </p>
              <div className="flex items-center gap-1.5 text-[10px] text-white/80 font-mono">
                <Music2 className="w-3 h-3 animate-spin text-white" />
                <span className="truncate max-w-[150px]">오리지널 사운드 &bull; Happy Shorts Master BGM</span>
              </div>
            </div>

            {/* Right Vertical Button Rail */}
            <div className="flex flex-col items-center gap-3 text-white">
              <div className="flex flex-col items-center gap-0.5">
                <div className="w-8 h-8 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center border border-white/20">
                  <ThumbsUp className="w-4 h-4 fill-white text-white drop-shadow" />
                </div>
                <span className="text-[9px] font-bold drop-shadow">12.4만</span>
              </div>

              <div className="flex flex-col items-center gap-0.5">
                <div className="w-8 h-8 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center border border-white/20">
                  <ThumbsDown className="w-4 h-4 text-white drop-shadow" />
                </div>
                <span className="text-[9px] font-bold drop-shadow">싫어요</span>
              </div>

              <div className="flex flex-col items-center gap-0.5">
                <div className="w-8 h-8 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center border border-white/20">
                  <MessageCircle className="w-4 h-4 fill-white text-white drop-shadow" />
                </div>
                <span className="text-[9px] font-bold drop-shadow">1,240</span>
              </div>

              <div className="flex flex-col items-center gap-0.5">
                <div className="w-8 h-8 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center border border-white/20">
                  <Share2 className="w-4 h-4 text-white drop-shadow" />
                </div>
                <span className="text-[9px] font-bold drop-shadow">공유</span>
              </div>

              <div className="flex flex-col items-center gap-0.5">
                <div className="w-8 h-8 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center border border-white/20">
                  <Repeat className="w-4 h-4 text-white drop-shadow" />
                </div>
                <span className="text-[9px] font-bold drop-shadow">리믹스</span>
              </div>

              <div className="w-7 h-7 rounded-lg bg-slate-900 border border-white/30 p-0.5 shadow">
                <div className="w-full h-full rounded bg-gradient-to-tr from-amber-400 to-indigo-500 animate-spin" />
              </div>
            </div>
          </div>
        </>
      )}

      {/* 2. INSTAGRAM REELS OVERLAY */}
      {platform === "reels" && (
        <>
          {/* Top Header */}
          <div className="w-full pt-3 px-3 flex items-center justify-between text-white bg-gradient-to-b from-black/60 to-transparent pb-6">
            <span className="text-xs font-bold tracking-tight text-white flex items-center gap-1">
              릴스 (Reels)
            </span>
            <Camera className="w-4 h-4 drop-shadow" />
          </div>

          {/* Central Safe Zone Guide */}
          <div className="flex-1 mx-3 my-1 border-2 border-dashed border-pink-400/70 rounded-2xl relative flex flex-col items-center justify-between p-2">
            <div className="bg-pink-500/90 text-white font-black text-[9px] px-2 py-0.5 rounded-full shadow-lg flex items-center gap-1 tracking-wide">
              <ShieldCheck className="w-3 h-3 stroke-[3]" />
              인스타그램 릴스 세이프존
            </div>
            <div className="text-[9px] text-pink-200/80 font-mono text-center bg-black/40 px-2 py-0.5 rounded backdrop-blur-sm">
              인스타 우측 아이콘 및 하단 캡션 안전 영역
            </div>
          </div>

          {/* Bottom & Right */}
          <div className="w-full pb-3 px-3 bg-gradient-to-t from-black/80 to-transparent pt-6 flex items-end justify-between">
            <div className="flex-1 pr-12 text-left space-y-1.5">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-yellow-400 via-pink-500 to-purple-600 p-0.5">
                  <div className="w-full h-full bg-black rounded-full" />
                </div>
                <span className="text-xs font-bold text-white drop-shadow">happy_shorts</span>
                <span className="text-[10px] font-bold border border-white/70 text-white px-2 py-0.5 rounded-md">
                  팔로우
                </span>
              </div>
              <p className="text-[11px] text-white line-clamp-2 drop-shadow font-normal">
                반드시 알아야 할 오늘자 실전 인사이트! 🔥 더보기
              </p>
              <div className="flex items-center gap-1 text-[10px] text-white/80">
                <Music2 className="w-3 h-3" />
                <span>happy_shorts &bull; 오리지널 오디오</span>
              </div>
            </div>

            <div className="flex flex-col items-center gap-3.5 text-white">
              <div className="flex flex-col items-center gap-0.5">
                <Heart className="w-5 h-5 fill-red-500 text-red-500 drop-shadow" />
                <span className="text-[9px] font-bold drop-shadow">8.9만</span>
              </div>
              <div className="flex flex-col items-center gap-0.5">
                <MessageCircle className="w-5 h-5 text-white drop-shadow" />
                <span className="text-[9px] font-bold drop-shadow">642</span>
              </div>
              <div className="flex flex-col items-center gap-0.5">
                <Send className="w-5 h-5 text-white drop-shadow" />
                <span className="text-[9px] font-bold drop-shadow">공유</span>
              </div>
              <MoreVertical className="w-5 h-5 text-white drop-shadow" />
              <div className="w-6 h-6 rounded border border-white/40 overflow-hidden">
                <div className="w-full h-full bg-slate-700" />
              </div>
            </div>
          </div>
        </>
      )}

      {/* 3. TIKTOK OVERLAY */}
      {platform === "tiktok" && (
        <>
          {/* Top Header */}
          <div className="w-full pt-3 px-3 flex items-center justify-between text-white/80 bg-gradient-to-b from-black/60 to-transparent pb-6">
            <span className="text-xs text-white/60">LIVE</span>
            <div className="flex items-center gap-3 text-xs font-bold text-white">
              <span className="text-white/60">팔로잉</span>
              <span className="text-white border-b-2 border-white pb-0.5">추천</span>
            </div>
            <Search className="w-4 h-4 text-white" />
          </div>

          {/* Central Safe Zone Guide */}
          <div className="flex-1 mx-3 my-1 border-2 border-dashed border-emerald-400/70 rounded-2xl relative flex flex-col items-center justify-between p-2">
            <div className="bg-emerald-500/90 text-slate-950 font-black text-[9px] px-2 py-0.5 rounded-full shadow-lg flex items-center gap-1 tracking-wide">
              <ShieldCheck className="w-3 h-3 stroke-[3]" />
              틱톡 (TikTok) 세이프존
            </div>
            <div className="text-[9px] text-emerald-200/80 font-mono text-center bg-black/40 px-2 py-0.5 rounded backdrop-blur-sm">
              틱톡 프로필/반응 버튼 및 하단 음원 바 안전 영역
            </div>
          </div>

          {/* Bottom & Right */}
          <div className="w-full pb-3 px-3 bg-gradient-to-t from-black/80 to-transparent pt-6 flex items-end justify-between">
            <div className="flex-1 pr-12 text-left space-y-1.5">
              <div className="flex items-center gap-1">
                <span className="text-xs font-bold text-white drop-shadow">@happyshorts</span>
              </div>
              <p className="text-[11px] text-white line-clamp-2 drop-shadow font-normal">
                이거 보고 진짜 소름 돋았음... #fyp #viral #추천
              </p>
              <div className="flex items-center gap-1 text-[10px] text-white/90 font-mono">
                <Music2 className="w-3 h-3 animate-spin" />
                <span className="truncate max-w-[140px]">오리지널 사운드 - Happy Shorts</span>
              </div>
            </div>

            <div className="flex flex-col items-center gap-3 text-white">
              <div className="relative mb-1">
                <div className="w-8 h-8 rounded-full bg-slate-800 border-2 border-white flex items-center justify-center font-bold text-xs text-white">
                  H
                </div>
                <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full bg-rose-500 text-white flex items-center justify-center text-[10px] font-bold">
                  +
                </div>
              </div>

              <div className="flex flex-col items-center gap-0.5">
                <Heart className="w-5 h-5 fill-rose-500 text-rose-500 drop-shadow" />
                <span className="text-[9px] font-bold drop-shadow">45.8만</span>
              </div>
              <div className="flex flex-col items-center gap-0.5">
                <MessageCircle className="w-5 h-5 fill-white text-white drop-shadow" />
                <span className="text-[9px] font-bold drop-shadow">3,200</span>
              </div>
              <div className="flex flex-col items-center gap-0.5">
                <Bookmark className="w-5 h-5 fill-amber-400 text-amber-400 drop-shadow" />
                <span className="text-[9px] font-bold drop-shadow">1.2만</span>
              </div>
              <div className="flex flex-col items-center gap-0.5">
                <Share2 className="w-5 h-5 fill-white text-white drop-shadow" />
                <span className="text-[9px] font-bold drop-shadow">9,410</span>
              </div>
              <div className="w-7 h-7 rounded-full bg-slate-950 border-2 border-slate-700 flex items-center justify-center animate-spin">
                <Disc className="w-4 h-4 text-slate-300" />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
