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
  ChevronDown,
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
  Music,
  Palette,
  ZoomIn,
  Smartphone,
  Target,
  Infinity,
  Image as ImageIcon,
  AlertTriangle,
  Lightbulb,
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
import SafeZoneOverlay, { SafeZonePlatform } from "@/components/SafeZoneOverlay";

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
  const [removeSubtitles, setRemoveSubtitles] = useState<boolean>(true);
  const [filterFillers, setFilterFillers] = useState<boolean>(true);

  // Pro Studio Quality Options (BGM, SFX, Color Grading, Dynamic Zoom, Smart Keywords, Keynote Stat Pill, Seamless Loop)
  const [studioOptionTab, setStudioOptionTab] = useState<"audio" | "visual" | "typography">("audio");
  const [bgmTrack, setBgmTrack] = useState<string>("auto");
  const [enableSfx, setEnableSfx] = useState<boolean>(true);
  const [colorGrade, setColorGrade] = useState<string>("vibrant_tech");
  const [dynamicZoom, setDynamicZoom] = useState<boolean>(true);
  const [smartKeywords, setSmartKeywords] = useState<boolean>(true);
  const [bounceAnimation, setBounceAnimation] = useState<boolean>(true);
  const [enableStatPill, setEnableStatPill] = useState<boolean>(true);
  const [seamlessLoop, setSeamlessLoop] = useState<boolean>(true);

  // Viral Retention & A/B Hook Testing
  const [selectedHookVariants, setSelectedHookVariants] = useState<Record<number, string>>({});
  const [safeZoneMode, setSafeZoneMode] = useState<SafeZonePlatform>("none");
  const [previewSafeZoneMode, setPreviewSafeZoneMode] = useState<SafeZonePlatform>("none");

  // Step 3: Analysis
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeProgress, setAnalyzeProgress] = useState(0);
  const [analyzeMessage, setAnalyzeMessage] = useState("");
  const [videoMeta, setVideoMeta] = useState<VideoMetadata | null>(null);
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [selectedHighlight, setSelectedHighlight] = useState<Highlight | null>(null);
  const [selectedHighlightIds, setSelectedHighlightIds] = useState<number[]>([]);
  const [transcriptSummary, setTranscriptSummary] = useState<{
    language?: string;
    duration?: number;
    duration_formatted?: string;
    segment_count?: number;
    total_words?: number;
    wpm_avg?: number;
    preview_segments?: Array<{ id: number; time: string; text: string }>;
  } | null>(null);
  const [showTranscriptDetails, setShowTranscriptDetails] = useState<boolean>(false);

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

  // Thumbnail Studio Editor state
  const [thumbEditorOpen, setThumbEditorOpen] = useState(false);
  const [thumbTargetOutput, setThumbTargetOutput] = useState<RenderedOutput | null>(null);
  const [thumbCandidates, setThumbCandidates] = useState<
    Array<{
      index: number;
      timestamp: number;
      offset_sec: number;
      file_path: string;
      preview_url: string;
    }>
  >([]);
  const [selectedCandidateIdx, setSelectedCandidateIdx] = useState<number>(0);
  const [thumbTitle, setThumbTitle] = useState("");
  const [thumbHook, setThumbHook] = useState("");
  const [thumbBadgeType, setThumbBadgeType] = useState<"warning" | "tip" | "fact" | "none">("warning");
  const [thumbBadgeLabel, setThumbBadgeLabel] = useState("긴급 대처법");
  const [thumbHeadlineStyle, setThumbHeadlineStyle] = useState<
    "yellow_on_black" | "black_on_yellow" | "white_on_red" | "white_on_black"
  >("yellow_on_black");
  const [thumbPunchlineStyle, setThumbPunchlineStyle] = useState<
    "white_on_black" | "yellow_on_black" | "black_on_yellow"
  >("white_on_black");
  const [thumbIsLoadingCandidates, setThumbIsLoadingCandidates] = useState(false);
  const [thumbIsRendering, setThumbIsRendering] = useState(false);
  const [thumbLivePreviewUrl, setThumbLivePreviewUrl] = useState<string | null>(null);

  const openThumbnailEditor = async (out: RenderedOutput) => {
    setThumbTargetOutput(out);
    const cleanT = (out.title || out.filename.replace("short_", "").replace(/\.[^/.]+$/, ""))
      .split("#")[0]
      .trim();
    const cleanH = (out.hook_text || "모르면 100% 갇힙니다").split("#")[0].trim();
    setThumbTitle(cleanT.slice(0, 16));
    setThumbHook(cleanH.slice(0, 16));
    setThumbBadgeType(out.virality_score && out.virality_score >= 85 ? "warning" : "tip");
    setThumbBadgeLabel(out.virality_score && out.virality_score >= 85 ? "긴급 대처법" : "핵심 꿀팁");
    setThumbHeadlineStyle("yellow_on_black");
    setThumbPunchlineStyle("white_on_black");
    setThumbLivePreviewUrl(out.cover_url || null);
    setSelectedCandidateIdx(0);
    setThumbEditorOpen(true);

    // Fetch candidate frames from video
    setThumbIsLoadingCandidates(true);
    try {
      const q = new URLSearchParams({
        video_path: out.filepath,
        duration: String(out.duration || 30),
        count: "4",
      });
      const res = await fetch(`/api/thumbnail/candidates?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        if (data.candidates && data.candidates.length > 0) {
          setThumbCandidates(data.candidates);
        }
      }
    } catch (e) {
      console.error("Failed to load thumbnail candidates:", e);
    } finally {
      setThumbIsLoadingCandidates(false);
    }
  };

  const handleRenderThumbnail = async (targetIdx?: number) => {
    if (!thumbTargetOutput) return;
    const activeIdx = targetIdx !== undefined ? targetIdx : selectedCandidateIdx;
    const cand = thumbCandidates[activeIdx];
    const targetTime = cand ? cand.timestamp : undefined;

    setThumbIsRendering(true);
    try {
      const payload = {
        video_path: thumbTargetOutput.filepath,
        title: thumbTitle,
        hook_text: thumbHook,
        badge_type: thumbBadgeType,
        badge_label: thumbBadgeLabel,
        headline_style: thumbHeadlineStyle,
        punchline_style: thumbPunchlineStyle,
        aspect_ratio: thumbTargetOutput.aspect_ratio || "9:16",
        target_time: targetTime,
      };

      const res = await fetch("/api/thumbnail/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.success && data.cover_url) {
          setThumbLivePreviewUrl(data.cover_url);
          // Sync with output card and preview modal
          setOutputs((prev) =>
            prev.map((o) =>
              o.filename === thumbTargetOutput.filename
                ? { ...o, cover_url: data.cover_url }
                : o
            )
          );
          setPreviewModalOutput((prev) =>
            prev && prev.filename === thumbTargetOutput.filename
              ? { ...prev, cover_url: data.cover_url }
              : prev
          );
        }
      }
    } catch (e) {
      console.error("Thumbnail render error:", e);
    } finally {
      setThumbIsRendering(false);
    }
  };

  // Background Task Persistence & Notification state
  const [completionToast, setCompletionToast] = useState<{
    title: string;
    message: string;
    count: number;
    type: "analyze" | "render";
  } | null>(null);

  useEffect(() => {
    if (completionToast) {
      const timer = setTimeout(() => {
        setCompletionToast(null);
      }, 9000);
      return () => clearTimeout(timer);
    }
  }, [completionToast]);

  // Initial Data Fetching
  const fetchStatusAndData = React.useCallback(async () => {
    try {
      const safeFetchJson = async (url: string) => {
        try {
          const r = await fetch(url);
          if (!r.ok) return null;
          return await r.json();
        } catch {
          return null;
        }
      };
      const [resStatus, resTpl, resRecent, resOutputs] = await Promise.all([
        safeFetchJson("/api/status"),
        safeFetchJson("/api/templates"),
        safeFetchJson("/api/recent-videos"),
        safeFetchJson("/api/outputs"),
      ]);
      if (resStatus) setSystemStatus(resStatus);
      if (resTpl?.templates) setTemplates(resTpl.templates);
      if (resRecent?.videos) setRecentVideos(resRecent.videos);
      if (resOutputs?.outputs) setOutputs(resOutputs.outputs);
    } catch (err) {
      console.warn("데이터 로딩 일시적 대기:", err);
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

  // Subscription handlers for background tasks with local persistence
  const activeAnalyzeStreamRef = useRef<{ cleanUp: () => void } | null>(null);
  const activeRenderStreamRef = useRef<{ cleanUp: () => void } | null>(null);

  const subscribeToAnalyzeJob = React.useCallback((jobId: string) => {
    if (activeAnalyzeStreamRef.current) {
      activeAnalyzeStreamRef.current.cleanUp();
    }

    setIsAnalyzing(true);
    let pollTimer: NodeJS.Timeout | null = null;
    let isCleanedUp = false;

    const cleanUpStream = () => {
      if (isCleanedUp) return;
      isCleanedUp = true;
      if (pollTimer) clearInterval(pollTimer);
      eventSource.close();
      activeAnalyzeStreamRef.current = null;
    };

    activeAnalyzeStreamRef.current = { cleanUp: cleanUpStream };

    const eventSource = new EventSource(`/api/jobs/${jobId}/events`);
    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.progress !== undefined) {
          setAnalyzeProgress((prev) => Math.max(prev, payload.progress));
        }
        if (payload.message) setAnalyzeMessage(payload.message);
        if (payload.video_metadata) setVideoMeta(payload.video_metadata);
        if (payload.transcript_summary) setTranscriptSummary(payload.transcript_summary);

        if (payload.status === "completed") {
          cleanUpStream();
          setIsAnalyzing(false);
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          if (payload.transcript_summary) {
            setTranscriptSummary(payload.transcript_summary);
          }
          const hlList = payload.highlights || [];
          setHighlights(hlList);
          if (hlList.length > 0) {
            const best = hlList[0];
            setSelectedHighlight(best);
            setSelectedHighlightIds(hlList.map((h: Highlight) => h.id));
            setPreviewTimeRange({ start: best.start_time, end: best.end_time });
          }
          setCompletionToast({
            title: "AI 하이라이트 분석 완료!",
            message: `총 ${hlList.length}개의 쇼츠 추천 구간을 도출했습니다.`,
            count: hlList.length,
            type: "analyze",
          });
          fetchStatusAndData();
        } else if (payload.status === "failed") {
          cleanUpStream();
          setIsAnalyzing(false);
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          setErrorMsg(`AI 분석 중 오류가 발생했습니다: ${payload.error}`);
        }
      } catch (e) {
        console.error("SSE parse error", e);
      }
    };

    eventSource.onerror = () => {
      // transient SSE errors handled by safety net polling
    };

    // Safety net polling fallback
    pollTimer = setInterval(async () => {
      try {
        const pollRes = await fetch(`/api/jobs/${jobId}`);
        if (!pollRes.ok) return;
        const pollData = await pollRes.json().catch(() => null);
        if (!pollData) return;
        if (pollData.progress !== undefined) {
          setAnalyzeProgress((prev) => Math.max(prev, pollData.progress));
        }
        if (pollData.message) setAnalyzeMessage(pollData.message);
        if (pollData.video_metadata) setVideoMeta(pollData.video_metadata);
        if (pollData.transcript_summary) setTranscriptSummary(pollData.transcript_summary);

        if (pollData.status === "completed") {
          cleanUpStream();
          setIsAnalyzing(false);
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          if (pollData.transcript_summary) setTranscriptSummary(pollData.transcript_summary);
          const hlList = pollData.highlights || [];
          setHighlights(hlList);
          if (hlList.length > 0) {
            const best = hlList[0];
            setSelectedHighlight(best);
            setSelectedHighlightIds(hlList.map((h: Highlight) => h.id));
            setPreviewTimeRange({ start: best.start_time, end: best.end_time });
          }
          setCompletionToast({
            title: "AI 하이라이트 분석 완료!",
            message: `총 ${hlList.length}개의 쇼츠 추천 구간을 도출했습니다.`,
            count: hlList.length,
            type: "analyze",
          });
          fetchStatusAndData();
        } else if (pollData.status === "failed") {
          cleanUpStream();
          setIsAnalyzing(false);
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          setErrorMsg(`AI 분석 중 오류가 발생했습니다: ${pollData.error}`);
        }
      } catch {
        // Ignore transient poll errors
      }
    }, 1500);
  }, [fetchStatusAndData]);

  const subscribeToRenderJob = React.useCallback((jobId: string) => {
    if (activeRenderStreamRef.current) {
      activeRenderStreamRef.current.cleanUp();
    }

    setIsRendering(true);
    let pollTimer: NodeJS.Timeout | null = null;
    let isCleanedUp = false;

    const cleanUpStream = () => {
      if (isCleanedUp) return;
      isCleanedUp = true;
      if (pollTimer) clearInterval(pollTimer);
      eventSource.close();
      activeRenderStreamRef.current = null;
    };

    activeRenderStreamRef.current = { cleanUp: cleanUpStream };

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
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          const results = payload.results || (payload.result ? [payload.result] : []);
          setBatchResults(results);
          setSelectedBatchIdx(0);
          if (results.length > 0) {
            setRenderedResult(results[0]);
          }
          setCompletionToast({
            title: "쇼츠 일괄 렌더링 완료!",
            message: `총 ${results.length}개의 쇼츠 제작이 완료되어 완성 보관함에 저장되었습니다.`,
            count: results.length,
            type: "render",
          });
          fetchStatusAndData();
        } else if (payload.status === "failed") {
          cleanUpStream();
          setIsRendering(false);
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          setErrorMsg(`렌더링 실패: ${payload.error}`);
        }
      } catch (e) {
        console.error("Render SSE parse error", e);
      }
    };

    eventSource.onerror = () => {
      // transient SSE errors handled by safety net polling
    };

    // Safety net polling fallback
    pollTimer = setInterval(async () => {
      try {
        const pollRes = await fetch(`/api/jobs/${jobId}`);
        if (!pollRes.ok) return;
        const pollData = await pollRes.json().catch(() => null);
        if (!pollData) return;
        if (pollData.progress !== undefined) {
          setRenderProgress((prev) => Math.max(prev, pollData.progress));
        }
        if (pollData.message) setRenderMessage(pollData.message);

        if (pollData.status === "completed") {
          cleanUpStream();
          setIsRendering(false);
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          const results = pollData.results || (pollData.result ? [pollData.result] : []);
          setBatchResults(results);
          setSelectedBatchIdx(0);
          if (results.length > 0) {
            setRenderedResult(results[0]);
          }
          setCompletionToast({
            title: "쇼츠 일괄 렌더링 완료!",
            message: `총 ${results.length}개의 쇼츠 제작이 완료되어 완성 보관함에 저장되었습니다.`,
            count: results.length,
            type: "render",
          });
          fetchStatusAndData();
        } else if (pollData.status === "failed") {
          cleanUpStream();
          setIsRendering(false);
          try {
            localStorage.removeItem("happy_active_job");
          } catch {}
          setErrorMsg(`렌더링 실패: ${pollData.error}`);
        }
      } catch {
        // Ignore transient poll errors
      }
    }, 1500);
  }, [fetchStatusAndData]);

  // Restore any background job running on page load/refresh
  useEffect(() => {
    try {
      const savedJobStr = localStorage.getItem("happy_active_job");
      if (!savedJobStr) return;
      const savedJob = JSON.parse(savedJobStr);
      if (!savedJob?.jobId || !savedJob?.type) return;

      fetch(`/api/jobs/${savedJob.jobId}`)
        .then((res) => (res.ok ? res.json() : null))
        .then((job) => {
          if (!job) {
            localStorage.removeItem("happy_active_job");
            return;
          }
          if (job.status === "running" || job.status === "pending") {
            if (savedJob.type === "analyze") {
              setAnalyzeProgress(job.progress || 10);
              setAnalyzeMessage(job.message || "AI 분석 세션 복원 중...");
              subscribeToAnalyzeJob(savedJob.jobId);
            } else if (savedJob.type === "render") {
              setRenderProgress(job.progress || 10);
              setRenderMessage(job.message || "쇼츠 렌더링 세션 복원 중...");
              subscribeToRenderJob(savedJob.jobId);
            }
          } else if (job.status === "completed") {
            localStorage.removeItem("happy_active_job");
            if (savedJob.type === "analyze") {
              if (job.transcript_summary) setTranscriptSummary(job.transcript_summary);
              const hlList = job.highlights || [];
              setHighlights(hlList);
              if (hlList.length > 0) {
                setSelectedHighlight(hlList[0]);
                setSelectedHighlightIds(hlList.map((h: Highlight) => h.id));
              }
            } else if (savedJob.type === "render") {
              const results = job.results || (job.result ? [job.result] : []);
              setBatchResults(results);
              setSelectedBatchIdx(0);
              if (results.length > 0) setRenderedResult(results[0]);
            }
          } else {
            localStorage.removeItem("happy_active_job");
          }
        })
        .catch(() => {
          localStorage.removeItem("happy_active_job");
        });
    } catch {
      // ignore localStorage errors
    }
  }, [subscribeToAnalyzeJob, subscribeToRenderJob]);

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

      if (!res.ok) {
        let errText = `서버 응답 오류 (${res.status})`;
        try {
          const errData = await res.json();
          errText = errData.detail || errData.message || errText;
        } catch {
          const rawText = await res.text();
          if (rawText) errText = rawText;
        }
        throw new Error(errText);
      }

      const data = await res.json();
      const jobId = data.job_id;

      try {
        localStorage.setItem(
          "happy_active_job",
          JSON.stringify({ jobId, type: "analyze", startTime: Date.now() })
        );
      } catch {}

      subscribeToAnalyzeJob(jobId);
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

    const targetHighlightsWithVariants = targetHighlights.map((h) => {
      const chosenVar = selectedHookVariants[h.id];
      let hook = h.hook_text;
      if (chosenVar && chosenVar !== "default" && h.hook_variants) {
        const v = (h.hook_variants as Record<string, string | undefined>)[chosenVar];
        if (v) hook = v;
      }
      return {
        ...h,
        hook_text: hook,
      };
    });

    try {
      const res = await fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: src,
          highlights: targetHighlightsWithVariants,
          highlight: targetHighlightsWithVariants[0],
          template_id: selectedTemplateId,
          subtitle_style: subtitleStyle,
          show_badge: showBadge,
          show_subtitles: subtitleStyle !== "none",
          aspect_ratio: aspectRatio,
          remove_subtitles: removeSubtitles,
          filter_fillers: filterFillers,
          bgm_track: bgmTrack,
          enable_sfx: enableSfx,
          color_grade: colorGrade,
          dynamic_zoom: dynamicZoom,
          smart_keywords: smartKeywords,
          bounce_animation: bounceAnimation,
          hook_variant_type: selectedHookVariants[targetHighlightsWithVariants[0]?.id] || "default",
          enable_stat_pill: enableStatPill,
          seamless_loop: seamlessLoop,
        }),
      });

      if (!res.ok) {
        let errText = `서버 렌더링 응답 오류 (${res.status})`;
        try {
          const errData = await res.json();
          errText = errData.detail || errData.message || errText;
        } catch {
          const rawText = await res.text();
          if (rawText) errText = rawText;
        }
        throw new Error(errText);
      }

      const data = await res.json();
      const jobId = data.job_id;

      try {
        localStorage.setItem(
          "happy_active_job",
          JSON.stringify({ jobId, type: "render", startTime: Date.now() })
        );
      } catch {}

      subscribeToRenderJob(jobId);
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
            <span>쇼츠 제작 스튜디오</span>
            {(isAnalyzing || isRendering) && (
              <span className="px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-mono animate-pulse flex items-center gap-1 font-bold">
                <Loader2 className="w-2.5 h-2.5 animate-spin" />
                {isRendering ? `렌더링 ${renderProgress}%` : `AI 분석 ${analyzeProgress}%`}
              </span>
            )}
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
            <span>완성 보관함 ({outputs.length})</span>
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
                  const isBusyHere = (s.num === 3 && isAnalyzing) || (s.num === 4 && isRendering);

                  return (
                    <React.Fragment key={s.num}>
                      <button
                        onClick={() => {
                          setCurrentStep(s.num);
                        }}
                        className={`flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                          isActive
                            ? "bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 shadow-sm"
                            : isDone
                            ? "text-emerald-400 hover:bg-slate-800/50"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs ${
                            isActive
                              ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/40"
                              : isBusyHere
                              ? "bg-rose-500/30 text-rose-300 border border-rose-500/50"
                              : isDone
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                              : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          {isBusyHere ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin text-rose-400" />
                          ) : isDone ? (
                            <Check className="w-3.5 h-3.5" />
                          ) : (
                            s.num
                          )}
                        </div>
                        <div className="hidden sm:block text-left">
                          <div className="flex items-center gap-1.5">
                            <p className="text-xs font-semibold">{s.label}</p>
                            {isBusyHere && (
                              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-rose-500/20 text-rose-300 font-bold animate-pulse">
                                {s.num === 3 ? `${analyzeProgress}%` : `${renderProgress}%`}
                              </span>
                            )}
                          </div>
                        </div>
                      </button>
                      {idx < 3 && <div className="flex-1 h-0.5 bg-slate-800 hidden md:block" />}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>

            {/* STEP 1: SOURCE SELECTION & CORE FORMAT */}
            {currentStep === 1 && (
              <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800/80 shadow-2xl flex flex-col gap-6 max-w-5xl mx-auto w-full">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800/80">
                  <div>
                    <h2 className="text-lg sm:text-xl font-bold text-white flex items-center gap-2.5">
                      <Video className="w-5 h-5 text-indigo-400" />
                      스텝 1. 영상 소스 입력 및 기본 규격 설정
                    </h2>
                    <p className="text-xs text-slate-400 mt-1">
                      유튜브 URL, 최근 작업 캐시, 또는 로컬 PC 영상을 지정하고 쇼츠 출력 규격을 선택하세요.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-semibold flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      100% 로컬 On-Device
                    </span>
                  </div>
                </div>

                {/* Source Mode Tabs */}
                <div className="grid grid-cols-3 gap-2.5 p-1 bg-slate-900/80 rounded-xl border border-slate-800">
                  <button
                    onClick={() => setSourceMode("youtube")}
                    className={`py-2.5 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                      sourceMode === "youtube"
                        ? "bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-md shadow-red-600/20"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                    }`}
                  >
                    <Radio className="w-4 h-4" />
                    유튜브 URL
                  </button>
                  <button
                    onClick={() => setSourceMode("recent")}
                    className={`py-2.5 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                      sourceMode === "recent"
                        ? "bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-md shadow-amber-600/20"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                    }`}
                  >
                    <Zap className="w-4 h-4" />
                    최근 작업 캐시 ({recentVideos.length}개)
                  </button>
                  <button
                    onClick={() => setSourceMode("local")}
                    className={`py-2.5 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                      sourceMode === "local"
                        ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-600/20"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                    }`}
                  >
                    <FolderOpen className="w-4 h-4" />
                    내 PC 로컬 영상
                  </button>
                </div>

                {/* Mode 1: YouTube Input */}
                {sourceMode === "youtube" && (
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-slate-300">유튜브 영상 URL 또는 영상 ID</label>
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="https://www.youtube.com/watch?v=... 또는 https://youtu.be/..."
                        value={youtubeUrl}
                        onChange={(e) => setYoutubeUrl(e.target.value)}
                        className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
                      />
                    </div>
                    <p className="text-[11px] text-slate-500 flex items-center gap-1.5 mt-0.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      이전에 작업했던 영상은 재다운로드 및 음성인식 없이 캐시를 자동 재사용합니다.
                    </p>
                  </div>
                )}

                {/* Mode 2: Recent Cached Videos */}
                {sourceMode === "recent" && (
                  <div className="flex flex-col gap-2">
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
                                  ? "bg-amber-500/10 border-amber-500/50 text-amber-200 shadow-sm"
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
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-slate-300">로컬 비디오 파일 절대 경로</label>
                    <input
                      type="text"
                      placeholder="/Users/.../my_video.mp4"
                      value={localPath}
                      onChange={(e) => setLocalPath(e.target.value)}
                      className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
                    />
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      터미널이나 파인더에서 파일을 복사하여 파일 절대 경로를 붙여넣으세요.
                    </p>
                  </div>
                )}

                {/* Core Specifications & Cleanups 2-Column Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  {/* Left Column: Aspect Ratio & Duration */}
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-col gap-3.5">
                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>화면 비율 (Aspect Ratio)</span>
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
                              : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span>📱 세로 9:16</span>
                          <span className="text-[10px] text-amber-400 font-normal">얼굴 자동추적</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setAspectRatio("16:9")}
                          className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold border transition flex items-center justify-center gap-1.5 ${
                            aspectRatio === "16:9"
                              ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm"
                              : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span>🖥️ 가로 16:9</span>
                          <span className="text-[10px] text-slate-500 font-normal">와이드</span>
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>목표 재생 시간</span>
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
                                ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm"
                                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            {d.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>후보 추출 개수</span>
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
                                ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm"
                                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            {cnt}개
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: AI Cleanups */}
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-col justify-between gap-3.5">
                    <div>
                      <label className="text-xs font-semibold text-slate-300 flex items-center justify-between mb-2">
                        <span>원본 영상 자막 클린업</span>
                        <span className={`font-bold ${removeSubtitles ? "text-amber-400" : "text-slate-500"}`}>
                          {removeSubtitles ? "LaMa AI 복원 켜짐" : "원본 유지"}
                        </span>
                      </label>
                      <button
                        type="button"
                        onClick={() => setRemoveSubtitles(!removeSubtitles)}
                        className={`w-full p-2.5 rounded-xl text-xs font-semibold border transition flex items-center justify-between ${
                          removeSubtitles
                            ? "bg-amber-500/10 border-amber-500/50 text-amber-200 shadow-sm"
                            : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <div className="text-left">
                          <p className="font-bold text-slate-200">🧹 LaMa 딥러닝 인페인팅</p>
                          <p className="text-[11px] text-slate-400 mt-0.5">블러 흔적 없이 배경/의류 완벽 복원</p>
                        </div>
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
                          {filterFillers ? "자동 필터링 켜짐" : "모든 단어 표시"}
                        </span>
                      </label>
                      <button
                        type="button"
                        onClick={() => setFilterFillers(!filterFillers)}
                        className={`w-full p-2.5 rounded-xl text-xs font-semibold border transition flex items-center justify-between ${
                          filterFillers
                            ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-200 shadow-sm"
                            : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <div className="text-left">
                          <p className="font-bold text-slate-200">✨ 추임새 자동 정리</p>
                          <p className="text-[11px] text-slate-400 mt-0.5">어, 음, 네, 아 등의 단독 팝업 방지</p>
                        </div>
                        <div
                          className={`w-8 h-4.5 flex items-center rounded-full p-0.5 transition duration-300 flex-shrink-0 ${
                            filterFillers ? "bg-emerald-500 justify-end" : "bg-slate-800 justify-start"
                          }`}
                        >
                          <div className="bg-white w-3.5 h-3.5 rounded-full shadow-md" />
                        </div>
                      </button>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60 text-[11px] text-slate-400 flex items-center gap-2">
                      <Zap className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                      <span>스텝 1에서 설정한 규격은 이후 템플릿과 렌더링에 자동 계승됩니다.</span>
                    </div>
                  </div>
                </div>

                {/* Footer Bar: Engine Specs & Proceed Button */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800/80">
                  <div className="flex items-center flex-wrap gap-2 text-[11px] text-slate-400">
                    <span className="flex items-center gap-1 bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800">
                      🎙️ Faster-Whisper Large-v3-Turbo
                    </span>
                    <span className="flex items-center gap-1 bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800">
                      🤖 Ollama Qwen2.5-14B 바이럴 채점
                    </span>
                  </div>

                  <button
                    onClick={handleProceedToTemplate}
                    className="w-full sm:w-auto px-7 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/25 transition"
                  >
                    다음 단계: 템플릿 선택
                    <ChevronRight className="w-4 h-4" />
                  </button>
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

                {/* Pro Studio Quality Suite (3-Tab Segmented Controls) */}
                <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 bg-slate-950/80 shadow-2xl flex flex-col gap-4">
                  {/* Studio Header & Tab Switcher */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-amber-400" />
                      <span className="text-sm font-bold text-slate-100">
                        스튜디오 프로 연출 (사운드 & 화질 & 타이포)
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30">
                        OpusClip/Submagic 급
                      </span>
                    </div>

                    {/* 3 Tabs */}
                    <div className="flex items-center p-1 bg-slate-900 rounded-xl border border-slate-800 text-xs">
                      <button
                        type="button"
                        onClick={() => setStudioOptionTab("audio")}
                        className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                          studioOptionTab === "audio"
                            ? "bg-indigo-600 text-white shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <Music className="w-3.5 h-3.5" />
                        <span>오디오 연출</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setStudioOptionTab("visual")}
                        className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                          studioOptionTab === "visual"
                            ? "bg-indigo-600 text-white shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <Palette className="w-3.5 h-3.5" />
                        <span>비주얼 & 카메라</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setStudioOptionTab("typography")}
                        className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
                          studioOptionTab === "typography"
                            ? "bg-indigo-600 text-white shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <Type className="w-3.5 h-3.5" />
                        <span>타이포 & 모션</span>
                      </button>
                    </div>
                  </div>

                  {/* Tab 1: Audio & Sound Design */}
                  {studioOptionTab === "audio" && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-3">
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Music className="w-4 h-4 text-indigo-400" />
                              BGM 배경음악 선곡
                            </span>
                            <span className="text-[11px] text-indigo-400 font-semibold">오토 더킹 내장</span>
                          </div>
                          <p className="text-[11px] text-slate-400">
                            음성 발화 구간에서는 BGM 볼륨이 자동으로 낮아져 대사가 또렷하게 전달됩니다.
                          </p>
                        </div>
                        <select
                          value={bgmTrack}
                          onChange={(e) => setBgmTrack(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-700/80 rounded-xl text-xs font-semibold text-slate-200 px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
                        >
                          <option value="auto">✨ 템플릿 맞춤 자동 선곡 (추천)</option>
                          <option value="lofi">☕ 로파이 팁스 (Study & Chill Beats)</option>
                          <option value="tech">⚡ 모던 테크 (Synth & Electronic)</option>
                          <option value="cinematic">🎬 시네마틱 (펄스 & 웅장한 사운드)</option>
                          <option value="none">🔇 BGM 배경음악 끄기</option>
                        </select>
                      </div>

                      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-3">
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Volume2 className="w-4 h-4 text-amber-400" />
                              바이럴 사운드 효과음 (SFX)
                            </span>
                            <span className={`text-[11px] font-bold ${enableSfx ? "text-amber-400" : "text-slate-500"}`}>
                              {enableSfx ? "켜짐" : "꺼짐"}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400">
                            쇼츠 시작 훅(Whoosh), 장면 전환, 핵심 키워드 강조(차임·팝) 효과음을 자동 합성합니다.
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => setEnableSfx(!enableSfx)}
                          className={`w-full py-2.5 px-3 rounded-xl text-xs font-bold border transition flex items-center justify-between ${
                            enableSfx
                              ? "bg-amber-500/15 border-amber-500/50 text-amber-300 shadow-sm"
                              : "bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-300"
                          }`}
                        >
                          <span>{enableSfx ? "🔔 바이럴 SFX 효과음 활성화됨" : "효과음 끄기"}</span>
                          <div className={`w-7 h-4 flex items-center rounded-full p-0.5 transition ${enableSfx ? "bg-amber-500 justify-end" : "bg-slate-800 justify-start"}`}>
                            <div className="bg-white w-3 h-3 rounded-full shadow" />
                          </div>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Tab 2: Visual & Camera Polish */}
                  {studioOptionTab === "visual" && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-3">
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Palette className="w-4 h-4 text-rose-400" />
                              시네마틱 컬러 그레이딩 (LUT 보정)
                            </span>
                            <span className="text-[11px] text-rose-400 font-semibold">알고리즘 CTR</span>
                          </div>
                          <p className="text-[11px] text-slate-400">
                            물빠진 원본 색감을 유튜브 피드에서 눈에 띄는 고채도·고명암비로 보정합니다.
                          </p>
                        </div>
                        <select
                          value={colorGrade}
                          onChange={(e) => setColorGrade(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-700/80 rounded-xl text-xs font-semibold text-slate-200 px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
                        >
                          <option value="vibrant_tech">⚡ 바이브런트 테크 (유튜브 추천 피드 CTR 극대화)</option>
                          <option value="warm_clean">☀️ 웜 클린 스튜디오 (따뜻하고 포근한 인물톤)</option>
                          <option value="film_contrast">🎬 시네마틱 필름 (영화 같은 깊은 대비)</option>
                          <option value="clean">✨ 클린 샤프닝 (선명도 및 윤곽 강화)</option>
                          <option value="none">원본 영상 색감 그대로 유지</option>
                        </select>
                      </div>

                      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-3">
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <ZoomIn className="w-4 h-4 text-cyan-400" />
                              다이내믹 펀치인 줌 (Punch-in Zoom)
                            </span>
                            <span className={`text-[11px] font-bold ${dynamicZoom ? "text-cyan-400" : "text-slate-500"}`}>
                              {dynamicZoom ? "1.10x 줌 켜짐" : "꺼짐"}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400">
                            강조 문장에서 카메라를 미세하게 줌인(1.10x)하여 시청 지속 시간을 극대화합니다.
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => setDynamicZoom(!dynamicZoom)}
                          className={`w-full py-2.5 px-3 rounded-xl text-xs font-bold border transition flex items-center justify-between ${
                            dynamicZoom
                              ? "bg-cyan-500/15 border-cyan-500/50 text-cyan-300 shadow-sm"
                              : "bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-300"
                          }`}
                        >
                          <span>{dynamicZoom ? "🔍 1.10x 다이내믹 줌 활성화됨" : "줌 효과 끄기"}</span>
                          <div className={`w-7 h-4 flex items-center rounded-full p-0.5 transition ${dynamicZoom ? "bg-cyan-500 justify-end" : "bg-slate-800 justify-start"}`}>
                            <div className="bg-white w-3 h-3 rounded-full shadow" />
                          </div>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Tab 3: Typography & Motion Animation */}
                  {studioOptionTab === "typography" && (
                    <div className="flex flex-col gap-3">
                      {/* Subtitle Style Selector */}
                      <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div>
                          <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                            <Type className="w-4 h-4 text-indigo-400" />
                            자막 출력 스타일
                          </span>
                          <p className="text-[11px] text-slate-400 mt-0.5">
                            영상 분위기에 어울리는 폰트 및 애니메이션 프리셋을 선택하세요.
                          </p>
                        </div>
                        <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
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
                      </div>

                      {/* 5 Pro Typography Toggles Grid */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {/* 1. Smart Keywords */}
                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-2">
                          <div>
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                              스마트 키워드 네온 강조
                            </span>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              숫자, 핵심 단어, 파워 키워드 자동 컬러링
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setSmartKeywords(!smartKeywords)}
                            className={`w-full py-1.5 px-2.5 rounded-lg text-xs font-semibold border transition flex items-center justify-between ${
                              smartKeywords
                                ? "bg-emerald-500/15 border-emerald-500/50 text-emerald-300"
                                : "bg-slate-950 border-slate-800 text-slate-500"
                            }`}
                          >
                            <span>{smartKeywords ? "🔤 네온 하이라이트" : "일반 단일색"}</span>
                            <div className={`w-6 h-3.5 flex items-center rounded-full p-0.5 transition ${smartKeywords ? "bg-emerald-500 justify-end" : "bg-slate-800 justify-start"}`}>
                              <div className="bg-white w-2.5 h-2.5 rounded-full shadow" />
                            </div>
                          </button>
                        </div>

                        {/* 2. Elastic Bounce */}
                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-2">
                          <div>
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Sparkles className="w-3.5 h-3.5 text-fuchsia-400" />
                              탄성 바운스 자막
                            </span>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              0.8x→1.15x 물리 기반 스프링 탄성 팝업
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setBounceAnimation(!bounceAnimation)}
                            className={`w-full py-1.5 px-2.5 rounded-lg text-xs font-semibold border transition flex items-center justify-between ${
                              bounceAnimation
                                ? "bg-fuchsia-500/15 border-fuchsia-500/50 text-fuchsia-300"
                                : "bg-slate-950 border-slate-800 text-slate-500"
                            }`}
                          >
                            <span>{bounceAnimation ? "🌀 탄성 바운스 켜짐" : "정적 팝업"}</span>
                            <div className={`w-6 h-3.5 flex items-center rounded-full p-0.5 transition ${bounceAnimation ? "bg-fuchsia-500 justify-end" : "bg-slate-800 justify-start"}`}>
                              <div className="bg-white w-2.5 h-2.5 rounded-full shadow" />
                            </div>
                          </button>
                        </div>

                        {/* 3. Stat Card */}
                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-2">
                          <div>
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Target className="w-3.5 h-3.5 text-amber-400" />
                              키노트 수치 요약 카드
                            </span>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              통계, 퍼센트, 지표 글래스모피즘 팝업
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setEnableStatPill(!enableStatPill)}
                            className={`w-full py-1.5 px-2.5 rounded-lg text-xs font-semibold border transition flex items-center justify-between ${
                              enableStatPill
                                ? "bg-amber-500/15 border-amber-500/50 text-amber-300"
                                : "bg-slate-950 border-slate-800 text-slate-500"
                            }`}
                          >
                            <span>{enableStatPill ? "📊 수치 요약 카드" : "카드 끄기"}</span>
                            <div className={`w-6 h-3.5 flex items-center rounded-full p-0.5 transition ${enableStatPill ? "bg-amber-500 justify-end" : "bg-slate-800 justify-start"}`}>
                              <div className="bg-white w-2.5 h-2.5 rounded-full shadow" />
                            </div>
                          </button>
                        </div>

                        {/* 4. Seamless Loop */}
                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-2">
                          <div>
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Infinity className="w-3.5 h-3.5 text-violet-400" />
                              무한 루프 싱크
                            </span>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              끝과 처음을 200ms 페이드로 매끄럽게 연결
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setSeamlessLoop(!seamlessLoop)}
                            className={`w-full py-1.5 px-2.5 rounded-lg text-xs font-semibold border transition flex items-center justify-between ${
                              seamlessLoop
                                ? "bg-violet-500/15 border-violet-500/50 text-violet-300"
                                : "bg-slate-950 border-slate-800 text-slate-500"
                            }`}
                          >
                            <span>{seamlessLoop ? "🔁 무한 루프 싱크" : "일반 컷"}</span>
                            <div className={`w-6 h-3.5 flex items-center rounded-full p-0.5 transition ${seamlessLoop ? "bg-violet-500 justify-end" : "bg-slate-800 justify-start"}`}>
                              <div className="bg-white w-2.5 h-2.5 rounded-full shadow" />
                            </div>
                          </button>
                        </div>

                        {/* 5. 3-Sec Hook Badge */}
                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-2">
                          <div>
                            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                              3초 훅 뱃지 타이틀
                            </span>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              영상 상단에 호기심 유발 헤드라인 표시
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setShowBadge(!showBadge)}
                            className={`w-full py-1.5 px-2.5 rounded-lg text-xs font-semibold border transition flex items-center justify-between ${
                              showBadge
                                ? "bg-indigo-500/15 border-indigo-500/50 text-indigo-300"
                                : "bg-slate-950 border-slate-800 text-slate-500"
                            }`}
                          >
                            <span>{showBadge ? "🏷️ 3초 훅 뱃지 켜짐" : "뱃지 숨김"}</span>
                            <div className={`w-6 h-3.5 flex items-center rounded-full p-0.5 transition ${showBadge ? "bg-indigo-500 justify-end" : "bg-slate-800 justify-start"}`}>
                              <div className="bg-white w-2.5 h-2.5 rounded-full shadow" />
                            </div>
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Bottom Sticky Action Bar (Clean & Focused) */}
                <div className="glass-panel p-4 sm:p-5 rounded-2xl border border-slate-800/80 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-4 sticky bottom-4 z-40 bg-slate-950/95 backdrop-blur-xl">
                  {/* Left: Currently Selected Template Pill */}
                  <div className="flex items-center gap-3 w-full sm:w-auto">
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

                  {/* Center: Clean Applied Specs Chips */}
                  <div className="hidden md:flex items-center gap-1.5 text-[11px] text-slate-400">
                    <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 font-semibold text-slate-300">
                      {aspectRatio === "9:16" ? "📱 9:16 세로" : "🖥️ 16:9 가로"}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800">
                      {subtitleStyle === "viral_pop" ? "🔥 키네틱" : subtitleStyle === "clean_minimal" ? "💬 미니멀" : "🚫 자막없음"}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800">
                      {colorGrade === "vibrant_tech" ? "⚡ 바이브런트" : "🎨 색감보정"}
                    </span>
                    {enableSfx && (
                      <span className="px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300 font-semibold">
                        🔔 SFX
                      </span>
                    )}
                  </div>

                  {/* Right: Proceed to Step 3 Button */}
                  <div className="w-full sm:w-auto flex justify-end">
                    <button
                      onClick={handleStartAnalysis}
                      className="w-full sm:w-auto px-7 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:opacity-95 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-xl shadow-rose-500/20 transition"
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

                      {/* AI 음성 분석 상세 리포트 (프로세스 세분화 카드) */}
                      {transcriptSummary && (
                        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col gap-3 shadow-md">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                                <AudioLines className="w-4 h-4" />
                              </div>
                              <div>
                                <h3 className="text-xs font-bold text-white flex items-center gap-2">
                                  <span>AI 음성 분석 & 단어 싱크 완료 리포트</span>
                                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono">
                                    Whisper STT 완료
                                  </span>
                                </h3>
                                <p className="text-[11px] text-slate-400">
                                  전체 음성을 정밀 분석하여 {transcriptSummary.segment_count?.toLocaleString()}개 대화 세그먼트를 추출했습니다.
                                </p>
                              </div>
                            </div>
                            <button
                              type="button"
                              onClick={() => setShowTranscriptDetails(!showTranscriptDetails)}
                              className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1.5"
                            >
                              <span>{showTranscriptDetails ? "스크립트 접기" : "대화 내역 펼치기"}</span>
                              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showTranscriptDetails ? "rotate-180" : ""}`} />
                            </button>
                          </div>

                          {/* 4 Metrics Pills */}
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 border-t border-slate-800/60">
                            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                              <span className="text-[10px] text-slate-400 block font-medium">분석된 총 길이</span>
                              <span className="text-sm font-bold text-white font-mono">{transcriptSummary.duration_formatted || "55분 52초"}</span>
                            </div>
                            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                              <span className="text-[10px] text-slate-400 block font-medium">전사된 발화 문장</span>
                              <span className="text-sm font-bold text-emerald-400 font-mono">{transcriptSummary.segment_count?.toLocaleString()}개</span>
                            </div>
                            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                              <span className="text-[10px] text-slate-400 block font-medium">단어 타임스탬프</span>
                              <span className="text-sm font-bold text-indigo-400 font-mono">{transcriptSummary.total_words?.toLocaleString()}단어</span>
                            </div>
                            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                              <span className="text-[10px] text-slate-400 block font-medium">평균 발화 속도</span>
                              <span className="text-sm font-bold text-amber-400 font-mono">{transcriptSummary.wpm_avg || 116} WPM</span>
                            </div>
                          </div>

                          {/* Expandable Transcript Dialogue Preview */}
                          {showTranscriptDetails && transcriptSummary.preview_segments && (
                            <div className="mt-2 p-3 rounded-xl bg-slate-950 border border-slate-800 max-h-48 overflow-y-auto space-y-1.5 text-xs font-mono">
                              <div className="text-[11px] text-slate-400 font-semibold mb-1 flex items-center justify-between">
                                <span>타임라인별 대화 스크립트 미리보기</span>
                                <span className="text-[10px] text-slate-400">초반 {transcriptSummary.preview_segments.length}개 구간</span>
                              </div>
                              {transcriptSummary.preview_segments.map((s, idx) => (
                                <div key={idx} className="flex items-start gap-2 text-slate-300 hover:bg-slate-900/60 p-1 rounded">
                                  <span className="text-indigo-400 shrink-0 font-bold">[{s.time}]</span>
                                  <span className="text-slate-200">{s.text}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

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

                                  {/* Seamless Infinite Loop Score Badge */}
                                  <span
                                    className="text-[11px] font-bold px-2 py-0.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1 font-mono"
                                    title="끝 문장과 첫 문장이 자연스럽게 연결되어 무한 반복 시청을 유도하는 싱크 지수입니다."
                                  >
                                    <Infinity className="w-3.5 h-3.5 stroke-[2.5]" />
                                    루프 {hl.loop_score || 88}점
                                  </span>

                                  {/* Apple Keynote Stat Pill Detected Badge */}
                                  {hl.stat_pill && (
                                    <span
                                      className="text-[11px] font-bold px-2 py-0.5 rounded-lg bg-violet-500/20 text-violet-300 border border-violet-500/40 flex items-center gap-1 font-mono"
                                      title={`영상 3.8초경 [${hl.stat_pill.metric}] 키노트 글래스모피즘 수치 카드가 자동 팝업됩니다.`}
                                    >
                                      <Target className="w-3.5 h-3.5" />
                                      카드 [{hl.stat_pill.metric}]
                                    </span>
                                  )}

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

                              <h3 className="font-bold text-sm text-white mt-1 mb-1.5">{hl.title}</h3>

                              {/* Hook Headline A/B Testing Variant Selector */}
                              <div className="space-y-2 mb-3">
                                {/* Currently Active Hook Headline Display */}
                                <div className="p-2.5 rounded-xl bg-gradient-to-r from-amber-500/10 via-rose-500/10 to-indigo-500/10 border border-amber-500/30 flex items-start gap-2 shadow-sm">
                                  <span className="text-sm shrink-0">🎯</span>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between text-[10px] font-semibold text-amber-300/80 mb-0.5">
                                      <span>적용된 훅 헤드라인</span>
                                      <span className="font-mono text-indigo-300">
                                        {selectedHookVariants[hl.id] === "curiosity"
                                          ? "🤔 호기심형"
                                          : selectedHookVariants[hl.id] === "urgency"
                                          ? "⚠️ 손실회피형"
                                          : selectedHookVariants[hl.id] === "benefit"
                                          ? "🚀 극대이득형"
                                          : "✨ 기본형"}
                                      </span>
                                    </div>
                                    <p className="text-xs text-amber-200 font-bold leading-snug">
                                      &quot;{
                                        (selectedHookVariants[hl.id] &&
                                          hl.hook_variants &&
                                          (hl.hook_variants as Record<string, string | undefined>)[selectedHookVariants[hl.id]]) ||
                                        hl.hook_text
                                      }&quot;
                                    </p>
                                  </div>
                                </div>

                                {/* Hook A/B Testing 3-Variant Switcher Buttons */}
                                {hl.hook_variants && (
                                  <div
                                    className="grid grid-cols-1 sm:grid-cols-3 gap-1.5 pt-0.5"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    {[
                                      {
                                        key: "curiosity",
                                        label: "🤔 호기심형",
                                        text: hl.hook_variants.curiosity,
                                        desc: "궁금증 유발",
                                      },
                                      {
                                        key: "urgency",
                                        label: "⚠️ 손실회피형",
                                        text: hl.hook_variants.urgency,
                                        desc: "놓치면 손해",
                                      },
                                      {
                                        key: "benefit",
                                        label: "🚀 극대이득형",
                                        text: hl.hook_variants.benefit,
                                        desc: "즉각적 결과",
                                      },
                                    ].map((v) => {
                                      const isCurrent =
                                        (selectedHookVariants[hl.id] || "default") === v.key;
                                      if (!v.text) return null;
                                      return (
                                        <button
                                          key={v.key}
                                          type="button"
                                          onClick={() => {
                                            setSelectedHookVariants((prev) => ({
                                              ...prev,
                                              [hl.id]: v.key,
                                            }));
                                            if (selectedHighlight?.id === hl.id) {
                                              setSelectedHighlight({
                                                ...selectedHighlight,
                                                hook_text: v.text || hl.hook_text,
                                              });
                                            }
                                          }}
                                          className={`p-2 rounded-xl text-left border transition flex flex-col justify-between gap-1 ${
                                            isCurrent
                                              ? "bg-slate-900 border-indigo-500 shadow-md ring-1 ring-indigo-500/60"
                                              : "bg-slate-950/60 border-slate-800/80 hover:bg-slate-900/80 hover:border-slate-700"
                                          }`}
                                        >
                                          <div className="flex items-center justify-between w-full">
                                            <span
                                              className={`text-[10px] font-bold ${
                                                isCurrent ? "text-indigo-300" : "text-slate-400"
                                              }`}
                                            >
                                              {v.label}
                                            </span>
                                            {isCurrent && (
                                              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                                            )}
                                          </div>
                                          <span className="text-[11px] text-slate-300 font-medium line-clamp-1 truncate">
                                            {v.text}
                                          </span>
                                        </button>
                                      );
                                    })}
                                  </div>
                                )}
                              </div>

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
                              <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[10px] text-slate-500 font-mono">
                                <div className="flex items-center gap-2">
                                  <span>후킹: {b.hook}/30</span>
                                  <span>흐름: {b.flow}/25</span>
                                  <span>가치: {b.value}/25</span>
                                  <span>트렌드: {b.trend}/20</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className="text-emerald-400/90 font-semibold">🔁 루프 싱크: {hl.loop_score || 88}점</span>
                                  {hl.stat_pill && (
                                    <span className="text-violet-400/90 font-semibold">📊 카드: {hl.stat_pill.metric}</span>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Right: Interactive Video Player & Trim Controller */}
                    <div className="lg:col-span-5 flex flex-col gap-4">
                      <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 flex flex-col gap-4 sticky top-24">
                        <div className="flex items-center justify-between pb-1 border-b border-slate-800/80">
                          <h3 className="text-sm font-bold text-white flex items-center gap-2">
                            <Play className="w-4 h-4 text-indigo-400" />
                            선택 구간 미리보기 & 타임라인 트림
                          </h3>

                          {/* Safe Zone Guideline Selector */}
                          <div className="flex items-center gap-1 bg-slate-900/90 border border-slate-800 p-0.5 rounded-lg text-[10px]">
                            <span className="text-slate-500 font-mono px-1 flex items-center gap-0.5">
                              <Smartphone className="w-2.5 h-2.5" /> 세이프존:
                            </span>
                            {[
                              { id: "none", label: "끄기" },
                              { id: "youtube", label: "쇼츠" },
                              { id: "reels", label: "릴스" },
                              { id: "tiktok", label: "틱톡" },
                            ].map((sz) => (
                              <button
                                key={sz.id}
                                type="button"
                                onClick={() => setPreviewSafeZoneMode(sz.id as SafeZonePlatform)}
                                className={`px-1.5 py-0.5 rounded font-bold transition ${
                                  previewSafeZoneMode === sz.id
                                    ? "bg-indigo-600 text-white shadow-sm"
                                    : "text-slate-400 hover:text-slate-200"
                                }`}
                              >
                                {sz.label}
                              </button>
                            ))}
                          </div>
                        </div>

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
                              <SafeZoneOverlay platform={previewSafeZoneMode} />
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

                            {/* Applied Studio Settings Summary Card */}
                            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs flex flex-col gap-2.5">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-300 flex items-center gap-1.5">
                                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                                  적용된 템플릿 & 스튜디오 사양
                                </span>
                                <span className="text-[10px] text-slate-500 font-mono">
                                  {templates.find((t) => t.id === selectedTemplateId)?.name}
                                </span>
                              </div>

                              <div className="flex flex-wrap gap-1.5 pt-1 border-t border-slate-800/80">
                                <span className="px-2 py-0.5 rounded-md bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 font-bold text-[10px]">
                                  {aspectRatio === "9:16" ? "📱 9:16 세로" : "🖥️ 16:9 가로"}
                                </span>
                                {removeSubtitles ? (
                                  <span className="px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/30 text-amber-300 font-semibold text-[10px]">
                                    🧹 LaMa 인페인팅
                                  </span>
                                ) : (
                                  <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-slate-400 text-[10px]">
                                    원본 자막
                                  </span>
                                )}
                                {filterFillers && (
                                  <span className="px-2 py-0.5 rounded-md bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-[10px]">
                                    ✨ 말버릇 필터
                                  </span>
                                )}
                                <span className="px-2 py-0.5 rounded-md bg-rose-500/15 border border-rose-500/30 text-rose-300 text-[10px]">
                                  {colorGrade === "vibrant_tech"
                                    ? "⚡ 바이브런트 테크"
                                    : colorGrade === "warm_clean"
                                    ? "☀️ 웜 클린"
                                    : colorGrade === "film_contrast"
                                    ? "🎬 시네마틱 필름"
                                    : colorGrade === "clean"
                                    ? "✨ 클린 샤픈"
                                    : "원본 색감"}
                                </span>
                                <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-slate-300 text-[10px]">
                                  🎵 BGM: {bgmTrack === "auto" ? "템플릿 자동" : bgmTrack === "none" ? "끄기" : bgmTrack}
                                </span>
                                {enableSfx && (
                                  <span className="px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[10px]">
                                    🔔 SFX ON
                                  </span>
                                )}
                                {dynamicZoom && (
                                  <span className="px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-[10px]">
                                    🔍 줌 1.10x
                                  </span>
                                )}
                                {smartKeywords && (
                                  <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[10px]">
                                    🔤 네온 키워드
                                  </span>
                                )}
                                {bounceAnimation && (
                                  <span className="px-2 py-0.5 rounded-md bg-fuchsia-500/10 border border-fuchsia-500/20 text-fuchsia-300 text-[10px]">
                                    🌀 탄성 바운스
                                  </span>
                                )}
                                {enableStatPill && (
                                  <span className="px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[10px]">
                                    📊 키노트 카드
                                  </span>
                                )}
                                {seamlessLoop && (
                                  <span className="px-2 py-0.5 rounded-md bg-violet-500/10 border border-violet-500/20 text-violet-300 text-[10px]">
                                    🔁 무한 루프
                                  </span>
                                )}
                              </div>

                              <p className="text-[10px] text-slate-500 pt-1">
                                💡 디자인이나 사운드 설정을 바꾸려면 상단 스텝 1 또는 2를 클릭하세요.
                              </p>
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
                      {/* Mobile Safe Zone Guideline Selector Bar */}
                      {aspectRatio === "9:16" && (
                        <div className="flex items-center gap-2 mb-3 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-xl shadow-lg">
                          <span className="text-xs font-bold text-slate-300 flex items-center gap-1">
                            <Smartphone className="w-3.5 h-3.5 text-indigo-400" /> 세이프존 검증:
                          </span>
                          <div className="flex items-center gap-1">
                            {[
                              { id: "none", label: "끄기" },
                              { id: "youtube", label: "유튜브 쇼츠" },
                              { id: "reels", label: "릴스" },
                              { id: "tiktok", label: "틱톡" },
                            ].map((sz) => (
                              <button
                                key={sz.id}
                                type="button"
                                onClick={() => setSafeZoneMode(sz.id as SafeZonePlatform)}
                                className={`px-2 py-0.5 rounded text-[11px] font-bold transition ${
                                  safeZoneMode === sz.id
                                    ? "bg-indigo-600 text-white shadow"
                                    : "text-slate-400 hover:text-slate-200"
                                }`}
                              >
                                {sz.label}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

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
                          {aspectRatio === "9:16" && (
                            <SafeZoneOverlay platform={safeZoneMode} />
                          )}
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

                            {out.cover_url && (
                              <a
                                href={out.cover_url}
                                download={`cover_${out.filename.replace(/\.mp4$/i, ".jpg")}`}
                                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-300 hover:text-amber-200 border border-slate-700 transition"
                                title="고화질 프로 썸네일(JPG) 다운로드"
                              >
                                <ImageIcon className="w-3.5 h-3.5" />
                              </a>
                            )}

                            <button
                              onClick={() => openThumbnailEditor(out)}
                              className="p-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition"
                              title="🎨 썸네일 맞춤 스튜디오"
                            >
                              <Palette className="w-3.5 h-3.5" />
                            </button>

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
                              영상 다운로드
                            </a>

                            {out.cover_url && (
                              <a
                                href={out.cover_url}
                                download={`cover_${out.filename.replace(/\.mp4$/i, ".jpg")}`}
                                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 hover:text-amber-200 border border-slate-700 text-xs font-bold flex items-center gap-1.5 transition"
                                title="고화질 프로 썸네일(JPG) 다운로드"
                              >
                                <ImageIcon className="w-3.5 h-3.5" />
                                썸네일 (JPG)
                              </a>
                            )}

                            <button
                              onClick={() => openThumbnailEditor(out)}
                              className="px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-bold flex items-center gap-1.5 transition"
                              title="🎨 썸네일 맞춤 스튜디오"
                            >
                              <Palette className="w-3.5 h-3.5" />
                              썸네일 편집
                            </button>

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

                          {/* Safe Zone Toggle in Gallery Modal */}
                          {previewModalOutput.aspect_ratio !== "16:9" && (
                            <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-0.5 rounded-lg text-[10px]">
                              <span className="text-slate-500 font-mono px-1 flex items-center gap-0.5">
                                <Smartphone className="w-2.5 h-2.5" /> 세이프존:
                              </span>
                              {[
                                { id: "none", label: "끄기" },
                                { id: "youtube", label: "쇼츠" },
                                { id: "reels", label: "릴스" },
                                { id: "tiktok", label: "틱톡" },
                              ].map((sz) => (
                                <button
                                  key={sz.id}
                                  type="button"
                                  onClick={() => setSafeZoneMode(sz.id as SafeZonePlatform)}
                                  className={`px-1.5 py-0.5 rounded font-bold transition ${
                                    safeZoneMode === sz.id
                                      ? "bg-indigo-600 text-white shadow-sm"
                                      : "text-slate-400 hover:text-slate-200"
                                  }`}
                                >
                                  {sz.label}
                                </button>
                              ))}
                            </div>
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
                      <div className="w-full md:w-[320px] shrink-0 flex items-center justify-center bg-black/90 rounded-2xl overflow-hidden border border-slate-800 shadow-xl relative">
                        <video
                          src={previewModalOutput.stream_url}
                          controls
                          autoPlay
                          className="w-full max-h-[60vh] object-contain"
                        />
                        {previewModalOutput.aspect_ratio !== "16:9" && (
                          <SafeZoneOverlay platform={safeZoneMode} />
                        )}
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

                          {previewModalOutput.cover_url && (
                            <a
                              href={previewModalOutput.cover_url}
                              download={`cover_${previewModalOutput.filename.replace(/\.mp4$/i, ".jpg")}`}
                              className="px-4 py-3 rounded-xl bg-slate-850 hover:bg-slate-800 text-amber-300 hover:text-amber-200 border border-amber-500/30 font-bold text-xs flex items-center justify-center gap-2 shadow-md transition"
                              title="고화질 프로 썸네일(JPG) 다운로드"
                            >
                              <ImageIcon className="w-4 h-4 text-amber-400" />
                              썸네일 저장 (JPG)
                            </a>
                          )}

                          <button
                            onClick={() => openThumbnailEditor(previewModalOutput)}
                            className="px-4 py-3 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 font-bold text-xs flex items-center justify-center gap-2 shadow-sm transition"
                            title="🎨 썸네일 맞춤 스튜디오"
                          >
                            <Palette className="w-4 h-4" />
                            썸네일 맞춤 편집
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ========================================================================= */}
              {/* 🎨 Creator-Grade Thumbnail Studio Modal */}
              {/* ========================================================================= */}
              {thumbEditorOpen && thumbTargetOutput && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
                  <div className="glass-panel bg-slate-950/95 border border-indigo-500/40 rounded-2xl max-w-4xl w-full max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
                    {/* Modal Header */}
                    <div className="p-4 sm:px-6 border-b border-slate-800 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
                          <Palette className="w-4 h-4" />
                        </div>
                        <div>
                          <h3 className="font-extrabold text-sm sm:text-base text-white flex items-center gap-2">
                            유튜브 1티어 썸네일 맞춤 스튜디오
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                              100% 로컬 고화질 9:16
                            </span>
                          </h3>
                          <p className="text-xs text-slate-400">
                            안면 인식 9:16 풀스크린 크롭 & 고대비 백플레이트 타이포 (이모지 없음)
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setThumbEditorOpen(false)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Modal Content: 2-column layout */}
                    <div className="p-4 sm:p-6 overflow-y-auto flex-1 grid grid-cols-1 md:grid-cols-12 gap-6">
                      {/* Left Column: 9:16 Live Preview (5 cols) */}
                      <div className="md:col-span-5 flex flex-col items-center gap-3">
                        <div className="text-xs font-bold text-slate-300 self-start flex items-center gap-1.5">
                          <Smartphone className="w-3.5 h-3.5 text-indigo-400" />
                          실시간 9:16 썸네일 미리보기
                        </div>
                        <div className="relative w-full max-w-[260px] aspect-[9/16] rounded-xl overflow-hidden border-2 border-indigo-500/30 shadow-2xl bg-slate-900 group">
                          {thumbLivePreviewUrl ? (
                            <img
                              src={thumbLivePreviewUrl}
                              alt="썸네일 미리보기"
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs">
                              미리보기 로딩 중...
                            </div>
                          )}

                          {thumbIsRendering && (
                            <div className="absolute inset-0 bg-black/60 backdrop-blur-xs flex flex-col items-center justify-center gap-2 text-white text-xs font-bold">
                              <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
                              <span>썸네일 렌더링 중...</span>
                            </div>
                          )}
                        </div>

                        {/* Quick Actions under preview */}
                        <div className="w-full max-w-[260px] flex flex-col gap-2 pt-1">
                          <button
                            onClick={() => handleRenderThumbnail()}
                            disabled={thumbIsRendering}
                            className="w-full py-2.5 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-md transition"
                          >
                            {thumbIsRendering ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            ) : (
                              <RefreshCw className="w-3.5 h-3.5" />
                            )}
                            변경사항 실시간 반영
                          </button>

                          {thumbLivePreviewUrl && (
                            <a
                              href={thumbLivePreviewUrl}
                              download={`thumbnail_${thumbTargetOutput.filename.replace(/\.mp4$/i, ".jpg")}`}
                              className="w-full py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold flex items-center justify-center gap-1.5 transition"
                            >
                              <Download className="w-3.5 h-3.5" />
                              고화질 JPG 다운로드
                            </a>
                          )}
                        </div>
                      </div>

                      {/* Right Column: Customization Controls (7 cols) */}
                      <div className="md:col-span-7 flex flex-col gap-5">
                        {/* 1. Best Face Frame Picker */}
                        <div>
                          <label className="text-xs font-bold text-slate-300 block mb-2 flex items-center justify-between">
                            <span className="flex items-center gap-1.5">
                              <Target className="w-3.5 h-3.5 text-rose-400" />
                              1. 인물 표정 베스트 컷 선택
                            </span>
                            {thumbIsLoadingCandidates && (
                              <span className="text-[11px] text-indigo-400 flex items-center gap-1">
                                <Loader2 className="w-3 h-3 animate-spin" />
                                프레임 분석 중...
                              </span>
                            )}
                          </label>

                          {thumbCandidates.length > 0 ? (
                            <div className="grid grid-cols-4 gap-2">
                              {thumbCandidates.map((cand, idx) => (
                                <div
                                  key={cand.index}
                                  onClick={() => {
                                    setSelectedCandidateIdx(idx);
                                    handleRenderThumbnail(idx);
                                  }}
                                  className={`relative cursor-pointer rounded-lg overflow-hidden border-2 aspect-[9/16] transition-all transform hover:scale-105 ${
                                    selectedCandidateIdx === idx
                                      ? "border-indigo-500 ring-2 ring-indigo-500/50 shadow-md"
                                      : "border-slate-800 hover:border-slate-600 opacity-70 hover:opacity-100"
                                  }`}
                                >
                                  <img
                                    src={cand.preview_url}
                                    alt={`후보 ${idx + 1}`}
                                    className="w-full h-full object-cover"
                                  />
                                  <div className="absolute bottom-0 inset-x-0 bg-black/70 py-0.5 text-center text-[9px] font-bold text-slate-200">
                                    {cand.offset_sec}초
                                  </div>
                                  {selectedCandidateIdx === idx && (
                                    <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-indigo-600 text-white flex items-center justify-center">
                                      <Check className="w-2.5 h-2.5 stroke-[3]" />
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs text-slate-500 py-2">
                              후보 프레임을 추출하는 중이거나 영상 기본 프레임을 사용합니다.
                            </p>
                          )}
                        </div>

                        {/* 2. Top Vector Badge (NO EMOJIS) */}
                        <div>
                          <label className="text-xs font-bold text-slate-300 block mb-2 flex items-center gap-1.5">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                            2. 상단 벡터 뱃지 심볼 (이모지 없음)
                          </label>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-2">
                            {[
                              { type: "warning", label: "긴급 대처법", icon: AlertTriangle, color: "text-rose-400" },
                              { type: "tip", label: "핵심 꿀팁", icon: Lightbulb, color: "text-amber-400" },
                              { type: "fact", label: "팩트 체크", icon: ShieldCheck, color: "text-sky-400" },
                              { type: "none", label: "뱃지 없음", icon: X, color: "text-slate-400" },
                            ].map((b) => {
                              const IconComponent = b.icon;
                              const isSelected = thumbBadgeType === b.type;
                              return (
                                <button
                                  key={b.type}
                                  type="button"
                                  onClick={() => {
                                    setThumbBadgeType(b.type as any);
                                    if (b.type !== "none") setThumbBadgeLabel(b.label);
                                  }}
                                  className={`py-2 px-2 rounded-xl border text-xs font-bold flex items-center justify-center gap-1.5 transition ${
                                    isSelected
                                      ? "bg-slate-800 border-indigo-500 text-white shadow-sm"
                                      : "bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200"
                                  }`}
                                >
                                  <IconComponent className={`w-3.5 h-3.5 ${b.color}`} />
                                  <span>{b.label.split(" ")[0]}</span>
                                </button>
                              );
                            })}
                          </div>

                          {thumbBadgeType !== "none" && (
                            <input
                              type="text"
                              value={thumbBadgeLabel}
                              onChange={(e) => setThumbBadgeLabel(e.target.value)}
                              placeholder="뱃지 문구 입력"
                              maxLength={10}
                              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                            />
                          )}
                        </div>

                        {/* 3. Headline & Punchline Typography */}
                        <div className="space-y-3">
                          <label className="text-xs font-bold text-slate-300 block flex items-center gap-1.5">
                            <Type className="w-3.5 h-3.5 text-indigo-400" />
                            3. 고대비 백플레이트 문구 수정
                          </label>

                          <div>
                            <span className="text-[11px] text-slate-400 mb-1 block">
                              상단 메인 헤드라인 (최대 16자)
                            </span>
                            <input
                              type="text"
                              value={thumbTitle}
                              onChange={(e) => setThumbTitle(e.target.value)}
                              placeholder="예: 3초 만에 문 여는 법"
                              maxLength={18}
                              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-bold transition"
                            />
                          </div>

                          <div>
                            <span className="text-[11px] text-slate-400 mb-1 block">
                              하단 강조 펀치라인 (원색 자막 완벽 커버, 최대 16자)
                            </span>
                            <input
                              type="text"
                              value={thumbHook}
                              onChange={(e) => setThumbHook(e.target.value)}
                              placeholder="예: 모르면 100% 갇힙니다"
                              maxLength={18}
                              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-bold transition"
                            />
                          </div>
                        </div>

                        {/* 4. Color Style Preset */}
                        <div>
                          <label className="text-xs font-bold text-slate-300 block mb-2 flex items-center gap-1.5">
                            <Palette className="w-3.5 h-3.5 text-purple-400" />
                            4. 타이포 컬러 스타일
                          </label>
                          <div className="grid grid-cols-3 gap-2">
                            {[
                              { id: "yellow_on_black", name: "🟡 옐로우 바", desc: "검정 박스 + 네온 옐로우" },
                              { id: "black_on_yellow", name: "⚡ 반전 형광 바", desc: "형광 옐로우 + 블랙" },
                              { id: "white_on_red", name: "🔴 경고 레드 바", desc: "레드 박스 + 화이트" },
                            ].map((s) => (
                              <button
                                key={s.id}
                                type="button"
                                onClick={() => setThumbHeadlineStyle(s.id as any)}
                                className={`py-2 px-2.5 rounded-xl border text-left transition ${
                                  thumbHeadlineStyle === s.id
                                    ? "bg-slate-800 border-indigo-500 text-white shadow-sm"
                                    : "bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200"
                                }`}
                              >
                                <div className="text-xs font-bold text-white">{s.name}</div>
                                <div className="text-[10px] text-slate-500 truncate">{s.desc}</div>
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Apply Final Button */}
                        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-end gap-2">
                          <button
                            onClick={() => setThumbEditorOpen(false)}
                            className="py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition"
                          >
                            닫기
                          </button>
                          <button
                            onClick={async () => {
                              await handleRenderThumbnail();
                              setThumbEditorOpen(false);
                            }}
                            disabled={thumbIsRendering}
                            className="py-2.5 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg transition"
                          >
                            <CheckCircle2 className="w-4 h-4" />
                            대표 썸네일로 확정 적용
                          </button>
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

      {/* Global Floating Background Task Dock */}
      {(isAnalyzing || isRendering) && (() => {
        const targetStep = isRendering ? 4 : 3;
        const isAlreadyThere = activeTab === "studio" && currentStep === targetStep;

        return (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-[92%] sm:w-auto min-w-[360px] max-w-xl glass-panel bg-slate-950/95 border border-indigo-500/40 shadow-2xl shadow-indigo-950/80 rounded-2xl p-3.5 backdrop-blur-xl animate-in slide-in-from-bottom duration-300">
            <div className="flex items-center justify-between gap-4">
              <div
                className="flex items-center gap-3 min-w-0 cursor-pointer"
                onClick={() => {
                  setActiveTab("studio");
                  setCurrentStep(targetStep);
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500/20 to-indigo-600/20 border border-rose-500/40 flex items-center justify-center shrink-0">
                  <Loader2 className="w-5 h-5 text-rose-400 animate-spin" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold text-rose-300 uppercase tracking-wider">
                      {isRendering ? "백그라운드 렌더링 작업 중" : "AI 하이라이트 분석 중"}
                    </span>
                    <span className="text-[11px] font-mono px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold">
                      {isRendering ? `${renderProgress}%` : `${analyzeProgress}%`}
                    </span>
                  </div>
                  <p className="text-xs text-white font-medium truncate mt-0.5 max-w-[260px] sm:max-w-[320px]">
                    {isRendering ? renderMessage : analyzeMessage}
                  </p>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 mt-2 overflow-hidden border border-slate-800">
                    <div
                      className="bg-gradient-to-r from-rose-500 via-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-300 shadow-sm"
                      style={{ width: `${isRendering ? renderProgress : analyzeProgress}%` }}
                    />
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  setActiveTab("studio");
                  setCurrentStep(targetStep);
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold shrink-0 shadow-md flex items-center gap-1.5 transition ${
                  isAlreadyThere
                    ? "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 shadow-slate-900/50"
                    : "bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-indigo-600/30"
                }`}
                title={
                  isAlreadyThere
                    ? "현재 진행 화면의 상단 진행 카드로 스크롤합니다."
                    : "현재 작업이 진행 중인 스튜디오 스텝으로 이동합니다."
                }
              >
                <span>{isAlreadyThere ? "진행 위치로 스크롤" : "작업 스텝으로 이동"}</span>
                <ChevronRight className={`w-3.5 h-3.5 ${isAlreadyThere ? "-rotate-90 transition-transform" : ""}`} />
              </button>
            </div>
          </div>
        );
      })()}

      {/* Global Completion Toast Notification */}
      {completionToast && (
        <div className="fixed top-20 right-6 z-50 max-w-sm w-full glass-panel bg-slate-950/95 border border-emerald-500/40 shadow-2xl shadow-emerald-950/60 rounded-2xl p-4 backdrop-blur-xl animate-in slide-in-from-top duration-300">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shrink-0 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                  {completionToast.title}
                </h4>
                <button
                  onClick={() => setCompletionToast(null)}
                  className="text-slate-400 hover:text-white p-0.5 rounded transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-slate-300 mt-1 leading-snug">
                {completionToast.message}
              </p>
              <div className="mt-3 flex items-center gap-2">
                {completionToast.type === "render" ? (
                  <button
                    onClick={() => {
                      setActiveTab("gallery");
                      setCompletionToast(null);
                    }}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1 shadow-md shadow-emerald-600/30"
                  >
                    <FolderOpen className="w-3.5 h-3.5" />
                    <span>완성 보관함에서 확인</span>
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      setActiveTab("studio");
                      setCurrentStep(3);
                      setCompletionToast(null);
                    }}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition flex items-center gap-1 shadow-md shadow-indigo-600/30"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>추천 구간 확인</span>
                  </button>
                )}
                <button
                  onClick={() => setCompletionToast(null)}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
                >
                  닫기
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
