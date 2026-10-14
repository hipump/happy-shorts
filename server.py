import os
import re
import sys
import json
import uuid
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any

import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from datetime import datetime
from src.models import VideoMetadata, Transcript, Highlight
from src.templates import TEMPLATES, get_template, ShortsTemplate
from src.downloader import prepare_source
from src.transcriber import transcribe_video
from src.highlighter import detect_highlights
from src.renderer import render_short
from src.pipeline import generate_youtube_metadata_file, sanitize_filename, get_unique_output_paths

app = FastAPI(
    title="Happy Shorts AI Studio API",
    description="로컬 100% 무료 AI 쇼츠 자동 생성기 웹 API (Ollama + Faster-Whisper + FFmpeg)",
    version="2.0.0"
)

# CORS Middleware for Next.js (port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file paths
BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Mount static media directories
app.mount("/media/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")
app.mount("/media/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.mount("/media/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# In-memory job state & event queues
jobs: Dict[str, Dict[str, Any]] = {}
job_subscribers: Dict[str, List[asyncio.Queue]] = {}

def add_job_subscriber(job_id: str) -> asyncio.Queue:
    if job_id not in job_subscribers:
        job_subscribers[job_id] = []
    q = asyncio.Queue()
    job_subscribers[job_id].append(q)
    return q

def remove_job_subscriber(job_id: str, q: asyncio.Queue):
    if job_id in job_subscribers and q in job_subscribers[job_id]:
        job_subscribers[job_id].remove(q)
        if not job_subscribers[job_id]:
            del job_subscribers[job_id]

async def emit_job_event(job_id: str, data: dict):
    if job_id in jobs:
        jobs[job_id].update(data)
    subscribers = list(job_subscribers.get(job_id, []))
    for q in subscribers:
        await q.put(data)

# Pydantic Models
class AnalyzeRequest(BaseModel):
    source: str = Field(..., description="유튜브 URL 또는 로컬 파일 경로")
    clips_count: int = Field(default=3, description="분석할 하이라이트 후보 개수")
    min_dur: int = Field(default=30, description="최소 쇼츠 길이 (초)")
    max_dur: int = Field(default=50, description="최대 쇼츠 길이 (초)")
    whisper_model: str = Field(default="large-v3-turbo", description="Whisper STT 모델")
    llm_model: str = Field(default="qwen2.5:14b", description="Ollama LLM 모델")

class RenderRequest(BaseModel):
    source: str = Field(..., description="원본 영상 소스")
    highlight: Optional[Dict[str, Any]] = Field(default=None, description="선택된 단일 하이라이트 정보")
    highlights: Optional[List[Dict[str, Any]]] = Field(default=None, description="복수 하이라이트 목록 (일괄 렌더링)")
    template_id: str = Field(default="browser_window", description="템플릿 ID")
    layout_override: Optional[str] = None
    subtitle_style: Optional[str] = None
    show_badge: bool = True
    show_subtitles: bool = True
    aspect_ratio: str = Field(default="9:16", description="영상 화면 비율 (9:16 또는 16:9)")
    remove_subtitles: bool = Field(default=False, description="원본 자막 삭제 (ai 처리라서 일부 뭉개짐이 있을 수 있음)")
    filter_fillers: bool = Field(default=True, description="추임새/말버릇(네, 어, 음 등) 자막 자동 제거")
    bgm_track: str = Field(default="auto", description="배경음악 트랙 (auto, lofi, tech, cinematic, none)")
    enable_sfx: bool = Field(default=True, description="효과음 (SFX: 훅 임팩트, 전환 우쉬, 키워드 딩)")
    color_grade: str = Field(default="vibrant", description="스튜디오 색감 보정 (vibrant, cinematic, clean, none)")
    dynamic_zoom: bool = Field(default=True, description="다이내믹 펀치인 줌")
    smart_keywords: bool = Field(default=True, description="스마트 키워드 자막 하이라이트")
    target_filename: Optional[str] = None

# Endpoints
@app.get("/api/audio-presets")
def list_audio_presets():
    """Returns available BGM tracks and SFX capabilities."""
    return {
        "bgm_tracks": [
            {"id": "auto", "name": "✨ 템플릿 맞춤 자동 선곡", "description": "템플릿 무드에 최적화된 BGM 자동 매칭"},
            {"id": "lofi", "name": "☕ 로파이 팁스 (Lofi Study)", "description": "지식, 팁, 브이로그, 인터뷰에 어울리는 잔잔한 비트"},
            {"id": "tech", "name": "⚡ 모던 테크 비트 (Tech Synth)", "description": "테크, 코딩, 주식, 트렌드에 어울리는 에너지 비트"},
            {"id": "cinematic", "name": "🎬 시네마틱 펄스 (Cinematic)", "description": "뉴스, 속보, 다큐멘터리에 어울리는 웅장한 펄스"},
            {"id": "none", "name": "🔇 BGM 끄기 (음소거)", "description": "배경음악 없이 원본 음성만 유지"}
        ],
        "color_grades": [
            {"id": "vibrant", "name": "🌈 스튜디오 비비드 (추천)", "description": "선명한 대비와 생동감 넘치는 채도 + 엣지 샤프닝"},
            {"id": "cinematic", "name": "🎞️ 시네마틱 필름", "description": "깊이 있는 영화 톤 콘트라스트"},
            {"id": "clean", "name": "✨ 클린 샤프닝", "description": "색감 왜곡 없이 또렷한 윤곽선 보정"},
            {"id": "none", "name": "원본 유지", "description": "원본 영상 색감 그대로"}
        ],
        "sfx_features": [
            "훅 시작 임팩트 사운드 (0.18초 펀치 힛)",
            "장면/배지 전환 우쉬 (3.2초 스위시)",
            "스마트 키워드 자막 차임 딩 (숫자/바이럴 단어 강조음)"
        ]
    }
@app.get("/api/status")
def get_system_status():
    """Checks local Ollama service, GPU/device and default models."""
    ollama_ok = False
    models_available = []
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=1.5)
        if res.status_code == 200:
            ollama_ok = True
            models_available = [m["name"] for m in res.json().get("models", [])]
    except Exception:
        pass

    return {
        "status": "online",
        "ollama_connected": ollama_ok,
        "available_llm_models": models_available,
        "active_llm_default": "qwen2.5:14b" if "qwen2.5:14b" in str(models_available) else "qwen2.5:7b",
        "active_whisper_default": "large-v3-turbo",
        "output_count": len(list(OUTPUT_DIR.glob("*.mp4"))),
        "downloads_count": len(list(DOWNLOADS_DIR.glob("*.mp4")))
    }

@app.get("/api/templates")
def list_templates():
    """Returns available shorts templates with design metadata."""
    result = []
    seen = set()
    for tpl_id, t in TEMPLATES.items():
        if t.id in seen:
            continue
        seen.add(t.id)
        result.append({
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "description": t.description,
            "layout_type": t.layout_type,
            "badge_style": t.badge_style,
            "badge_prefix": t.badge_prefix,
            "subtitle_style": t.subtitle_style,
            "active_color": list(t.active_color),
            "normal_color": list(t.normal_color),
            "font_name": t.font_name,
            "sub_font_name": getattr(t, "sub_font_name", "pretendard"),
            "video_box": list(t.video_box)
        })
    return {"templates": result}

@app.get("/api/recent-videos")
def list_recent_videos():
    """Returns cached videos in downloads directory for instant reuse."""
    items = []
    for f in DOWNLOADS_DIR.glob("*.mp4"):
        if f.is_file() and f.stat().st_size > 1024:
            stat = f.stat()
            items.append({
                "filename": f.name,
                "filepath": str(f),
                "size_mb": round(stat.st_size / (1024 * 1024), 1),
                "modified_at": stat.st_mtime,
                "stream_url": f"/media/downloads/{f.name}"
            })
    items.sort(key=lambda x: x["modified_at"], reverse=True)
    return {"videos": items}

video_meta_cache: Dict[str, dict] = {}

def get_cached_video_meta(video_path: Path) -> dict:
    key = str(video_path)
    try:
        mtime = video_path.stat().st_mtime
    except Exception:
        mtime = 0.0
    if key in video_meta_cache and video_meta_cache[key].get("mtime") == mtime:
        return video_meta_cache[key]

    width = 1080
    height = 1920
    duration = 30.0
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-of", "csv=s=x:p=0", str(video_path)
        ], text=True, timeout=2.0).strip().split("x")
        if len(out) >= 2:
            width = int(out[0])
            height = int(out[1])
        if len(out) >= 3 and out[2]:
            duration = round(float(out[2]), 1)
    except Exception:
        pass

    aspect_ratio = "16:9" if width > height else "9:16"
    data = {
        "mtime": mtime,
        "width": width,
        "height": height,
        "duration": duration,
        "aspect_ratio": aspect_ratio
    }
    video_meta_cache[key] = data
    return data

@app.get("/api/outputs")
def list_outputs():
    """Returns all generated shorts in output directory with rich metadata."""
    items = []
    for f in OUTPUT_DIR.glob("*.mp4"):
        if f.is_file():
            stat = f.stat()
            stem = f.stem
            base_key = stem[6:] if stem.startswith("short_") else stem
            
            # Matching txt file
            txt_path = OUTPUT_DIR / f"shorts_info_{base_key}.txt"
            txt_fallback = OUTPUT_DIR / f"{stem}.txt"
            seo_info = ""
            if txt_path.exists():
                try:
                    seo_info = txt_path.read_text(encoding="utf-8")
                except Exception:
                    pass
            elif txt_fallback.exists():
                try:
                    seo_info = txt_fallback.read_text(encoding="utf-8")
                except Exception:
                    pass

            # Matching cover jpg (auto-generate if missing)
            cover_path = OUTPUT_DIR / f"cover_{base_key}.jpg"
            if not cover_path.exists():
                try:
                    subprocess.run([
                        "ffmpeg", "-y", "-ss", "00:00:01.0", "-i", str(f),
                        "-vframes", "1", "-q:v", "2", str(cover_path)
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                except Exception:
                    pass

            cover_url = f"/media/output/{cover_path.name}" if cover_path.exists() else None

            # Video technical metadata
            vmeta = get_cached_video_meta(f)

            # Parse SEO content for rich display
            title = ""
            virality_score = None
            tags = []
            if seo_info:
                score_m = re.search(r"바이럴\s*점수:\s*(\d+)점", seo_info)
                if score_m:
                    virality_score = int(score_m.group(1))

                title_m = re.search(r"1안:\s*(.+)", seo_info)
                if title_m:
                    title = title_m.group(1).strip()

                tags = list(dict.fromkeys(re.findall(r"#[\w가-힣]+", seo_info)))[:6]

            if not title:
                cleaned = re.sub(r"^(short_|shorts_)", "", stem)
                cleaned = cleaned.replace("_", " ").strip()
                title = cleaned if cleaned else f.name

            items.append({
                "filename": f.name,
                "filepath": str(f),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified_at": stat.st_mtime,
                "stream_url": f"/media/output/{f.name}",
                "cover_url": cover_url,
                "seo_content": seo_info,
                "title": title,
                "virality_score": virality_score,
                "tags": tags,
                "duration": vmeta["duration"],
                "aspect_ratio": vmeta["aspect_ratio"],
                "width": vmeta["width"],
                "height": vmeta["height"]
            })
    items.sort(key=lambda x: x["modified_at"], reverse=True)
    return {"outputs": items}

@app.post("/api/open-folder")
def open_output_folder():
    """Opens output folder in Mac Finder."""
    try:
        subprocess.run(["open", str(OUTPUT_DIR)], check=True)
        return {"success": True, "message": "Finder 열기 완료"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Long-running background analyze worker
async def run_analysis_task(job_id: str, req: AnalyzeRequest):
    loop = asyncio.get_event_loop()

    def make_progress_cb(step_num: int):
        def cb(pct: int, msg: str):
            payload = {
                "status": "running",
                "progress": max(5, min(99, int(pct))),
                "step": step_num,
                "message": msg
            }
            asyncio.run_coroutine_threadsafe(emit_job_event(job_id, payload), loop)
        return cb

    try:
        await emit_job_event(job_id, {
            "status": "running",
            "progress": 5,
            "step": 1,
            "message": "AI 분석 세션을 시작하고 영상 스트림을 연결하는 중..."
        })

        # Run in threadpool so event loop remains responsive
        prep_cb = make_progress_cb(1)
        metadata: VideoMetadata = await loop.run_in_executor(
            None,
            lambda: prepare_source(req.source, callback=prep_cb)
        )

        stream_url = ""
        local_p = Path(metadata.local_path).resolve()
        downloads_res = DOWNLOADS_DIR.resolve()
        output_res = OUTPUT_DIR.resolve()

        if downloads_res in local_p.parents or local_p.parent == downloads_res or (DOWNLOADS_DIR / local_p.name).exists():
            stream_url = f"/media/downloads/{local_p.name}"
        elif output_res in local_p.parents or local_p.parent == output_res or (OUTPUT_DIR / local_p.name).exists():
            stream_url = f"/media/output/{local_p.name}"
        elif local_p.exists():
            target_link = DOWNLOADS_DIR / local_p.name
            if not target_link.exists():
                try:
                    os.symlink(local_p, target_link)
                except Exception:
                    pass
            stream_url = f"/media/downloads/{local_p.name}"

        await emit_job_event(job_id, {
            "status": "running",
            "progress": 28,
            "step": 2,
            "message": f"음성 인식 및 단어 단위 타임스탬프 추출 시작 (Whisper: {req.whisper_model})...",
            "video_metadata": {
                "title": metadata.title,
                "duration": metadata.duration,
                "width": metadata.width,
                "height": metadata.height,
                "local_path": metadata.local_path,
                "stream_url": stream_url
            }
        })

        trans_cb = make_progress_cb(2)
        transcript: Transcript = await loop.run_in_executor(
            None,
            lambda: transcribe_video(metadata.local_path, model_size=req.whisper_model, callback=trans_cb)
        )

        await emit_job_event(job_id, {
            "status": "running",
            "progress": 65,
            "step": 3,
            "message": f"AI 하이라이트 문맥 분석 및 OpusClip 4기둥 바이럴 채점 준비 (대화 {len(transcript.segments)}개 구간)...",
            "transcript_summary": {
                "language": transcript.language,
                "duration": transcript.duration,
                "segment_count": len(transcript.segments),
                "total_words": sum(len(s.words) for s in transcript.segments)
            }
        })

        detect_count = max(3, req.clips_count)
        target_dur = (req.min_dur, req.max_dur)

        hl_cb = make_progress_cb(3)
        heartbeat_stop = asyncio.Event()

        async def llm_heartbeat():
            current_p = 71
            heartbeat_msgs = [
                f"Ollama LLM ({req.llm_model}) 심층 문맥 추론 및 바이럴 구간 탐색 중...",
                "OpusClip 4기둥 (후킹력, 스토리 흐름, 정보 가치, 트렌드성) 채점 중...",
                "시청 지속 시간(AVD) 극대화 및 이탈 방지 구간 탐색 중...",
                "한국어 문장 어미(~다, ~요, ~죠) 문법적 경계 스냅 연산 중...",
                "자연스러운 음성 연결을 위한 룸톤 오디오 패딩 보정 중..."
            ]
            idx = 0
            while not heartbeat_stop.is_set():
                try:
                    await asyncio.wait_for(heartbeat_stop.wait(), timeout=2.5)
                    break
                except asyncio.TimeoutError:
                    if current_p < 84:
                        current_p += 2
                        msg = heartbeat_msgs[idx % len(heartbeat_msgs)]
                        idx += 1
                        await emit_job_event(job_id, {
                            "status": "running",
                            "progress": current_p,
                            "step": 3,
                            "message": msg
                        })

        hb_task = asyncio.create_task(llm_heartbeat())
        try:
            highlights: List[Highlight] = await loop.run_in_executor(
                None,
                lambda: detect_highlights(
                    transcript=transcript,
                    model_name=req.llm_model,
                    max_count=detect_count,
                    target_duration_range=target_dur,
                    video_path=metadata.local_path,
                    callback=hl_cb
                )
            )
        finally:
            heartbeat_stop.set()
            await hb_task

        highlights.sort(key=lambda h: h.virality_score, reverse=True)
        for i, h in enumerate(highlights, 1):
            h.id = i

        hl_dicts = [h.model_dump() for h in highlights]

        await emit_job_event(job_id, {
            "status": "completed",
            "progress": 100,
            "step": 4,
            "message": f"AI 분석 완료! 총 {len(highlights)}개 고득점 후보 구간 도출됨",
            "highlights": hl_dicts,
            "video_metadata": {
                "title": metadata.title,
                "duration": metadata.duration,
                "width": metadata.width,
                "height": metadata.height,
                "local_path": metadata.local_path,
                "stream_url": stream_url
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        await emit_job_event(job_id, {
            "status": "failed",
            "progress": 0,
            "error": str(e)
        })

@app.post("/api/analyze")
async def start_analysis(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "type": "analyze",
        "status": "pending",
        "progress": 0,
        "source": req.source,
        "created_at": asyncio.get_event_loop().time()
    }
    background_tasks.add_task(run_analysis_task, job_id, req)
    return {"job_id": job_id, "status": "pending"}

# Long-running background render worker
async def run_render_task(job_id: str, req: RenderRequest):
    loop = asyncio.get_event_loop()

    def make_progress_cb(step_num: int):
        def cb(pct: int, msg: str):
            payload = {
                "status": "running",
                "progress": max(5, min(99, int(pct))),
                "step": step_num,
                "message": msg
            }
            asyncio.run_coroutine_threadsafe(emit_job_event(job_id, payload), loop)
        return cb

    try:
        await emit_job_event(job_id, {
            "status": "running",
            "progress": 8,
            "step": 1,
            "message": "렌더링 작업 준비 중 (오디오 및 자막 싱크 정렬)..."
        })

        metadata: VideoMetadata = await loop.run_in_executor(None, prepare_source, req.source)
        transcript: Transcript = await loop.run_in_executor(
            None,
            lambda: transcribe_video(metadata.local_path, model_size="large-v3-turbo")
        )

        # Determine target highlights list
        if req.highlights and len(req.highlights) > 0:
            target_highlights = [Highlight(**h) for h in req.highlights]
        elif req.highlight:
            target_highlights = [Highlight(**req.highlight)]
        else:
            raise ValueError("렌더링할 하이라이트 구간이 지정되지 않았습니다.")

        # Template setup
        tpl = get_template(req.template_id)
        if req.layout_override:
            tpl.layout_type = req.layout_override
        if req.subtitle_style:
            tpl.subtitle_style = req.subtitle_style
        if not req.show_badge:
            tpl.badge_style = "none"

        safe_title = sanitize_filename(metadata.title)
        ratio_tag = "16:9 가로" if req.aspect_ratio == "16:9" else "9:16 세로"
        sub_tag = " (원본 자막 AI 제거 적용)" if req.remove_subtitles else ""

        total_clips = len(target_highlights)
        rendered_results = []

        for clip_idx, h_obj in enumerate(target_highlights, 1):
            clip_base_pct = int(((clip_idx - 1) / total_clips) * 100)
            clip_span = max(1, int(100 / total_clips))

            def make_clip_progress_cb(stage_step: int):
                def cb(pct: int, msg: str):
                    overall_p = clip_base_pct + int((pct / 100) * clip_span)
                    overall_p = max(5, min(99, overall_p))
                    prefix = f"[{clip_idx}/{total_clips}번째 쇼츠] " if total_clips > 1 else ""
                    payload = {
                        "status": "running",
                        "progress": overall_p,
                        "step": stage_step,
                        "message": f"{prefix}{msg}"
                    }
                    asyncio.run_coroutine_threadsafe(emit_job_event(job_id, payload), loop)
                return cb

            prefix_msg = f"[{clip_idx}/{total_clips}번째 쇼츠] " if total_clips > 1 else ""
            await emit_job_event(job_id, {
                "status": "running",
                "progress": max(5, clip_base_pct + 4),
                "step": 2,
                "message": f"{prefix_msg}{ratio_tag} 비주얼 리프레임 & 템플릿 [{tpl.name}] 합성 준비 중...{sub_tag}"
            })

            if req.target_filename and total_clips == 1:
                target_stem = Path(req.target_filename).stem
                counter = 1
                cand_stem = target_stem
                while (OUTPUT_DIR / f"{cand_stem}.mp4").exists():
                    cand_stem = f"{target_stem}_{counter}"
                    counter += 1
                out_filename = f"{cand_stem}.mp4"
                base_key = cand_stem[6:] if cand_stem.startswith("short_") else cand_stem
                out_path = OUTPUT_DIR / out_filename
                cover_path = OUTPUT_DIR / f"cover_{base_key}.jpg"
                out_txt_path = OUTPUT_DIR / f"shorts_info_{base_key}.txt"
            else:
                out_video_str, out_cover_str, out_meta_str = get_unique_output_paths(OUTPUT_DIR, safe_title, h_obj.id)
                out_path = Path(out_video_str)
                out_filename = out_path.name
                cover_path = Path(out_cover_str)
                out_txt_path = Path(out_meta_str)

            render_cb = make_clip_progress_cb(3)
            await loop.run_in_executor(
                None,
                lambda: render_short(
                    metadata=metadata,
                    highlight=h_obj,
                    transcript=transcript,
                    template=tpl,
                    output_path=str(out_path),
                    show_subtitles=req.show_subtitles and tpl.subtitle_style != "none",
                    subtitle_style=tpl.subtitle_style,
                    active_color=tpl.active_color,
                    normal_color=tpl.normal_color,
                    font_name=tpl.font_name,
                    normalize_audio=True,
                    aspect_ratio=req.aspect_ratio,
                    remove_subtitles=req.remove_subtitles,
                    filter_fillers=req.filter_fillers,
                    bgm_track=req.bgm_track,
                    enable_sfx=req.enable_sfx,
                    color_grade=req.color_grade,
                    dynamic_zoom=req.dynamic_zoom,
                    smart_keywords=req.smart_keywords,
                    callback=render_cb
                )
            )

            # Generate YouTube SEO Text File
            await loop.run_in_executor(
                None,
                lambda: generate_youtube_metadata_file(
                    output_txt_path=str(out_txt_path),
                    highlight=h_obj,
                    metadata=metadata,
                    output_video_path=str(out_path)
                )
            )

            seo_content = ""
            if out_txt_path.exists():
                seo_content = out_txt_path.read_text(encoding="utf-8")

            # Extract high-res cover thumbnail
            try:
                await loop.run_in_executor(
                    None,
                    lambda: subprocess.run([
                        "ffmpeg", "-y", "-ss", "00:00:01.5", "-i", str(out_path),
                        "-vframes", "1", "-q:v", "2", str(cover_path)
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                )
            except Exception:
                pass

            cover_url = f"/media/output/{cover_path.name}" if cover_path.exists() else None

            rendered_results.append({
                "filename": out_filename,
                "filepath": str(out_path),
                "stream_url": f"/media/output/{out_filename}",
                "cover_url": cover_url,
                "seo_content": seo_content,
                "virality_score": h_obj.virality_score,
                "title": h_obj.title,
                "hook_text": h_obj.hook_text,
                "id": h_obj.id,
                "duration": h_obj.duration
            })

        await emit_job_event(job_id, {
            "status": "completed",
            "progress": 100,
            "step": 4,
            "message": f"총 {total_clips}개 쇼츠 일괄 렌더링 완성!" if total_clips > 1 else "쇼츠 렌더링 완성!",
            "result": rendered_results[0],
            "results": rendered_results
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        await emit_job_event(job_id, {
            "status": "failed",
            "progress": 0,
            "error": str(e)
        })

@app.post("/api/render")
async def start_render(req: RenderRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "type": "render",
        "status": "pending",
        "progress": 0,
        "created_at": asyncio.get_event_loop().time()
    }
    background_tasks.add_task(run_render_task, job_id, req)
    return {"job_id": job_id, "status": "pending"}

@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="해당 작업 ID를 찾을 수 없습니다.")
    return jobs[job_id]

@app.get("/api/jobs/{job_id}/events")
async def stream_job_events(job_id: str):
    """Server-Sent Events (SSE) real-time event stream for smooth progress."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="해당 작업 ID를 찾을 수 없습니다.")

    async def event_generator():
        q = add_job_subscriber(job_id)
        try:
            # First send current state immediately
            initial_state = dict(jobs.get(job_id, {}))
            yield {"data": json.dumps(initial_state, ensure_ascii=False)}

            if initial_state.get("status") in ["completed", "failed"]:
                return

            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield {"data": json.dumps(data, ensure_ascii=False)}
                    if data.get("status") in ["completed", "failed"]:
                        break
                except asyncio.TimeoutError:
                    current_status = jobs.get(job_id, {}).get("status")
                    if current_status in ["completed", "failed"]:
                        yield {"data": json.dumps(jobs[job_id], ensure_ascii=False)}
                        break
                    yield {"event": "ping", "data": "keep-alive"}
        finally:
            remove_job_subscriber(job_id, q)

    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Happy Shorts 로컬 API 서버 시작 (http://localhost:8000)")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
