import os
from pathlib import Path
from typing import List
from src.models import Transcript, Highlight, Word

def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp H:MM:SS.cc"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def generate_ass_subtitles(
    transcript: Transcript,
    highlight: Highlight,
    output_ass_path: str,
    font_name: str = "Black Han Sans",
    font_size: int = 56,
    active_color: str = "&H0000FFFF&",  # Yellow in BGR (&H00BBGGRR&)
    inactive_color: str = "&H00FFFFFF&", # Pure White
    outline_color: str = "&H00000000&",  # Black
    margin_v: int = 380,                 # Safe area above shorts interface
    words_per_line: int = 4
) -> str:
    """
    Generate viral shorts-style ASS subtitles with active-word pop/highlight animation.
    All timestamps are shifted relative to highlight.start_time.
    """
    # 1. Collect all words within the highlight interval
    clip_words: List[Word] = []
    clip_start = highlight.start_time
    clip_end = highlight.end_time

    for seg in transcript.segments:
        for w in seg.words:
            # Word must overlap with highlight window
            if w.end > clip_start and w.start < clip_end:
                # Adjust time relative to clip start (00:00:00)
                rel_start = max(0.0, w.start - clip_start)
                rel_end = min(clip_end - clip_start, w.end - clip_start)
                clip_words.append(Word(
                    word=w.word,
                    start=round(rel_start, 2),
                    end=round(rel_end, 2)
                ))

    # If no word-level timestamps exist, fallback to segment level
    if not clip_words:
        for seg in transcript.segments:
            if seg.end > clip_start and seg.start < clip_end:
                rel_start = max(0.0, seg.start - clip_start)
                rel_end = min(clip_end - clip_start, seg.end - clip_start)
                clip_words.append(Word(
                    word=seg.text,
                    start=round(rel_start, 2),
                    end=round(rel_end, 2)
                ))

    # 2. Chunk words into short, rapid punchy groups (3-4 words per group)
    groups = []
    current_group: List[Word] = []
    
    for w in clip_words:
        current_group.append(w)
        # End group if reaches words_per_line or natural pause (> 0.5s)
        if len(current_group) >= words_per_line:
            groups.append(current_group)
            current_group = []
        elif len(current_group) > 1 and (w.start - current_group[-2].end > 0.6):
            groups.append(current_group[:-1])
            current_group = [w]
            
    if current_group:
        groups.append(current_group)

    # 3. Create ASS Header
    ass_header = f"""[Script Info]
Title: Viral Shorts Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{inactive_color},&H000000FF&,{outline_color},&H80000000&,1,0,0,0,100,100,2,0,1,7,3,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []

    # 4. For each word in each group, create an active-highlight event
    for grp in groups:
        if not grp:
            continue
        group_start = grp[0].start
        group_end = grp[-1].end
        
        # In case the group duration is extremely short, ensure at least 0.8s visibility
        if group_end - group_start < 0.6:
            group_end = group_start + 0.8

        for i, active_w in enumerate(grp):
            w_start = format_ass_time(active_w.start)
            w_end = format_ass_time(active_w.end)
            
            # Format text: words before active, active word (highlighted in yellow + slight pop), words after active
            line_parts = []
            for j, w in enumerate(grp):
                if j == i:
                    # Active word: Highlighted color + bold pop scale
                    line_parts.append(r"{\c" + active_color + r"\fscx112\fscy112}" + w.word + r"{\r}")
                else:
                    line_parts.append(r"{\c" + inactive_color + r"}" + w.word)
                    
            styled_text = " ".join(line_parts)
            events.append(f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{styled_text}")

    # Write ASS file
    Path(output_ass_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")

    return output_ass_path
