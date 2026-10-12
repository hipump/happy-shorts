import os
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.models import Word, Highlight, VideoMetadata
from src.templates import ShortsTemplate, get_template

FONT_BLACK_HAN_SANS = "assets/fonts/BlackHanSans-Regular.ttf"
FONT_PRETENDARD = "assets/fonts/Pretendard-ExtraBold.ttf"

def get_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()

def split_hook_headline(title: str, hook_text: str) -> Tuple[str, str]:
    """
    Intelligently splits headline into 2 impactful tiers:
    Line 1: Setup / Context (e.g., '운전 중 터치 한 번으로')
    Line 2: High-impact punchline (e.g., '모르면 100만원 손해인 기능!')
    """
    emoji_pattern = r'[\U00010000-\U0010ffff\u2600-\u27bf\ud83c-\ud83e\ud83d\udc00-\udfff]'
    clean_hook = re.sub(emoji_pattern, '', hook_text.strip().strip("\"'「」『』")).strip() if hook_text else ""
    clean_title = re.sub(emoji_pattern, '', title.strip().strip("\"'「」『』")).strip() if title else ""

    def clean_res(p1: str, p2: str) -> Tuple[str, str]:
        c1 = re.sub(emoji_pattern, '', p1).strip()
        c2 = re.sub(emoji_pattern, '', p2).strip()
        return c1, c2

    # Delimiter-based split
    source = clean_hook if clean_hook else clean_title
    for sep in ["\n", " | ", " - ", " : ", " / ", "｜"]:
        if sep in source:
            parts = source.split(sep, 1)
            p1, p2 = parts[0].strip(), parts[1].strip()
            if p1 and p2:
                return clean_res(p1, p2)

    # If title and hook are different and both concise
    if clean_title and clean_hook and clean_title != clean_hook:
        if len(clean_title) <= 22 and len(clean_hook) <= 26:
            return clean_res(clean_title, clean_hook)

    # Word-based split around midpoint
    words = source.split()
    if len(words) <= 1:
        return clean_res(source, "")
    if len(words) == 2:
        return clean_res(words[0], words[1])

    mid = len(words) // 2
    return clean_res(" ".join(words[:mid]), " ".join(words[mid:]))


def draw_marker(draw: ImageDraw.ImageDraw, bbox: List[int], color: Tuple[int, int, int, int] = (255, 230, 0, 210), pad_x: int = 12):
    """Draws a semi-transparent highlighter marker tape strip under text."""
    x1, y1, x2, y2 = bbox
    th = y2 - y1
    my1 = int(y2 - th * 0.55)
    my2 = int(y2 + 4)
    draw.rectangle([x1 - pad_x, my1, x2 + pad_x, my2], fill=color)

def draw_3d_text(
    draw: ImageDraw.ImageDraw,
    pos: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, int, int],
    stroke_fill: Tuple[int, int, int] = (0, 0, 0),
    stroke_width: int = 6,
    shadow_offset: Tuple[int, int] = (3, 4),
    anchor: str = "mm"
):
    """Draws 3D extruded text with drop shadow and heavy stroke."""
    x, y = pos
    # Drop shadow
    if shadow_offset[0] != 0 or shadow_offset[1] != 0:
        draw.text(
            (x + shadow_offset[0], y + shadow_offset[1]),
            text,
            font=font,
            fill=(0, 0, 0, 200),
            stroke_width=stroke_width,
            stroke_fill=(0, 0, 0, 200),
            anchor=anchor
        )
    # Main text with stroke
    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
        anchor=anchor
    )

def render_template_background(
    template: ShortsTemplate,
    highlight: Highlight,
    metadata: VideoMetadata,
    output_path: str,
    canvas_w: int = 1080,
    canvas_h: int = 1920
) -> str:
    """
    Renders the rich MiriCanvas/Canva/AlphaCut base graphic canvas:
    - Background texture (Portal white, Navy mesh grid, or Dark slate glow)
    - Top Hook Deck (Header bar / Titlebar + 2-line headline with highlighter marker)
    - Video Container Frame (Drop shadow, borders, window titlebars, corner chips)
    - Bottom Deck (Briefing card / Console box / Hashtag chips / Bullet points)
    """
    img = Image.new("RGBA", (canvas_w, canvas_h), (20, 24, 32, 255))
    draw = ImageDraw.Draw(img)

    f_black_72 = get_font(FONT_BLACK_HAN_SANS, 72)
    f_black_58 = get_font(FONT_BLACK_HAN_SANS, 58)
    f_pret_50 = get_font(FONT_PRETENDARD, 50)
    f_pret_36 = get_font(FONT_PRETENDARD, 36)
    f_pret_28 = get_font(FONT_PRETENDARD, 28)
    f_pret_22 = get_font(FONT_PRETENDARD, 22)

    line1, line2 = split_hook_headline(highlight.title, highlight.hook_text)
    if not line1:
        line1 = "놓치면 후회하는 핵심 명장면"
    if not line2:
        line2 = f"클립 #{highlight.id} 지금 바로 확인!"

    # =========================================================================
    # 1. NEWS PORTAL (미리캔버스 속보 & 뉴스 포털)
    # =========================================================================
    if template.layout_type == "news_portal":
        img = Image.new("RGBA", (canvas_w, canvas_h), (247, 248, 250, 255))
        draw = ImageDraw.Draw(img)

        # 1-1. Top Broadcast Red Bar
        draw.rectangle([0, 0, canvas_w, 130], fill=(215, 25, 35, 255))
        draw.text((70, 65), "MIRI NEWS", font=f_pret_36, fill=(255, 255, 255), anchor="lm")
        # LIVE pill with red dot
        draw.rounded_rectangle([320, 44, 460, 86], radius=21, fill=(0, 0, 0, 200))
        draw.ellipse([335, 57, 351, 73], fill=(255, 50, 50))
        draw.text((400, 65), "LIVE", font=f_pret_28, fill=(255, 255, 255), anchor="mm")
        draw.text((canvas_w - 70, 65), "속보 특보", font=f_pret_28, fill=(255, 255, 255), anchor="rm")

        # 1-2. Headline Block
        hy = 165
        # Red category chip
        draw.rounded_rectangle([70, hy, 380, hy + 46], radius=8, fill=(255, 230, 235), outline=(255, 180, 190), width=1)
        draw.text((82, hy + 23), "긴급 속보  •  필독 리포트", font=f_pret_28, fill=(215, 25, 35), anchor="lm")

        # Line 1
        draw.text((70, hy + 62), line1, font=f_pret_50, fill=(20, 24, 30), anchor="lt")

        # Line 2 with Highlighter Marker Tape
        l2_font = f_pret_50
        l2_bbox = l2_font.getbbox(line2)
        if (l2_bbox[2] - l2_bbox[0]) > 900:
            l2_font = f_pret_36
            l2_bbox = l2_font.getbbox(line2)
        l2_w = l2_bbox[2] - l2_bbox[0]
        l2_h = l2_bbox[3] - l2_bbox[1]
        draw_marker(draw, [70, hy + 125, 70 + l2_w, hy + 125 + l2_h], color=template.marker_color, pad_x=8)
        draw.text((70, hy + 125), line2, font=l2_font, fill=(10, 12, 16), anchor="lt")

        # Byline
        draw.text((70, hy + 200), "단독 취재 | 핵심 꿀팁 특종  •  실시간 제보", font=f_pret_22, fill=(120, 125, 135), anchor="lt")
        draw.line([(70, hy + 235), (canvas_w - 70, hy + 235)], fill=(220, 225, 235), width=2)

        # 1-3. Video Container Frame (70, 460, 940, 528)
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=16, fill=(20, 24, 30))
        # Top-left red sticker on video frame
        draw.rounded_rectangle([vx + 20, vy + 20, vx + 220, vy + 66], radius=10, fill=(215, 25, 35, 245))
        draw.text((vx + 120, vy + 43), "HOT 실시간 제보", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # 1-4. Bottom News Briefing Card
        by = vy + vh + 40
        draw.rounded_rectangle([70, by, canvas_w - 70, by + 460], radius=24, fill=(255, 255, 255), outline=(220, 225, 235), width=2)
        # Card header badge
        draw.rounded_rectangle([100, by + 28, 280, by + 72], radius=12, fill=(20, 24, 30))
        draw.text((190, by + 50), "현장 자막 브리핑", font=f_pret_22, fill=(255, 255, 255), anchor="mm")

        # Broadcast Live Subtitle Console Strip
        draw.rounded_rectangle([95, by + 86, canvas_w - 95, by + 236], radius=16, fill=(18, 22, 30))

        # Bullet summary points
        pts = highlight.summary_points if highlight.summary_points else [
            f"{highlight.title} 실전 핵심 설정",
            "상황별 권장 사용 가이드"
        ]
        p1 = f"• {pts[0]}"
        p2 = f"• {pts[1]}" if len(pts) > 1 else f"• {highlight.title} 실전 활용 팁"
        draw.text((100, by + 265), p1[:38], font=f_pret_28, fill=(40, 45, 55), anchor="lt")
        draw.text((100, by + 320), p2[:38], font=f_pret_28, fill=(40, 45, 55), anchor="lt")
        draw.text((100, by + 385), "• 자세한 내용은 화면 상단 링크 및 더보기란 참조", font=f_pret_22, fill=(120, 125, 140), anchor="lt")

    # =========================================================================
    # 2. BROWSER WINDOW (인터넷창 / 맥OS 브라우저 창 썸네일)
    # =========================================================================
    elif template.layout_type == "browser_window":
        img = Image.new("RGBA", (canvas_w, canvas_h), (24, 28, 38, 255))
        draw = ImageDraw.Draw(img)

        # Grid lines
        for gx in range(0, canvas_w, 40):
            draw.line([(gx, 0), (gx, canvas_h)], fill=(34, 40, 56, 120), width=1)
        for gy in range(0, canvas_h, 40):
            draw.line([(0, gy), (canvas_w, gy)], fill=(34, 40, 56, 120), width=1)

        # Top Attention Tag
        tag_text = f"[TIP {highlight.id:02d}] {line1[:16]}"
        tag_b = f_pret_36.getbbox(tag_text)
        tag_w = tag_b[2] - tag_b[0] + 52
        draw.rounded_rectangle([540 - tag_w // 2, 75, 540 + tag_w // 2, 135], radius=30, fill=(255, 230, 0), outline=(0, 0, 0), width=2)
        draw.text((540, 105), tag_text, font=f_pret_36, fill=(10, 12, 16), anchor="mm")

        # 2-line Headline
        draw.text((540, 175), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        l2_font = f_black_72
        l2_bbox = f_black_72.getbbox(line2)
        if (l2_bbox[2] - l2_bbox[0]) > 900:
            l2_font = f_black_58
        draw_3d_text(
            draw, (540, 250), line2, l2_font,
            fill=template.active_color, stroke_fill=(0, 0, 0), stroke_width=8, shadow_offset=(4, 4)
        )

        # macOS Window Frame (Y: 340 to 1480)
        wx1, wy1 = 50, 340
        ww = canvas_w - 100
        wh = 1140
        wx2, wy2 = wx1 + ww, wy1 + wh

        draw.rounded_rectangle([wx1 + 8, wy1 + 12, wx2 + 8, wy2 + 12], radius=28, fill=(0, 0, 0, 180))
        draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=28, fill=(240, 243, 250), outline=(255, 255, 255, 150), width=2)

        # Titlebar
        draw.rounded_rectangle([wx1, wy1, wx2, wy1 + 75], radius=28, fill=(225, 229, 238))
        draw.rectangle([wx1, wy1 + 45, wx2, wy1 + 75], fill=(225, 229, 238))
        # Traffic lights (🔴 🟡 🟢)
        draw.ellipse([wx1 + 25, wy1 + 26, wx1 + 47, wy1 + 48], fill=(255, 95, 87))
        draw.ellipse([wx1 + 55, wy1 + 26, wx1 + 77, wy1 + 48], fill=(254, 188, 46))
        draw.ellipse([wx1 + 85, wy1 + 26, wx1 + 107, wy1 + 48], fill=(40, 201, 64))

        # URL Address Bar
        draw.rounded_rectangle([wx1 + 135, wy1 + 16, wx2 - 35, wy1 + 58], radius=14, fill=(255, 255, 255), outline=(200, 205, 216), width=1)
        draw.text((wx1 + 160, wy1 + 37), "https://shorts.app/tips/highlight-guide", font=f_pret_22, fill=(90, 95, 110), anchor="lm")

        # Viewport border for video
        vx, vy, vw, vh = template.video_box
        draw.rectangle([vx - 2, vy - 2, vx + vw + 2, vy + vh + 2], fill=(0, 0, 0))

        # Window Subtitle Console Box
        sub_box_y = vy + vh + 45
        draw.rounded_rectangle([wx1 + 30, sub_box_y, wx2 - 30, sub_box_y + 170], radius=20, fill=(20, 24, 34))

        # Window Hashtag Chips
        chip_y = sub_box_y + 200
        chips = [f"#{w}" for w in highlight.title.split() if len(w) > 1]
        if len(chips) < 3:
            chips += ["#핵심가이드", "#추천팁", "#필수체크"]
        chips = chips[:4]
        cx = wx1 + 35
        for ch in chips:
            ch_b = f_pret_28.getbbox(ch)
            ch_w = ch_b[2] - ch_b[0] + 32
            draw.rounded_rectangle([cx, chip_y, cx + ch_w, chip_y + 50], radius=14, fill=(215, 222, 235))
            draw.text((cx + ch_w // 2, chip_y + 25), ch, font=f_pret_28, fill=(35, 40, 55), anchor="mm")
            cx += ch_w + 14

        draw.text((540, 1550), "지금 바로 확인해 보세요 (좋아요 & 저장)", font=f_pret_36, fill=(255, 255, 255), anchor="mm")

    # =========================================================================
    # 3. NEON MAGAZINE (캔바 & 알파컷 인포 매거진)
    # =========================================================================
    elif template.layout_type == "neon_magazine":
        img = Image.new("RGBA", (canvas_w, canvas_h), (14, 16, 24, 255))
        draw = ImageDraw.Draw(img)

        # Radial Cyan Glow
        glow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        dg = ImageDraw.Draw(glow)
        dg.ellipse([140, 400, 940, 1200], fill=(0, 200, 255, 40))
        glow = glow.filter(ImageFilter.GaussianBlur(80))
        img.alpha_composite(glow)
        draw = ImageDraw.Draw(img)

        # Top Gold Pill Badge
        badge_text = f"[KEY {highlight.id:02d}] {line1[:16]}"
        badge_b = f_pret_36.getbbox(badge_text)
        badge_w = badge_b[2] - badge_b[0] + 52
        draw.rounded_rectangle([540 - badge_w // 2, 75, 540 + badge_w // 2, 135], radius=30, fill=(255, 215, 0), outline=(255, 255, 255), width=2)
        draw.text((540, 105), badge_text, font=f_pret_36, fill=(10, 12, 16), anchor="mm")

        # 2-line Headline
        draw.text((540, 180), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        l2_font = f_black_72
        l2_bbox = f_black_72.getbbox(line2)
        if (l2_bbox[2] - l2_bbox[0]) > 900:
            l2_font = f_black_58
        draw_3d_text(
            draw, (540, 255), line2, l2_font,
            fill=template.active_color, stroke_fill=(0, 0, 0), stroke_width=8, shadow_offset=(4, 4)
        )

        # Video container with Glowing Cyan Border
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 6, vy - 6, vx + vw + 6, vy + vh + 6], radius=26, fill=(0, 255, 220, 200))
        draw.rounded_rectangle([vx, vy, vx + vw, vy + vh], radius=22, fill=(0, 0, 0))

        # Warning sticker on top-right corner of video card
        draw.rounded_rectangle([vx + vw - 220, vy + 20, vx + vw - 20, vy + 68], radius=12, fill=(255, 45, 85, 240))
        draw.text((vx + vw - 120, vy + 44), "HOT 필수시청", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # Bottom Summary Point Card
        sc_y = 1170
        draw.rounded_rectangle([80, sc_y, canvas_w - 80, sc_y + 240], radius=22, fill=(22, 26, 38, 240), outline=(255, 255, 255, 40), width=2)
        draw.text((120, sc_y + 40), "[요약] 실전 핵심 가이드", font=f_pret_36, fill=(255, 215, 0), anchor="lt")
        pts = highlight.summary_points if highlight.summary_points else [
            f"{highlight.title} 실전 핵심 설정",
            "상황별 권장 사용 가이드"
        ]
        p1 = f"• {pts[0]}"
        p2 = f"• {pts[1]}" if len(pts) > 1 else f"• {highlight.title} 실전 활용 팁"
        draw.text((120, sc_y + 100), p1[:38], font=f_pret_28, fill=(235, 240, 255), anchor="lt")
        draw.text((120, sc_y + 155), p2[:38], font=f_pret_28, fill=(235, 240, 255), anchor="lt")

    # =========================================================================
    # 4. MINIMAL EDU & OTHERS (캔바 모던 클린 & 기본)
    # =========================================================================
    else:
        img = Image.new("RGBA", (canvas_w, canvas_h), (20, 24, 34, 255))
        draw = ImageDraw.Draw(img)

        # Top Pill
        draw.rounded_rectangle([340, 80, 740, 140], radius=30, fill=(35, 42, 58), outline=(80, 95, 125), width=2)
        draw.text((540, 110), "[지식] 핵심 1분 지식 요약", font=f_pret_36, fill=(255, 255, 255), anchor="mm")

        # 2-line Headline
        draw.text((540, 185), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0), anchor="mm")
        l2_bbox = f_pret_50.getbbox(line2)
        l2_w = l2_bbox[2] - l2_bbox[0]
        l2_h = l2_bbox[3] - l2_bbox[1]
        cx = (canvas_w - l2_w) // 2
        draw_marker(draw, [cx, 260 - l2_h // 2, cx + l2_w, 260 + l2_h // 2], color=template.marker_color, pad_x=12)
        draw.text((540, 260), line2, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")

        # Video container
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 3, vy - 3, vx + vw + 3, vy + vh + 3], radius=16, fill=(0, 0, 0))

        # Bottom Knowledge Card
        sc_y = 1200
        draw.rounded_rectangle([80, sc_y, canvas_w - 80, sc_y + 220], radius=20, fill=(28, 34, 48), outline=(60, 72, 95), width=2)
        draw.text((120, sc_y + 35), "[노트] 핵심 지식 정리", font=f_pret_36, fill=(255, 255, 255), anchor="lt")
        pts = highlight.summary_points if highlight.summary_points else [
            f"{highlight.title} 실전 핵심 가이드",
            "상황별 권장 사용법 정리"
        ]
        p1 = f"• {pts[0]}"
        p2 = f"• {pts[1]}" if len(pts) > 1 else f"• {highlight.title} 실전 활용 팁"
        draw.text((120, sc_y + 95), p1[:38], font=f_pret_28, fill=(210, 220, 235), anchor="lt")
        draw.text((120, sc_y + 145), p2[:38], font=f_pret_28, fill=(180, 195, 215), anchor="lt")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG")
    return output_path

def render_top_header(
    title: str,
    hook_text: str,
    output_path: str,
    clip_idx: int = 1,
    badge_style: str = "gold_pill",
    badge_prefix: str = "[TIP]",
    canvas_w: int = 1080,
    canvas_h: int = 1920
) -> str:
    """Renders intro hook pill badge for smart_crop layout."""
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    clean_title = title.strip().strip("\"'「」『』")
    if not clean_title:
        clean_title = f"핵심 하이라이트 #{clip_idx}"

    prefix = badge_prefix if badge_prefix else "[TIP]"
    hook_label = f"{prefix} {clean_title}"
    font_badge = get_font(FONT_PRETENDARD, 38)
    bbox = font_badge.getbbox(hook_label)
    text_w = bbox[2] - bbox[0]

    max_w = 900
    if text_w > max_w:
        font_size = max(26, int(38 * (max_w / text_w)))
        font_badge = get_font(FONT_PRETENDARD, font_size)
        bbox = font_badge.getbbox(hook_label)
        text_w = bbox[2] - bbox[0]

    pad_x = 44
    badge_w = text_w + pad_x * 2
    badge_h = 62
    bx1 = (canvas_w - badge_w) // 2
    by1 = 280
    bx2 = bx1 + badge_w
    by2 = by1 + badge_h

    if badge_style == "red_pill":
        fill_color = (180, 20, 30, 245)
        outline_color = (255, 80, 90, 230)
    elif badge_style == "minimal_pill":
        fill_color = (35, 40, 50, 240)
        outline_color = (120, 130, 150, 200)
    else:
        fill_color = (20, 24, 34, 240)
        outline_color = (255, 230, 0, 210)

    draw.rounded_rectangle([bx1, by1 + 4, bx2, by2 + 4], radius=31, fill=(0, 0, 0, 130))
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=31, fill=fill_color, outline=outline_color, width=2)
    draw.text((canvas_w // 2, by1 + badge_h // 2), hook_label, font=font_badge, fill=(255, 255, 255, 255), anchor="mm")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path



def render_subtitle_frame(
    words_group: List[Word],
    active_idx: int,
    output_path: str,
    style: str = "viral_pop",
    active_color: Tuple[int, int, int] = (255, 230, 0),
    normal_color: Tuple[int, int, int] = (255, 255, 255),
    marker_color: Optional[Tuple[int, int, int, int]] = None,
    font_name: str = "black_han_sans",
    canvas_w: int = 1080,
    canvas_h: int = 1920,
    y_center: int = 1360
):
    """
    Renders floating kinetic typography with configurable template colors, fonts, and highlighter tape.
    Guarantees clean, professional typography without artificial AI emojis.
    """
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    chosen_font_path = FONT_PRETENDARD if font_name == "pretendard" else FONT_BLACK_HAN_SANS

    if style == "clean_minimal" or font_name == "pretendard":
        active_font = get_font(chosen_font_path, 64)
        normal_font = get_font(chosen_font_path, 56)
        stroke_w = 8
    else:
        # viral_pop default
        active_font = get_font(chosen_font_path, 72)
        normal_font = get_font(chosen_font_path, 64)
        stroke_w = 9

    space_w = 26
    emoji_pattern = r'[\U00010000-\U0010ffff\u2600-\u27bf\ud83c-\ud83e\ud83d\udc00-\udfff]'

    # Measure sanitized words
    word_widths = []
    clean_words = []
    for i, w in enumerate(words_group):
        clean_w = re.sub(emoji_pattern, '', w.word).strip()
        clean_words.append(clean_w)
        f = active_font if i == active_idx else normal_font
        if clean_w:
            bbox = f.getbbox(clean_w)
            w_w = bbox[2] - bbox[0]
        else:
            w_w = 0
        word_widths.append(w_w)

    valid_words = [cw for cw in clean_words if cw]
    if not valid_words:
        img.save(output_path, "PNG")
        return

    total_content_w = sum(word_widths) + space_w * (len(clean_words) - 1)
    curr_x = (canvas_w - total_content_w) // 2

    # Draw Words
    for i, clean_w in enumerate(clean_words):
        if not clean_w:
            continue
        w_len = word_widths[i]
        word_center_x = curr_x + w_len // 2
        f = active_font if i == active_idx else normal_font
        col = (*active_color, 255) if i == active_idx else (*normal_color, 255)
        s_width = stroke_w if i == active_idx else max(5, stroke_w - 2)

        # Highlighter Marker Tape behind active word
        if i == active_idx and marker_color:
            wb = f.getbbox(clean_w)
            wh = wb[3] - wb[1]
            draw_marker(draw, [curr_x, y_center - wh // 2, curr_x + w_len, y_center + wh // 2], color=marker_color, pad_x=10)

        # Drop shadow
        draw.text(
            (word_center_x + 3, y_center + 4),
            clean_w,
            font=f,
            fill=(0, 0, 0, 220),
            anchor="mm"
        )
        # Stroke + fill
        draw.text(
            (word_center_x, y_center),
            clean_w,
            font=f,
            fill=col,
            stroke_width=s_width,
            stroke_fill=(0, 0, 0, 255),
            anchor="mm"
        )

        curr_x += w_len + space_w

    img.save(output_path, "PNG")

def generate_subtitle_track(
    words: List[Word],
    clip_duration: float,
    output_dir: str,
    style: str = "viral_pop",
    active_color: Tuple[int, int, int] = (255, 230, 0),
    normal_color: Tuple[int, int, int] = (255, 255, 255),
    marker_color: Optional[Tuple[int, int, int, int]] = None,
    font_name: str = "black_han_sans",
    max_words_per_group: int = 3,
    y_center: int = 1360
) -> Tuple[str, str]:
    """
    Generate timed PNG sequence and an ffconcat descriptor file.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    blank_png = str(out_dir / "blank.png")
    blank_img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    blank_img.save(blank_png, "PNG")

    if not words or style == "none":
        concat_file = str(out_dir / "subtitles.txt")
        with open(concat_file, "w", encoding="utf-8") as f:
            f.write("ffconcat version 1.0\n")
            f.write("file blank.png\n")
            f.write(f"duration {clip_duration:.2f}\n")
            f.write("file blank.png\n")
        return concat_file, blank_png

    # Group words into 2~3 word chunks
    groups: List[List[Word]] = []
    current_grp: List[Word] = []

    for w_idx, w in enumerate(words):
        current_grp.append(w)
        ends_sentence = any(w.word.endswith(p) for p in [".", "?", "!", "~", ","])

        has_pause = False
        if len(current_grp) > 1 and w_idx + 1 < len(words):
            next_w = words[w_idx + 1]
            if next_w.start - w.end > 0.35:
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
            display_end = min(last_end + 0.3, next_start - 0.04)
        else:
            display_end = min(clip_duration, last_end + 0.45)
        display_end = max(last_end, display_end)

        # Gap before group
        if grp_start > curr_timeline:
            gap = round(grp_start - curr_timeline, 3)
            if gap > 0.04:
                concat_entries.append(("blank.png", gap))
                curr_timeline = grp_start

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
            render_subtitle_frame(
                grp,
                active_idx=i,
                output_path=frame_path,
                style=style,
                active_color=active_color,
                normal_color=normal_color,
                marker_color=marker_color,
                font_name=font_name,
                y_center=y_center
            )

            concat_entries.append((frame_filename, dur))
            curr_timeline += dur
            frame_idx += 1

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
