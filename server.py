import os
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
job_queues: Dict[str, asyncio.Queue] = {}

def get_job_queue(job_id: str) -> asyncio.Queue:
    if job_id not in job_queues:
        job_queues[job_id] = asyncio.Queue()
    return job_queues[job_id]

async def emit_job_event(job_id: str, data: dict):
    if job_id in jobs:
        jobs[job_id].update(data)
    q = get_job_queue(job_id)
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
    highlight: Dict[str, Any] = Field(..., description="선택된 하이라이트 정보")
    template_id: str = Field(default="browser_window", description="템플릿 ID")
    layout_override: Optional[str] = None
    subtitle_style: Optional[str] = None
    show_badge: bool = True
    show_subtitles: bool = True
    aspect_ratio: str = Field(default="9:16", description="영상 화면 비율 (9:16 또는 16:9)")
    remove_subtitles: bool = Field(default=False, description="원본 자막 삭제 (ai 처리라서 일부 뭉개짐이 있을 수 있음)")
    filter_fillers: bool = Field(default=True, description="추임새/말버릇(네, 어, 음 등) 자막 자동 제거")
    target_filename: Optional[str] = None

# Endpoints
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

@app.get("/api/outputs")
def list_outputs():
    """Returns all generated shorts in output directory."""
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

            # Matching cover jpg
            cover_path = OUTPUT_DIR / f"cover_{base_key}.jpg"
            cover_url = f"/media/output/{cover_path.name}" if cover_path.exists() else None

            items.append({
                "filename": f.name,
                "filepath": str(f),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified_at": stat.st_mtime,
                "stream_url": f"/media/output/{f.name}",
                "cover_url": cover_url,
                "seo_content": seo_info
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
    try:
        await emit_job_event(job_id, {
            "status": "running",
            "progress": 10,
            "step": 1,
            "message": "영상 소스 준비 및 다운로드 확인 중..."
        })

        # Run in threadpool so event loop remains responsive
        loop = asyncio.get_event_loop()
        metadata: VideoMetadata = await loop.run_in_executor(None, prepare_source, req.source)

        stream_url = ""
        if str(metadata.local_path).startswith(str(DOWNLOADS_DIR)):
            rel_name = Path(metadata.local_path).name
            stream_url = f"/media/downloads/{rel_name}"

        await emit_job_event(job_id, {
            "status": "running",
            "progress": 30,
            "step": 2,
            "message": f"음성 인식 및 단어 단위 타임스탬프 추출 중 (Whisper: {req.whisper_model})...",
            "video_metadata": {
                "title": metadata.title,
                "duration": metadata.duration,
                "width": metadata.width,
                "height": metadata.height,
                "local_path": metadata.local_path,
                "stream_url": stream_url
            }
        })

        transcript: Transcript = await loop.run_in_executor(
            None,
            lambda: transcribe_video(metadata.local_path, model_size=req.whisper_model)
        )

        await emit_job_event(job_id, {
            "status": "running",
            "progress": 65,
            "step": 3,
            "message": f"AI 하이라이트 문맥 분석 및 OpusClip 4기둥 바이럴 채점 중 (Ollama: {req.llm_model})...",
            "transcript_summary": {
                "language": transcript.language,
                "duration": transcript.duration,
                "segment_count": len(transcript.segments),
                "total_words": sum(len(s.words) for s in transcript.segments)
            }
        })

        detect_count = max(3, req.clips_count)
        target_dur = (req.min_dur, req.max_dur)

        highlights: List[Highlight] = await loop.run_in_executor(
            None,
            lambda: detect_highlights(
                transcript=transcript,
                model_name=req.llm_model,
                max_count=detect_count,
                target_duration_range=target_dur,
                video_path=metadata.local_path
            )
        )

        highlights.sort(key=lambda h: h.virality_score, reverse=True)
        for i, h in enumerate(highlights, 1):
            h.id = i

        hl_dicts = [h.model_dump() for h in highlights]

        await emit_job_event(job_id, {
            "status": "completed",
            "progress": 100,
            "step": 4,
            "message": f"AI 분석 완료! 총 {len(highlights)}개 고득점 후보 구간 도출됨",
            "highlights": hl_dicts
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
    try:
        await emit_job_event(job_id, {
            "status": "running",
            "progress": 10,
            "message": "렌더링 작업 준비 중 (오디오 및 자막 싱크 정렬)..."
        })

        loop = asyncio.get_event_loop()

        metadata: VideoMetadata = await loop.run_in_executor(None, prepare_source, req.source)
        transcript: Transcript = await loop.run_in_executor(
            None,
            lambda: transcribe_video(metadata.local_path, model_size="large-v3-turbo")
        )

        h_data = req.highlight
        h_obj = Highlight(**h_data)

        # Template setup
        tpl = get_template(req.template_id)
        if req.layout_override:
            tpl.layout_type = req.layout_override
        if req.subtitle_style:
            tpl.subtitle_style = req.subtitle_style
        if not req.show_badge:
            tpl.badge_style = "none"

        safe_title = sanitize_filename(metadata.title)
        if req.target_filename:
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

        ratio_tag = "16:9 가로" if req.aspect_ratio == "16:9" else "9:16 세로"
        sub_tag = " (원본 자막 AI 제거 적용)" if req.remove_subtitles else ""
        await emit_job_event(job_id, {
            "status": "running",
            "progress": 35,
            "message": f"{ratio_tag} 비주얼 리프레임 & 템플릿 [{tpl.name}] 합성 중...{sub_tag}"
        })

        # Render clip
        render_res = await loop.run_in_executor(
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
                filter_fillers=req.filter_fillers
            )
        )

        await emit_job_event(job_id, {
            "status": "running",
            "progress": 85,
            "message": "2026 알고리즘 최적화 유튜브 메타데이터 생성 중..."
        })

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

        await emit_job_event(job_id, {
            "status": "completed",
            "progress": 100,
            "message": "쇼츠 렌더링 완성!",
            "result": {
                "filename": out_filename,
                "filepath": str(out_path),
                "stream_url": f"/media/output/{out_filename}",
                "cover_url": cover_url,
                "seo_content": seo_content,
                "virality_score": h_obj.virality_score,
                "title": h_obj.title,
                "hook_text": h_obj.hook_text
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
        q = get_job_queue(job_id)
        # First send current state
        yield {"data": json.dumps(jobs[job_id], ensure_ascii=False)}
        while True:
            try:
                data = await asyncio.wait_for(q.get(), timeout=25.0)
                yield {"data": json.dumps(data, ensure_ascii=False)}
                if data.get("status") in ["completed", "failed"]:
                    break
            except asyncio.TimeoutError:
                # Keep-alive ping
                yield {"event": "ping", "data": "keep-alive"}

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    print("🚀 Happy Shorts 로컬 API 서버 시작 (http://localhost:8000)")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
