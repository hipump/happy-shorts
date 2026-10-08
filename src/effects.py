import os
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
from src.models import Word, Highlight

FONT_BLACK_HAN_SANS = "assets/fonts/BlackHanSans-Regular.ttf"
FONT_PRETENDARD = "assets/fonts/Pretendard-ExtraBold.ttf"

def get_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()

def render_hook_badge(
    hook_text: str,
    output_path: str,
    canvas_w: int = 1080,
    canvas_h: int = 1920
) -> str:
    """
    Renders an eye-catching top pill badge for the hook text.
    Positioned around Y=240 (safe top zone).
    """
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = 48
    font = get_font(FONT_BLACK_HAN_SANS, font_size)
    bbox = font.getbbox(hook_text)
    text_w = bbox[2] - bbox[0]
    
    # Auto-scale font if text width is too wide for screen
    max_text_w = canvas_w - 140
    if text_w > max_text_w:
        font_size = max(26, int(font_size * (max_text_w / text_w)))
        font = get_font(FONT_BLACK_HAN_SANS, font_size)
        bbox = font.getbbox(hook_text)
        text_w = bbox[2] - bbox[0]

    text_h = bbox[3] - bbox[1]
    
    padding_x = 36
    padding_y = 16
    pill_w = text_w + padding_x * 2
    pill_h = text_h + padding_y * 2
    
    # Centered horizontally at Y=230
    pill_x1 = (canvas_w - pill_w) // 2
    pill_y1 = 230
    pill_x2 = pill_x1 + pill_w
    pill_y2 = pill_y1 + pill_h
    
    # Draw drop shadow for the pill
    shadow_offset = 6
    draw.rounded_rectangle(
        [pill_x1, pill_y1 + shadow_offset, pill_x2, pill_y2 + shadow_offset],
        radius=24,
        fill=(0, 0, 0, 140)
    )
    
    # Draw dark pill background with subtle golden/yellow border
    draw.rounded_rectangle(
        [pill_x1, pill_y1, pill_x2, pill_y2],
        radius=24,
        fill=(15, 15, 20, 230),
        outline=(255, 230, 0, 220),
        width=3
    )
    
    # Draw text inside pill
    text_center_x = canvas_w // 2
    text_center_y = pill_y1 + pill_h // 2
    draw.text(
        (text_center_x, text_center_y),
        hook_text,
        font=font,
        fill=(255, 255, 255, 255),
        anchor="mm"
    )
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path

def render_subtitle_frame(
    words_group: List[Word],
    active_idx: int,
    output_path: str,
    canvas_w: int = 1080,
    canvas_h: int = 1920,
    y_center: int = 1480
):
    """
    Renders a group of words where active_idx word is highlighted in vibrant yellow/gold.
    """
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    normal_font = get_font(FONT_BLACK_HAN_SANS, 56)
    active_font = get_font(FONT_BLACK_HAN_SANS, 64)
    
    space_w = normal_font.getbbox(" ")[2] - normal_font.getbbox(" ")[0]
    
    # Measure total line width
    word_widths = []
    for i, w in enumerate(words_group):
        f = active_font if i == active_idx else normal_font
        bbox = f.getbbox(w.word)
        w_w = bbox[2] - bbox[0]
        word_widths.append(w_w)
        
    total_line_w = sum(word_widths) + space_w * (len(words_group) - 1)
    
    # Start X to center the line
    curr_x = (canvas_w - total_line_w) // 2
    
    # Draw each word
    for i, w in enumerate(words_group):
        w_len = word_widths[i]
        word_center_x = curr_x + w_len // 2
        
        if i == active_idx:
            # Active word: Drop shadow + thick black stroke + bright yellow fill
            draw.text(
                (word_center_x + 4, y_center + 4),
                w.word,
                font=active_font,
                fill=(0, 0, 0, 180),
                stroke_width=6,
                stroke_fill=(0, 0, 0, 180),
                anchor="mm"
            )
            draw.text(
                (word_center_x, y_center),
                w.word,
                font=active_font,
                fill=(255, 235, 0, 255),  # Vibrant Shorts Yellow
                stroke_width=7,
                stroke_fill=(0, 0, 0, 255),
                anchor="mm"
            )
        else:
            # Inactive words: Drop shadow + thick black stroke + white fill
            draw.text(
                (word_center_x + 3, y_center + 3),
                w.word,
                font=normal_font,
                fill=(0, 0, 0, 160),
                stroke_width=5,
                stroke_fill=(0, 0, 0, 160),
                anchor="mm"
            )
            draw.text(
                (word_center_x, y_center),
                w.word,
                font=normal_font,
                fill=(255, 255, 255, 255),
                stroke_width=6,
                stroke_fill=(0, 0, 0, 255),
                anchor="mm"
            )
            
        curr_x += w_len + space_w
        
    img.save(output_path, "PNG")

def generate_subtitle_track(
    words: List[Word],
    clip_duration: float,
    output_dir: str,
    max_words_per_group: int = 4
) -> Tuple[str, str]:
    """
    Generate timed PNG sequence and an ffconcat descriptor file.
    Groups words intelligently by sentence endings and pauses, with zero timeline drift.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    blank_png = str(out_dir / "blank.png")
    blank_img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    blank_img.save(blank_png, "PNG")
    
    if not words:
        concat_file = str(out_dir / "subtitles.txt")
        with open(concat_file, "w", encoding="utf-8") as f:
            f.write("ffconcat version 1.0\n")
            f.write("file blank.png\n")
            f.write(f"duration {clip_duration:.2f}\n")
            f.write("file blank.png\n")
        return concat_file, blank_png

    # Group words into chunks: split on punctuation (. ? !), pause (>0.5s), or max_words_per_group
    groups: List[List[Word]] = []
    current_grp: List[Word] = []
    
    for w in words:
        current_grp.append(w)
        ends_sentence = any(w.word.endswith(p) for p in [".", "?", "!", "~"])
        
        has_pause = False
        if len(current_grp) > 1 and len(words) > words.index(w) + 1:
            next_w = words[words.index(w) + 1]
            if next_w.start - w.end > 0.4:
                has_pause = True
                
        if len(current_grp) >= max_words_per_group or ends_sentence or has_pause:
            groups.append(current_grp)
            current_grp = []
            
    if current_grp:
        groups.append(current_grp)
        
    concat_entries = []
    curr_timeline = 0.0
    frame_idx = 0
    
    for g_idx, grp in enumerate(groups):
        if not grp:
            continue
            
        grp_start = max(0.0, grp[0].start)
        last_end = grp[-1].end
        
        if g_idx < len(groups) - 1:
            next_start = groups[g_idx + 1][0].start
            display_end = min(last_end + 0.35, next_start - 0.05)
        else:
            display_end = min(clip_duration, last_end + 0.5)
        display_end = max(last_end, display_end)
        
        # Gap before group
        if grp_start > curr_timeline:
            gap = round(grp_start - curr_timeline, 3)
            if gap > 0.04:
                concat_entries.append(("blank.png", gap))
                curr_timeline = grp_start
                
        # Generate frames for each word in this group
        for i, w in enumerate(grp):
            w_start = max(curr_timeline, w.start)
            if i < len(grp) - 1:
                next_w_start = grp[i + 1].start
                w_end = max(w_start + 0.08, next_w_start)
            else:
                w_end = max(w_start + 0.08, display_end)
                
            dur = max(0.06, round(w_end - curr_timeline, 3))
            
            frame_filename = f"sub_{frame_idx:04d}.png"
            frame_path = str(out_dir / frame_filename)
            render_subtitle_frame(grp, active_idx=i, output_path=frame_path)
            
            concat_entries.append((frame_filename, dur))
            curr_timeline += dur
            frame_idx += 1
            
    # Remaining time to end of clip
    if curr_timeline < clip_duration:
        remaining = round(clip_duration - curr_timeline, 3)
        if remaining > 0.04:
            concat_entries.append(("blank.png", remaining))
        
    concat_file = str(out_dir / "subtitles.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        f.write("ffconcat version 1.0\n")
        for filename, dur in concat_entries:
            f.write(f"file {filename}\n")
            f.write(f"duration {dur}\n")
        f.write("file blank.png\n")
        
    return concat_file, blank_png
