import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from src.models import Highlight, Transcript, VideoMetadata, Word
from src.framing import build_framing_filter
from src.effects import render_hook_badge, generate_subtitle_track

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def render_short(
    metadata: VideoMetadata,
    highlight: Highlight,
    transcript: Transcript,
    output_path: str,
    layout_mode: str = "blur_background",
    show_badge: bool = True,
    show_progress_bar: bool = True,
    normalize_audio: bool = True
) -> str:
    """
    Renders a complete, professional, viral-ready YouTube Short with:
    - 9:16 layout (blurred background or face-centered crop)
    - Animated word-by-word highlighted subtitles
    - Eye-catching top hook badge
    - Real-time animated progress bar
    - Loudness-normalized audio (-14 LUFS)
    """
    clip_id = f"clip_{highlight.id}_{int(highlight.start_time)}"
    clip_temp_dir = TEMP_DIR / clip_id
    clip_temp_dir.mkdir(parents=True, exist_ok=True)

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

    # If no word timestamps, use segment texts
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

    # 2. Generate subtitle sequence and concat file
    sub_concat_file, _ = generate_subtitle_track(
        words=clip_words,
        clip_duration=duration,
        output_dir=str(clip_temp_dir / "subs")
    )

    # 3. Generate hook title badge
    badge_png = None
    if show_badge and highlight.hook_text:
        badge_png = str(clip_temp_dir / "badge.png")
        render_hook_badge(highlight.hook_text, badge_png)

    # 4. Build Filter Complex
    # Part A: Base layout
    base_filter, current_label = build_framing_filter(
        layout_mode=layout_mode,
        orig_width=metadata.width,
        orig_height=metadata.height,
        video_path=metadata.local_path,
        start_time=start_time,
        end_time=end_time
    )

    filter_chains = [base_filter]

    # Part B: Overlay Subtitles (Input 1 is sub_concat_file)
    filter_chains.append(f"[{current_label}][1:v]overlay=0:0:shortest=1[v_sub]")
    current_label = "v_sub"

    # Part C: Overlay Hook Badge (Input 2 if badge exists)
    input_idx_badge = 2
    if badge_png and os.path.exists(badge_png):
        filter_chains.append(f"[{current_label}][{input_idx_badge}:v]overlay=0:0[v_badge]")
        current_label = "v_badge"

    # Part D: Bottom Progress Bar
    if show_progress_bar:
        # Background track + animated expanding yellow bar
        pb_filter = (
            f"[{current_label}]drawbox=x=0:y=1890:w=iw:h=8:color=black@0.4:t=fill,"
            f"drawbox=x=0:y=1890:w='iw*t/{duration:.2f}':h=8:color=#FFE600@0.95:t=fill[v_out]"
        )
        filter_chains.append(pb_filter)
        current_label = "v_out"

    full_filter_complex = ";".join(filter_chains)

    # 5. Build FFmpeg command
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", metadata.local_path,
        "-f", "concat",
        "-safe", "0",
        "-i", sub_concat_file
    ]

    if badge_png and os.path.exists(badge_png):
        cmd.extend(["-loop", "1", "-t", str(duration), "-i", badge_png])

    cmd.extend([
        "-filter_complex", full_filter_complex,
        "-map", f"[{current_label}]",
        "-map", "0:a?"
    ])

    # Audio filter
    if normalize_audio:
        cmd.extend(["-af", "loudnorm=I=-14:LRA=11:TP=-1.5"])

    # Output encoding
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
