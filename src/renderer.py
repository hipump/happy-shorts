import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Callable
from src.models import Highlight, Transcript, VideoMetadata, Word
from src.templates import ShortsTemplate, get_template
from src.framing import build_framing_filter
from src.effects import render_template_background, render_top_header, generate_subtitle_track

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def render_short(
    metadata: Optional[VideoMetadata] = None,
    highlight: Optional[Highlight] = None,
    transcript: Optional[Transcript] = None,
    output_path: str = "",
    template: Optional[ShortsTemplate] = None,
    template_id: str = "browser_window",
    layout_mode: Optional[str] = None,
    show_badge: bool = True,
    badge_style: str = "gold_pill",
    badge_prefix: str = "[TIP]",
    show_subtitles: bool = True,
    subtitle_style: Optional[str] = None,
    active_color: tuple = (255, 230, 0),
    normal_color: tuple = (255, 255, 255),
    font_name: str = "black_han_sans",
    show_progress_bar: bool = False,
    normalize_audio: bool = True,
    video_path: Optional[str] = None,
    aspect_ratio: str = "9:16",
    remove_subtitles: bool = False,
    filter_fillers: bool = True,
    callback: Optional[Callable[[int, str], None]] = None,
    **kwargs
) -> str:
    """
    Renders a complete, professional, viral-ready YouTube Short with:
    - Rich Graphic Template Canvas (News Portal, macOS Browser Window, Neon Magazine, Canva Minimal)
    - Aspect Ratio: "9:16" (1080x1920) or "16:9" (1920x1080)
    - Face tracking center adjustment for horizontal sources converted to 9:16
    - Source burned-in subtitle removal (delogo inpainting)
    - 2-tier Punch Headline with Highlighter Marker Tape
    - Structured containers & bullet summary cards
    - Word-by-word kinetic subtitles with double stroke & highlighter tape
    - Loudness-normalized audio (-14 LUFS)
    """
    if metadata is None:
        eff_vp = str(video_path or kwargs.get("video_path", ""))
        if not eff_vp:
            raise ValueError("Either 'metadata' or 'video_path' must be provided to render_short")
        import cv2
        cap = cv2.VideoCapture(eff_vp)
        vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
        vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
        vdur = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0) / max(1.0, float(cap.get(cv2.CAP_PROP_FPS) or 30))
        cap.release()
        metadata = VideoMetadata(
            video_id=Path(eff_vp).stem,
            title=Path(eff_vp).stem,
            duration=vdur,
            width=vw,
            height=vh,
            local_path=eff_vp,
            source="Local File",
            is_url=False
        )

    if highlight is None:
        raise ValueError("'highlight' must be provided to render_short")

    if transcript is None:
        transcript = Transcript(segments=[], text="", language="ko", duration=0.0)

    clip_id = f"clip_{highlight.id}_{int(highlight.start_time)}"
    clip_temp_dir = TEMP_DIR / clip_id
    clip_temp_dir.mkdir(parents=True, exist_ok=True)

    if template is None:
        template = get_template(template_id)

    # Allow parameter overrides if explicitly provided
    eff_layout = layout_mode if layout_mode else template.layout_type
    eff_sub_style = subtitle_style if subtitle_style else template.subtitle_style
    eff_active_col = active_color if active_color != (255, 230, 0) else template.active_color
    eff_normal_col = normal_color if normal_color != (255, 255, 255) else template.normal_color
    eff_font = font_name if font_name != "black_han_sans" else template.font_name

    start_time = highlight.start_time
    end_time = highlight.end_time
    duration = max(1.0, round(end_time - start_time, 2))

    is_landscape = (aspect_ratio == "16:9")
    canvas_w = 1920 if is_landscape else 1080
    canvas_h = 1080 if is_landscape else 1920

    # 1. Collect and adjust word timestamps relative to clip start
    if callback:
        callback(20, "클립 타임라인 및 트랜스크립트 싱크 분석 중...")

    clip_words = []
    for seg in transcript.segments:
        for w in seg.words:
            if w.end > start_time and w.start < end_time:
                rel_start = max(0.0, round(w.start - start_time, 2))
                rel_end = min(duration, round(w.end - start_time, 2))
                clip_words.append(Word(
                    word=w.word,
                    start=rel_start,
                    end=rel_end
                ))

    # If no word timestamps, fallback to segment text
    if not clip_words:
        for seg in transcript.segments:
            if seg.end > start_time and seg.start < end_time:
                rel_start = max(0.0, round(seg.start - start_time, 2))
                rel_end = min(duration, round(seg.end - start_time, 2))
                clip_words.append(Word(
                    word=seg.text,
                    start=rel_start,
                    end=rel_end
                ))

    input_args = [
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", metadata.local_path
    ]
    filter_chains = []
    next_input_idx = 1

    ratio_desc = "16:9 가로 와이드" if is_landscape else "9:16 세로 쇼츠"
    if callback:
        sub_info = " (원본 자막 AI 제거 포함)" if remove_subtitles else ""
        callback(35, f"{ratio_desc} 비주얼 프레이밍 & 템플릿 [{template.name}] 캔버스 합성 중...{sub_info}")

    # 2. Template Background or Framing Filter
    if is_landscape:
        # 16:9 Widescreen video framing
        base_filter, current_label = build_framing_filter(
            layout_mode=eff_layout,
            orig_width=metadata.width,
            orig_height=metadata.height,
            video_path=metadata.local_path,
            start_time=start_time,
            end_time=end_time,
            aspect_ratio="16:9",
            remove_subtitles=remove_subtitles
        )
        filter_chains.append(base_filter)

        # Optional Top Header for 16:9 widescreen
        if show_badge and template.badge_style != "none":
            badge_png = str(clip_temp_dir / "badge.png")
            render_top_header(
                title=highlight.title,
                hook_text=highlight.hook_text,
                output_path=badge_png,
                clip_idx=highlight.id,
                badge_style=template.badge_style,
                badge_prefix=template.badge_prefix,
                canvas_w=1920,
                canvas_h=1080
            )
            input_args.extend(["-loop", "1", "-t", "4.0", "-i", badge_png])
            badge_idx = next_input_idx
            next_input_idx += 1
            filter_chains.append(f"[{current_label}][{badge_idx}:v]overlay=0:0:enable='lte(t,3.5)'[v_badge]")
            current_label = "v_badge"

    elif eff_layout == "smart_crop":
        base_filter, current_label = build_framing_filter(
            layout_mode="smart_crop",
            orig_width=metadata.width,
            orig_height=metadata.height,
            video_path=metadata.local_path,
            start_time=start_time,
            end_time=end_time,
            aspect_ratio="9:16",
            remove_subtitles=remove_subtitles
        )
        filter_chains.append(base_filter)

        # Optional Top Header for smart crop
        if show_badge and template.badge_style != "none":
            badge_png = str(clip_temp_dir / "badge.png")
            render_top_header(
                title=highlight.title,
                hook_text=highlight.hook_text,
                output_path=badge_png,
                clip_idx=highlight.id,
                badge_style=template.badge_style,
                badge_prefix=template.badge_prefix,
                canvas_w=1080,
                canvas_h=1920
            )
            input_args.extend(["-loop", "1", "-t", "4.0", "-i", badge_png])
            badge_idx = next_input_idx
            next_input_idx += 1
            filter_chains.append(f"[{current_label}][{badge_idx}:v]overlay=0:0:enable='lte(t,3.5)'[v_badge]")
            current_label = "v_badge"
    else:
        # Pre-render full graphic background for 9:16 template layouts
        bg_png = str(clip_temp_dir / "template_bg.png")
        render_template_background(
            template=template,
            highlight=highlight,
            metadata=metadata,
            output_path=bg_png,
            canvas_w=1080,
            canvas_h=1920
        )
        input_args.extend(["-loop", "1", "-t", str(duration), "-i", bg_png])
        bg_idx = next_input_idx
        next_input_idx += 1

        base_filter, current_label = build_framing_filter(
            layout_mode=eff_layout,
            orig_width=metadata.width,
            orig_height=metadata.height,
            video_path=metadata.local_path,
            start_time=start_time,
            end_time=end_time,
            video_box=template.video_box,
            bg_input_idx=bg_idx,
            aspect_ratio="9:16",
            remove_subtitles=remove_subtitles
        )
        filter_chains.append(base_filter)

    # 3. Subtitles
    if show_subtitles and eff_sub_style != "none" and clip_words:
        sub_y = int(canvas_h * 0.82) if is_landscape else template.subtitle_y
        if sub_y > 0:
            if callback:
                callback(55, f"키네틱 타이포그래피 자막 시퀀스 렌더링 중 (스타일: {eff_sub_style})...")
            sub_concat_file, _ = generate_subtitle_track(
                words=clip_words,
                clip_duration=duration,
                output_dir=str(clip_temp_dir / "subs"),
                style=eff_sub_style,
                active_color=eff_active_col,
                normal_color=eff_normal_col,
                marker_color=template.marker_color if eff_layout in ["neon_magazine", "news_portal"] else None,
                font_name=eff_font,
                max_words_per_group=4 if is_landscape else 3,
                canvas_w=canvas_w,
                canvas_h=canvas_h,
                y_center=sub_y,
                filter_fillers=filter_fillers
            )
            input_args.extend(["-f", "concat", "-safe", "0", "-i", sub_concat_file])
            sub_input_idx = next_input_idx
            next_input_idx += 1

            filter_chains.append(f"[{current_label}][{sub_input_idx}:v]overlay=0:0:shortest=1[v_sub]")
            current_label = "v_sub"

    full_filter_complex = ";".join(filter_chains)

    # 4. Build & Run FFmpeg Command
    if callback:
        callback(72, "FFmpeg 하드웨어 가속 비디오 인코딩 & -14 LUFS 오디오 노멀라이징 중...")

    cmd = ["ffmpeg", "-y"]
    cmd.extend(input_args)
    cmd.extend([
        "-filter_complex", full_filter_complex,
        "-map", f"[{current_label}]",
        "-map", "0:a?"
    ])

    if normalize_audio:
        cmd.extend(["-af", "loudnorm=I=-14:LRA=11:TP=-1.5"])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(duration),
        output_path
    ])

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg rendering failed: {result.stderr[-1000:]}")

    if callback:
        callback(88, "비디오 스트림 인코딩 완료 및 임시 리소스 정리 중...")

    # Clean up temp frames for this clip
    shutil.rmtree(clip_temp_dir, ignore_errors=True)

    return output_path

