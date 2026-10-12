import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from src.models import Highlight, Transcript, VideoMetadata, Word
from src.templates import ShortsTemplate, get_template
from src.framing import build_framing_filter
from src.effects import render_template_background, render_top_header, generate_subtitle_track

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def render_short(
    metadata: VideoMetadata,
    highlight: Highlight,
    transcript: Transcript,
    output_path: str,
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
    **kwargs
) -> str:
    """
    Renders a complete, professional, viral-ready YouTube Short with:
    - Rich Graphic Template Canvas (News Portal, macOS Browser Window, Neon Magazine, Canva Minimal)
    - 2-tier Punch Headline with Highlighter Marker Tape
    - Structured containers & bullet summary cards
    - Word-by-word kinetic subtitles with double stroke & highlighter tape
    - Loudness-normalized audio (-14 LUFS)
    """
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

    # 1. Collect and adjust word timestamps relative to clip start
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

    # 2. Template Background or Smart Crop
    if eff_layout in ["news_portal", "browser_window", "neon_magazine", "minimal_edu", "source_pure"]:
        # Pre-render full graphic background
        bg_png = str(clip_temp_dir / "template_bg.png")
        render_template_background(
            template=template,
            highlight=highlight,
            metadata=metadata,
            output_path=bg_png
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
            bg_input_idx=bg_idx
        )
        filter_chains.append(base_filter)

    elif eff_layout == "smart_crop":
        base_filter, current_label = build_framing_filter(
            layout_mode="smart_crop",
            orig_width=metadata.width,
            orig_height=metadata.height,
            video_path=metadata.local_path,
            start_time=start_time,
            end_time=end_time
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
                badge_prefix=template.badge_prefix
            )
            input_args.extend(["-loop", "1", "-t", "4.0", "-i", badge_png])
            badge_idx = next_input_idx
            next_input_idx += 1
            filter_chains.append(f"[{current_label}][{badge_idx}:v]overlay=0:0:enable='lte(t,3.5)'[v_badge]")
            current_label = "v_badge"

    else:
        # Generic studio card fallback
        base_filter, current_label = build_framing_filter(
            layout_mode="studio_card",
            orig_width=metadata.width,
            orig_height=metadata.height,
            video_path=metadata.local_path,
            start_time=start_time,
            end_time=end_time
        )
        filter_chains.append(base_filter)

    # 3. Subtitles
    if show_subtitles and eff_sub_style != "none" and clip_words and template.subtitle_y > 0:
        sub_y = template.subtitle_y
        sub_concat_file, _ = generate_subtitle_track(
            words=clip_words,
            clip_duration=duration,
            output_dir=str(clip_temp_dir / "subs"),
            style=eff_sub_style,
            active_color=eff_active_col,
            normal_color=eff_normal_col,
            marker_color=template.marker_color if eff_layout in ["neon_magazine", "news_portal"] else None,
            font_name=eff_font,
            max_words_per_group=3,
            y_center=sub_y
        )
        input_args.extend(["-f", "concat", "-safe", "0", "-i", sub_concat_file])
        sub_input_idx = next_input_idx
        next_input_idx += 1

        filter_chains.append(f"[{current_label}][{sub_input_idx}:v]overlay=0:0:shortest=1[v_sub]")
        current_label = "v_sub"

    full_filter_complex = ";".join(filter_chains)

    # 4. Build & Run FFmpeg Command
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

    # Clean up temp frames for this clip
    shutil.rmtree(clip_temp_dir, ignore_errors=True)

    return output_path

