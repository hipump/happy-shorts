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
  Grid,
  List,
  Search,
  HardDrive,
  X,
  Tag,
  Loader2,
  CheckCircle2,
  Cpu,
  AudioLines,
  Type,
  Volume2,
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
  const [selectedHighlightIds, setSelectedHighlightIds] = useState<number[]>([]);

  // Step 4: Rendering
  const [isRendering, setIsRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState(0);
  const [renderMessage, setRenderMessage] = useState("");
  const [renderedResult, setRenderedResult] = useState<RenderedOutput | null>(null);
  const [batchResults, setBatchResults] = useState<RenderedOutput[]>([]);
  const [selectedBatchIdx, setSelectedBatchIdx] = useState<number>(0);

  // Interactive Video Player & Trimming
  const [previewTimeRange, setPreviewTimeRange] = useState<{ start: number; end: number }>({ start: 0, end: 0 });
  const previewVideoRef = useRef<HTMLVideoElement | null>(null);
  const [isPreviewPlaying, setIsPreviewPlaying] = useState(false);

  // UI state
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Gallery state
  const [galleryViewMode, setGalleryViewMode] = useState<"grid" | "feed">("grid");
  const [galleryFilter, setGalleryFilter] = useState<"all" | "9:16" | "16:9">("all");
  const [gallerySearch, setGallerySearch] = useState<string>("");
  const [previewModalOutput, setPreviewModalOutput] = useState<RenderedOutput | null>(null);

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
    setAnalyzeMessage("AI 분석 세션을 시작하고 영상 스트림을 연결하는 중...");
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

      // Subscribe to Server-Sent Events (SSE) with polling fallback
      let pollTimer: NodeJS.Timeout | null = null;
      const cleanUpStream = () => {
        if (pollTimer) clearInterval(pollTimer);
        eventSource.close();
      };

      const eventSource = new EventSource(`/api/jobs/${jobId}/events`);
      eventSource.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.progress !== undefined) {
            setAnalyzeProgress((prev) => Math.max(prev, payload.progress));
          }
          if (payload.message) setAnalyzeMessage(payload.message);

          if (payload.video_metadata) {
            setVideoMeta(payload.video_metadata);
          }

          if (payload.status === "completed") {
            cleanUpStream();
            setIsAnalyzing(false);
            const hlList = payload.highlights || [];
            setHighlights(hlList);
            if (hlList.length > 0) {
              const best = hlList[0];
              setSelectedHighlight(best);
              setSelectedHighlightIds(hlList.map((h: Highlight) => h.id));
              setPreviewTimeRange({ start: best.start_time, end: best.end_time });
            }
          } else if (payload.status === "failed") {
            cleanUpStream();
            setIsAnalyzing(false);
            setErrorMsg(`AI 분석 중 오류가 발생했습니다: ${payload.error}`);
          }
        } catch (e) {
          console.error("SSE parse error", e);
        }
      };

      eventSource.onerror = () => {
        // Do not immediately close on transient SSE errors; polling fallback handles it
      };

      // Safety net polling every 1.5s
      pollTimer = setInterval(async () => {
        try {
          const pollRes = await fetch(`/api/jobs/${jobId}`);
          if (!pollRes.ok) return;
          const pollData = await pollRes.json();
          if (pollData.progress !== undefined) {
            setAnalyzeProgress((prev) => Math.max(prev, pollData.progress));
          }
          if (pollData.message) setAnalyzeMessage(pollData.message);
          if (pollData.video_metadata) setVideoMeta(pollData.video_metadata);

          if (pollData.status === "completed") {
            cleanUpStream();
            setIsAnalyzing(false);
            const hlList = pollData.highlights || [];
            setHighlights(hlList);
            if (hlList.length > 0) {
              const best = hlList[0];
              setSelectedHighlight(best);
              setSelectedHighlightIds(hlList.map((h: Highlight) => h.id));
              setPreviewTimeRange({ start: best.start_time, end: best.end_time });
            }
          } else if (pollData.status === "failed") {
            cleanUpStream();
            setIsAnalyzing(false);
            setErrorMsg(`AI 분석 중 오류가 발생했습니다: ${pollData.error}`);
          }
        } catch {
          // Ignore transient poll errors
        }
      }, 1500);
    } catch (err: unknown) {
      setIsAnalyzing(false);
      setErrorMsg(err instanceof Error ? err.message : "분석 요청에 실패했습니다.");
    }
  };

  // Compute effective stream URL for preview player
  const effectiveStreamUrl = React.useMemo(() => {
    if (videoMeta?.stream_url) return videoMeta.stream_url;
    if (sourceMode === "recent" && selectedRecent?.stream_url) return selectedRecent.stream_url;
    if (sourceMode === "local" && localPath) {
      const filename = localPath.split("/").pop();
      if (filename) return `/media/downloads/${filename}`;
    }
    return "";
  }, [videoMeta, sourceMode, selectedRecent, localPath]);

  // Start Final Render (Step 4) - Supports single clip or full batch
  const handleStartRender = async (mode: "batch" | "selected" = "batch") => {
    const src = getEffectiveSource();
    if (!src) {
      setErrorMsg("유효한 영상 소스가 없습니다.");
      return;
    }

    let targetHighlights: Highlight[] = [];
    if (mode === "selected") {
      if (!selectedHighlight) {
        setErrorMsg("선택된 하이라이트 구간이 없습니다.");
        return;
      }
      targetHighlights = [{
        ...selectedHighlight,
        start_time: previewTimeRange.start,
        end_time: previewTimeRange.end,
        duration: Math.max(1, previewTimeRange.end - previewTimeRange.start),
      }];
    } else {
      // Batch mode: use checked candidate IDs
      targetHighlights = highlights.filter((h) => selectedHighlightIds.includes(h.id));
      if (targetHighlights.length === 0) {
        if (selectedHighlight) {
          targetHighlights = [{
            ...selectedHighlight,
            start_time: previewTimeRange.start,
            end_time: previewTimeRange.end,
            duration: Math.max(1, previewTimeRange.end - previewTimeRange.start),
          }];
        } else if (highlights.length > 0) {
          targetHighlights = highlights;
        } else {
          setErrorMsg("생성할 쇼츠 후보를 1개 이상 선택해주세요.");
          return;
        }
      }
    }

    setErrorMsg(null);
    setIsRendering(true);
    setRenderProgress(8);
    setRenderMessage(
      targetHighlights.length > 1
        ? `총 ${targetHighlights.length}개 쇼츠 일괄 생성 시작 (1번째 쇼츠 준비 중)...`
        : "렌더링 세션 초기화 및 파라미터 검증 중..."
    );
    setCurrentStep(4);

    try {
      const res = await fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: src,
          highlights: targetHighlights,
          highlight: targetHighlights[0],
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

      // Subscribe to Server-Sent Events (SSE) with polling fallback
      let pollTimer: NodeJS.Timeout | null = null;
      const cleanUpStream = () => {
        if (pollTimer) clearInterval(pollTimer);
        eventSource.close();
      };

      const eventSource = new EventSource(`/api/jobs/${jobId}/events`);
      eventSource.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.progress !== undefined) {
            setRenderProgress((prev) => Math.max(prev, payload.progress));
          }
          if (payload.message) setRenderMessage(payload.message);

          if (payload.status === "completed") {
            cleanUpStream();
            setIsRendering(false);
            const results = payload.results || (payload.result ? [payload.result] : []);
            setBatchResults(results);
            setSelectedBatchIdx(0);
            if (results.length > 0) {
              setRenderedResult(results[0]);
            }
            fetchStatusAndData();
          } else if (payload.status === "failed") {
            cleanUpStream();
            setIsRendering(false);
            setErrorMsg(`렌더링 실패: ${payload.error}`);
          }
        } catch (e) {
          console.error("Render SSE parse error", e);
        }
      };

      eventSource.onerror = () => {
        // Do not immediately close on transient SSE errors; polling fallback handles it
      };

      // Safety net polling every 1.5s
      pollTimer = setInterval(async () => {
        try {
          const pollRes = await fetch(`/api/jobs/${jobId}`);
          if (!pollRes.ok) return;
          const pollData = await pollRes.json();
          if (pollData.progress !== undefined) {
            setRenderProgress((prev) => Math.max(prev, pollData.progress));
          }
          if (pollData.message) setRenderMessage(pollData.message);

          if (pollData.status === "completed") {
            cleanUpStream();
            setIsRendering(false);
            const results = pollData.results || (pollData.result ? [pollData.result] : []);
            setBatchResults(results);
            setSelectedBatchIdx(0);
            if (results.length > 0) {
              setRenderedResult(results[0]);
            }
            fetchStatusAndData();
          } else if (pollData.status === "failed") {
            cleanUpStream();
            setIsRendering(false);
            setErrorMsg(`렌더링 실패: ${pollData.error}`);
          }
        } catch {
          // Ignore transient poll errors
        }
      }, 1500);
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
      try {
        previewVideoRef.current.currentTime = hl.start_time;
        const playPromise = previewVideoRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => setIsPreviewPlaying(true))
            .catch(() => setIsPreviewPlaying(false));
        }
      } catch (err) {
        console.error("Preview video playback error:", err);
      }
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
                        onSelect={() => {
                          setSelectedTemplateId(tpl.id);
                          setAspectRatio("9:16");
                        }}
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
                        <span>📱 9:16 세로 (쇼츠 템플릿)</span>
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
                        <span>🖥️ 16:9 가로 (와이드)</span>
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
                  <div className="glass-panel p-8 md:p-10 rounded-2xl border border-slate-800/80 flex flex-col gap-8 shadow-2xl relative overflow-hidden">
                    {/* Background subtle glow */}
                    <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -z-0" />
                    <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none -z-0" />

                    {/* Header with Live Badge & Overall Progress */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80 relative z-10">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs font-semibold animate-pulse">
                            <span className="w-2 h-2 rounded-full bg-emerald-400" />
                            AI 파이프라인 실시간 가동 중
                          </span>
                          <span className="text-xs text-slate-400 font-mono">
                            large-v3-turbo &bull; qwen2.5:14b
                          </span>
                        </div>
                        <h3 className="text-xl md:text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
                          <Sparkles className="w-6 h-6 text-amber-400" />
                          AI 바이럴 하이라이트 심층 분석 중
                        </h3>
                        <p className="text-xs text-slate-400 mt-1">
                          영상의 음성, 맥락, 감정선, 정보 가치를 다차원으로 분석하여 최적의 쇼츠 구간을 도출합니다.
                        </p>
                      </div>

                      <div className="flex flex-col md:items-end justify-center min-w-[140px]">
                        <div className="flex items-baseline gap-1">
                          <span className="text-3xl md:text-4xl font-mono font-black bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-400 bg-clip-text text-transparent">
                            {analyzeProgress}%
                          </span>
                          <span className="text-xs font-mono text-slate-400 uppercase">완료</span>
                        </div>
                        <span className="text-[11px] text-slate-400">전체 4단계 파이프라인</span>
                      </div>
                    </div>

                    {/* Live Processing Action Card */}
                    <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 md:p-5 flex items-center gap-4 relative z-10 shadow-inner">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500/20 to-indigo-500/20 border border-indigo-500/40 flex items-center justify-center shrink-0">
                        <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-[11px] font-mono text-indigo-300 font-semibold uppercase tracking-wider mb-0.5">
                          현재 처리 중인 단계
                        </div>
                        <div className="text-sm md:text-base font-bold text-white truncate">
                          {analyzeMessage}
                        </div>
                      </div>
                    </div>

                    {/* Main Progress Bar */}
                    <div className="space-y-1 relative z-10">
                      <div className="w-full bg-slate-900 rounded-full h-3 p-0.5 border border-slate-800 overflow-hidden shadow-inner">
                        <div
                          className="bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 h-full rounded-full transition-all duration-300 shadow-md shadow-indigo-500/40"
                          style={{ width: `${analyzeProgress}%` }}
                        />
                      </div>
                    </div>

                    {/* 4-Step Visual Stepper Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 relative z-10">
                      {[
                        {
                          stepNum: 1,
                          title: "소스 준비 & 다운로드",
                          desc: "스트림 캐싱 및 오디오 분리",
                          icon: Download,
                          isDone: analyzeProgress >= 27,
                          isActive: analyzeProgress < 27,
                          rangeText: "0% ~ 26%",
                        },
                        {
                          stepNum: 2,
                          title: "Whisper 음성 인식",
                          desc: "단어 단위 발화 싱크 추출",
                          icon: AudioLines,
                          isDone: analyzeProgress >= 65,
                          isActive: analyzeProgress >= 27 && analyzeProgress < 65,
                          rangeText: "27% ~ 64%",
                        },
                        {
                          stepNum: 3,
                          title: "문맥 분석 & OpusClip 채점",
                          desc: "4기둥 채점 및 어미 경계 스냅",
                          icon: Cpu,
                          isDone: analyzeProgress >= 90,
                          isActive: analyzeProgress >= 65 && analyzeProgress < 90,
                          rangeText: "65% ~ 89%",
                        },
                        {
                          stepNum: 4,
                          title: "하이라이트 & 훅 확정",
                          desc: "2026 CTR 훅 타이틀 도출",
                          icon: Flame,
                          isDone: analyzeProgress >= 100,
                          isActive: analyzeProgress >= 90,
                          rangeText: "90% ~ 100%",
                        },
                      ].map((s) => {
                        const Icon = s.icon;
                        return (
                          <div
                            key={s.stepNum}
                            className={`p-4 rounded-xl border transition-all flex flex-col justify-between min-h-[110px] ${
                              s.isActive
                                ? "bg-slate-900/90 border-indigo-500 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500/50"
                                : s.isDone
                                ? "bg-emerald-950/20 border-emerald-500/40"
                                : "bg-slate-950/40 border-slate-800/60 opacity-60"
                            }`}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span
                                className={`text-[10px] font-mono px-2 py-0.5 rounded-md font-bold ${
                                  s.isActive
                                    ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                                    : s.isDone
                                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                    : "bg-slate-800 text-slate-500 border border-slate-700"
                                }`}
                              >
                                STEP {s.stepNum}
                              </span>

                              {s.isDone ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                              ) : s.isActive ? (
                                <span className="flex items-center gap-1 text-[11px] font-semibold text-indigo-400">
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                  처리 중
                                </span>
                              ) : (
                                <Clock className="w-3.5 h-3.5 text-slate-600" />
                              )}
                            </div>

                            <div>
                              <div className="flex items-center gap-1.5 font-bold text-xs text-white">
                                <Icon
                                  className={`w-3.5 h-3.5 ${
                                    s.isActive
                                      ? "text-indigo-400"
                                      : s.isDone
                                      ? "text-emerald-400"
                                      : "text-slate-500"
                                  }`}
                                />
                                <span>{s.title}</span>
                              </div>
                              <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">{s.desc}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Informative Tip Footer */}
                    <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/60 text-xs text-slate-400 flex items-center gap-2.5 relative z-10">
                      <Zap className="w-4 h-4 text-amber-400 shrink-0" />
                      <span>
                        <strong className="text-slate-300">스마트 경계 스냅: </strong>
                        대화 중간에 어색하게 끊기지 않도록 한국어 문법 종결어미(~다, ~요, ~죠)와 오디오 룸톤(250ms)을 자동으로 정합합니다.
                      </span>
                    </div>
                  </div>
                ) : (
                  /* Analysis Completed: OpusClip Candidate Cards */
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left: Candidate List */}
                    <div className="lg:col-span-7 flex flex-col gap-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div>
                          <h2 className="text-lg font-bold text-white flex items-center gap-2">
                            <Flame className="w-5 h-5 text-amber-500" />
                            AI 바이럴 하이라이트 후보 ({highlights.length}개 발견)
                          </h2>
                          <p className="text-xs text-slate-400 mt-1">
                            OpusClip 4기둥 바이럴 점수가 가장 높은 구간 순으로 추천되었습니다.
                          </p>
                        </div>

                        {highlights.length > 0 && (
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => {
                                if (selectedHighlightIds.length === highlights.length) {
                                  setSelectedHighlightIds([]);
                                } else {
                                  setSelectedHighlightIds(highlights.map((h) => h.id));
                                }
                              }}
                              className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition flex items-center gap-1.5"
                            >
                              <Check className="w-3.5 h-3.5" />
                              {selectedHighlightIds.length === highlights.length ? "전체 해제" : "후보 전체 선택"}
                            </button>
                            <span className="text-xs font-semibold px-2 py-1 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                              {selectedHighlightIds.length}개 선택됨
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Prominent Batch Render CTA Banner */}
                      {highlights.length > 0 && (
                        <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 via-rose-500/10 to-indigo-500/10 border border-indigo-500/30 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-lg">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-rose-500 flex items-center justify-center text-white shadow-md shadow-amber-500/30 shrink-0">
                              <Sparkles className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="text-xs font-bold text-white flex items-center gap-1.5">
                                <span>추천 쇼츠 일괄 생성 모드</span>
                                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-mono">
                                  {selectedHighlightIds.length}개 일괄
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-400 mt-0.5">
                                체크된 후보 쇼츠들을 한 번에 연속 렌더링하고 각각의 SEO 패키지까지 완성합니다.
                              </p>
                            </div>
                          </div>

                          <button
                            type="button"
                            onClick={() => handleStartRender("batch")}
                            disabled={selectedHighlightIds.length === 0}
                            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:opacity-95 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-rose-500/30 transition disabled:opacity-50 shrink-0"
                          >
                            <Flame className="w-4 h-4 fill-current" />
                            선택된 {selectedHighlightIds.length}개 쇼츠 모두 일괄 생성
                          </button>
                        </div>
                      )}

                      <div className="flex flex-col gap-3">
                        {highlights.map((hl) => {
                          const isSelected = selectedHighlight?.id === hl.id;
                          const isChecked = selectedHighlightIds.includes(hl.id);
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
                                  {/* Checkbox for batch selection */}
                                  <button
                                    type="button"
                                    title={isChecked ? "일괄 생성에서 제외" : "일괄 생성에 포함"}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setSelectedHighlightIds((prev) =>
                                        prev.includes(hl.id) ? prev.filter((id) => id !== hl.id) : [...prev, hl.id]
                                      );
                                    }}
                                    className={`w-6 h-6 rounded-lg flex items-center justify-center border transition ${
                                      isChecked
                                        ? "bg-indigo-600 border-indigo-400 text-white shadow-sm"
                                        : "bg-slate-900 border-slate-700 text-transparent hover:border-slate-500"
                                    }`}
                                  >
                                    <Check className="w-4 h-4 stroke-[3]" />
                                  </button>

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

                                  {isSelected && (
                                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1 font-semibold">
                                      <Play className="w-2.5 h-2.5 fill-current" />
                                      미리보기 선택됨
                                    </span>
                                  )}
                                </div>

                                <div className="flex items-center gap-2">
                                  <div className="text-xs font-mono text-slate-400 flex items-center gap-1">
                                    <Clock className="w-3.5 h-3.5" />
                                    {formatSeconds(hl.start_time)} ~ {formatSeconds(hl.end_time)} ({Math.round(hl.duration)}초)
                                  </div>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleSelectHighlightCandidate(hl);
                                    }}
                                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white transition"
                                    title="이 구간 영상 미리보기 재생"
                                  >
                                    <Play className="w-3.5 h-3.5 fill-current" />
                                  </button>
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

                        {effectiveStreamUrl ? (
                          <div className="space-y-2">
                            <div className="relative aspect-video bg-black rounded-xl overflow-hidden border border-slate-800">
                              <video
                                ref={previewVideoRef}
                                src={effectiveStreamUrl}
                                controls
                                playsInline
                                className="w-full h-full object-contain"
                                onTimeUpdate={(e) => {
                                  const current = (e.target as HTMLVideoElement).currentTime;
                                  if (previewTimeRange.end > 0 && current >= previewTimeRange.end) {
                                    (e.target as HTMLVideoElement).pause();
                                    setIsPreviewPlaying(false);
                                  }
                                }}
                                onPlay={() => setIsPreviewPlaying(true)}
                                onPause={() => setIsPreviewPlaying(false)}
                              />
                            </div>
                            <div className="flex items-center justify-between text-xs bg-slate-950/60 px-3 py-2 rounded-xl border border-slate-800">
                              <span className="text-slate-400 text-[11px]">
                                현재 구간: {formatSeconds(previewTimeRange.start)} ~ {formatSeconds(previewTimeRange.end)}
                              </span>
                              <button
                                type="button"
                                onClick={() => {
                                  if (previewVideoRef.current) {
                                    if (isPreviewPlaying) {
                                      previewVideoRef.current.pause();
                                      setIsPreviewPlaying(false);
                                    } else {
                                      previewVideoRef.current.currentTime = previewTimeRange.start;
                                      previewVideoRef.current.play().then(() => setIsPreviewPlaying(true)).catch(() => {});
                                    }
                                  }
                                }}
                                className="px-2.5 py-1 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 font-bold flex items-center gap-1 transition"
                              >
                                {isPreviewPlaying ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3 fill-current" />}
                                <span>{isPreviewPlaying ? "일시정지" : "선택구간 재생"}</span>
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="aspect-video bg-slate-950/60 rounded-xl border border-slate-800 flex flex-col items-center justify-center p-4 text-center">
                            <Video className="w-8 h-8 text-slate-600 mb-2" />
                            <span className="text-xs text-slate-400 font-medium">
                              영상 스트림을 로드하는 중입니다...
                            </span>
                            <span className="text-[11px] text-slate-500 mt-1">
                              (AI 분석이 완료되면 원본 영상 미리보기가 자동으로 연결됩니다)
                            </span>
                          </div>
                        )}

                        {selectedHighlight && (
                          <div className="flex flex-col gap-3 pt-2 border-t border-slate-800">
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-400">구간 세부 조정 (초)</span>
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
                                    📱 9:16 세로 (쇼츠 템플릿)
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
                                    🖥️ 16:9 가로 (와이드)
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

                            <div className="flex flex-col gap-2 pt-1">
                              <button
                                type="button"
                                onClick={() => handleStartRender("selected")}
                                className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center gap-2 border border-slate-700 transition"
                              >
                                <Scissors className="w-4 h-4 text-indigo-400" />
                                현재 선택된 #{selectedHighlight.id}번 구간만 단독 렌더링
                              </button>

                              <button
                                type="button"
                                onClick={() => handleStartRender("batch")}
                                disabled={selectedHighlightIds.length === 0}
                                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 via-violet-600 to-rose-600 hover:opacity-95 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
                              >
                                <Film className="w-4 h-4" />
                                🔥 추천된 {selectedHighlightIds.length}개 쇼츠 모두 일괄 생성하기 ({aspectRatio})
                              </button>
                            </div>
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
                  <div className="glass-panel p-8 md:p-10 rounded-2xl border border-slate-800/80 flex flex-col gap-8 shadow-2xl relative overflow-hidden">
                    {/* Background subtle glow */}
                    <div className="absolute top-0 right-1/4 w-96 h-96 bg-rose-500/10 rounded-full blur-3xl pointer-events-none -z-0" />
                    <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -z-0" />

                    {/* Header with Live Badge & Overall Progress */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80 relative z-10">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs font-semibold animate-pulse">
                            <span className="w-2 h-2 rounded-full bg-rose-400" />
                            실시간 비디오 합성 & 인코딩 가동 중
                          </span>
                          <span className="text-xs text-slate-400 font-mono">
                            {aspectRatio === "16:9" ? "1920x1080 Widescreen" : "1080x1920 Shorts"} &bull; -14 LUFS
                          </span>
                        </div>
                        <h3 className="text-xl md:text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
                          <Film className="w-6 h-6 text-rose-400" />
                          {aspectRatio === "16:9" ? "16:9 와이드 영상" : "9:16 모바일 쇼츠"} 렌더링 제작 중
                        </h3>
                        <p className="text-xs text-slate-400 mt-1">
                          선택한 템플릿과 자막 스타일을 적용하고 방송 규격 오디오로 인코딩합니다.
                        </p>
                      </div>

                      <div className="flex flex-col md:items-end justify-center min-w-[140px]">
                        <div className="flex items-baseline gap-1">
                          <span className="text-3xl md:text-4xl font-mono font-black bg-gradient-to-r from-rose-400 via-indigo-400 to-violet-400 bg-clip-text text-transparent">
                            {renderProgress}%
                          </span>
                          <span className="text-xs font-mono text-slate-400 uppercase">완료</span>
                        </div>
                        <span className="text-[11px] text-slate-400">전체 4단계 렌더링</span>
                      </div>
                    </div>

                    {/* Live Processing Action Card */}
                    <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 md:p-5 flex items-center gap-4 relative z-10 shadow-inner">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500/20 to-indigo-500/20 border border-rose-500/40 flex items-center justify-center shrink-0">
                        <Loader2 className="w-5 h-5 text-rose-400 animate-spin" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-[11px] font-mono text-rose-300 font-semibold uppercase tracking-wider mb-0.5">
                          현재 처리 중인 단계
                        </div>
                        <div className="text-sm md:text-base font-bold text-white truncate">
                          {renderMessage}
                        </div>
                      </div>
                    </div>

                    {/* Main Progress Bar */}
                    <div className="space-y-1 relative z-10">
                      <div className="w-full bg-slate-900 rounded-full h-3 p-0.5 border border-slate-800 overflow-hidden shadow-inner">
                        <div
                          className="bg-gradient-to-r from-rose-500 via-indigo-600 to-violet-600 h-full rounded-full transition-all duration-300 shadow-md shadow-rose-500/40"
                          style={{ width: `${renderProgress}%` }}
                        />
                      </div>
                    </div>

                    {/* 4-Step Visual Stepper Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 relative z-10">
                      {[
                        {
                          stepNum: 1,
                          title: "타임라인 동기화",
                          desc: "구간 컷 & 룸톤 패딩 보정",
                          icon: Scissors,
                          isDone: renderProgress >= 25,
                          isActive: renderProgress < 25,
                        },
                        {
                          stepNum: 2,
                          title: "비주얼 & 자막 렌더링",
                          desc: "캔버스 합성 및 키네틱 자막",
                          icon: Type,
                          isDone: renderProgress >= 70,
                          isActive: renderProgress >= 25 && renderProgress < 70,
                        },
                        {
                          stepNum: 3,
                          title: "FFmpeg 하드웨어 인코딩",
                          desc: "H.264 인코딩 & -14 LUFS 정규화",
                          icon: Cpu,
                          isDone: renderProgress >= 90,
                          isActive: renderProgress >= 70 && renderProgress < 90,
                        },
                        {
                          stepNum: 4,
                          title: "SEO 패키지 & 커버 완성",
                          desc: "유튜브 메타데이터 & 썸네일",
                          icon: Sparkles,
                          isDone: renderProgress >= 100,
                          isActive: renderProgress >= 90,
                        },
                      ].map((s) => {
                        const Icon = s.icon;
                        return (
                          <div
                            key={s.stepNum}
                            className={`p-4 rounded-xl border transition-all flex flex-col justify-between min-h-[110px] ${
                              s.isActive
                                ? "bg-slate-900/90 border-rose-500 shadow-lg shadow-rose-500/10 ring-1 ring-rose-500/50"
                                : s.isDone
                                ? "bg-emerald-950/20 border-emerald-500/40"
                                : "bg-slate-950/40 border-slate-800/60 opacity-60"
                            }`}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span
                                className={`text-[10px] font-mono px-2 py-0.5 rounded-md font-bold ${
                                  s.isActive
                                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                    : s.isDone
                                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                    : "bg-slate-800 text-slate-500 border border-slate-700"
                                }`}
                              >
                                STEP {s.stepNum}
                              </span>

                              {s.isDone ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                              ) : s.isActive ? (
                                <span className="flex items-center gap-1 text-[11px] font-semibold text-rose-400">
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                  인코딩 중
                                </span>
                              ) : (
                                <Clock className="w-3.5 h-3.5 text-slate-600" />
                              )}
                            </div>

                            <div>
                              <div className="flex items-center gap-1.5 font-bold text-xs text-white">
                                <Icon
                                  className={`w-3.5 h-3.5 ${
                                    s.isActive
                                      ? "text-rose-400"
                                      : s.isDone
                                      ? "text-emerald-400"
                                      : "text-slate-500"
                                  }`}
                                />
                                <span>{s.title}</span>
                              </div>
                              <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">{s.desc}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Informative Tip Footer */}
                    <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/60 text-xs text-slate-400 flex items-center gap-2.5 relative z-10">
                      <Volume2 className="w-4 h-4 text-rose-400 shrink-0" />
                      <span>
                        <strong className="text-slate-300">-14 LUFS 오디오 표준화: </strong>
                        유튜브 알고리즘 및 모바일 환경에 최적화된 음압 정규화를 적용하여 소리가 찢어지지 않고 선명하게 전달됩니다.
                      </span>
                    </div>
                  </div>
                ) : renderedResult ? (
                  /* Finished Shorts Result View */
                  <div className="flex flex-col gap-6">
                    {/* Batch Results Navigation Bar if multiple shorts generated */}
                    {batchResults.length > 1 && (
                      <div className="glass-panel p-4 rounded-2xl border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">
                            <Sparkles className="w-4 h-4" />
                          </div>
                          <div>
                            <span className="text-xs font-bold text-white flex items-center gap-1.5">
                              일괄 생성 완료 ({batchResults.length}개 쇼츠 제작됨)
                            </span>
                            <p className="text-[11px] text-slate-400">
                              쇼츠 탭을 클릭하여 각 쇼츠의 영상 미리보기와 개별 SEO 메타데이터를 전환하세요.
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 overflow-x-auto pb-1 max-w-full">
                          {batchResults.map((item, idx) => {
                            const isCurrent =
                              (renderedResult?.filename === item.filename) ||
                              (selectedBatchIdx === idx);
                            return (
                              <button
                                key={item.filename || idx}
                                type="button"
                                onClick={() => {
                                  setSelectedBatchIdx(idx);
                                  setRenderedResult(item);
                                }}
                                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 ${
                                  isCurrent
                                    ? "bg-gradient-to-r from-rose-600 via-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/30 ring-2 ring-indigo-400"
                                    : "bg-slate-900 text-slate-300 hover:text-white border border-slate-800 hover:border-slate-700"
                                }`}
                              >
                                <Flame className="w-3.5 h-3.5 text-amber-400" />
                                <span>쇼츠 #{item.id || idx + 1}</span>
                                {item.virality_score && (
                                  <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-black/40 text-amber-300 font-mono">
                                    {item.virality_score}점
                                  </span>
                                )}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}

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
                </div>
              ) : null}
              </div>
            )}
          </div>
        )}

        {/* VIEW 2: OUTPUTS GALLERY */}
        {activeTab === "gallery" && (() => {
          const filteredOutputs = outputs.filter((out) => {
            if (gallerySearch.trim()) {
              const q = gallerySearch.toLowerCase();
              const matchName = out.filename.toLowerCase().includes(q);
              const matchTitle = (out.title || "").toLowerCase().includes(q);
              const matchTags = (out.tags || []).some((t) => t.toLowerCase().includes(q));
              if (!matchName && !matchTitle && !matchTags) return false;
            }
            if (galleryFilter === "9:16" && out.aspect_ratio !== "9:16") return false;
            if (galleryFilter === "16:9" && out.aspect_ratio !== "16:9") return false;
            return true;
          });

          const totalStorageMb = outputs.reduce((acc, cur) => acc + cur.size_mb, 0);

          return (
            <div className="flex flex-col gap-6">
              {/* Header & Stats Dashboard */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-black text-white flex items-center gap-2.5">
                    <FolderOpen className="w-6 h-6 text-amber-400" />
                    생성된 쇼츠 보관함
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      {outputs.length}개
                    </span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    완성된 쇼츠 영상과 2026 알고리즘 최적화 SEO 업로드 가이드를 확인하고 원클릭으로 다운로드하세요.
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <div className="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
                    <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
                    <span>
                      총 저장 용량: <strong className="text-white font-bold">{totalStorageMb.toFixed(1)} MB</strong>
                    </span>
                  </div>

                  <button
                    onClick={fetchStatusAndData}
                    className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
                    title="새로고침"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>

                  <button
                    onClick={handleOpenFinder}
                    className="flex items-center gap-1.5 text-xs bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white font-bold px-4 py-2.5 rounded-xl shadow-md transition"
                  >
                    <FolderOpen className="w-3.5 h-3.5" />
                    Finder 폴더 열기
                  </button>
                </div>
              </div>

              {/* Filter, Search & View Mode Toolbar */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
                {/* Search */}
                <div className="relative flex-1 max-w-md">
                  <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="제목, 파일명, 해시태그 검색..."
                    value={gallerySearch}
                    onChange={(e) => setGallerySearch(e.target.value)}
                    className="w-full bg-slate-950/90 border border-slate-800 rounded-xl pl-9 pr-8 py-2 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                  {gallerySearch && (
                    <button
                      onClick={() => setGallerySearch("")}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Filters & View Switcher */}
                <div className="flex items-center gap-2 justify-between sm:justify-end">
                  {/* Aspect Ratio Filter */}
                  <div className="flex items-center p-1 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                    <button
                      onClick={() => setGalleryFilter("all")}
                      className={`px-3 py-1 rounded-lg font-bold transition text-[11px] ${
                        galleryFilter === "all"
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      전체 ({outputs.length})
                    </button>
                    <button
                      onClick={() => setGalleryFilter("9:16")}
                      className={`px-3 py-1 rounded-lg font-bold transition text-[11px] ${
                        galleryFilter === "9:16"
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      📱 9:16 세로
                    </button>
                    <button
                      onClick={() => setGalleryFilter("16:9")}
                      className={`px-3 py-1 rounded-lg font-bold transition text-[11px] ${
                        galleryFilter === "16:9"
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      🖥️ 16:9 가로
                    </button>
                  </div>

                  {/* View Mode */}
                  <div className="flex items-center p-1 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                    <button
                      onClick={() => setGalleryViewMode("grid")}
                      className={`p-1.5 rounded-lg transition ${
                        galleryViewMode === "grid"
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                      title="📱 쇼츠 그리드 뷰 (9:16 갤러리 피드)"
                    >
                      <Grid className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setGalleryViewMode("feed")}
                      className={`p-1.5 rounded-lg transition ${
                        galleryViewMode === "feed"
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                      title="📋 상세 리스트 뷰 (비디오 + SEO 가이드)"
                    >
                      <List className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Gallery Content */}
              {outputs.length === 0 ? (
                <div className="glass-panel p-16 rounded-2xl border border-slate-800 text-center flex flex-col items-center justify-center gap-4">
                  <Film className="w-12 h-12 text-slate-600" />
                  <div>
                    <h3 className="text-sm font-bold text-slate-300">아직 생성된 쇼츠가 없습니다</h3>
                    <p className="text-xs text-slate-500 mt-1">스튜디오에서 첫 번째 쇼츠를 만들어 보세요!</p>
                  </div>
                  <button
                    onClick={() => setActiveTab("studio")}
                    className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition"
                  >
                    쇼츠 제작 시작
                  </button>
                </div>
              ) : filteredOutputs.length === 0 ? (
                <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center flex flex-col items-center justify-center gap-3 text-slate-400">
                  <Search className="w-8 h-8 text-slate-600" />
                  <p className="text-xs">검색 조건에 맞는 영상이 없습니다.</p>
                  <button
                    onClick={() => {
                      setGallerySearch("");
                      setGalleryFilter("all");
                    }}
                    className="text-xs text-indigo-400 hover:underline"
                  >
                    필터 초기화
                  </button>
                </div>
              ) : galleryViewMode === "grid" ? (
                /* VIEW MODE 1: SHORTS GRID (Native 9:16 vertical cards with no letterbox voids) */
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                  {filteredOutputs.map((out) => {
                    const isLandscape = out.aspect_ratio === "16:9";
                    return (
                      <div
                        key={out.filename}
                        className="glass-card rounded-2xl border border-slate-800/80 overflow-hidden flex flex-col justify-between group hover:border-indigo-500/50 hover:shadow-xl hover:shadow-indigo-500/10 transition-all hover:-translate-y-1"
                      >
                        {/* 9:16 Media Container */}
                        <div
                          onClick={() => setPreviewModalOutput(out)}
                          className={`relative cursor-pointer bg-slate-950 overflow-hidden ${
                            isLandscape ? "aspect-video" : "aspect-[9/16]"
                          }`}
                        >
                          {out.cover_url ? (
                            <img
                              src={out.cover_url}
                              alt={out.title || out.filename}
                              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                            />
                          ) : (
                            <video
                              src={out.stream_url}
                              className="w-full h-full object-cover"
                              preload="metadata"
                            />
                          )}

                          {/* Hover Play Button Overlay */}
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <div className="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform">
                              <Play className="w-5 h-5 fill-white ml-0.5" />
                            </div>
                          </div>

                          {/* Floating Badges */}
                          <div className="absolute top-2 left-2 flex items-center gap-1 z-10">
                            <span className="px-1.5 py-0.5 rounded-md text-[10px] font-bold bg-black/70 text-slate-200 backdrop-blur-md border border-white/10">
                              {isLandscape ? "🖥️ 16:9" : "📱 9:16"}
                            </span>
                          </div>

                          {out.virality_score && (
                            <div className="absolute top-2 right-2 z-10">
                              <span className="px-1.5 py-0.5 rounded-md text-[10px] font-extrabold bg-gradient-to-r from-amber-500 to-rose-500 text-white shadow-md flex items-center gap-0.5">
                                <Flame className="w-3 h-3 fill-white" />
                                {out.virality_score}점
                              </span>
                            </div>
                          )}

                          {/* Bottom Gradient with Duration & Size */}
                          <div className="absolute inset-x-0 bottom-0 p-2 pt-6 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-center justify-between text-[10px] text-slate-300 font-medium">
                            <span>{out.duration ? `${out.duration}초` : `${out.size_mb} MB`}</span>
                            <span>{out.size_mb} MB</span>
                          </div>
                        </div>

                        {/* Card Info & Actions */}
                        <div className="p-3 flex flex-col justify-between flex-1 gap-2">
                          <div>
                            <h4
                              className="font-bold text-xs text-white line-clamp-2 leading-snug group-hover:text-indigo-300 transition"
                              title={out.title || out.filename}
                            >
                              {out.title || out.filename}
                            </h4>
                            <p className="text-[10px] text-slate-500 mt-1">
                              {new Date(out.modified_at * 1000).toLocaleDateString()}
                            </p>
                          </div>

                          <div className="flex items-center gap-1.5 pt-1 border-t border-slate-800/60">
                            <button
                              onClick={() => setPreviewModalOutput(out)}
                              className="flex-1 py-1.5 px-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-[11px] font-bold flex items-center justify-center gap-1 transition"
                              title="재생 및 SEO 확인"
                            >
                              <Play className="w-3 h-3 fill-indigo-300" />
                              재생
                            </button>

                            <a
                              href={out.stream_url}
                              download={out.filename}
                              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
                              title="영상 다운로드"
                            >
                              <Download className="w-3.5 h-3.5" />
                            </a>

                            {out.seo_content && (
                              <button
                                onClick={() => copyToClipboard(out.seo_content || "", out.filename)}
                                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
                                title="SEO 설명글 복사"
                              >
                                {copiedKey === out.filename ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                /* VIEW MODE 2: DETAILED FEED (Horizontal Split Card with snug 9:16 player + rich SEO) */
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
                  {filteredOutputs.map((out) => {
                    const isLandscape = out.aspect_ratio === "16:9";
                    return (
                      <div
                        key={out.filename}
                        className="glass-card rounded-2xl border border-slate-800/80 p-4 flex flex-col sm:flex-row gap-4 hover:border-slate-700 transition"
                      >
                        {/* Left Video / Cover (No black side voids!) */}
                        <div
                          onClick={() => setPreviewModalOutput(out)}
                          className={`relative shrink-0 cursor-pointer rounded-xl overflow-hidden bg-slate-950 border border-slate-800 group shadow-md ${
                            isLandscape
                              ? "w-full sm:w-[240px] aspect-video"
                              : "w-full sm:w-[170px] aspect-[9/16]"
                          }`}
                        >
                          {out.cover_url ? (
                            <img
                              src={out.cover_url}
                              alt={out.title || out.filename}
                              className="w-full h-full object-cover transition-transform group-hover:scale-105"
                            />
                          ) : (
                            <video
                              src={out.stream_url}
                              className="w-full h-full object-cover"
                              preload="metadata"
                            />
                          )}

                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-lg">
                              <Play className="w-4 h-4 fill-white ml-0.5" />
                            </div>
                          </div>

                          <div className="absolute top-2 left-2 z-10">
                            <span className="px-1.5 py-0.5 rounded-md text-[10px] font-bold bg-black/70 text-slate-200 backdrop-blur-md border border-white/10">
                              {isLandscape ? "🖥️ 16:9" : "📱 9:16"}
                            </span>
                          </div>

                          {out.virality_score && (
                            <div className="absolute top-2 right-2 z-10">
                              <span className="px-1.5 py-0.5 rounded-md text-[10px] font-extrabold bg-gradient-to-r from-amber-500 to-rose-500 text-white shadow-md flex items-center gap-0.5">
                                <Flame className="w-3 h-3 fill-white" />
                                {out.virality_score}점
                              </span>
                            </div>
                          )}

                          <div className="absolute inset-x-0 bottom-0 p-2 bg-gradient-to-t from-black/90 to-transparent flex items-center justify-between text-[10px] text-slate-300 font-medium">
                            <span>{out.duration ? `${out.duration}초` : ""}</span>
                            <span>{out.size_mb} MB</span>
                          </div>
                        </div>

                        {/* Right Rich Metadata & SEO */}
                        <div className="flex-1 flex flex-col justify-between min-w-0 gap-3">
                          <div>
                            <div className="flex items-start justify-between gap-2">
                              <h4
                                onClick={() => setPreviewModalOutput(out)}
                                className="font-bold text-sm text-white hover:text-indigo-300 cursor-pointer line-clamp-2 leading-snug transition"
                              >
                                {out.title || out.filename}
                              </h4>
                            </div>

                            <p className="text-[11px] text-slate-500 font-mono mt-1 truncate" title={out.filename}>
                              {out.filename}
                            </p>

                            {/* Meta Tags Row */}
                            <div className="flex items-center gap-2 flex-wrap text-[11px] text-slate-400 mt-2">
                              <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                                {isLandscape ? "🖥️ 16:9 가로" : "📱 9:16 세로"}
                              </span>
                              {out.duration ? (
                                <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                                  ⏱️ {out.duration}초
                                </span>
                              ) : null}
                              <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                                💾 {out.size_mb} MB
                              </span>
                              <span className="text-slate-500">
                                📅 {new Date(out.modified_at * 1000).toLocaleDateString()}
                              </span>
                            </div>

                            {/* Hashtags Preview */}
                            {out.tags && out.tags.length > 0 && (
                              <div className="flex items-center gap-1.5 flex-wrap mt-2.5">
                                {out.tags.map((tag) => (
                                  <span
                                    key={tag}
                                    onClick={() => copyToClipboard(tag, tag)}
                                    className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 hover:bg-indigo-500/20 cursor-pointer transition flex items-center gap-1"
                                    title="클릭하여 태그 복사"
                                  >
                                    <Tag className="w-2.5 h-2.5" />
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* Action Toolbar */}
                          <div className="flex items-center gap-2 pt-2 border-t border-slate-800/80">
                            <button
                              onClick={() => setPreviewModalOutput(out)}
                              className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 transition shadow-sm"
                            >
                              <Play className="w-3.5 h-3.5 fill-white" />
                              시네마 재생
                            </button>

                            <a
                              href={out.stream_url}
                              download={out.filename}
                              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold flex items-center gap-1.5 transition"
                            >
                              <Download className="w-3.5 h-3.5" />
                              다운로드
                            </a>

                            {out.seo_content && (
                              <button
                                onClick={() => copyToClipboard(out.seo_content || "", out.filename)}
                                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold flex items-center gap-1.5 transition"
                                title="유튜브 업로드용 제목/설명/태그 전체 복사"
                              >
                                {copiedKey === out.filename ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                                SEO 가이드 복사
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* CINEMA PLAYER & SEO MODAL */}
              {previewModalOutput && (
                <div
                  className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200"
                  onClick={() => setPreviewModalOutput(null)}
                >
                  <div
                    className="glass-panel w-full max-w-4xl max-h-[92vh] rounded-3xl border border-slate-700 p-6 flex flex-col gap-5 overflow-hidden shadow-2xl relative"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {/* Modal Header */}
                    <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                      <div className="min-w-0 pr-4">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            {previewModalOutput.aspect_ratio === "16:9" ? "🖥️ 16:9 가로" : "📱 9:16 세로"}
                          </span>
                          {previewModalOutput.virality_score && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                              <Flame className="w-3 h-3 fill-amber-300" />
                              바이럴 {previewModalOutput.virality_score}점
                            </span>
                          )}
                        </div>
                        <h3 className="text-base font-bold text-white truncate mt-1">
                          {previewModalOutput.title || previewModalOutput.filename}
                        </h3>
                      </div>

                      <button
                        onClick={() => setPreviewModalOutput(null)}
                        className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Modal Body: Split Video Player + SEO Details */}
                    <div className="flex flex-col md:flex-row gap-6 overflow-y-auto pr-1">
                      {/* Video Player */}
                      <div className="w-full md:w-[320px] shrink-0 flex items-center justify-center bg-black/90 rounded-2xl overflow-hidden border border-slate-800 shadow-xl">
                        <video
                          src={previewModalOutput.stream_url}
                          controls
                          autoPlay
                          className="w-full max-h-[60vh] object-contain"
                        />
                      </div>

                      {/* SEO Guide & Download Pane */}
                      <div className="flex-1 flex flex-col justify-between gap-4">
                        <div className="flex flex-col gap-3">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                              <Sparkles className="w-4 h-4 text-amber-400" />
                              2026 알고리즘 최적화 유튜브 업로드 가이드
                            </span>
                            {previewModalOutput.seo_content && (
                              <button
                                onClick={() => copyToClipboard(previewModalOutput.seo_content || "", "modal_full")}
                                className="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold flex items-center gap-1 transition"
                              >
                                {copiedKey === "modal_full" ? (
                                  <Check className="w-3 h-3 text-white" />
                                ) : (
                                  <Copy className="w-3 h-3" />
                                )}
                                전체 복사
                              </button>
                            )}
                          </div>

                          {previewModalOutput.seo_content ? (
                            <pre className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-300 text-[11px] font-mono leading-relaxed whitespace-pre-wrap max-h-[38vh] overflow-y-auto">
                              {previewModalOutput.seo_content}
                            </pre>
                          ) : (
                            <div className="p-6 rounded-xl bg-slate-950/80 border border-slate-800 text-center text-xs text-slate-500">
                              메타데이터 파일이 생성되지 않은 이전 영상입니다.
                            </div>
                          )}

                          {previewModalOutput.tags && previewModalOutput.tags.length > 0 && (
                            <div className="flex items-center gap-1.5 flex-wrap">
                              {previewModalOutput.tags.map((tag) => (
                                <span
                                  key={tag}
                                  onClick={() => copyToClipboard(tag, `modal_${tag}`)}
                                  className="px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-500/20 cursor-pointer transition flex items-center gap-1"
                                >
                                  <Tag className="w-3 h-3" />
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Modal Action Footer */}
                        <div className="flex items-center gap-3 pt-3 border-t border-slate-800">
                          <a
                            href={previewModalOutput.stream_url}
                            download={previewModalOutput.filename}
                            className="flex-1 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg transition"
                          >
                            <Download className="w-4 h-4" />
                            MP4 파일 다운로드 ({previewModalOutput.size_mb} MB)
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })()}
      </main>
    </div>
  );
}
