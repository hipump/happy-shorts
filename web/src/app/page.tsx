"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  Play,
  Pause,
  Video,
  Flame,
  Scissors,
  Copy,
  Check,
  FolderOpen,
  RefreshCw,
  Sliders,
  Layers,
  Film,
  ExternalLink,
  ChevronRight,
  ArrowLeft,
  FileText,
  Clock,
  Laptop,
  Radio,
  Download,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  Zap,
} from "lucide-react";
import {
  Template,
  Highlight,
  VideoMetadata,
  RecentVideo,
  RenderedOutput,
  SystemStatus,
} from "@/types";
import TemplateMockupCard from "@/components/TemplateMockupCard";

export default function HappyShortsApp() {
  const [activeTab, setActiveTab] = useState<"studio" | "gallery">("studio");
  const [currentStep, setCurrentStep] = useState<number>(1);

  // System & Data
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [recentVideos, setRecentVideos] = useState<RecentVideo[]>([]);
  const [outputs, setOutputs] = useState<RenderedOutput[]>([]);

  // Step 1: Source
  const [sourceMode, setSourceMode] = useState<"youtube" | "local" | "recent">("youtube");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [localPath, setLocalPath] = useState("");
  const [selectedRecent, setSelectedRecent] = useState<RecentVideo | null>(null);
  const [clipsCount, setClipsCount] = useState<number>(3);
  const [minDur, setMinDur] = useState<number>(30);
  const [maxDur, setMaxDur] = useState<number>(50);

  // Step 2: Template & Options
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("browser_window");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [subtitleStyle, setSubtitleStyle] = useState<string>("viral_pop");
  const [showBadge, setShowBadge] = useState<boolean>(true);
  const [aspectRatio, setAspectRatio] = useState<"9:16" | "16:9">("9:16");
  const [removeSubtitles, setRemoveSubtitles] = useState<boolean>(false);
  const [filterFillers, setFilterFillers] = useState<boolean>(true);

  // Step 3: Analysis
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeProgress, setAnalyzeProgress] = useState(0);
  const [analyzeMessage, setAnalyzeMessage] = useState("");
  const [videoMeta, setVideoMeta] = useState<VideoMetadata | null>(null);
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [selectedHighlight, setSelectedHighlight] = useState<Highlight | null>(null);

  // Step 4: Rendering
  const [isRendering, setIsRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState(0);
  const [renderMessage, setRenderMessage] = useState("");
  const [renderedResult, setRenderedResult] = useState<RenderedOutput | null>(null);

  // Interactive Video Player & Trimming
  const [previewTimeRange, setPreviewTimeRange] = useState<{ start: number; end: number }>({ start: 0, end: 0 });
  const previewVideoRef = useRef<HTMLVideoElement | null>(null);
  const [isPreviewPlaying, setIsPreviewPlaying] = useState(false);

  // UI state
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Initial Data Fetching
  const fetchStatusAndData = React.useCallback(async () => {
    try {
      const [resStatus, resTpl, resRecent, resOutputs] = await Promise.all([
        fetch("/api/status").then((r) => r.json()),
        fetch("/api/templates").then((r) => r.json()),
        fetch("/api/recent-videos").then((r) => r.json()),
        fetch("/api/outputs").then((r) => r.json()),
      ]);
      setSystemStatus(resStatus);
      setTemplates(resTpl.templates || []);
      setRecentVideos(resRecent.videos || []);
      setOutputs(resOutputs.outputs || []);
    } catch (err) {
      console.error("데이터 로딩 실패:", err);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchStatusAndData();
    }, 0);
    const interval = setInterval(fetchStatusAndData, 8000);
    return () => {
      clearTimeout(timer);
      clearInterval(interval);
    };
  }, [fetchStatusAndData]);

  const getEffectiveSource = (): string => {
    if (sourceMode === "youtube") return youtubeUrl.trim();
    if (sourceMode === "local") return localPath.trim();
    if (sourceMode === "recent" && selectedRecent) return selectedRecent.filepath;
    return "";
  };

  // Step 1 Validation & Proceed
  const handleProceedToTemplate = () => {
    const src = getEffectiveSource();
    if (!src) {
      setErrorMsg("영상 소스 (유튜브 URL 또는 파일)를 지정해주세요.");
      return;
    }
    setErrorMsg(null);
    setCurrentStep(2);
  };

  // Start AI Analysis (Step 3)
  const handleStartAnalysis = async () => {
    const src = getEffectiveSource();
    if (!src) {
      setErrorMsg("먼저 스텝 1에서 변환할 영상 소스를 선택하거나 입력해주세요.");
      setCurrentStep(1);
      return;
    }

    setErrorMsg(null);
    setIsAnalyzing(true);
    setAnalyzeProgress(5);
    setAnalyzeMessage("분석 작업을 초기화하는 중...");
    setCurrentStep(3);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: src,
          clips_count: clipsCount,
          min_dur: minDur,
          max_dur: maxDur,
          whisper_model: "large-v3-turbo",
          llm_model: "qwen2.5:14b",
        }),
      });

      const data = await res.json();
      const jobId = data.job_id;

      // Subscribe to Server-Sent Events (SSE)
      const eventSource = new EventSource(`/api/jobs/${jobId}/events`);
      eventSource.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.progress !== undefined) setAnalyzeProgress(payload.progress);
          if (payload.message) setAnalyzeMessage(payload.message);

          if (payload.video_metadata) {
            setVideoMeta(payload.video_metadata);
          }

          if (payload.status === "completed") {
            setIsAnalyzing(false);
            setHighlights(payload.highlights || []);
            if (payload.highlights && payload.highlights.length > 0) {
              const best = payload.highlights[0];
              setSelectedHighlight(best);
              setPreviewTimeRange({ start: best.start_time, end: best.end_time });
            }
            eventSource.close();
          } else if (payload.status === "failed") {
            setIsAnalyzing(false);
            setErrorMsg(`AI 분석 중 오류가 발생했습니다: ${payload.error}`);
            eventSource.close();
          }
        } catch (e) {
          console.error("SSE parse error", e);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };
    } catch (err: unknown) {
      setIsAnalyzing(false);
      setErrorMsg(err instanceof Error ? err.message : "분석 요청에 실패했습니다.");
    }
  };

  // Start Final Render (Step 4)
  const handleStartRender = async () => {
    const src = getEffectiveSource();
    if (!selectedHighlight || !src) return;

    setErrorMsg(null);
    setIsRendering(true);
    setRenderProgress(10);
    setRenderMessage("쇼츠 렌더링 파이프라인 시작...");
    setCurrentStep(4);

    try {
      // Apply any user-modified time adjustments
      const customHighlight = {
        ...selectedHighlight,
        start_time: previewTimeRange.start,
        end_time: previewTimeRange.end,
        duration: previewTimeRange.end - previewTimeRange.start,
      };

      const res = await fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: src,
          highlight: customHighlight,
          template_id: selectedTemplateId,
          subtitle_style: subtitleStyle,
          show_badge: showBadge,
          show_subtitles: subtitleStyle !== "none",
          aspect_ratio: aspectRatio,
          remove_subtitles: removeSubtitles,
          filter_fillers: filterFillers,
        }),
      });

      const data = await res.json();
      const jobId = data.job_id;

      const eventSource = new EventSource(`/api/jobs/${jobId}/events`);
      eventSource.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.progress !== undefined) setRenderProgress(payload.progress);
          if (payload.message) setRenderMessage(payload.message);

          if (payload.status === "completed") {
            setIsRendering(false);
            setRenderedResult(payload.result);
            fetchStatusAndData();
            eventSource.close();
          } else if (payload.status === "failed") {
            setIsRendering(false);
            setErrorMsg(`렌더링 실패: ${payload.error}`);
            eventSource.close();
          }
        } catch (e) {
          console.error("Render SSE parse error", e);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };
    } catch (err: unknown) {
      setIsRendering(false);
      setErrorMsg(err instanceof Error ? err.message : "렌더링 요청에 실패했습니다.");
    }
  };

  // Finder Open Handler
  const handleOpenFinder = async () => {
    try {
      await fetch("/api/open-folder", { method: "POST" });
    } catch (err) {
      console.error(err);
    }
  };

  // Clipboard copy helper
  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Video Preview Seeking
  const handleSelectHighlightCandidate = (hl: Highlight) => {
    setSelectedHighlight(hl);
    setPreviewTimeRange({ start: hl.start_time, end: hl.end_time });
    if (previewVideoRef.current) {
      previewVideoRef.current.currentTime = hl.start_time;
      previewVideoRef.current.play();
      setIsPreviewPlaying(true);
    }
  };

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="min-h-screen bg-[#07080e] text-slate-100 flex flex-col selection:bg-indigo-500/30">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-rose-500/20">
              <Film className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg bg-gradient-to-r from-amber-300 via-rose-300 to-indigo-300 bg-clip-text text-transparent">
                  Happy Shorts Studio
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  AI v2.0
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">100% 로컬 무료 구동 • Qwen2.5-14B & Whisper Large-v3</p>
            </div>
          </div>
        </div>

        {/* Center Mode Switch Tabs */}
        <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-slate-800 shadow-inner">
          <button
            onClick={() => setActiveTab("studio")}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              activeTab === "studio"
                ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            쇼츠 제작 스튜디오
          </button>
          <button
            onClick={() => setActiveTab("gallery")}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              activeTab === "gallery"
                ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <FolderOpen className="w-4 h-4" />
            완성 보관함 ({outputs.length})
          </button>
        </div>

        {/* Right Status Indicators */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 text-xs bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300">
            <span
              className={`w-2 h-2 rounded-full ${
                systemStatus?.ollama_connected ? "bg-emerald-400 animate-pulse" : "bg-rose-400"
              }`}
            />
            <span className="text-slate-400">Ollama:</span>
            <span className="font-semibold text-emerald-400">
              {systemStatus?.ollama_connected ? "Qwen2.5-14B (온라인)" : "오프라인"}
            </span>
          </div>

          <button
            onClick={handleOpenFinder}
            title="Mac Finder에서 output 폴더 열기"
            className="flex items-center gap-1.5 text-xs bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition"
          >
            <FolderOpen className="w-3.5 h-3.5 text-amber-400" />
            Finder 열기
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 flex flex-col gap-6">
        {errorMsg && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm px-4 py-3 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
            <button onClick={() => setErrorMsg(null)} className="text-xs text-rose-400 hover:underline">
              닫기
            </button>
          </div>
        )}

        {/* VIEW 1: STUDIO (WIZARD FLOW) */}
        {activeTab === "studio" && (
          <div className="flex flex-col gap-8">
            {/* Step Wizard Header Indicator */}
            <div className="glass-panel p-4 rounded-2xl flex items-center justify-between border border-slate-800/80">
              <div className="flex items-center gap-2 md:gap-6 w-full">
                {[
                  { num: 1, label: "영상 소스 입력", icon: Video },
                  { num: 2, label: "템플릿 & 디자인", icon: Layers },
                  { num: 3, label: "AI 하이라이트 분석", icon: Sparkles },
                  { num: 4, label: "쇼츠 완성 & SEO", icon: Film },
                ].map((s, idx) => {
                  const Icon = s.icon;
                  const isActive = currentStep === s.num;
                  const isDone = currentStep > s.num;

                  return (
                    <React.Fragment key={s.num}>
                      <button
                        onClick={() => {
                          if (!isAnalyzing && !isRendering) {
                            if (s.num <= 2 || isDone) {
                              setCurrentStep(s.num);
                            }
                          }
                        }}
                        disabled={isAnalyzing || isRendering}
                        className={`flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                          isActive
                            ? "bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 shadow-sm"
                            : isDone
                            ? "text-emerald-400 hover:bg-slate-800/50"
                            : "text-slate-500"
                        }`}
                      >
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs ${
                            isActive
                              ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/40"
                              : isDone
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                              : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          {isDone ? <Check className="w-3.5 h-3.5" /> : s.num}
                        </div>
                        <div className="hidden sm:block text-left">
                          <p className="text-xs font-semibold">{s.label}</p>
                        </div>
                      </button>
                      {idx < 3 && <div className="flex-1 h-0.5 bg-slate-800 hidden md:block" />}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>

            {/* STEP 1: SOURCE SELECTION */}
            {currentStep === 1 && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800/80 flex flex-col gap-6">
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                      <Video className="w-5 h-5 text-indigo-400" />
                      스텝 1. 변환할 영상 소스를 선택하세요
                    </h2>
                    <p className="text-xs text-slate-400 mt-1">
                      유튜브 영상 주소를 넣거나, 로컬 파일 또는 이미 작업했던 캐시 영상을 원클릭으로 재사용할 수 있습니다.
                    </p>
                  </div>

                  {/* Source Mode Tabs */}
                  <div className="grid grid-cols-3 gap-3 p-1 bg-slate-900/80 rounded-xl border border-slate-800">
                    <button
                      onClick={() => setSourceMode("youtube")}
                      className={`py-2.5 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                        sourceMode === "youtube"
                          ? "bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-md"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <Radio className="w-4 h-4" />
                      유튜브 URL (자동 다운)
                    </button>
                    <button
                      onClick={() => setSourceMode("recent")}
                      className={`py-2.5 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                        sourceMode === "recent"
                          ? "bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-md"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <Zap className="w-4 h-4" />
                      최근 캐시 영상 ({recentVideos.length}개)
                    </button>
                    <button
                      onClick={() => setSourceMode("local")}
                      className={`py-2.5 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                        sourceMode === "local"
                          ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <FolderOpen className="w-4 h-4" />
                      내 PC 로컬 영상
                    </button>
                  </div>

                  {/* Mode 1: YouTube */}
                  {sourceMode === "youtube" && (
                    <div className="flex flex-col gap-3">
                      <label className="text-xs font-semibold text-slate-300">유튜브 영상 URL 또는 영상 ID</label>
                      <div className="relative">
                        <input
                          type="text"
                          placeholder="https://www.youtube.com/watch?v=... 또는 단축 URL"
                          value={youtubeUrl}
                          onChange={(e) => setYoutubeUrl(e.target.value)}
                          className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
                        />
                      </div>
                      <p className="text-[11px] text-slate-500 flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        이전에 작업했던 영상은 재다운로드 및 음성인식 없이 캐시를 자동 재사용합니다.
                      </p>
                    </div>
                  )}

                  {/* Mode 2: Recent Cached Videos */}
                  {sourceMode === "recent" && (
                    <div className="flex flex-col gap-3">
                      <label className="text-xs font-semibold text-slate-300">
                        재사용할 캐시 영상 선택 (STT 즉시 재사용)
                      </label>
                      {recentVideos.length === 0 ? (
                        <div className="p-8 text-center bg-slate-950/40 rounded-xl border border-slate-800 text-slate-500 text-xs">
                          저장된 이전 작업 영상이 없습니다. 유튜브 URL을 먼저 입력해 보세요.
                        </div>
                      ) : (
                        <div className="max-h-56 overflow-y-auto flex flex-col gap-2 pr-1">
                          {recentVideos.map((v) => {
                            const isSelected = selectedRecent?.filename === v.filename;
                            return (
                              <div
                                key={v.filename}
                                onClick={() => setSelectedRecent(v)}
                                className={`p-3 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                                  isSelected
                                    ? "bg-amber-500/10 border-amber-500/50 text-amber-200"
                                    : "bg-slate-950/50 border-slate-800/80 hover:bg-slate-900 text-slate-300"
                                }`}
                              >
                                <div className="flex items-center gap-3 overflow-hidden">
                                  <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0 font-bold text-xs">
                                    MP4
                                  </div>
                                  <div className="overflow-hidden">
                                    <p className="text-xs font-semibold truncate">{v.filename}</p>
                                    <p className="text-[11px] text-slate-500">{v.size_mb} MB</p>
                                  </div>
                                </div>
                                {isSelected && (
                                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500 text-black">
                                    선택됨
                                  </span>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Mode 3: Local File */}
                  {sourceMode === "local" && (
                    <div className="flex flex-col gap-3">
                      <label className="text-xs font-semibold text-slate-300">로컬 비디오 파일 경로</label>
                      <input
                        type="text"
                        placeholder="/Users/.../my_video.mp4"
                        value={localPath}
                        onChange={(e) => setLocalPath(e.target.value)}
                        className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
                      />
                      <p className="text-[11px] text-slate-500">
                        터미널이나 파인더에서 파일을 복사하여 파일 절대 경로를 붙여넣으세요.
                      </p>
                    </div>
                  )}

                  {/* Settings: Duration & Clips */}
                  <div className="pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>쇼츠 목표 재생 시간</span>
                        <span className="text-indigo-400 font-bold">
                          {minDur}초 ~ {maxDur}초
                        </span>
                      </label>
                      <div className="flex gap-2">
                        {[
                          { label: "표준 (30~50초)", min: 30, max: 50 },
                          { label: "빠름 (20~35초)", min: 20, max: 35 },
                          { label: "완결 (45~60초)", min: 45, max: 60 },
                        ].map((d) => (
                          <button
                            key={d.label}
                            type="button"
                            onClick={() => {
                              setMinDur(d.min);
                              setMaxDur(d.max);
                            }}
                            className={`flex-1 py-1.5 px-2 rounded-lg text-[11px] font-semibold border transition ${
                              minDur === d.min && maxDur === d.max
                                ? "bg-indigo-600/20 border-indigo-500 text-indigo-300"
                                : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            {d.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>하이라이트 후보 추출 개수</span>
                        <span className="text-indigo-400 font-bold">{clipsCount}개 후보</span>
                      </label>
                      <div className="flex gap-2">
                        {[1, 2, 3, 5].map((cnt) => (
                          <button
                            key={cnt}
                            type="button"
                            onClick={() => setClipsCount(cnt)}
                            className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold border transition ${
                              clipsCount === cnt
                                ? "bg-indigo-600/20 border-indigo-500 text-indigo-300"
                                : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            {cnt}개
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Settings: Aspect Ratio & Subtitle Removal */}
                  <div className="pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>영상의 화면 비율 (Aspect Ratio)</span>
                        <span className="text-indigo-400 font-bold">
                          {aspectRatio === "9:16" ? "9:16 세로 (쇼츠)" : "16:9 가로 (와이드)"}
                        </span>
                      </label>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setAspectRatio("9:16")}
                          className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold border transition flex items-center justify-center gap-1.5 ${
                            aspectRatio === "9:16"
                              ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm"
                              : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span>📱 세로 (9:16)</span>
                          <span className="text-[10px] text-amber-400 font-normal">얼굴 자동 추적</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setAspectRatio("16:9")}
                          className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold border transition flex items-center justify-center gap-1.5 ${
                            aspectRatio === "16:9"
                              ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm"
                              : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span>🖥️ 가로 (16:9)</span>
                          <span className="text-[10px] text-slate-500 font-normal">유튜브 와이드</span>
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>원본 영상 자막 처리</span>
                        <span className={`font-bold ${removeSubtitles ? "text-amber-400" : "text-slate-500"}`}>
                          {removeSubtitles ? "AI 제거 활성화" : "원본 자막 유지"}
                        </span>
                      </label>
                      <button
                        type="button"
                        onClick={() => setRemoveSubtitles(!removeSubtitles)}
                        className={`w-full py-2 px-3 rounded-xl text-xs font-semibold border transition flex items-center justify-between ${
                          removeSubtitles
                            ? "bg-amber-500/10 border-amber-500/50 text-amber-200 shadow-sm"
                            : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <span className="text-left truncate pr-2">
                          원본 자막 삭제 (ai 처리라서 일부 뭉개짐이 있을 수 있음)
                        </span>
                        <div
                          className={`w-8 h-4.5 flex items-center rounded-full p-0.5 transition duration-300 flex-shrink-0 ${
                            removeSubtitles ? "bg-amber-500 justify-end" : "bg-slate-800 justify-start"
                          }`}
                        >
                          <div className="bg-white w-3.5 h-3.5 rounded-full shadow-md" />
                        </div>
                      </button>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>말버릇 / 추임새 자막 정리</span>
                        <span className={`font-bold ${filterFillers ? "text-emerald-400" : "text-slate-500"}`}>
                          {filterFillers ? "자동 필터링 (추천)" : "모든 단어 표시"}
                        </span>
                      </label>
                      <button
                        type="button"
                        onClick={() => setFilterFillers(!filterFillers)}
                        className={`w-full py-2 px-3 rounded-xl text-xs font-semibold border transition flex items-center justify-between ${
                          filterFillers
                            ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-200 shadow-sm"
                            : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <span className="text-left truncate pr-2">
                          추임새/말버릇 제거 (어, 음, 네, 아 등의 단독 팝업 방지)
                        </span>
                        <div
                          className={`w-8 h-4.5 flex items-center rounded-full p-0.5 transition duration-300 flex-shrink-0 ${
                            filterFillers ? "bg-emerald-500 justify-end" : "bg-slate-800 justify-start"
                          }`}
                        >
                          <div className="bg-white w-3.5 h-3.5 rounded-full shadow-md" />
                        </div>
                      </button>
                    </div>
                  </div>

                  <div className="flex justify-end pt-2">
                    <button
                      onClick={handleProceedToTemplate}
                      className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold text-sm flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition"
                    >
                      다음 단계: 템플릿 선택
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Right Info Box */}
                <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 flex flex-col gap-4">
                  <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
                    <Sparkles className="w-4 h-4" />
                    업그레이드된 AI 엔진 사양
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                      <p className="font-semibold text-slate-200">🎙️ Faster-Whisper Large-v3-Turbo</p>
                      <p className="text-slate-400 mt-1">밀리초 단위 단어 음성인식으로 정확도 극대화</p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                      <p className="font-semibold text-slate-200">🤖 Ollama Qwen2.5-14B</p>
                      <p className="text-slate-400 mt-1">
                        더 정교한 문맥 파악과 OpusClip 기준 4기둥 바이럴 채점 (Hook, Flow, Value, Trend)
                      </p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                      <p className="font-semibold text-emerald-400">💰 100% 무료 로컬 처리</p>
                      <p className="text-slate-400 mt-1">외부 유료 API 요금 0원, 데이터 유출 없이 Mac에서 전과정 처리</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* STEP 2: TEMPLATE & VISUAL DESIGN (MIRICANVAS STYLE) */}
            {currentStep === 2 && (
              <div className="flex flex-col gap-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-md flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        미리캔버스 갤러리 스타일
                      </span>
                      <span className="text-xs text-slate-500">• 총 {templates.length}개 프리미엄 쇼츠 템플릿</span>
                    </div>
                    <h2 className="text-xl font-bold text-white mt-1 flex items-center gap-2">
                      <Layers className="w-5 h-5 text-indigo-400" />
                      스텝 2. 쇼츠 디자인 템플릿을 선택하세요
                    </h2>
                    <p className="text-xs text-slate-400 mt-1">
                      카드 속 9:16 비주얼 목업을 직접 확인하고 원하는 영상 스타일에 맞는 템플릿을 선택하세요.
                    </p>
                  </div>
                  <button
                    onClick={() => setCurrentStep(1)}
                    className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition bg-slate-900/80 px-3 py-2 rounded-xl border border-slate-800"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    이전으로
                  </button>
                </div>

                {/* Category Filter Pills Bar (MiriCanvas Style) */}
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none text-xs">
                  {[
                    { id: "all", label: "✨ 전체보기", count: templates.length },
                    { id: "테슬라 및 테크", label: "⚡ 테슬라·HUD", count: templates.filter(t => t.category === "테슬라 및 테크").length },
                    { id: "브이로그 및 감성", label: "🌿 브이로그·스티커", count: templates.filter(t => t.category === "브이로그 및 감성").length },
                    { id: "챌린지 및 프로모션", label: "🏋️ 챌린지·프로모션", count: templates.filter(t => t.category === "챌린지 및 프로모션").length },
                    { id: "뉴스 및 이슈", label: "🚨 뉴스·속보", count: templates.filter(t => t.category === "뉴스 및 이슈").length },
                    { id: "SNS 및 통화", label: "📱 SNS·릴스·통화", count: templates.filter(t => t.category === "SNS 및 통화").length },
                    { id: "밈 및 썰", label: "🐸 밈·웹툰·사진첩", count: templates.filter(t => t.category === "밈 및 썰").length },
                    { id: "정보 및 리뷰", label: "💻 꿀팁·정보·테크", count: templates.filter(t => t.category === "정보 및 리뷰").length },
                    { id: "영화 및 리뷰", label: "🎬 영화·드라마·시네마", count: templates.filter(t => t.category === "영화 및 리뷰").length },
                    { id: "메신저 및 대화", label: "💬 카톡·썰 대화", count: templates.filter(t => t.category === "메신저 및 대화").length },
                    { id: "랭킹 및 퀴즈", label: "🏆 랭킹·차트·퀴즈", count: templates.filter(t => t.category === "랭킹 및 퀴즈").length },
                    { id: "상품 및 리뷰", label: "🛍️ 별점·내돈내산", count: templates.filter(t => t.category === "상품 및 리뷰").length },
                    { id: "동기부여 및 명언", label: "🔥 명언·동기부여", count: templates.filter(t => t.category === "동기부여 및 명언").length },
                    { id: "인포 매거진", label: "✨ 네온 매거진", count: templates.filter(t => t.category === "인포 매거진").length },
                    { id: "교육 및 강의", label: "💡 1분 지식·강의", count: templates.filter(t => t.category === "교육 및 강의").length },
                    { id: "브이로그 및 일상", label: "📷 폴라로이드 브이로그", count: templates.filter(t => t.category === "브이로그 및 일상").length },
                    { id: "인터뷰 및 토크", label: "👤 9:16 인물 토크", count: templates.filter(t => t.category === "인터뷰 및 토크").length },
                    { id: "자체 자막 영상", label: "🎞️ 순정 원본 보존", count: templates.filter(t => t.category === "자체 자막 영상").length },
                  ].map((cat) => {
                    const isActive = selectedCategory === cat.id;
                    return (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => setSelectedCategory(cat.id)}
                        className={`px-3 py-1.5 rounded-full font-semibold whitespace-nowrap transition flex items-center gap-1.5 ${
                          isActive
                            ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 border border-indigo-400"
                            : "bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700"
                        }`}
                      >
                        <span>{cat.label}</span>
                        {cat.count > 0 && (
                          <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isActive ? "bg-white/20 text-white" : "bg-slate-800 text-slate-500"}`}>
                            {cat.count}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* 9:16 Visual Template Cards Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {(selectedCategory === "all" ? templates : templates.filter((t) => t.category === selectedCategory)).map(
                    (tpl) => (
                      <TemplateMockupCard
                        key={tpl.id}
                        template={tpl}
                        isSelected={selectedTemplateId === tpl.id}
                        onSelect={() => setSelectedTemplateId(tpl.id)}
                      />
                    )
                  )}
                </div>

                {/* Bottom Sticky Action & Fine-Tuning Panel */}
                <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 shadow-2xl flex flex-col lg:flex-row items-center justify-between gap-6 sticky bottom-4 z-40 bg-slate-950/90 backdrop-blur-xl">
                  {/* Left: Currently Selected Template Pill */}
                  <div className="flex items-center gap-3 w-full lg:w-auto">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center font-bold text-white shadow-md shadow-indigo-600/30 flex-shrink-0">
                      ✓
                    </div>
                    <div className="overflow-hidden">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          선택된 템플릿
                        </span>
                        <span className="text-xs font-bold text-white truncate">
                          {templates.find((t) => t.id === selectedTemplateId)?.name || "템플릿 선택"}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 truncate mt-0.5">
                        {templates.find((t) => t.id === selectedTemplateId)?.description}
                      </p>
                    </div>
                  </div>

                  {/* Center: Subtitle Style & Badge Toggle */}
                  <div className="flex items-center flex-wrap gap-4 w-full lg:w-auto justify-start lg:justify-center">
                    <div className="flex items-center gap-1.5 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-xs">
                      {[
                        { id: "viral_pop", label: "🔥 키네틱 팝 자막" },
                        { id: "clean_minimal", label: "💬 클린 미니멀" },
                        { id: "none", label: "🚫 자막 없음" },
                      ].map((s) => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => setSubtitleStyle(s.id)}
                          className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                            subtitleStyle === s.id
                              ? "bg-indigo-600 text-white shadow"
                              : "text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          {s.label}
                        </button>
                      ))}
                    </div>

                    <div className="flex items-center gap-2 text-xs text-slate-300 bg-slate-900/90 px-3 py-1.5 rounded-xl border border-slate-800">
                      <span>3초 훅 뱃지:</span>
                      <button
                        type="button"
                        onClick={() => setShowBadge(!showBadge)}
                        className={`w-9 h-5 flex items-center rounded-full p-0.5 transition duration-300 ${
                          showBadge ? "bg-indigo-600 justify-end" : "bg-slate-800 justify-start"
                        }`}
                      >
                        <div className="bg-white w-3.5 h-3.5 rounded-full shadow-md" />
                      </button>
                    </div>

                    {/* Aspect Ratio Pill */}
                    <div className="flex items-center gap-1 text-xs text-slate-300 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
                      <button
                        type="button"
                        onClick={() => setAspectRatio("9:16")}
                        className={`px-2.5 py-1 rounded-lg font-bold transition flex items-center gap-1 ${
                          aspectRatio === "9:16"
                            ? "bg-indigo-600 text-white shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <span>📱 9:16 세로</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setAspectRatio("16:9")}
                        className={`px-2.5 py-1 rounded-lg font-bold transition flex items-center gap-1 ${
                          aspectRatio === "16:9"
                            ? "bg-indigo-600 text-white shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <span>🖥️ 16:9 가로</span>
                      </button>
                    </div>

                    {/* Subtitle Removal Toggle */}
                    <button
                      type="button"
                      onClick={() => setRemoveSubtitles(!removeSubtitles)}
                      title="원본 자막 삭제 (ai 처리라서 일부 뭉개짐이 있을 수 있음)"
                      className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-xl border transition ${
                        removeSubtitles
                          ? "bg-amber-500/15 border-amber-500/50 text-amber-300 font-semibold"
                          : "bg-slate-900/90 border-slate-800 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <span>원본 자막 삭제</span>
                      <div
                        className={`w-7 h-4 flex items-center rounded-full p-0.5 transition duration-300 ${
                          removeSubtitles ? "bg-amber-500 justify-end" : "bg-slate-800 justify-start"
                        }`}
                      >
                        <div className="bg-white w-3 h-3 rounded-full shadow-md" />
                      </div>
                    </button>

                    {/* Filler Word Removal Toggle */}
                    <button
                      type="button"
                      onClick={() => setFilterFillers(!filterFillers)}
                      title="추임새/말버릇 제거 (어, 음, 네, 아 등의 단독 팝업 방지)"
                      className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-xl border transition ${
                        filterFillers
                          ? "bg-emerald-500/15 border-emerald-500/50 text-emerald-300 font-semibold"
                          : "bg-slate-900/90 border-slate-800 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <span>말버릇/추임새 정리</span>
                      <div
                        className={`w-7 h-4 flex items-center rounded-full p-0.5 transition duration-300 ${
                          filterFillers ? "bg-emerald-500 justify-end" : "bg-slate-800 justify-start"
                        }`}
                      >
                        <div className="bg-white w-3 h-3 rounded-full shadow-md" />
                      </div>
                    </button>
                  </div>

                  {/* Right: Proceed Button */}
                  <div className="w-full lg:w-auto flex justify-end">
                    <button
                      onClick={handleStartAnalysis}
                      className="w-full lg:w-auto px-7 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:opacity-95 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-xl shadow-rose-500/20 transition"
                    >
                      <Sparkles className="w-4 h-4" />
                      AI 하이라이트 분석 시작
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* STEP 3: AI ANALYSIS & CANDIDATE SELECTOR (OPUSCLIP STYLE) */}
            {currentStep === 3 && (
              <div className="flex flex-col gap-6">
                {/* Analyzing In-Progress Screen */}
                {isAnalyzing ? (
                  <div className="glass-panel p-12 rounded-2xl border border-slate-800/80 flex flex-col items-center justify-center text-center gap-6 min-h-[400px]">
                    <div className="relative">
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-600 flex items-center justify-center animate-pulse-glow shadow-2xl shadow-indigo-500/30">
                        <Sparkles className="w-10 h-10 text-white" />
                      </div>
                    </div>

                    <div className="max-w-md w-full">
                      <h3 className="text-xl font-bold text-white mb-2">AI 하이라이트 분석 진행 중...</h3>
                      <p className="text-xs text-slate-400 mb-6">{analyzeMessage}</p>

                      {/* Progress Bar */}
                      <div className="w-full bg-slate-900 rounded-full h-3 p-0.5 border border-slate-800 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 h-full rounded-full transition-all duration-300 shadow-sm shadow-indigo-500/50"
                          style={{ width: `${analyzeProgress}%` }}
                        />
                      </div>
                      <div className="flex justify-between items-center mt-2 text-xs font-mono text-slate-500">
                        <span>진행률</span>
                        <span className="text-indigo-400 font-bold">{analyzeProgress}%</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  /* Analysis Completed: OpusClip Candidate Cards */
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left: Candidate List */}
                    <div className="lg:col-span-7 flex flex-col gap-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h2 className="text-lg font-bold text-white flex items-center gap-2">
                            <Flame className="w-5 h-5 text-amber-500" />
                            AI 바이럴 하이라이트 후보 ({highlights.length}개 발견)
                          </h2>
                          <p className="text-xs text-slate-400 mt-1">
                            OpusClip 4기둥 바이럴 점수가 가장 높은 구간 순으로 추천되었습니다.
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-col gap-3">
                        {highlights.map((hl) => {
                          const isSelected = selectedHighlight?.id === hl.id;
                          const b = hl.score_breakdown || { hook: 25, flow: 20, value: 20, trend: 15 };

                          return (
                            <div
                              key={hl.id}
                              onClick={() => handleSelectHighlightCandidate(hl)}
                              className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                                isSelected
                                  ? "bg-gradient-to-r from-slate-900/90 to-indigo-950/50 border-indigo-500 shadow-lg ring-1 ring-indigo-500/60"
                                  : "glass-card hover:border-slate-700"
                              }`}
                            >
                              <div className="flex items-start justify-between gap-4 mb-2">
                                <div className="flex items-center gap-2.5">
                                  <span className="text-xs font-bold px-2 py-0.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                                    #{hl.id}
                                  </span>
                                  <span
                                    className={`text-xs font-black px-2.5 py-0.5 rounded-lg flex items-center gap-1 ${
                                      hl.virality_score >= 90
                                        ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                        : hl.virality_score >= 80
                                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                                        : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                                    }`}
                                  >
                                    <Flame className="w-3.5 h-3.5 fill-current" />
                                    {hl.virality_score}점
                                  </span>
                                </div>

                                <div className="text-xs font-mono text-slate-400 flex items-center gap-1">
                                  <Clock className="w-3.5 h-3.5" />
                                  {formatSeconds(hl.start_time)} ~ {formatSeconds(hl.end_time)} ({Math.round(hl.duration)}초)
                                </div>
                              </div>

                              <h3 className="font-bold text-sm text-white mt-1 mb-1">{hl.title}</h3>
                              <p className="text-xs text-amber-300 font-medium bg-amber-500/10 px-2 py-1 rounded-md inline-block mb-3">
                                💬 &quot;{hl.hook_text}&quot;
                              </p>

                              {/* Summary takeaway points */}
                              {hl.summary_points && hl.summary_points.length > 0 && (
                                <ul className="text-xs text-slate-400 space-y-1 mb-3">
                                  {hl.summary_points.map((pt, i) => (
                                    <li key={i} className="flex items-start gap-1.5">
                                      <span className="text-indigo-400">•</span>
                                      <span>{pt}</span>
                                    </li>
                                  ))}
                                </ul>
                              )}

                              {/* Score Breakdown Pills */}
                              <div className="flex items-center gap-2 pt-2 border-t border-slate-800 text-[10px] text-slate-500 font-mono">
                                <span>후킹: {b.hook}/30</span>
                                <span>흐름: {b.flow}/25</span>
                                <span>가치: {b.value}/25</span>
                                <span>트렌드: {b.trend}/20</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Right: Interactive Video Player & Trim Controller */}
                    <div className="lg:col-span-5 flex flex-col gap-4">
                      <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 flex flex-col gap-4 sticky top-24">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          <Play className="w-4 h-4 text-indigo-400" />
                          선택 구간 미리보기 & 타임라인 트림
                        </h3>

                        {videoMeta?.stream_url ? (
                          <div className="relative aspect-video bg-black rounded-xl overflow-hidden border border-slate-800">
                            <video
                              ref={previewVideoRef}
                              src={videoMeta.stream_url}
                              controls
                              className="w-full h-full object-contain"
                              onTimeUpdate={(e) => {
                                const current = (e.target as HTMLVideoElement).currentTime;
                                if (previewTimeRange.end > 0 && current >= previewTimeRange.end) {
                                  (e.target as HTMLVideoElement).pause();
                                  setIsPreviewPlaying(false);
                                }
                              }}
                            />
                          </div>
                        ) : (
                          <div className="aspect-video bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-center text-xs text-slate-500">
                            미리보기 플레이어 준비 완료
                          </div>
                        )}

                        {selectedHighlight && (
                          <div className="flex flex-col gap-3 pt-2 border-t border-slate-800">
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-400">구간 조정 (초)</span>
                              <span className="font-mono text-indigo-300 font-bold">
                                {formatSeconds(previewTimeRange.start)} ~ {formatSeconds(previewTimeRange.end)} (
                                {Math.round(previewTimeRange.end - previewTimeRange.start)}초)
                              </span>
                            </div>

                            {/* Trim range slider inputs */}
                            <div className="grid grid-cols-2 gap-3">
                              <div>
                                <label className="text-[11px] text-slate-500 mb-1 block">시작 시간 (초)</label>
                                <input
                                  type="number"
                                  step="0.5"
                                  value={previewTimeRange.start}
                                  onChange={(e) =>
                                    setPreviewTimeRange({
                                      ...previewTimeRange,
                                      start: parseFloat(e.target.value) || 0,
                                    })
                                  }
                                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                                />
                              </div>
                              <div>
                                <label className="text-[11px] text-slate-500 mb-1 block">종료 시간 (초)</label>
                                <input
                                  type="number"
                                  step="0.5"
                                  value={previewTimeRange.end}
                                  onChange={(e) =>
                                    setPreviewTimeRange({
                                      ...previewTimeRange,
                                      end: parseFloat(e.target.value) || 0,
                                    })
                                  }
                                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                                />
                              </div>
                            </div>

                            {/* Output Settings Summary & Toggles */}
                            <div className="flex flex-col gap-2 p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
                              <div className="flex items-center justify-between">
                                <span className="text-slate-400 font-semibold">출력 화면 비율:</span>
                                <div className="flex items-center gap-1">
                                  <button
                                    type="button"
                                    onClick={() => setAspectRatio("9:16")}
                                    className={`px-2 py-0.5 rounded text-[11px] font-bold transition ${
                                      aspectRatio === "9:16"
                                        ? "bg-indigo-600 text-white shadow-sm"
                                        : "bg-slate-900 text-slate-400 hover:text-slate-200"
                                    }`}
                                  >
                                    📱 9:16 세로 (얼굴 추적)
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => setAspectRatio("16:9")}
                                    className={`px-2 py-0.5 rounded text-[11px] font-bold transition ${
                                      aspectRatio === "16:9"
                                        ? "bg-indigo-600 text-white shadow-sm"
                                        : "bg-slate-900 text-slate-400 hover:text-slate-200"
                                    }`}
                                  >
                                    🖥️ 16:9 가로
                                  </button>
                                </div>
                              </div>

                              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
                                <span className="text-slate-400 font-semibold">원본 자막 처리:</span>
                                <button
                                  type="button"
                                  onClick={() => setRemoveSubtitles(!removeSubtitles)}
                                  className={`px-2 py-0.5 rounded text-[11px] font-bold transition flex items-center gap-1.5 ${
                                    removeSubtitles
                                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                                      : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200"
                                  }`}
                                >
                                  <span>{removeSubtitles ? "🧹 AI 자막 삭제 적용 중" : "✨ 원본 자막 유지"}</span>
                                </button>
                              </div>

                              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
                                <span className="text-slate-400 font-semibold">말버릇 자막 정리:</span>
                                <button
                                  type="button"
                                  onClick={() => setFilterFillers(!filterFillers)}
                                  className={`px-2 py-0.5 rounded text-[11px] font-bold transition flex items-center gap-1.5 ${
                                    filterFillers
                                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                      : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200"
                                  }`}
                                >
                                  <span>{filterFillers ? "✨ 말버릇(네/어/음) 정리 켜짐" : "모든 단어 표시"}</span>
                                </button>
                              </div>
                            </div>

                            <button
                              onClick={handleStartRender}
                              className="mt-2 w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 via-violet-600 to-rose-600 hover:opacity-90 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition"
                            >
                              <Film className="w-4 h-4" />
                              선택한 구간으로 {aspectRatio === "16:9" ? "16:9 와이드 영상" : "9:16 쇼츠"} 렌더링 시작
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* STEP 4: RENDERING PROGRESS & COMPLETED RESULT */}
            {currentStep === 4 && (
              <div className="flex flex-col gap-6">
                {isRendering ? (
                  <div className="glass-panel p-12 rounded-2xl border border-slate-800/80 flex flex-col items-center justify-center text-center gap-6 min-h-[400px]">
                    <div className="relative">
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-rose-500 via-indigo-600 to-violet-600 flex items-center justify-center animate-pulse-glow shadow-2xl shadow-indigo-500/30">
                        <Film className="w-10 h-10 text-white" />
                      </div>
                    </div>

                    <div className="max-w-md w-full">
                      <h3 className="text-xl font-bold text-white mb-2">9:16 쇼츠 렌더링 진행 중...</h3>
                      <p className="text-xs text-slate-400 mb-6">{renderMessage}</p>

                      <div className="w-full bg-slate-900 rounded-full h-3 p-0.5 border border-slate-800 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-rose-500 via-indigo-600 to-violet-600 h-full rounded-full transition-all duration-300 shadow-sm shadow-rose-500/50"
                          style={{ width: `${renderProgress}%` }}
                        />
                      </div>
                      <div className="flex justify-between items-center mt-2 text-xs font-mono text-slate-500">
                        <span>FFmpeg 렌더링</span>
                        <span className="text-rose-400 font-bold">{renderProgress}%</span>
                      </div>
                    </div>
                  </div>
                ) : renderedResult ? (
                  /* Finished Shorts Result View */
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left: Video Player */}
                    <div className="lg:col-span-5 flex flex-col items-center justify-center">
                      <div className={`w-full ${aspectRatio === "16:9" ? "max-w-[560px] rounded-[28px]" : "max-w-[340px] rounded-[36px]"} bg-slate-950 p-3 border-4 border-slate-800 shadow-2xl shadow-indigo-500/10`}>
                        {/* Notch for 9:16 mobile shorts */}
                        {aspectRatio === "9:16" && (
                          <div className="w-28 h-4 bg-slate-800 rounded-full mx-auto mb-2" />
                        )}
                        <div className={`relative ${aspectRatio === "16:9" ? "aspect-video rounded-[18px]" : "aspect-[9/16] rounded-[24px]"} overflow-hidden bg-black`}>
                          <video
                            src={renderedResult.stream_url}
                            controls
                            autoPlay
                            loop
                            className="w-full h-full object-contain"
                          />
                        </div>
                      </div>

                      <div className="flex items-center gap-3 mt-4">
                        <a
                          href={renderedResult.stream_url}
                          download={renderedResult.filename}
                          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-md transition"
                        >
                          <Download className="w-3.5 h-3.5" />
                          쇼츠 MP4 다운로드
                        </a>
                        <button
                          onClick={handleOpenFinder}
                          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition"
                        >
                          <FolderOpen className="w-3.5 h-3.5" />
                          Finder 열기
                        </button>
                      </div>
                    </div>

                    {/* Right: 2026 YouTube Shorts SEO Metadata Center */}
                    <div className="lg:col-span-7 flex flex-col gap-4">
                      <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 flex flex-col gap-4">
                        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                          <div>
                            <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                              <Check className="w-4 h-4" />
                              쇼츠 제작 완료!
                            </span>
                            <h2 className="text-lg font-bold text-white mt-1">2026 유튜브 알고리즘 SEO 패키지</h2>
                          </div>
                          <button
                            onClick={() => {
                              setCurrentStep(1);
                              setRenderedResult(null);
                            }}
                            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition"
                          >
                            새 쇼츠 만들기
                          </button>
                        </div>

                        {/* SEO guide content display */}
                        <div className="flex flex-col gap-3 text-xs">
                          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 relative group">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-bold text-amber-300">📌 추천 제목 1안 (CTR 최적화)</span>
                              <button
                                onClick={() =>
                                  copyToClipboard(
                                    renderedResult.title || "완성된 쇼츠",
                                    "title1"
                                  )
                                }
                                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white"
                              >
                                {copiedKey === "title1" ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                                {copiedKey === "title1" ? "복사됨!" : "복사"}
                              </button>
                            </div>
                            <p className="text-slate-200 font-semibold">{renderedResult.title}</p>
                          </div>

                          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 relative group">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-bold text-indigo-300">📝 전체 유튜브 설명란 및 태그 TXT</span>
                              <button
                                onClick={() =>
                                  copyToClipboard(renderedResult.seo_content || "", "fullSeo")
                                }
                                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white"
                              >
                                {copiedKey === "fullSeo" ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                                {copiedKey === "fullSeo" ? "전체 복사됨!" : "전체 복사"}
                              </button>
                            </div>
                            <pre className="text-slate-300 whitespace-pre-wrap font-sans text-xs max-h-64 overflow-y-auto leading-relaxed">
                              {renderedResult.seo_content || "메타데이터가 생성되었습니다."}
                            </pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            )}
          </div>
        )}

        {/* VIEW 2: OUTPUTS GALLERY */}
        {activeTab === "gallery" && (
          <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <FolderOpen className="w-5 h-5 text-amber-500" />
                  생성된 쇼츠 보관함 ({outputs.length}개)
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  로컬 output 디렉토리에 저장된 완성 쇼츠 파일들을 언제든 다시 시청하고 다운로드할 수 있습니다.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={fetchStatusAndData}
                  className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                  title="새로고침"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
                <button
                  onClick={handleOpenFinder}
                  className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-xl border border-slate-700 transition"
                >
                  <FolderOpen className="w-3.5 h-3.5 text-amber-400" />
                  Finder 열기
                </button>
              </div>
            </div>

            {outputs.length === 0 ? (
              <div className="glass-panel p-16 rounded-2xl border border-slate-800 text-center flex flex-col items-center justify-center gap-4">
                <Film className="w-12 h-12 text-slate-600" />
                <div>
                  <h3 className="text-sm font-bold text-slate-300">아직 생성된 쇼츠가 없습니다</h3>
                  <p className="text-xs text-slate-500 mt-1">첫 번째 쇼츠를 만들어 보세요!</p>
                </div>
                <button
                  onClick={() => setActiveTab("studio")}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition"
                >
                  쇼츠 제작 시작
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {outputs.map((out) => (
                  <div
                    key={out.filename}
                    className="glass-card rounded-2xl border border-slate-800/80 overflow-hidden flex flex-col justify-between"
                  >
                    <div>
                      {/* Video Player */}
                      <div className="aspect-[9/16] max-h-[380px] bg-black relative flex items-center justify-center overflow-hidden">
                        <video
                          src={out.stream_url}
                          controls
                          className="w-full h-full object-contain"
                        />
                      </div>

                      <div className="p-4">
                        <h4 className="font-bold text-xs text-white truncate" title={out.filename}>
                          {out.filename}
                        </h4>
                        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
                          <span>{out.size_mb} MB</span>
                          <span>{new Date(out.modified_at * 1000).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 pt-0 flex items-center gap-2">
                      <a
                        href={out.stream_url}
                        download={out.filename}
                        className="flex-1 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-bold flex items-center justify-center gap-1.5 transition"
                      >
                        <Download className="w-3.5 h-3.5" />
                        다운로드
                      </a>
                      {out.seo_content && (
                        <button
                          onClick={() => copyToClipboard(out.seo_content || "", out.filename)}
                          className="py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1 border border-slate-700 transition"
                          title="SEO 설명글 복사"
                        >
                          {copiedKey === out.filename ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                          SEO 복사
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
