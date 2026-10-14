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

def draw_card_with_shadow(
    img: Image.Image,
    box: List[int],
    radius: int = 24,
    fill: Tuple[int, int, int, int] = (255, 255, 255, 255),
    outline: Optional[Tuple[int, int, int, int]] = (220, 225, 235, 255),
    width: int = 2,
    shadow_blur: int = 16,
    shadow_offset: Tuple[int, int] = (0, 8),
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 60)
):
    """Draws a card with multi-layer soft blur drop shadow and crisp outline."""
    bx1, by1, bx2, by2 = box
    sx1, sy1 = bx1 + shadow_offset[0], by1 + shadow_offset[1]
    sx2, sy2 = bx2 + shadow_offset[0], by2 + shadow_offset[1]

    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    s_draw.rounded_rectangle([sx1, sy1, sx2, sy2], radius=radius, fill=shadow_color)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
    img.alpha_composite(shadow_layer)

    card_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card_layer)
    c_draw.rounded_rectangle([bx1, by1, bx2, by2], radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(card_layer)

def make_vertical_gradient(w: int, h: int, c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> Image.Image:
    """Creates a smooth 2-stop vertical gradient background."""
    grad = Image.new("RGBA", (1, h))
    for y in range(h):
        f = y / max(1, h - 1)
        r = int(c1[0] + f * (c2[0] - c1[0]))
        g = int(c1[1] + f * (c2[1] - c1[1]))
        b = int(c1[2] + f * (c2[2] - c1[2]))
        grad.putpixel((0, y), (r, g, b, 255))
    return grad.resize((w, h), Image.Resampling.BILINEAR)

def draw_tesla_t(draw: ImageDraw.ImageDraw, x: int, y: int, col: Tuple[int, int, int] = (235, 25, 45)):
    """Draws precise vector Tesla 'T' badge."""
    draw.polygon([(x - 22, y), (x + 22, y), (x + 20, y + 6), (x - 20, y + 6)], fill=col)
    draw.polygon([(x - 14, y + 10), (x + 14, y + 10), (x + 4, y + 42), (x - 4, y + 42)], fill=col)
    draw.arc([x - 28, y - 4, x + 28, y + 12], 200, 340, fill=col, width=4)

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
    f_black_72 = get_font(FONT_BLACK_HAN_SANS, 72)
    f_black_58 = get_font(FONT_BLACK_HAN_SANS, 58)
    f_pret_50 = get_font(FONT_PRETENDARD, 50)
    f_pret_36 = get_font(FONT_PRETENDARD, 36)
    f_pret_28 = get_font(FONT_PRETENDARD, 28)
    f_pret_22 = get_font(FONT_PRETENDARD, 22)
    f_pret_18 = get_font(FONT_PRETENDARD, 18)

    line1, line2 = split_hook_headline(highlight.title, highlight.hook_text)
    if not line1:
        line1 = "놓치면 후회하는 핵심 명장면"
    if not line2:
        line2 = f"클립 #{highlight.id} 지금 바로 확인!"

    # =========================================================================
    # 1. NEWS PORTAL (미리캔버스 속보 & 뉴스 포털)
    # =========================================================================
    if template.layout_type == "news_portal":
        img = make_vertical_gradient(canvas_w, canvas_h, (248, 250, 254), (236, 240, 248))
        draw = ImageDraw.Draw(img)

        # 1-1. Top Broadcast Red Bar
        draw.rectangle([0, 0, canvas_w, 136], fill=(215, 25, 38, 255))
        draw.text((70, 68), "MIRI NEWS", font=f_black_58, fill=(255, 255, 255), anchor="lm")
        # LIVE pill with red dot
        draw.rounded_rectangle([380, 46, 520, 90], radius=22, fill=(0, 0, 0, 180))
        draw.ellipse([400, 60, 416, 76], fill=(255, 60, 60))
        draw.text((465, 68), "LIVE", font=f_pret_28, fill=(255, 255, 255), anchor="mm")
        draw.text((canvas_w - 70, 68), "속보 특보", font=f_pret_28, fill=(255, 255, 255), anchor="rm")

        # 1-2. Floating Headline Card with Drop Shadow
        hy = 165
        head_box = [60, hy, canvas_w - 60, hy + 265]
        draw_card_with_shadow(img, head_box, radius=24, fill=(255, 255, 255, 255), outline=(225, 230, 240, 255), shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 40))

        draw = ImageDraw.Draw(img)
        # Red category chip
        draw.rounded_rectangle([90, hy + 22, 350, hy + 64], radius=10, fill=(255, 235, 238), outline=(255, 180, 190), width=1)
        draw.text((105, hy + 43), "긴급 속보 • 단독 리포트", font=f_pret_22, fill=(215, 25, 38), anchor="lm")

        # Line 1
        draw.text((90, hy + 102), line1[:28], font=f_pret_36, fill=(20, 25, 35), anchor="lm")

        # Line 2 with Highlighter Marker Tape
        l2_font = f_black_58
        l2_bbox = l2_font.getbbox(line2)
        if (l2_bbox[2] - l2_bbox[0]) > 880:
            l2_font = f_pret_36
            l2_bbox = l2_font.getbbox(line2)
        l2_w = l2_bbox[2] - l2_bbox[0]
        l2_h = l2_bbox[3] - l2_bbox[1]
        draw_marker(draw, [90, hy + 155, 90 + l2_w, hy + 155 + l2_h], color=template.marker_color, pad_x=10)
        draw.text((90, hy + 180), line2, font=l2_font, fill=(255, 255, 255) if template.marker_color[0] > 180 else (10, 12, 16), anchor="lm")

        # Byline
        draw.text((90, hy + 236), "단독 취재 | 핵심 꿀팁 특종 • 실시간 제보", font=f_pret_18, fill=(130, 135, 145), anchor="lm")

        # 1-3. Video Container Frame with Drop Shadow
        vx, vy, vw, vh = template.video_box
        v_shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        vs_draw = ImageDraw.Draw(v_shadow)
        vs_draw.rounded_rectangle([vx - 2, vy + 6, vx + vw + 2, vy + vh + 10], radius=20, fill=(0, 0, 0, 70))
        v_shadow = v_shadow.filter(ImageFilter.GaussianBlur(16))
        img.alpha_composite(v_shadow)

        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([vx - 3, vy - 3, vx + vw + 3, vy + vh + 3], radius=18, fill=(20, 24, 30))
        # Top-left red sticker on video frame
        draw.rounded_rectangle([vx + 20, vy + 20, vx + 220, vy + 66], radius=10, fill=(215, 25, 38, 245))
        draw.text((vx + 120, vy + 43), "HOT 실시간 제보", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # 1-4. Bottom News Briefing Card with Drop Shadow
        by = vy + vh + 32
        b_box = [60, by, canvas_w - 60, by + 460]
        draw_card_with_shadow(img, b_box, radius=24, fill=(255, 255, 255, 255), outline=(225, 230, 240, 255), shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 40))

        draw = ImageDraw.Draw(img)
        # Card header badge
        draw.rounded_rectangle([b_box[0] + 30, b_box[1] + 25, b_box[0] + 280, b_box[1] + 68], radius=12, fill=(215, 25, 38))
        draw.text((b_box[0] + 155, b_box[1] + 46), "MIRI NEWS 현장 브리핑", font=f_pret_22, fill=(255, 255, 255), anchor="mm")
        draw.text((b_box[2] - 30, b_box[1] + 46), "FACT-CHECK 완료", font=f_pret_22, fill=(120, 130, 145), anchor="rm")

        # Subtitle slot background pill
        draw.rounded_rectangle([b_box[0] + 25, b_box[1] + 90, b_box[2] - 25, b_box[1] + 210], radius=16, fill=(18, 22, 30))

        # Bullet summary points
        pts = highlight.summary_points if highlight.summary_points else [
            f"{highlight.title} 실전 핵심 설정",
            "상황별 권장 사용 가이드"
        ]
        p1 = f"• {pts[0]}"
        p2 = f"• {pts[1]}" if len(pts) > 1 else f"• {highlight.title} 실전 활용 팁"
        draw.text((b_box[0] + 35, b_box[1] + 250), p1[:34], font=f_pret_36, fill=(25, 30, 40), anchor="lm")
        draw.text((b_box[0] + 35, b_box[1] + 315), p2[:34], font=f_pret_28, fill=(70, 80, 95), anchor="lm")
        draw.text((b_box[0] + 35, b_box[1] + 380), "• [보도국] 자세한 내용은 상단 링크 및 채널에서 확인 가능", font=f_pret_22, fill=(130, 140, 155), anchor="lm")

        # Bottom News Ticker Bar
        draw.rectangle([0, canvas_h - 70, canvas_w, canvas_h], fill=(20, 24, 32))
        draw.text((70, canvas_h - 35), "▶ [단독 속보] 해피 쇼츠 스튜디오 AI 자동 생성기 100% 로컬 무료 구동 중", font=f_pret_22, fill=(255, 255, 255), anchor="lm")

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

        # Window Content Tip Card (inside macOS browser, no empty holes)
        sub_box_y = vy + vh + 25
        # Subtitle slot inside macOS window
        draw.rounded_rectangle([wx1 + 30, sub_box_y, wx2 - 30, sub_box_y + 130], radius=16, fill=(255, 255, 255), outline=(210, 216, 228), width=1)

        # Window Content Tip Card
        tip_y = sub_box_y + 155
        draw.rounded_rectangle([wx1 + 30, tip_y, wx2 - 30, tip_y + 135], radius=16, fill=(255, 255, 255), outline=(215, 220, 232), width=1)
        draw.text((wx1 + 55, tip_y + 24), "💡 실전 추천 포인트 & 가이드", font=f_pret_28, fill=(25, 30, 45), anchor="lt")
        pts = highlight.summary_points if highlight.summary_points else [f"{highlight.title} 핵심 설정", "추천 활용법"]
        draw.text((wx1 + 55, tip_y + 64), f"• {pts[0][:34]}", font=f_pret_28, fill=(50, 55, 70), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((wx1 + 55, tip_y + 98), f"• {p2[:34]}", font=f_pret_22, fill=(100, 105, 120), anchor="lt")

        # Window Hashtag Chips
        chip_y = tip_y + 160
        chips = [f"#{w}" for w in highlight.title.split() if len(w) > 1]
        if len(chips) < 3:
            chips += ["#핵심가이드", "#추천팁", "#쇼츠꿀팁"]
        chips = chips[:4]
        cx = wx1 + 35
        for ch in chips:
            ch_b = f_pret_28.getbbox(ch)
            ch_w = ch_b[2] - ch_b[0] + 32
            draw.rounded_rectangle([cx, chip_y, cx + ch_w, chip_y + 46], radius=12, fill=(215, 222, 235))
            draw.text((cx + ch_w // 2, chip_y + 23), ch, font=f_pret_28, fill=(35, 40, 55), anchor="mm")
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

        # Dedicated Glowing Subtitle Slot
        draw.rounded_rectangle([80, 940, canvas_w - 80, 1095], radius=20, fill=(18, 22, 32, 230), outline=(0, 255, 220, 90), width=2)
        draw.text((540, 965), "⚡ KEY INSIGHT", font=f_pret_22, fill=(0, 255, 220), anchor="mm")

        # Bottom Summary Point Card
        sc_y = 1135
        draw.rounded_rectangle([80, sc_y, canvas_w - 80, sc_y + 250], radius=22, fill=(22, 26, 38, 240), outline=(255, 255, 255, 40), width=2)
        draw.text((120, sc_y + 35), "[요약] 실전 핵심 가이드", font=f_pret_36, fill=(255, 215, 0), anchor="lt")
        pts = highlight.summary_points if highlight.summary_points else [
            f"{highlight.title} 실전 핵심 설정",
            "상황별 권장 사용 가이드"
        ]
        p1 = f"• {pts[0]}"
        p2 = f"• {pts[1]}" if len(pts) > 1 else f"• {highlight.title} 실전 활용 팁"
        draw.text((120, sc_y + 95), p1[:38], font=f_pret_28, fill=(235, 240, 255), anchor="lt")
        draw.text((120, sc_y + 155), p2[:38], font=f_pret_28, fill=(235, 240, 255), anchor="lt")
        draw.text((120, sc_y + 205), "• 전체 핵심 내용은 상단 링크에서 바로 확인하세요", font=f_pret_22, fill=(140, 150, 175), anchor="lt")

    # =========================================================================
    # 4. MESSENGER CHAT (카카오톡 / DM 대화 & 썰풀이)
    # =========================================================================
    elif template.layout_type == "messenger_chat":
        # Kakao Blue-grey background
        img = Image.new("RGBA", (canvas_w, canvas_h), (186, 206, 224, 255))
        draw = ImageDraw.Draw(img)

        # Top Chat Header Bar
        draw.rectangle([0, 0, canvas_w, 140], fill=(255, 255, 255, 240))
        # Profile circle
        draw.ellipse([60, 35, 130, 105], fill=(254, 229, 0))
        draw.text((95, 70), "💬", font=f_pret_36, anchor="mm")
        draw.text((150, 58), "익명 제보자 단톡방", font=f_pret_36, fill=(25, 25, 25), anchor="lm")
        draw.text((150, 95), "참여 1.2만명  •  실시간 썰", font=f_pret_22, fill=(110, 115, 125), anchor="lm")
        draw.line([(0, 140), (canvas_w, 140)], fill=(210, 220, 230), width=2)

        # Top Question Bubble (Yellow)
        draw.rounded_rectangle([60, 170, 780, 260], radius=20, fill=(254, 229, 0))
        draw.text((90, 215), line1[:22], font=f_pret_36, fill=(25, 25, 25), anchor="lm")

        # Second Bubble (White)
        draw.rounded_rectangle([60, 280, 850, 370], radius=20, fill=(255, 255, 255))
        draw.text((90, 325), line2[:24], font=f_pret_36, fill=(25, 25, 25), anchor="lm")

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=24, fill=(255, 255, 255))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Reply Input Bar Simulation
        draw.rounded_rectangle([50, canvas_h - 140, canvas_w - 50, canvas_h - 60], radius=40, fill=(255, 255, 255), outline=(200, 210, 225), width=2)
        draw.text((90, canvas_h - 100), "메시지를 입력하세요...", font=f_pret_28, fill=(150, 155, 165), anchor="lm")
        draw.rounded_rectangle([canvas_w - 150, canvas_h - 130, canvas_w - 65, canvas_h - 70], radius=30, fill=(254, 229, 0))
        draw.text((canvas_w - 108, canvas_h - 100), "전송", font=f_pret_22, fill=(25, 25, 25), anchor="mm")

    # =========================================================================
    # 5. RANKING CHART (100만 유튜버 랭킹 TOP 5)
    # =========================================================================
    elif template.layout_type == "ranking_chart":
        img = Image.new("RGBA", (canvas_w, canvas_h), (18, 16, 26, 255))
        draw = ImageDraw.Draw(img)

        # Top Gold Crown / Trophy Badge
        draw.rounded_rectangle([330, 70, 750, 145], radius=35, fill=(255, 140, 0), outline=(255, 220, 100), width=3)
        draw.text((540, 108), "🏆 TOP RANKING #1", font=f_pret_36, fill=(255, 255, 255), anchor="mm")

        # 2-line Headline
        draw.text((540, 190), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        draw_3d_text(draw, (540, 265), line2, f_black_72, fill=template.active_color, stroke_fill=(0, 0, 0), stroke_width=8)

        # Video Frame with Orange Flame Glow
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 6, vy - 6, vx + vw + 6, vy + vh + 6], radius=24, fill=(255, 120, 0, 240))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Ranking Specs Card with Dedicated Subtitle Slot
        sc_y = vy + vh + 35
        draw.rounded_rectangle([70, sc_y, canvas_w - 70, sc_y + 370], radius=24, fill=(30, 25, 42), outline=(255, 140, 0, 100), width=2)
        draw.rounded_rectangle([100, sc_y + 22, 280, sc_y + 66], radius=12, fill=(255, 140, 0))
        draw.text((190, sc_y + 44), "🔥 실시간 1위", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, sc_y + 80, canvas_w - 95, sc_y + 195], radius=16, fill=(18, 15, 26), outline=(255, 140, 0, 80), width=1)

        # Summary bullet points placed below subtitle slot
        pts = highlight.summary_points if highlight.summary_points else [f"{highlight.title} 핵심 포인트", "절대 놓치면 안 되는 이유"]
        draw.text((100, sc_y + 225), f"🥇 1위 선정 이유: {pts[0][:32]}", font=f_pret_28, fill=(245, 245, 255), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((100, sc_y + 285), f"⚡ 체크 포인트: {p2[:32]}", font=f_pret_28, fill=(245, 245, 255), anchor="lt")
        draw.text((100, sc_y + 335), "• 다음 순위 영상은 채널에서 바로 확인 가능합니다", font=f_pret_22, fill=(160, 150, 180), anchor="lt")

    # =========================================================================
    # 6. PRODUCT REVIEW (5성 별점 & 내돈내산 리뷰)
    # =========================================================================
    elif template.layout_type == "product_review":
        img = Image.new("RGBA", (canvas_w, canvas_h), (245, 248, 250, 255))
        draw = ImageDraw.Draw(img)

        # Top Rating Pill
        draw.rounded_rectangle([320, 65, 760, 135], radius=35, fill=(0, 230, 160), outline=(0, 180, 120), width=2)
        draw.text((540, 100), "★★★★★  평점 4.9", font=f_pret_36, fill=(10, 25, 20), anchor="mm")

        # Headline
        draw.text((540, 180), line1, font=f_pret_50, fill=(20, 30, 40), anchor="mm")
        l2_bbox = f_pret_50.getbbox(line2)
        l2_w = l2_bbox[2] - l2_bbox[0]
        l2_h = l2_bbox[3] - l2_bbox[1]
        cx = (canvas_w - l2_w) // 2
        draw_marker(draw, [cx, 255 - l2_h // 2, cx + l2_w, 255 + l2_h // 2], color=(0, 230, 160, 190), pad_x=12)
        draw.text((540, 255), line2, font=f_pret_50, fill=(10, 20, 30), anchor="mm")

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=24, fill=(20, 30, 40))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Pros/Cons Card with Dedicated Subtitle Slot
        sc_y = vy + vh + 35
        draw.rounded_rectangle([70, sc_y, canvas_w - 70, sc_y + 370], radius=24, fill=(255, 255, 255), outline=(210, 225, 235), width=2)
        draw.rounded_rectangle([100, sc_y + 22, 320, sc_y + 66], radius=12, fill=(0, 200, 140))
        draw.text((210, sc_y + 44), "내돈내산 솔직 평가", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, sc_y + 80, canvas_w - 95, sc_y + 195], radius=16, fill=(240, 245, 248), outline=(0, 200, 140, 90), width=1)

        # Summary bullet points placed below subtitle slot
        pts = highlight.summary_points if highlight.summary_points else [f"{highlight.title} 실전 장점", "주의할 점 및 추천 대상"]
        draw.text((100, sc_y + 225), f"✔ 추천 포인트: {pts[0][:32]}", font=f_pret_28, fill=(30, 40, 50), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((100, sc_y + 285), f"💡 구매 전 체크: {p2[:32]}", font=f_pret_28, fill=(30, 40, 50), anchor="lt")
        draw.text((100, sc_y + 335), "• 실사용자 평점 및 실시간 최저가는 본문 링크 참고", font=f_pret_22, fill=(120, 135, 145), anchor="lt")

    # =========================================================================
    # 7. MOTIVATION QUOTE (명언 & 동기부여 블랙 매거진)
    # =========================================================================
    elif template.layout_type == "motivation_quote":
        img = Image.new("RGBA", (canvas_w, canvas_h), (12, 12, 15, 255))
        draw = ImageDraw.Draw(img)

        # Huge Gold Quote Marks
        draw.text((540, 95), "“", font=f_black_72, fill=(245, 200, 80), anchor="mm")

        # Headline Quotes
        draw.text((540, 175), line1, font=f_pret_50, fill=(240, 240, 245), stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")
        draw.text((540, 250), f"\"{line2}\"", font=f_pret_50, fill=(245, 200, 80), stroke_width=3, stroke_fill=(0, 0, 0), anchor="mm")

        # Video Frame with Gold Border
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=20, fill=(245, 200, 80, 200))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Wisdom Reflection Card with Dedicated Subtitle Slot
        sc_y = vy + vh + 35
        draw.rounded_rectangle([80, sc_y, canvas_w - 80, sc_y + 370], radius=24, fill=(20, 20, 26), outline=(245, 200, 80, 80), width=1)
        draw.text((540, sc_y + 38), "✦ 오늘의 인생 인사이트 ✦", font=f_pret_36, fill=(245, 200, 80), anchor="mm")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, sc_y + 75, canvas_w - 95, sc_y + 190], radius=16, fill=(16, 16, 22), outline=(245, 200, 80, 70), width=1)

        # Reflection text placed below subtitle slot
        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "매일 실천하는 마인드셋"]
        draw.text((540, sc_y + 235), pts[0][:36], font=f_pret_28, fill=(220, 225, 235), anchor="mm")
        p2 = pts[1] if len(pts) > 1 else "지금 바로 저장하고 반복해 보세요"
        draw.text((540, sc_y + 295), p2[:36], font=f_pret_28, fill=(160, 165, 180), anchor="mm")
        draw.text((540, sc_y + 340), "지금 바로 저장하고 매일 아침 되새겨 보세요", font=f_pret_22, fill=(120, 125, 140), anchor="mm")

    # =========================================================================
    # 8. QUIZ & BALANCE GAME (A vs B 밸런스 게임)
    # =========================================================================
    elif template.layout_type == "quiz_balance":
        img = Image.new("RGBA", (canvas_w, canvas_h), (22, 20, 32, 255))
        draw = ImageDraw.Draw(img)

        # Top Quiz Tag
        draw.rounded_rectangle([340, 65, 740, 135], radius=35, fill=(255, 60, 80), outline=(255, 255, 255), width=2)
        draw.text((540, 100), "🔥 당신의 선택은?", font=f_pret_36, fill=(255, 255, 255), anchor="mm")

        # Headline
        draw.text((540, 180), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        draw_3d_text(draw, (540, 260), line2, f_black_72, fill=(255, 230, 0), stroke_fill=(0, 0, 0), stroke_width=8)

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=20, fill=(255, 60, 80))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Dedicated Subtitle Banner Slot directly under video
        draw.rounded_rectangle([70, 1005, canvas_w - 70, 1120], radius=18, fill=(16, 14, 24), outline=(255, 60, 80, 120), width=2)
        draw.text((540, 1030), "💬 실시간 시청자 토론", font=f_pret_22, fill=(255, 180, 190), anchor="mm")

        # Bottom A vs B Vote Card (Placed BELOW subtitle slot)
        box_y = 1150
        # Box A (Blue)
        draw.rounded_rectangle([70, box_y, 520, box_y + 250], radius=20, fill=(25, 50, 120), outline=(80, 130, 255), width=2)
        draw.text((295, box_y + 60), "옵션 A", font=f_pret_36, fill=(255, 255, 255), anchor="mm")
        draw.text((295, box_y + 130), "댓글로 A 투표!", font=f_pret_28, fill=(200, 220, 255), anchor="mm")
        draw.text((295, box_y + 195), "선택 비율 54%", font=f_pret_28, fill=(140, 200, 255), anchor="mm")

        # Box B (Red)
        draw.rounded_rectangle([560, box_y, 1010, box_y + 250], radius=20, fill=(120, 25, 45), outline=(255, 80, 100), width=2)
        draw.text((785, box_y + 60), "옵션 B", font=f_pret_36, fill=(255, 255, 255), anchor="mm")
        draw.text((785, box_y + 130), "댓글로 B 투표!", font=f_pret_28, fill=(255, 200, 210), anchor="mm")
        draw.text((785, box_y + 195), "선택 비율 46%", font=f_pret_28, fill=(255, 170, 180), anchor="mm")

    # =========================================================================
    # 9. VLOG POLAROID (인스타 감성 폴라로이드)
    # =========================================================================
    elif template.layout_type == "vlog_polaroid":
        # Warm cream background
        img = Image.new("RGBA", (canvas_w, canvas_h), (242, 238, 230, 255))
        draw = ImageDraw.Draw(img)

        # Washi Tape Sticker (Top-center)
        draw.rectangle([440, 60, 640, 110], fill=(220, 195, 160, 220))

        # Headline
        draw.text((540, 160), f"DAY LOG  •  {line1}", font=f_pret_36, fill=(70, 60, 50), anchor="mm")
        draw.text((540, 230), line2, font=f_pret_50, fill=(35, 30, 25), anchor="mm")

        # Polaroid White Paper Card Frame (holds the video)
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 25, vy - 25, vx + vw + 25, vy + vh + 85], radius=16, fill=(255, 255, 255), outline=(215, 210, 200), width=2)
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))
        # Polaroid bottom caption note
        draw.text((vx + 20, vy + vh + 45), f"MEMORIES  #{highlight.id:02d}  •  {highlight.title[:24]}", font=f_pret_28, fill=(100, 90, 80), anchor="lm")

        # Bottom Journal Note with Dedicated Subtitle Slot
        sc_y = 1040
        draw.rounded_rectangle([80, sc_y, canvas_w - 80, sc_y + 360], radius=20, fill=(255, 255, 255, 200), outline=(215, 210, 200), width=1)
        draw.text((120, sc_y + 28), "오늘의 감성 기록", font=f_pret_28, fill=(120, 105, 95), anchor="lt")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, sc_y + 65, canvas_w - 95, sc_y + 180], radius=16, fill=(248, 244, 236), outline=(215, 210, 200), width=1)

        pts = highlight.summary_points if highlight.summary_points else [highlight.title]
        draw.text((120, sc_y + 215), f"• {pts[0][:36]}", font=f_pret_28, fill=(60, 50, 40), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else "소중한 순간을 영상으로 기록합니다"
        draw.text((120, sc_y + 270), f"• {p2[:36]}", font=f_pret_28, fill=(90, 80, 70), anchor="lt")
        draw.text((120, sc_y + 320), "• [VLOG] 감성 일상 쇼츠 시리즈 연재 중", font=f_pret_22, fill=(140, 130, 120), anchor="lt")

    # =========================================================================
    # 10. FACETIME CALL (아이폰 화상통화 / FaceTime UI)
    # =========================================================================
    elif template.layout_type == "facetime_call":
        img = Image.new("RGBA", (canvas_w, canvas_h), (15, 18, 24, 255))
        draw = ImageDraw.Draw(img)

        # Top iOS Status Bar
        draw.text((80, 50), "9:41", font=f_pret_28, fill=(255, 255, 255), anchor="lm")
        draw.text((canvas_w - 80, 50), "5G  85%", font=f_pret_28, fill=(255, 255, 255), anchor="rm")

        # Top Call Status Pill
        draw.rounded_rectangle([330, 95, 750, 155], radius=30, fill=(30, 35, 45, 220), outline=(255, 255, 255, 60), width=1)
        draw.ellipse([360, 117, 376, 133], fill=(0, 230, 130))
        draw.text((540, 125), "화상 통화 연결 중 • 02:45", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # Headline
        draw.text((540, 210), line1, font=f_pret_36, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Call Control Bar
        by = vy + vh + 50
        # Mute button
        draw.ellipse([220, by, 320, by + 100], fill=(50, 55, 65, 240))
        draw.text((270, by + 50), "🔇", font=f_pret_36, anchor="mm")
        # End Call Red Button
        draw.ellipse([490, by, 590, by + 100], fill=(235, 50, 50))
        draw.text((540, by + 50), "📞", font=f_pret_36, fill=(255, 255, 255), anchor="mm")
        # Flip Camera Button
        draw.ellipse([760, by, 860, by + 100], fill=(50, 55, 65, 240))
        draw.text((810, by + 50), "📷", font=f_pret_36, anchor="mm")

    # =========================================================================
    # 11. INSTAGRAM REELS (인스타 릴스 & 피드 UI)
    # =========================================================================
    elif template.layout_type == "instagram_reels":
        img = Image.new("RGBA", (canvas_w, canvas_h), (12, 14, 20, 255))
        draw = ImageDraw.Draw(img)

        # Top Bar
        draw.text((60, 60), "Reels", font=f_pret_50, fill=(255, 255, 255), anchor="lt")
        draw.text((canvas_w - 60, 60), "📷", font=f_pret_36, fill=(255, 255, 255), anchor="rt")

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Right Action Column
        rx = canvas_w - 90
        actions = [("❤️", "2.5만"), ("💬", "1,420"), ("✈️", "공유"), ("🔖", "저장")]
        for idx, (icon, label) in enumerate(actions):
            ay = 950 + idx * 110
            draw.text((rx, ay), icon, font=f_pret_36, anchor="mm")
            draw.text((rx, ay + 38), label, font=f_pret_22, fill=(240, 240, 245), anchor="mm")

        # Bottom Profile & Caption
        draw.ellipse([60, 1660, 120, 1720], fill=(255, 215, 0))
        draw.text((90, 1690), "✨", font=f_pret_28, anchor="mm")
        draw.text((140, 1675), "@shorts_studio", font=f_pret_28, fill=(255, 255, 255), anchor="lm")
        draw.rounded_rectangle([320, 1660, 410, 1695], radius=8, fill=(0, 0, 0, 120), outline=(255, 255, 255), width=1)
        draw.text((365, 1677), "팔로우", font=f_pret_22, fill=(255, 255, 255), anchor="mm")
        draw.text((60, 1740), line1[:30], font=f_pret_28, fill=(255, 255, 255), anchor="lm")
        draw.text((60, 1785), f"🎵 원본 오디오  •  {highlight.title[:20]}", font=f_pret_22, fill=(200, 205, 220), anchor="lm")

    # =========================================================================
    # 12. IPHONE GALLERY & MEME (iOS 사진첩 삭제 경고 팝업 밈)
    # =========================================================================
    elif template.layout_type == "iphone_gallery":
        img = Image.new("RGBA", (canvas_w, canvas_h), (245, 245, 247, 255))
        draw = ImageDraw.Draw(img)

        # Top iOS Navigation Bar
        draw.rectangle([0, 0, canvas_w, 140], fill=(255, 255, 255))
        draw.text((60, 70), "‹ 앨범", font=f_pret_36, fill=(0, 122, 255), anchor="lm")
        draw.text((540, 70), "전체 사진", font=f_pret_36, fill=(10, 12, 16), anchor="mm")
        draw.text((canvas_w - 60, 70), "선택", font=f_pret_36, fill=(0, 122, 255), anchor="rm")
        draw.line([(0, 140), (canvas_w, 140)], fill=(220, 222, 230), width=1)

        # Headline
        draw.text((540, 200), line1, font=f_pret_50, fill=(20, 25, 35), anchor="mm")
        draw.text((540, 265), line2, font=f_pret_36, fill=(100, 105, 120), anchor="mm")

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=20, fill=(255, 255, 255), outline=(220, 222, 230), width=2)
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Dedicated Subtitle Slot Banner
        draw.rounded_rectangle([80, 1305, canvas_w - 80, 1425], radius=18, fill=(235, 238, 245), outline=(210, 215, 225), width=1)

        # Bottom iOS Action Sheet / Alert Dialog (Classic Meme format placed below subtitle)
        dy = 1460
        draw.rounded_rectangle([100, dy, canvas_w - 100, dy + 220], radius=24, fill=(255, 255, 255), outline=(210, 215, 225), width=2)
        draw.text((540, dy + 50), "이 사진이 모든 기기의 갤러리에서 삭제됩니다.", font=f_pret_28, fill=(30, 35, 45), anchor="mm")
        draw.line([(100, dy + 95), (canvas_w - 100, dy + 95)], fill=(230, 232, 240), width=1)
        draw.text((540, dy + 145), "사진 삭제", font=f_pret_36, fill=(255, 59, 48), anchor="mm")

    # =========================================================================
    # 13. MEME CARTOON (웹툰 & 페페 카툰 리액션 템플릿)
    # =========================================================================
    elif template.layout_type == "meme_cartoon":
        img = Image.new("RGBA", (canvas_w, canvas_h), (252, 250, 245, 255))
        draw = ImageDraw.Draw(img)

        # Comic Speech Bubble
        draw.rounded_rectangle([70, 70, canvas_w - 70, 240], radius=24, fill=(255, 235, 80), outline=(20, 20, 25), width=4)
        draw.text((540, 130), f"\"{line1}\"", font=f_black_72, fill=(20, 20, 25), anchor="mm")
        draw.text((540, 195), f"▶ {line2}", font=f_pret_36, fill=(40, 40, 50), anchor="mm")

        # Video Frame with Comic Ink Border
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 6, vy - 6, vx + vw + 6, vy + vh + 6], radius=16, fill=(20, 20, 25))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Webtoon Reaction Deck with Dedicated Subtitle Slot
        by = vy + vh + 30
        draw.rounded_rectangle([70, by, canvas_w - 70, by + 370], radius=24, fill=(255, 255, 255), outline=(20, 20, 25), width=4)
        draw.rounded_rectangle([100, by + 22, 330, by + 66], radius=12, fill=(20, 20, 25))
        draw.text((215, by + 44), "💬 실시간 베댓 1위", font=f_pret_28, fill=(255, 235, 80), anchor="mm")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, by + 80, canvas_w - 95, by + 195], radius=16, fill=(250, 248, 238), outline=(20, 20, 25), width=2)

        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "ㅋㅋㅋ 댓글 보고 인정함"]
        draw.text((100, by + 225), f"\" {pts[0][:34]} \"", font=f_pret_36, fill=(20, 20, 25), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else "이거 나만 지금 알았냐 ㅋㅋㅋ"
        draw.text((100, by + 290), f"▶ {p2[:36]}", font=f_pret_28, fill=(80, 85, 95), anchor="lt")
        draw.text((100, by + 335), "👍 4.8천개  •  답글 284개  •  공유하기", font=f_pret_22, fill=(120, 125, 135), anchor="lt")

    # =========================================================================
    # 14. CINEMA PREVIEW (금주 개봉작 시네마틱 필름 티켓)
    # =========================================================================
    elif template.layout_type == "cinema_preview":
        img = Image.new("RGBA", (canvas_w, canvas_h), (14, 15, 20, 255))
        draw = ImageDraw.Draw(img)

        # Top Ticket Strip
        draw.rounded_rectangle([80, 60, canvas_w - 80, 140], radius=18, fill=(28, 30, 40), outline=(245, 210, 110, 120), width=2)
        draw.text((110, 100), "CINEMA PREVIEW • TICKET NO. 0824", font=f_pret_28, fill=(245, 210, 110), anchor="lm")
        draw.text((canvas_w - 110, 100), "★ ★ ★ ★ ★  9.8", font=f_pret_28, fill=(255, 255, 255), anchor="rm")

        # Headline
        draw.text((540, 190), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")
        draw.text((540, 260), f"《 {line2} 》", font=f_pret_36, fill=(245, 210, 110), anchor="mm")

        # Video Frame with Cinematic Gold Border
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=16, fill=(245, 210, 110, 180))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Film Synopsis Card with Dedicated Subtitle Slot
        by = vy + vh + 35
        draw.rounded_rectangle([70, by, canvas_w - 70, by + 370], radius=24, fill=(24, 26, 36), outline=(245, 210, 110, 80), width=1)
        draw.text((110, by + 38), "[화제작 시네마 프리뷰]", font=f_pret_36, fill=(245, 210, 110), anchor="lt")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, by + 75, canvas_w - 95, by + 190], radius=16, fill=(15, 17, 24), outline=(245, 210, 110, 60), width=1)

        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "놓치면 안 될 명장면"]
        draw.text((110, by + 225), f"• 감상 포인트: {pts[0][:32]}", font=f_pret_28, fill=(230, 235, 245), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((110, by + 285), f"• 주요 특징: {p2[:32]}", font=f_pret_28, fill=(180, 190, 205), anchor="lt")
        draw.text((110, by + 335), "• 극장 개봉 및 OTT 스트리밍 일정 채널 커뮤니티 확인", font=f_pret_22, fill=(130, 140, 155), anchor="lt")

    # =========================================================================
    # 15. PIE CHART REACTION (흔한 팬의 일상.. 분노·답답함 99% 원형 차트)
    # =========================================================================
    elif template.layout_type == "pie_chart_reaction":
        img = Image.new("RGBA", (canvas_w, canvas_h), (18, 20, 30, 255))
        draw = ImageDraw.Draw(img)

        # Top Headline
        draw.rounded_rectangle([320, 65, 760, 135], radius=35, fill=(255, 60, 60))
        draw.text((540, 100), "🔥 흔한 팬들의 현실 반응", font=f_pret_36, fill=(255, 255, 255), anchor="mm")
        draw.text((540, 185), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        draw_3d_text(draw, (540, 265), line2, f_black_72, fill=(255, 220, 0), stroke_fill=(0, 0, 0), stroke_width=8)

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=20, fill=(255, 70, 70))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Statistics Deck with Dedicated Subtitle Slot
        by = vy + vh + 30
        draw.rounded_rectangle([70, by, canvas_w - 70, by + 380], radius=24, fill=(28, 32, 48), outline=(255, 80, 80, 80), width=2)
        # Stats Badges
        draw.rounded_rectangle([100, by + 20, 280, by + 68], radius=12, fill=(235, 50, 50))
        draw.text((190, by + 44), "답답함 45%", font=f_pret_28, fill=(255, 255, 255), anchor="mm")
        draw.rounded_rectangle([310, by + 20, 490, by + 68], radius=12, fill=(255, 130, 0))
        draw.text((400, by + 44), "분노 35%", font=f_pret_28, fill=(255, 255, 255), anchor="mm")
        draw.rounded_rectangle([520, by + 20, 700, by + 68], radius=12, fill=(255, 200, 0))
        draw.text((610, by + 44), "화병 19%", font=f_pret_28, fill=(20, 20, 20), anchor="mm")
        draw.rounded_rectangle([730, by + 20, 910, by + 68], radius=12, fill=(50, 200, 120))
        draw.text((820, by + 44), "이성 1%", font=f_pret_28, fill=(20, 20, 20), anchor="mm")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, by + 85, canvas_w - 95, by + 200], radius=16, fill=(18, 20, 32), outline=(255, 80, 80, 60), width=1)

        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "100% 실화... 내 모습인 줄 알았다"]
        draw.text((100, by + 235), f"\" {pts[0][:32]} \"", font=f_pret_36, fill=(255, 255, 255), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else "공감되면 좋아요와 댓글 남겨주세요!"
        draw.text((100, by + 300), f"• {p2[:36]}", font=f_pret_28, fill=(200, 210, 230), anchor="lt")
        draw.text((100, by + 345), "• 공감되면 좋아요와 댓글 남겨주세요!", font=f_pret_22, fill=(150, 160, 180), anchor="lt")

    # =========================================================================
    # 16. CHALLENGE FITNESS (오운완 챌린지 & 운동 루틴 미션)
    # =========================================================================
    elif template.layout_type == "challenge_fitness":
        img = Image.new("RGBA", (canvas_w, canvas_h), (18, 14, 20, 255))
        draw = ImageDraw.Draw(img)

        # Top Challenge Banner
        draw.rounded_rectangle([320, 65, 760, 135], radius=35, fill=(255, 45, 45), outline=(255, 120, 120), width=2)
        draw.text((540, 100), "🔥 [D-DAY] 오운완 챌린지", font=f_pret_36, fill=(255, 255, 255), anchor="mm")
        draw.text((540, 185), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        draw_3d_text(draw, (540, 265), line2, f_black_72, fill=(255, 60, 40), stroke_fill=(0, 0, 0), stroke_width=8)

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 6, vy - 6, vx + vw + 6, vy + vh + 6], radius=24, fill=(255, 50, 50))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Mission Checklist Card with Dedicated Subtitle Slot
        by = vy + vh + 30
        draw.rounded_rectangle([70, by, canvas_w - 70, by + 370], radius=24, fill=(30, 22, 32), outline=(255, 60, 60, 100), width=2)
        draw.rounded_rectangle([100, by + 22, 310, by + 66], radius=12, fill=(255, 45, 45))
        draw.text((205, by + 44), "오늘의 루틴 미션", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, by + 80, canvas_w - 95, by + 195], radius=16, fill=(18, 14, 22), outline=(255, 60, 60, 70), width=1)

        pts = highlight.summary_points if highlight.summary_points else [f"{highlight.title} 실전 루틴", "매일 꾸준히 반복하기"]
        draw.text((100, by + 225), f"✔ 미션 1: {pts[0][:32]}", font=f_pret_28, fill=(255, 245, 245), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((100, by + 285), f"🔥 미션 2: {p2[:32]}", font=f_pret_28, fill=(255, 245, 245), anchor="lt")
        draw.text((100, by + 335), "• 오운완 인증하고 오늘 하루도 갓생 완성!", font=f_pret_22, fill=(200, 170, 180), anchor="lt")

    # =========================================================================
    # 17. MINIMAL EDU (캔바 모던 클린 교육)
    # =========================================================================
    elif template.layout_type == "minimal_edu":
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

        # Bottom Knowledge Card with Dedicated Subtitle Slot
        sc_y = 1000
        draw.rounded_rectangle([70, sc_y, canvas_w - 70, sc_y + 370], radius=20, fill=(28, 34, 48), outline=(60, 72, 95), width=2)
        draw.text((110, sc_y + 35), "[노트] 핵심 지식 정리", font=f_pret_36, fill=(255, 255, 255), anchor="lt")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, sc_y + 75, canvas_w - 95, sc_y + 190], radius=16, fill=(18, 22, 32), outline=(60, 75, 105), width=1)

        pts = highlight.summary_points if highlight.summary_points else [
            f"{highlight.title} 실전 핵심 가이드",
            "상황별 권장 사용법 정리"
        ]
        p1 = f"• {pts[0]}"
        p2 = f"• {pts[1]}" if len(pts) > 1 else f"• {highlight.title} 실전 활용 팁"
        draw.text((110, sc_y + 225), p1[:38], font=f_pret_28, fill=(210, 220, 235), anchor="lt")
        draw.text((110, sc_y + 285), p2[:38], font=f_pret_28, fill=(180, 195, 215), anchor="lt")
        draw.text((110, sc_y + 335), "• [지식 보관소] 유익했다면 저장하고 친구에게 공유하세요", font=f_pret_22, fill=(130, 145, 165), anchor="lt")

    # =========================================================================
    # 20. VLOG STICKER LIFESTYLE (나를 바꾼 습관 3가지 & 감성 3D 스티커)
    # =========================================================================
    elif template.layout_type == "vlog_sticker_lifestyle":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Soft top dark vignette
        for y in range(480):
            alpha = int(140 * (1 - y / 480))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Top Pastel Wave Badge
        draw.rounded_rectangle([380, 95, 700, 155], radius=30, fill=(232, 255, 130, 235), outline=(255, 255, 255, 220), width=2)
        draw.text((540, 125), "〰️ SELF TALK 〰️", font=f_pret_28, fill=(25, 40, 15), anchor="mm")

        # Title Tier 1 & Tier 2
        draw.text((540, 215), f"★  {line1[:16]}  ★", font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(15, 20, 25), anchor="mm")
        draw.text((540, 295), line2[:18], font=f_black_72, fill=(232, 255, 130), stroke_width=6, stroke_fill=(20, 30, 15), anchor="mm")

        # Floating 3D Stickers (Clean Styled Badges)
        # 1. Coffee cup sticker (left)
        draw_card_with_shadow(img, [60, 360, 230, 430], radius=20, fill=(255, 250, 240, 245), outline=(230, 215, 195, 255), shadow_blur=12, shadow_offset=(0, 6), shadow_color=(0, 0, 0, 50))
        draw = ImageDraw.Draw(img)
        draw.text((145, 395), "☕ COFFEE", font=f_pret_22, fill=(120, 80, 50), anchor="mm")

        # 2. Yoga bubble sticker (right)
        draw_card_with_shadow(img, [canvas_w - 230, 350, canvas_w - 60, 420], radius=20, fill=(248, 238, 255, 245), outline=(225, 210, 245, 255), shadow_blur=12, shadow_offset=(0, 6), shadow_color=(0, 0, 0, 50))
        draw = ImageDraw.Draw(img)
        draw.text((canvas_w - 145, 385), "🧘 REST", font=f_pret_22, fill=(110, 60, 160), anchor="mm")

        # 3. Plant sticker (bottom right)
        draw_card_with_shadow(img, [canvas_w - 230, 1370, canvas_w - 60, 1440], radius=20, fill=(235, 255, 240, 245), outline=(200, 240, 210, 255), shadow_blur=12, shadow_offset=(0, 6), shadow_color=(0, 0, 0, 50))
        draw = ImageDraw.Draw(img)
        draw.text((canvas_w - 145, 1405), "🌿 HABIT", font=f_pret_22, fill=(35, 120, 55), anchor="mm")

    # =========================================================================
    # 21. VLOG MONEY SALARY (프리랜서 평균 수입 & 테이프 스티커)
    # =========================================================================
    elif template.layout_type == "vlog_money_salary":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Soft top dark vignette
        for y in range(540):
            alpha = int(150 * (1 - y / 540))
            draw.line([(0, y), (canvas_w, y)], fill=(10, 12, 18, alpha))

        # Top Pink Capsule
        draw.rounded_rectangle([320, 100, 760, 165], radius=32, fill=(255, 225, 235, 240), outline=(255, 180, 205), width=2)
        draw.text((540, 132), "{ FREELANCER VLOG }", font=f_pret_28, fill=(215, 45, 95), anchor="mm")

        # Bold Title
        draw.text((540, 235), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(15, 15, 20), anchor="mm")

        # Diagonal Tape Stickers
        # Mint Tape (left)
        draw.rounded_rectangle([90, 320, 520, 395], radius=8, fill=(185, 245, 230, 245), outline=(120, 220, 200), width=2)
        draw.text((305, 357), "진짜 월 1000만원?", font=f_pret_36, fill=(15, 80, 70), anchor="mm")
        # Yellow Tape (right)
        draw.rounded_rectangle([530, 415, 980, 490], radius=8, fill=(255, 245, 180, 245), outline=(235, 215, 130), width=2)
        draw.text((755, 452), "꾸준히 일 받는 법", font=f_pret_36, fill=(95, 75, 10), anchor="mm")

        # Golden Revenue Badge
        draw_card_with_shadow(img, [canvas_w - 240, 210, canvas_w - 60, 275], radius=16, fill=(255, 235, 120, 245), outline=(235, 205, 50, 255), shadow_blur=10, shadow_offset=(0, 5), shadow_color=(0, 0, 0, 50))
        draw = ImageDraw.Draw(img)
        draw.text((canvas_w - 150, 242), "$$$ REVENUE", font=f_pret_22, fill=(120, 90, 10), anchor="mm")

        # Bottom Creator Watermark
        draw.text((540, 1820), "@designer.miri  •  실시간 VLOG", font=f_pret_22, fill=(255, 255, 255, 190), anchor="mm")

    # =========================================================================
    # 22. PROMO FITNESS GYM (미리짐 오운완 챌린지 & 참여방법 CTA)
    # =========================================================================
    elif template.layout_type == "promo_fitness_gym":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Top Bar & Brand Logo
        draw.text((70, 75), "MIRIGYM", font=f_black_58, fill=(235, 30, 45), anchor="lm")
        draw.ellipse([canvas_w - 180, 50, canvas_w - 130, 100], outline=(255, 255, 255, 200), width=2)
        draw.text((canvas_w - 155, 75), "+", font=f_pret_36, fill=(255, 255, 255), anchor="mm")
        draw.ellipse([canvas_w - 110, 50, canvas_w - 60, 100], outline=(255, 255, 255, 200), width=2)
        draw.text((canvas_w - 85, 75), "♡", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # Top Header Title (Relocated to top for clean poster look)
        draw.text((70, 145), "미리짐 오운완 챌린지", font=f_black_58, fill=(255, 255, 255), anchor="lt")
        draw.text((70, 220), "선착순 특별 이벤트!", font=f_pret_36, fill=(255, 220, 0), anchor="lt")

        # Bottom Cinematic Dark Gradient
        for y in range(1200, canvas_h):
            alpha = int(225 * ((y - 1200) / (canvas_h - 1200)))
            draw.line([(0, y), (canvas_w, y)], fill=(5, 8, 14, alpha))

        # Red CTA Button & Date (Anchored neatly at bottom)
        draw.rounded_rectangle([70, 1440, 310, 1515], radius=12, fill=(235, 25, 45))
        draw.text((190, 1477), "▶ 참여방법", font=f_pret_36, fill=(255, 255, 255), anchor="mm")
        draw.text((340, 1477), "한 달간 선착순 특별 혜택!", font=f_pret_28, fill=(235, 240, 250), anchor="lm")

        # Benefit description
        draw.text((70, 1545), "#오운완 #인증샷 태그하고 업로드!", font=f_pret_28, fill=(255, 220, 0), anchor="lt")
        draw.text((70, 1590), "운동 후 필수인 프리미엄 단백질 쉐이크 1잔 즉시 증정", font=f_pret_28, fill=(240, 245, 255), anchor="lt")
        draw.text((70, 1635), "업로드 후 데스크 직원에게 화면 보여주면 바로 수령", font=f_pret_22, fill=(180, 190, 210), anchor="lt")

        # Bottom Red Progress Bar
        draw.line([(70, 1870), (canvas_w - 70, 1870)], fill=(70, 75, 85), width=6)
        draw.line([(70, 1870), (450, 1870)], fill=(235, 25, 45), width=6)

    # =========================================================================
    # 23. YOUTH TIPS PICK (모르면 손해보는 청년혜택 총정리)
    # =========================================================================
    elif template.layout_type == "youth_tips_pick":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Soft top dark vignette
        for y in range(540):
            alpha = int(160 * (1 - y / 540))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Top Subhead
        draw.text((80, 95), "놓치면 진짜 아까워요!", font=f_pret_36, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0), anchor="lt")

        # Main Headline 1
        draw.text((80, 160), "모르면 손해보는", font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="lt")

        # Neon Yellow Box + Highlight Text
        draw.rectangle([80, 240, 460, 330], fill=(235, 255, 30))
        draw.text((270, 285), "청년혜택", font=f_black_58, fill=(10, 15, 20), anchor="mm")
        draw.text((490, 250), "총정리", font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="lt")

        # Floating PICK! Sticker (Bottom Left)
        draw.ellipse([80, 1460, 310, 1540], fill=(235, 255, 30))
        draw.text((195, 1500), "PICK", font=f_black_58, fill=(15, 20, 25), anchor="mm")
        draw.text((195, 1570), "저장하고 써보세요!", font=f_pret_28, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")

        # Disclaimer
        draw.text((canvas_w - 80, 1860), "* 2026 정부지원 정책 기준 (상세 기준 문의)", font=f_pret_22, fill=(255, 255, 255, 180), anchor="rm")

    # =========================================================================
    # 24. DRAMA WEEKLY PREVIEW (이번 주 가장 많이 본 명장면 다시보기)
    # =========================================================================
    elif template.layout_type == "drama_weekly_preview":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Top Pill
        draw.rounded_rectangle([300, 100, 780, 165], radius=32, fill=(225, 25, 40), outline=(255, 80, 90), width=2)
        draw.text((540, 132), "▶ 이번 주 짧은 드라마", font=f_pret_28, fill=(255, 255, 255), anchor="mm")

        # Center Bold Clean Headline
        draw.text((540, 230), "'가장 많이", font=f_black_72, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 10, 15), anchor="mm")
        draw.text((540, 320), "본 장면'", font=f_black_72, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 10, 15), anchor="mm")
        draw.text((540, 410), "다시 보기!", font=f_black_72, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 10, 15), anchor="mm")

        # Bottom Red Card: WEEKLY PREVIEW
        draw.rounded_rectangle([70, 1560, canvas_w - 70, 1830], radius=24, fill=(225, 25, 40))
        draw.text((110, 1610), "WEEKLY PREVIEW", font=f_black_58, fill=(255, 255, 255), anchor="lt")
        draw.rectangle([110, 1690, 240, 1775], fill=(20, 20, 25))
        draw.text((175, 1732), "▶", font=f_pret_36, fill=(225, 25, 40), anchor="mm")
        draw.text((270, 1715), "TODAY PICK! ✔", font=f_pret_28, fill=(255, 255, 255), anchor="lm")
        draw.text((270, 1755), "풀버전은 고정 댓글 확인하실 수 있습니다.", font=f_pret_22, fill=(255, 230, 235), anchor="lm")

    # =========================================================================
    # 25. TESLA FSD VISION (테슬라 FSD 자율주행 HUD 대시보드)
    # =========================================================================
    elif template.layout_type == "tesla_fsd_vision":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

        # 1. Top Glass HUD Gradient
        top_glass = Image.new("RGBA", (1, 260))
        for y in range(260):
            alpha = int(240 * (1.0 - (y / 260) ** 1.8))
            top_glass.putpixel((0, y), (10, 13, 20, alpha))
        img.alpha_composite(top_glass.resize((canvas_w, 260), Image.Resampling.BILINEAR), (0, 0))

        draw = ImageDraw.Draw(img)

        # Left: Tesla Red Brand
        draw_tesla_t(draw, 80, 60)
        draw.text((120, 50), "TESLA", font=f_pret_36, fill=(255, 255, 255), anchor="lm")
        draw.text((120, 88), "FSD v13.2 AUTOPILOT", font=f_pret_22, fill=(150, 165, 185), anchor="lm")

        # Center: Drive Mode & FSD Pill
        draw.text((540, 50), "P   R   N   D*", font=f_pret_28, fill=(140, 150, 170), anchor="mm")
        draw.rounded_rectangle([390, 75, 690, 125], radius=16, fill=(12, 38, 28, 230), outline=(0, 230, 140), width=2)
        draw.text((540, 98), "🟢 FSD 자율주행 활성화", font=f_pret_22, fill=(0, 245, 160), anchor="mm")

        # Right: Speedometer & Speed Limit Sign
        draw.text((canvas_w - 180, 52), "105", font=f_black_72, fill=(255, 255, 255), anchor="rm")
        draw.text((canvas_w - 172, 58), "km/h", font=f_pret_22, fill=(170, 185, 205), anchor="lm")

        sl_cx, sl_cy = canvas_w - 110, 52
        draw.ellipse([sl_cx - 24, sl_cy - 24, sl_cx + 24, sl_cy + 24], fill=(255, 255, 255), outline=(235, 25, 45), width=5)
        draw.text((sl_cx, sl_cy), "100", font=f_pret_18, fill=(10, 10, 10), anchor="mm")

        # Battery Status
        draw.text((canvas_w - 80, 100), "88% ⚡ 432km", font=f_pret_22, fill=(0, 230, 140), anchor="rm")

        # 2. Bottom Control Dock with Frosted Glass Drop Shadow
        dock_box = [60, 1680, canvas_w - 60, 1860]
        draw_card_with_shadow(img, dock_box, radius=28, fill=(14, 18, 26, 235), outline=(50, 65, 85, 200), width=2, shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 100))

        draw = ImageDraw.Draw(img)
        # Controls
        draw.text((110, 1745), "21.5°C 💨", font=f_pret_28, fill=(255, 255, 255), anchor="lm")
        draw.text((110, 1795), "♨️ 좌석 열선 2단", font=f_pret_22, fill=(150, 165, 185), anchor="lm")

        # Media & Nav
        draw.text((540, 1735), "🎵 Spotify: Ambient Driving", font=f_pret_28, fill=(255, 255, 255), anchor="mm")
        draw.rounded_rectangle([360, 1762, 720, 1768], radius=3, fill=(45, 55, 75))
        draw.rounded_rectangle([360, 1762, 530, 1768], radius=3, fill=(0, 230, 140))
        nav_dest = highlight.title[:22] if highlight.title else "판교 테크노밸리"
        draw.text((540, 1805), f"📍 목적지: {nav_dest}", font=f_pret_22, fill=(160, 175, 195), anchor="mm")

        # Right Status
        draw.text((canvas_w - 110, 1745), "🔋 AUTO", font=f_pret_28, fill=(0, 230, 140), anchor="rm")
        draw.text((canvas_w - 110, 1795), "🚗 헤드라이트 ON", font=f_pret_22, fill=(150, 165, 185), anchor="rm")

    else:
        # Generic clean fallback
        img = Image.new("RGBA", (canvas_w, canvas_h), (20, 24, 34, 255))
        draw = ImageDraw.Draw(img)
        draw.text((540, 180), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0), anchor="mm")
        draw.text((540, 250), line2, font=f_pret_50, fill=(255, 230, 0), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    if img.mode == "RGBA":
        img.save(output_path, "PNG")
    else:
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
