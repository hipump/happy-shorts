import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Callable
from src.models import Highlight, Transcript, VideoMetadata, Word
from src.templates import ShortsTemplate, get_template
from src.framing import build_framing_filter
from src.effects import (
    render_template_background,
    render_top_header,
    generate_subtitle_track,
    render_keynote_stat_pill
)
from src.audio import build_audio_pipeline
from src.inpainting import LamaInpainter, inpaint_video_subtitles

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
    bgm_track: str = "auto",
    enable_sfx: bool = True,
    color_grade: str = "vibrant_tech",
    dynamic_zoom: bool = True,
    smart_keywords: bool = True,
    bounce_animation: bool = True,
    hook_variant_type: str = "default",
    enable_stat_pill: bool = True,
    seamless_loop: bool = True,
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

    # Resolve Hook A/B testing variant if specified
    if hook_variant_type and hook_variant_type != "default" and getattr(highlight, "hook_variants", None):
        chosen_hook = highlight.hook_variants.get(hook_variant_type)
        if chosen_hook:
            highlight.hook_text = chosen_hook

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

    active_video_path = metadata.local_path
    slice_start = start_time
    slice_end = end_time
    framing_remove_subtitles = remove_subtitles

    if remove_subtitles:
        lama = LamaInpainter.get_instance()
        if lama is not None:
            if callback:
                callback(20, "AI 딥러닝 자막 제거(LaMa Inpainting) 복원 처리 중...")
            clean_slice = str(clip_temp_dir / "inpainted_source.mp4")
            try:
                def inpaint_cb(p: int, msg: str):
                    if callback:
                        # Smoothly scale inpainting (0..100) into 20%..33% of overall short progress
                        scaled_p = 20 + int(p * 0.13)
                        callback(scaled_p, msg)

                inpaint_video_subtitles(
                    input_video=metadata.local_path,
                    output_video=clean_slice,
                    start_time=start_time,
                    end_time=end_time,
                    aspect_ratio=aspect_ratio,
                    callback=inpaint_cb
                )
                active_video_path = clean_slice
                slice_start = 0.0
                slice_end = duration
                framing_remove_subtitles = False  # Completely restored with LaMa deep learning, no delogo blur
            except Exception as e:
                print(f"[Renderer] LaMa inpainting failed, falling back to delogo: {e}")
                framing_remove_subtitles = True

    input_args = [
        "-ss", str(slice_start),
        "-to", str(slice_end),
        "-i", active_video_path
    ]
    filter_chains = []
    next_input_idx = 1

    ratio_desc = "16:9 가로 와이드" if is_landscape else "9:16 세로 쇼츠"
    if callback:
        sub_info = " (원본 자막 AI 제거 완료)" if (remove_subtitles and not framing_remove_subtitles) else (" (원본 자막 delogo 제거)" if remove_subtitles else "")
        callback(35, f"{ratio_desc} 비주얼 프레이밍 & 템플릿 [{template.name}] 캔버스 합성 중...{sub_info}")

    # 2. Template Background or Framing Filter
    if is_landscape:
        # 16:9 Widescreen video framing
        base_filter, current_label = build_framing_filter(
            layout_mode=eff_layout,
            orig_width=metadata.width,
            orig_height=metadata.height,
            video_path=active_video_path,
            start_time=slice_start,
            end_time=slice_end,
            aspect_ratio="16:9",
            remove_subtitles=framing_remove_subtitles,
            color_grade=color_grade,
            enable_punch_in_zoom=dynamic_zoom
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
            video_path=active_video_path,
            start_time=slice_start,
            end_time=slice_end,
            aspect_ratio="9:16",
            remove_subtitles=framing_remove_subtitles,
            color_grade=color_grade,
            enable_punch_in_zoom=dynamic_zoom
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
            video_path=active_video_path,
            start_time=slice_start,
            end_time=slice_end,
            video_box=template.video_box,
            bg_input_idx=bg_idx,
            aspect_ratio="9:16",
            remove_subtitles=framing_remove_subtitles,
            color_grade=color_grade,
            enable_punch_in_zoom=dynamic_zoom
        )
        filter_chains.append(base_filter)

    # 3. Subtitles
    kw_sfx_cues = []
    if show_subtitles and eff_sub_style != "none" and clip_words:
        sub_y = int(canvas_h * 0.82) if is_landscape else template.subtitle_y
        if sub_y > 0:
            if callback:
                callback(55, f"키네틱 타이포그래피 자막 시퀀스 렌더링 중 (스타일: {eff_sub_style})...")
            sub_concat_file, _, kw_sfx_cues = generate_subtitle_track(
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
                filter_fillers=filter_fillers,
                smart_keywords=smart_keywords,
                bounce_animation=bounce_animation
            )
            input_args.extend(["-f", "concat", "-safe", "0", "-i", sub_concat_file])
            sub_input_idx = next_input_idx
            next_input_idx += 1

            filter_chains.append(f"[{current_label}][{sub_input_idx}:v]overlay=0:0:shortest=1[v_sub]")
            current_label = "v_sub"

    # 3.5. Apple Keynote Glassmorphic Stat Pill Overlay (High-impact metric highlight)
    if enable_stat_pill and duration >= 8.0:
        stat_info = getattr(highlight, "stat_pill", None)
        if not stat_info and transcript:
            from src.highlighter import extract_stat_pill_from_transcript
            stat_info = extract_stat_pill_from_transcript(transcript, start_time, end_time)

        if stat_info:
            stat_png = str(clip_temp_dir / "stat_pill.png")
            if is_landscape:
                stat_y = 380
            elif template.video_box:
                stat_y = template.video_box[1] + 68
            else:
                stat_y = 360

            render_keynote_stat_pill(
                metric_text=stat_info.get("metric", "100%"),
                label_text=stat_info.get("label", "KEY METRIC • 실전 핵심 가치"),
                icon_type=stat_info.get("icon", "money"),
                output_path=stat_png,
                canvas_w=canvas_w,
                canvas_h=canvas_h,
                y_pos=stat_y
            )
            p_start = float(stat_info.get("rel_time", 3.8))
            p_end = min(duration - 0.8, p_start + 3.0)
            p_dur = max(0.8, round(p_end - p_start, 2))
            input_args.extend(["-loop", "1", "-t", str(p_dur), "-i", stat_png])
            stat_idx = next_input_idx
            next_input_idx += 1
            fade_dur = 0.28
            out_fade_st = max(0.2, round(p_dur - fade_dur, 2))
            filter_chains.append(
                f"[{stat_idx}:v]format=rgba,fade=t=in:st=0:d={fade_dur}:alpha=1,fade=t=out:st={out_fade_st}:d={fade_dur}:alpha=1[v_stat_fade];"
                f"[{current_label}][v_stat_fade]overlay=0:0:enable='between(t,{p_start:.2f},{p_end:.2f})'[v_stat]"
            )
            current_label = "v_stat"

    # 4. Audio Pipeline: Speech Master + BGM Ducking + Dynamic SFX
    if callback:
        callback(68, "BGM 사이드체인 오토 더킹 및 바이럴 SFX 오디오 믹싱 중...")

    all_sfx_cues = []
    if enable_sfx:
        all_sfx_cues.append(("impact", 0.18))
        if duration >= 5.0:
            all_sfx_cues.append(("whoosh", 3.2))
        if kw_sfx_cues:
            all_sfx_cues.extend(kw_sfx_cues)

    audio_inputs, audio_filters, final_audio_label, next_input_idx = build_audio_pipeline(
        clip_duration=duration,
        start_input_idx=next_input_idx,
        bgm_choice=bgm_track,
        template_id=template_id,
        enable_sfx=enable_sfx,
        sfx_cues=all_sfx_cues,
        bgm_volume=0.28,
        seamless_loop=seamless_loop
    )
    input_args.extend(audio_inputs)
    filter_chains.extend(audio_filters)

    full_filter_complex = ";".join(filter_chains)

    # 5. Build & Run FFmpeg Command
    if callback:
        callback(74, "FFmpeg 하드웨어 가속 비디오 인코딩 & -14 LUFS 오디오 마스터링 중...")

    cmd = ["ffmpeg", "-y"]
    cmd.extend(input_args)
    cmd.extend([
        "-filter_complex", full_filter_complex,
        "-map", f"[{current_label}]",
        "-map", f"[{final_audio_label}]"
    ])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    temp_render_path = str(clip_temp_dir / "encoded_final.mp4")
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(duration),
        temp_render_path
    ])

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg rendering failed: {result.stderr[-1000:]}")

        # Atomically move completed video to output_path
        shutil.move(temp_render_path, output_path)

        if callback:
            callback(88, "비디오 스트림 인코딩 완료 및 임시 리소스 정리 중...")

        return output_path
    finally:
        # Clean up temp frames for this clip
        shutil.rmtree(clip_temp_dir, ignore_errors=True)

