import os
import re
import math
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.models import Word, Highlight, VideoMetadata
from src.templates import ShortsTemplate, get_template

FONTS_DIR = Path("assets/fonts")

FONT_BLACK_HAN_SANS = str(FONTS_DIR / "BlackHanSans-Regular.ttf")
FONT_PRETENDARD = str(FONTS_DIR / "Pretendard-ExtraBold.ttf")

FONT_REGISTRY: Dict[str, str] = {
    # 1. Extreme Bold & Impact (속보, 펀치라인, 뉴스, HUD)
    "gasoek": "GasoekOne-Regular.ttf",
    "black_han_sans": "BlackHanSans-Regular.ttf",
    "dohyeon": "DoHyeon-Regular.ttf",
    
    # 2. Cute, Meme, Comic & Casual (예능, 밈, 카툰, 퀴즈, 챌린지)
    "bagel": "BagelFatOne-Regular.ttf",
    "jua": "Jua-Regular.ttf",
    
    # 3. Emotion, Classic Serif & Cinema (명언, 감성, 영화, 드라마)
    "gowun_batang": "GowunBatang-Bold.ttf",
    "song_myung": "SongMyung-Regular.ttf",
    
    # 4. Handwriting & Lifestyle Vlog (브이로그, 일기, 스티커)
    "dongle": "Dongle-Bold.ttf",
    "gaegu": "Gaegu-Bold.ttf",
    "poor_story": "PoorStory-Regular.ttf",
    "yeon_sung": "YeonSung-Regular.ttf",
    
    # 5. Clean Modern & Tech (지식, 테크, 모던 교육)
    "pretendard": "Pretendard-ExtraBold.ttf",
    "sunflower": "Sunflower-Bold.ttf",
    
    # 6. Artistic, Calligraphy & Graphic Design (파격 아트, 먹물 캘리, 레트로 포스터)
    "kirang": "KirangHaerang-Regular.ttf",
    "dokdo": "Dokdo-Regular.ttf",
    "east_sea_dokdo": "EastSeaDokdo-Regular.ttf",
    "black_white_picture": "BlackAndWhitePicture-Regular.ttf",
    "nanum_brush": "NanumBrushScript-Regular.ttf",
    "nanum_pen": "NanumPenScript-Regular.ttf",
}

FONT_ALIASES: Dict[str, str] = {
    "black_han_sans": "black_han_sans",
    "blackhansans": "black_han_sans",
    "pretendard": "pretendard",
    "pretendard_extrabold": "pretendard",
    "dohyeon": "dohyeon",
    "bm_dohyeon": "dohyeon",
    "jua": "jua",
    "bm_jua": "jua",
    "bagel": "bagel",
    "bagel_fat_one": "bagel",
    "bagelfatone": "bagel",
    "gasoek": "gasoek",
    "gasoek_one": "gasoek",
    "gasoekone": "gasoek",
    "gowun_batang": "gowun_batang",
    "gowun": "gowun_batang",
    "batang": "gowun_batang",
    "song_myung": "song_myung",
    "songmyung": "song_myung",
    "dongle": "dongle",
    "gaegu": "gaegu",
    "poor_story": "poor_story",
    "poorstory": "poor_story",
    "sunflower": "sunflower",
    "yeon_sung": "yeon_sung",
    "yeonsung": "yeon_sung",
    "kirang": "kirang",
    "kirang_haerang": "kirang",
    "kiranghaerang": "kirang",
    "dokdo": "dokdo",
    "east_sea_dokdo": "east_sea_dokdo",
    "eastseadokdo": "east_sea_dokdo",
    "black_white_picture": "black_white_picture",
    "bw_picture": "black_white_picture",
    "vintage": "black_white_picture",
    "nanum_brush": "nanum_brush",
    "brush": "nanum_brush",
    "nanum_pen": "nanum_pen",
    "pen": "nanum_pen",
}

def resolve_font_path(font_name_or_path: str) -> str:
    """Resolve font key, alias, or path into an absolute/relative font file path."""
    if not font_name_or_path:
        return FONT_BLACK_HAN_SANS
    
    if os.path.exists(font_name_or_path):
        return font_name_or_path
        
    key = str(font_name_or_path).lower().strip()
    canonical = FONT_ALIASES.get(key, key)
    filename = FONT_REGISTRY.get(canonical)
    if filename:
        p = FONTS_DIR / filename
        if p.exists():
            return str(p)
            
    direct = FONTS_DIR / font_name_or_path
    if direct.exists():
        return str(direct)
        
    if "pret" in key:
        return FONT_PRETENDARD
    return FONT_BLACK_HAN_SANS

def get_font(font_path_or_key: str, size: int) -> ImageFont.FreeTypeFont:
    path = resolve_font_path(font_path_or_key)
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
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


def draw_marker(
    draw: ImageDraw.ImageDraw,
    bbox: List[int],
    color: Tuple[int, int, int, int] = (255, 230, 0, 210),
    pad_x: int = 14,
    style: str = "full"
):
    """Draws a semi-transparent highlighter marker tape strip with clean padding."""
    x1, y1, x2, y2 = bbox
    th = y2 - y1
    if style == "underline":
        my1 = int(y2 - th * 0.45)
        my2 = int(y2 + 4)
        draw.rounded_rectangle([x1 - pad_x, my1, x2 + pad_x, my2], radius=6, fill=color)
    else:
        # Full highlighter tape strip behind text with modern rounded corners
        my1 = int(y1 - 6)
        my2 = int(y2 + 6)
        draw.rounded_rectangle([x1 - pad_x, my1, x2 + pad_x, my2], radius=10, fill=color)

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

def draw_gradient_text_art(
    target_img: Image.Image,
    center_xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    top_color: Tuple[int, int, int],
    bottom_color: Tuple[int, int, int],
    stroke_color: Tuple[int, int, int] = (15, 18, 25),
    stroke_width: int = 7,
    shadow_offset: Tuple[int, int] = (0, 7),
    shadow_blur: int = 8,
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 160)
) -> Tuple[int, int, int, int]:
    """
    Renders high-impact gradient typography with soft drop shadow.
    Looks like professional graphic logotype artwork.
    """
    cx, cy = center_xy
    dummy = Image.new("RGBA", (10, 10))
    d_draw = ImageDraw.Draw(dummy)
    bbox = d_draw.textbbox((0, 0), text, font=font, anchor="mm")
    tw = max(10, bbox[2] - bbox[0])
    th = max(10, bbox[3] - bbox[1])

    pad = 50 + stroke_width + shadow_blur
    lw = tw + pad * 2
    lh = th + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    lcx, lcy = lw // 2, lh // 2

    # 1. Soft blurred drop shadow
    if shadow_blur > 0 or shadow_offset != (0, 0):
        shadow_img = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow_img)
        sdraw.text(
            (lcx + shadow_offset[0], lcy + shadow_offset[1]),
            text, font=font, fill=shadow_color,
            stroke_width=stroke_width + 2, stroke_fill=shadow_color,
            anchor="mm"
        )
        if shadow_blur > 0:
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur))
        layer.alpha_composite(shadow_img)

    # 2. Heavy border stroke
    if stroke_width > 0:
        ldraw.text(
            (lcx, lcy), text, font=font,
            fill=stroke_color, stroke_width=stroke_width, stroke_fill=stroke_color,
            anchor="mm"
        )

    # 3. Gradient filled face
    mask_img = Image.new("L", (lw, lh), 0)
    mdraw = ImageDraw.Draw(mask_img)
    mdraw.text((lcx, lcy), text, font=font, fill=255, anchor="mm")

    grad_img = Image.new("RGBA", (lw, lh))
    y_start = lcy - th // 2
    y_end = max(y_start + 1, lcy + th // 2)
    for y in range(lh):
        ratio = max(0.0, min(1.0, (y - y_start) / max(1, (y_end - y_start))))
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        for x in range(lw):
            grad_img.putpixel((x, y), (r, g, b, 255))

    layer.paste(grad_img, (0, 0), mask=mask_img)

    dst_x = cx - lcx
    dst_y = cy - lcy
    target_img.alpha_composite(layer, (dst_x, dst_y))
    return (cx - tw // 2, cy - th // 2, cx + tw // 2, cy + th // 2)

def draw_3d_extruded_text_art(
    target_img: Image.Image,
    center_xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    front_color: Tuple[int, int, int] = (255, 230, 0),
    side_color: Tuple[int, int, int] = (220, 70, 0),
    stroke_color: Tuple[int, int, int] = (15, 18, 24),
    depth: int = 12,
    stroke_width: int = 6
) -> Tuple[int, int, int, int]:
    """
    Renders chunky 3D extruded block lettering with layered perspective depth.
    Looks like a 3D sculpted toy/game/YouTube mega-title!
    """
    cx, cy = center_xy
    dummy = Image.new("RGBA", (10, 10))
    d_draw = ImageDraw.Draw(dummy)
    bbox = d_draw.textbbox((0, 0), text, font=font, anchor="mm")
    tw = max(10, bbox[2] - bbox[0])
    th = max(10, bbox[3] - bbox[1])

    pad = 40 + depth + stroke_width
    lw = tw + pad * 2
    lh = th + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    lcx, lcy = lw // 2, lh // 2

    # 1. Base drop shadow behind the 3D block
    s_img = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(s_img)
    sdraw.text(
        (lcx, lcy + depth + 4),
        text, font=font, fill=(0, 0, 0, 180),
        stroke_width=stroke_width + 4, stroke_fill=(0, 0, 0, 180),
        anchor="mm"
    )
    s_img = s_img.filter(ImageFilter.GaussianBlur(8))
    layer.alpha_composite(s_img)

    # 2. Extrusion steps from back to front
    for d in range(depth, 0, -1):
        ratio = d / depth
        cr = max(0, int(side_color[0] * (0.6 + 0.4 * (1 - ratio))))
        cg = max(0, int(side_color[1] * (0.6 + 0.4 * (1 - ratio))))
        cb = max(0, int(side_color[2] * (0.6 + 0.4 * (1 - ratio))))
        ldraw.text(
            (lcx, lcy + d),
            text, font=font, fill=(cr, cg, cb),
            stroke_width=stroke_width, stroke_fill=stroke_color,
            anchor="mm"
        )

    # 3. Front face with crisp stroke
    ldraw.text(
        (lcx, lcy),
        text, font=font, fill=front_color,
        stroke_width=stroke_width, stroke_fill=stroke_color,
        anchor="mm"
    )

    dst_x = cx - lcx
    dst_y = cy - lcy
    target_img.alpha_composite(layer, (dst_x, dst_y))
    return (cx - tw // 2, cy - th // 2, cx + tw // 2, cy + th // 2 + depth)

def draw_neon_glow_text_art(
    target_img: Image.Image,
    center_xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    neon_color: Tuple[int, int, int] = (0, 255, 230),
    core_color: Tuple[int, int, int] = (255, 255, 255),
    glow_radius: int = 16
) -> Tuple[int, int, int, int]:
    """
    Renders radiant cyberpunk neon light tube typography with multi-stage glow.
    """
    cx, cy = center_xy
    dummy = Image.new("RGBA", (10, 10))
    d_draw = ImageDraw.Draw(dummy)
    bbox = d_draw.textbbox((0, 0), text, font=font, anchor="mm")
    tw = max(10, bbox[2] - bbox[0])
    th = max(10, bbox[3] - bbox[1])

    pad = 40 + glow_radius
    lw = tw + pad * 2
    lh = th + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    lcx, lcy = lw // 2, lh // 2

    # Wide outer glow
    g1 = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    g1_draw = ImageDraw.Draw(g1)
    g1_draw.text((lcx, lcy), text, font=font, fill=(*neon_color, 240), stroke_width=10, stroke_fill=(*neon_color, 240), anchor="mm")
    g1 = g1.filter(ImageFilter.GaussianBlur(glow_radius))
    layer.alpha_composite(g1)

    # Tight inner glow
    g2 = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    g2_draw = ImageDraw.Draw(g2)
    g2_draw.text((lcx, lcy), text, font=font, fill=(*neon_color, 255), stroke_width=3, stroke_fill=(*neon_color, 255), anchor="mm")
    g2 = g2.filter(ImageFilter.GaussianBlur(max(2, glow_radius // 3)))
    layer.alpha_composite(g2)

    # Core white hot tube
    ldraw = ImageDraw.Draw(layer)
    ldraw.text((lcx, lcy), text, font=font, fill=core_color, stroke_width=2, stroke_fill=(*neon_color, 200), anchor="mm")

    dst_x = cx - lcx
    dst_y = cy - lcy
    target_img.alpha_composite(layer, (dst_x, dst_y))
    return (cx - tw // 2, cy - th // 2, cx + tw // 2, cy + th // 2)

def draw_sticker_badge_text_art(
    target_img: Image.Image,
    center_xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    text_color: Tuple[int, int, int] = (15, 20, 30),
    sticker_border_color: Tuple[int, int, int] = (255, 255, 255),
    border_width: int = 12,
    angle_deg: float = -2.0
) -> Tuple[int, int, int, int]:
    """
    Renders die-cut vinyl sticker typography with crisp white cut-line and peel shadow.
    """
    cx, cy = center_xy
    dummy = Image.new("RGBA", (10, 10))
    d_draw = ImageDraw.Draw(dummy)
    bbox = d_draw.textbbox((0, 0), text, font=font, anchor="mm")
    tw = max(10, bbox[2] - bbox[0])
    th = max(10, bbox[3] - bbox[1])

    pad = 40 + border_width
    lw = tw + pad * 2
    lh = th + pad * 2
    sticker = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sticker)
    scx, scy = lw // 2, lh // 2

    # Die-cut border
    sdraw.text((scx, scy), text, font=font, fill=sticker_border_color, stroke_width=border_width, stroke_fill=sticker_border_color, anchor="mm")
    # Face
    sdraw.text((scx, scy), text, font=font, fill=text_color, anchor="mm")

    if angle_deg != 0.0:
        sticker = sticker.rotate(angle_deg, resample=Image.Resampling.BICUBIC, expand=True)

    sw, sh = sticker.size
    shadow_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    alpha = sticker.split()[-1]
    shadow_img.paste((0, 0, 0, 130), (0, 0), mask=alpha)
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(5))

    target_img.alpha_composite(shadow_img, (cx - sw // 2 + 3, cy - sh // 2 + 5))
    target_img.alpha_composite(sticker, (cx - sw // 2, cy - sh // 2))
    return (cx - sw // 2, cy - sh // 2, cx + sw // 2, cy + sh // 2)

def draw_brush_splash_text_art(
    target_img: Image.Image,
    center_xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    text_color: Tuple[int, int, int] = (255, 255, 255),
    brush_bg_color: Tuple[int, int, int, int] = (195, 25, 35, 240)
) -> Tuple[int, int, int, int]:
    """
    Renders dynamic calligraphy artwork with expressive ink slash banner.
    """
    cx, cy = center_xy
    dummy = Image.new("RGBA", (10, 10))
    d_draw = ImageDraw.Draw(dummy)
    bbox = d_draw.textbbox((0, 0), text, font=font, anchor="mm")
    tw = max(10, bbox[2] - bbox[0])
    th = max(10, bbox[3] - bbox[1])

    draw = ImageDraw.Draw(target_img)
    bx1 = cx - tw // 2 - 28
    bx2 = cx + tw // 2 + 28
    by1 = cy - th // 2 - 12
    by2 = cy + th // 2 + 12

    poly = [
        (bx1 - 12, by1 + 4),
        (cx - 20, by1 - 5),
        (bx2 + 18, by1 + 3),
        (bx2 + 6, by2 + 6),
        (cx + 30, by2 + 3),
        (bx1 - 5, by2 - 3)
    ]
    draw.polygon(poly, fill=brush_bg_color)
    draw.text((cx + 2, cy + 2), text, font=font, fill=(0, 0, 0, 200), anchor="mm")
    draw.text((cx, cy), text, font=font, fill=text_color, stroke_width=2, stroke_fill=(15, 15, 20), anchor="mm")
    return (bx1, by1, bx2, by2)

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

# =========================================================================
# Mathematical Precision Vector Icon Drawing Helpers (Zero Unicode Emojis)
# =========================================================================

def draw_vector_star(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 14,
    fill: Tuple[int, int, int] = (255, 215, 0),
    outline: Optional[Tuple[int, int, int]] = None
):
    """Draws a mathematically precise 5-point star centered at (cx, cy)."""
    points = []
    outer_r = size
    inner_r = size * 0.42
    for i in range(10):
        angle = -math.pi / 2 + i * (math.pi / 5)
        r = outer_r if i % 2 == 0 else inner_r
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=fill, outline=outline)

def draw_vector_trophy(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 24,
    fill: Tuple[int, int, int] = (255, 205, 50)
):
    """Draws a clean geometric trophy cup centered at (cx, cy)."""
    top_w, bot_w, cup_h = size * 0.76, size * 0.46, size * 0.54
    top_y = cy - size * 0.5
    cup_bot_y = top_y + cup_h
    # Cup body
    cup_pts = [
        (cx - top_w / 2, top_y),
        (cx + top_w / 2, top_y),
        (cx + bot_w / 2, cup_bot_y),
        (cx - bot_w / 2, cup_bot_y),
    ]
    draw.polygon(cup_pts, fill=fill)

    # Handles
    handle_w = size * 0.22
    hw = max(2, int(size * 0.1))
    draw.arc([cx - top_w / 2 - handle_w, top_y + 3, cx - top_w / 2 + handle_w, top_y + cup_h * 0.85], 90, 270, fill=fill, width=hw)
    draw.arc([cx + top_w / 2 - handle_w, top_y + 3, cx + top_w / 2 + handle_w, top_y + cup_h * 0.85], 270, 90, fill=fill, width=hw)

    # Stem
    stem_w, stem_h = size * 0.18, size * 0.22
    draw.rectangle([cx - stem_w / 2, cup_bot_y, cx + stem_w / 2, cup_bot_y + stem_h], fill=fill)

    # Base
    base_w, base_h = size * 0.72, size * 0.18
    base_y = cup_bot_y + stem_h
    draw.rounded_rectangle([cx - base_w / 2, base_y, cx + base_w / 2, base_y + base_h], radius=int(base_h * 0.35), fill=fill)

def draw_vector_flame(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 24,
    fill: Tuple[int, int, int] = (255, 95, 30)
):
    """Draws a modern sharp flame/fire icon centered at (cx, cy)."""
    h = size
    w = size * 0.75
    flame_pts = [
        (cx, cy - h * 0.52),
        (cx + w * 0.36, cy - h * 0.15),
        (cx + w * 0.5, cy + h * 0.22),
        (cx + w * 0.34, cy + h * 0.48),
        (cx, cy + h * 0.52),
        (cx - w * 0.34, cy + h * 0.48),
        (cx - w * 0.5, cy + h * 0.22),
        (cx - w * 0.36, cy - h * 0.15),
        (cx - w * 0.1, cy + h * 0.05),
    ]
    draw.polygon(flame_pts, fill=fill)
    # Inner bright lick
    inner_h = h * 0.45
    inner_w = w * 0.42
    inner_pts = [
        (cx, cy + h * 0.06),
        (cx + inner_w * 0.5, cy + h * 0.3),
        (cx, cy + h * 0.47),
        (cx - inner_w * 0.5, cy + h * 0.3),
    ]
    draw.polygon(inner_pts, fill=(255, 225, 70))

def draw_vector_lightning(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 22,
    fill: Tuple[int, int, int] = (255, 215, 0)
):
    """Draws a clean geometric lightning bolt centered at (cx, cy)."""
    h = size
    w = size * 0.58
    pts = [
        (cx - w * 0.12, cy - h * 0.5),
        (cx + w * 0.5, cy - h * 0.5),
        (cx + w * 0.05, cy - h * 0.04),
        (cx + w * 0.55, cy - h * 0.04),
        (cx - w * 0.45, cy + h * 0.5),
        (cx - w * 0.1, cy + h * 0.08),
        (cx - w * 0.55, cy + h * 0.08),
    ]
    draw.polygon(pts, fill=fill)

def draw_vector_check(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 18,
    stroke_color: Tuple[int, int, int] = (0, 230, 160),
    width: int = 3
):
    """Draws a crisp geometric checkmark centered at (cx, cy)."""
    pts = [
        (cx - size * 0.45, cy),
        (cx - size * 0.1, cy + size * 0.38),
        (cx + size * 0.45, cy - size * 0.38)
    ]
    draw.line(pts, fill=stroke_color, width=width, joint="curve")

def draw_vector_chat_bubble(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    w: float = 26,
    h: float = 18,
    fill: Tuple[int, int, int] = (255, 255, 255)
):
    """Draws a speech bubble icon with tail centered at (cx, cy)."""
    bx1 = cx - w / 2
    by1 = cy - h / 2 - 2
    bx2 = cx + w / 2
    by2 = cy + h / 2 - 2
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=int(h * 0.38), fill=fill)
    tail_pts = [
        (cx - w * 0.22, by2),
        (cx - w * 0.42, by2 + 5),
        (cx - w * 0.05, by2),
    ]
    draw.polygon(tail_pts, fill=fill)

def draw_vector_heart(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 20,
    fill: Tuple[int, int, int] = (255, 60, 80)
):
    """Draws a sleek heart icon centered at (cx, cy)."""
    draw.ellipse([cx - size * 0.5, cy - size * 0.42, cx + 1, cy + size * 0.1], fill=fill)
    draw.ellipse([cx - 1, cy - size * 0.42, cx + size * 0.5, cy + size * 0.1], fill=fill)
    draw.polygon([
        (cx - size * 0.49, cy - size * 0.08),
        (cx + size * 0.49, cy - size * 0.08),
        (cx, cy + size * 0.52)
    ], fill=fill)

def draw_vector_paperplane(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 20,
    fill: Tuple[int, int, int] = (255, 255, 255)
):
    """Draws a sleek paper plane / share icon."""
    pts = [
        (cx + size * 0.48, cy - size * 0.44),
        (cx - size * 0.48, cy),
        (cx - size * 0.08, cy + size * 0.15),
        (cx - size * 0.08, cy + size * 0.45),
        (cx + size * 0.15, cy + size * 0.22),
    ]
    draw.polygon(pts, fill=fill)

def draw_vector_bookmark(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 20,
    fill: Tuple[int, int, int] = (255, 255, 255)
):
    """Draws a sleek bookmark icon."""
    w, h = size * 0.65, size * 0.85
    x1, y1 = cx - w / 2, cy - h / 2
    x2, y2 = cx + w / 2, cy + h / 2
    pts = [
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (cx, y2 - h * 0.32),
        (x1, y2)
    ]
    draw.polygon(pts, fill=fill)

def draw_vector_mic(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 22,
    fill: Tuple[int, int, int] = (255, 255, 255),
    muted: bool = False
):
    """Draws a clean microphone icon with optional slash for muted."""
    bw, bh = size * 0.36, size * 0.6
    draw.rounded_rectangle([cx - bw / 2, cy - size * 0.45, cx + bw / 2, cy - size * 0.45 + bh], radius=int(bw * 0.45), fill=fill)
    draw.arc([cx - size * 0.36, cy - size * 0.22, cx + size * 0.36, cy + size * 0.32], 0, 180, fill=fill, width=2)
    draw.line([(cx, cy + size * 0.32), (cx, cy + size * 0.48)], fill=fill, width=2)
    draw.line([(cx - size * 0.22, cy + size * 0.48), (cx + size * 0.22, cy + size * 0.48)], fill=fill, width=2)
    if muted:
        draw.line([(cx - size * 0.45, cy - size * 0.45), (cx + size * 0.45, cy + size * 0.45)], fill=(255, 60, 60), width=3)

def draw_vector_phone(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 24,
    fill: Tuple[int, int, int] = (255, 255, 255)
):
    """Draws a classic phone handset receiver icon."""
    # Curved handset
    draw.rounded_rectangle([cx - size * 0.45, cy - size * 0.16, cx + size * 0.45, cy + size * 0.16], radius=int(size * 0.12), fill=fill)
    draw.rounded_rectangle([cx - size * 0.48, cy - size * 0.38, cx - size * 0.22, cy + size * 0.16], radius=int(size * 0.1), fill=fill)
    draw.rounded_rectangle([cx + size * 0.22, cy - size * 0.38, cx + size * 0.48, cy + size * 0.16], radius=int(size * 0.1), fill=fill)

def draw_vector_camera(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    size: float = 22,
    fill: Tuple[int, int, int] = (255, 255, 255)
):
    """Draws a clean camera icon."""
    bw, bh = size * 0.9, size * 0.65
    draw.rounded_rectangle([cx - bw / 2, cy - bh / 2 + 3, cx + bw / 2, cy + bh / 2 + 3], radius=int(size * 0.14), fill=fill)
    draw.rounded_rectangle([cx - size * 0.2, cy - bh / 2 - 3, cx + size * 0.2, cy - bh / 2 + 3], radius=3, fill=fill)
    lens_r = size * 0.22
    draw.ellipse([cx - lens_r, cy + 3 - lens_r, cx + lens_r, cy + 3 + lens_r], fill=(30, 35, 45), outline=fill, width=2)

def draw_tesla_t(draw: ImageDraw.ImageDraw, x: int, y: int, col: Tuple[int, int, int] = (235, 25, 45)):
    """Draws precise vector Tesla 'T' badge."""
    draw.polygon([(x - 22, y), (x + 22, y), (x + 20, y + 6), (x - 20, y + 6)], fill=col)
    draw.polygon([(x - 14, y + 10), (x + 14, y + 10), (x + 4, y + 42), (x - 4, y + 42)], fill=col)
    draw.arc([x - 28, y - 4, x + 28, y + 12], 200, 340, fill=col, width=4)

EMOJI_PATTERN = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27bf\u2b50\u2b55\ud83c-\ud83e\ud83d\udc00-\udfff★☆✦✧]')

def clean_emoji_text(text: str) -> str:
    """Strips all emoji characters and star symbols to maintain clean editorial typography."""
    if not text:
        return ""
    cleaned = EMOJI_PATTERN.sub('', text)
    return re.sub(r'\s+', ' ', cleaned).strip()

def draw_pill_badge(
    draw: ImageDraw.ImageDraw,
    center_y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: Tuple,
    text_color: Tuple,
    outline_color: Optional[Tuple] = None,
    outline_width: int = 1,
    icon_type: Optional[str] = None,
    icon_color: Optional[Tuple] = None,
    icon_size: int = 22,
    stars_count: int = 0,
    pad_x: int = 50,
    badge_h: int = 58,
    radius: Optional[int] = None,
    canvas_w: int = 1080
) -> Tuple[int, int, int, int]:
    """
    Draws a mathematically centered pill badge with dynamic width matching the content.
    Prevents text overflowing badge boundaries and guarantees zero icon-text overlap.
    Enforces generous horizontal padding so text never touches curved pill caps.
    Automatically downscales font size if content is long.
    """
    text = clean_emoji_text(text)

    if radius is None:
        radius = badge_h // 2

    # Generous clearance: at least (radius * 1.3) + 24 so text is never near curve
    effective_pad_x = max(pad_x, int(radius * 1.3) + 24, 48)
    gap = 16

    # Measure content and auto-downscale if badge exceeds maximum canvas bounds
    max_allowed_w = canvas_w - 100
    current_font = font

    text_bbox = current_font.getbbox(text)
    text_w = text_bbox[2] - text_bbox[0]

    if stars_count > 0:
        star_step = icon_size + 8
        stars_w = stars_count * star_step - 8
        content_w = stars_w + gap + text_w
    elif icon_type:
        content_w = icon_size + gap + text_w
    else:
        content_w = text_w

    total_w = content_w + effective_pad_x * 2
    if total_w > max_allowed_w:
        extra_w = (icon_size + gap if icon_type else (stars_w + gap if stars_count > 0 else 0))
        target_text_w = max_allowed_w - effective_pad_x * 2 - extra_w
        ratio = max(0.5, target_text_w / max(1, text_w))
        base_size = getattr(font, "size", 28)
        new_size = max(20, int(base_size * ratio))
        font_path = getattr(font, "path", FONT_PRETENDARD)
        current_font = get_font(font_path, new_size)
        text_bbox = current_font.getbbox(text)
        text_w = text_bbox[2] - text_bbox[0]
        if stars_count > 0:
            content_w = stars_w + gap + text_w
        elif icon_type:
            content_w = icon_size + gap + text_w
        else:
            content_w = text_w
        badge_w = content_w + effective_pad_x * 2
    else:
        badge_w = total_w

    bx1 = (canvas_w - badge_w) // 2
    bx2 = bx1 + badge_w
    by1 = center_y - badge_h // 2
    by2 = center_y + badge_h // 2

    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=radius, fill=fill_color, outline=outline_color, width=outline_width)

    content_start_x = bx1 + effective_pad_x

    if stars_count > 0:
        s_col = icon_color if icon_color else text_color
        star_step = icon_size + 8
        for i in range(stars_count):
            scx = content_start_x + i * star_step + icon_size // 2
            draw_vector_star(draw, scx, center_y, size=icon_size // 2, fill=s_col)
        text_x = content_start_x + stars_count * star_step - 8 + gap
        draw.text((text_x, center_y), text, font=current_font, fill=text_color, anchor="lm")
    elif icon_type:
        i_col = icon_color if icon_color else text_color
        icx = content_start_x + icon_size // 2
        if icon_type == "trophy":
            draw_vector_trophy(draw, icx, center_y, size=icon_size, fill=i_col)
        elif icon_type == "flame":
            draw_vector_flame(draw, icx, center_y, size=icon_size, fill=i_col)
        elif icon_type == "star":
            draw_vector_star(draw, icx, center_y, size=icon_size // 2, fill=i_col)
        elif icon_type == "check":
            draw_vector_check(draw, icx, center_y, size=icon_size // 2, stroke_color=i_col, width=3)
        elif icon_type == "lightning":
            draw_vector_lightning(draw, icx, center_y, size=icon_size, fill=i_col)
        elif icon_type == "chat":
            draw_vector_chat_bubble(draw, icx, center_y, w=icon_size, h=int(icon_size * 0.75), fill=i_col)
        elif icon_type == "dot":
            dot_r = max(5, icon_size // 3)
            draw.ellipse([icx - dot_r, center_y - dot_r, icx + dot_r, center_y + dot_r], fill=i_col)

        text_x = content_start_x + icon_size + gap
        draw.text((text_x, center_y), text, font=current_font, fill=text_color, anchor="lm")
    else:
        draw.text((canvas_w // 2, center_y), text, font=current_font, fill=text_color, anchor="mm")

    return (bx1, by1, bx2, by2)

def draw_tag_badge(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: Tuple,
    text_color: Tuple,
    icon_type: Optional[str] = None,
    icon: Optional[str] = None,
    icon_color: Optional[Tuple] = None,
    icon_size: int = 18,
    pad_x: int = 24,
    tag_h: int = 48,
    radius: int = 12,
    outline_color: Optional[Tuple] = None,
    outline_width: int = 1,
    align: str = "left"
) -> Tuple[int, int, int, int]:
    """
    Draws a tag badge with generous horizontal padding, zero icon-text overlap.
    Supports align='left', 'right', or 'center'.
    """
    text = clean_emoji_text(text)
    if icon_type is None and icon is not None:
        icon_type = icon

    pad_x = max(pad_x, 20)
    tag_h = max(tag_h, 42)
    gap = 12

    current_font = font
    text_bbox = current_font.getbbox(text)
    text_w = text_bbox[2] - text_bbox[0]

    if icon_type:
        content_w = icon_size + gap + text_w
    else:
        content_w = text_w

    tag_w = content_w + pad_x * 2
    if align == "right":
        bx2 = x
        bx1 = x - tag_w
    elif align == "center":
        bx1 = x - tag_w // 2
        bx2 = bx1 + tag_w
    else:
        bx1 = x
        bx2 = x + tag_w

    by1 = y
    by2 = y + tag_h
    cy = (by1 + by2) // 2

    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=radius, fill=fill_color, outline=outline_color, width=outline_width)

    if icon_type:
        i_col = icon_color if icon_color else text_color
        icx = bx1 + pad_x + icon_size // 2
        if icon_type == "flame":
            draw_vector_flame(draw, icx, cy, size=icon_size, fill=i_col)
        elif icon_type == "star":
            draw_vector_star(draw, icx, cy, size=icon_size // 2, fill=i_col)
        elif icon_type == "check":
            draw_vector_check(draw, icx, cy, size=icon_size // 2, stroke_color=i_col, width=3)
        elif icon_type == "chat":
            draw_vector_chat_bubble(draw, icx, cy, w=icon_size, h=int(icon_size * 0.75), fill=i_col)
        elif icon_type == "lightning":
            draw_vector_lightning(draw, icx, cy, size=icon_size, fill=i_col)
        elif icon_type == "dot":
            dot_r = max(4, icon_size // 3)
            draw.ellipse([icx - dot_r, cy - dot_r, icx + dot_r, cy + dot_r], fill=i_col)

        text_x = bx1 + pad_x + icon_size + gap
        draw.text((text_x, cy), text, font=current_font, fill=text_color, anchor="lm")
    else:
        draw.text((bx1 + tag_w // 2, cy), text, font=current_font, fill=text_color, anchor="mm")

    return (bx1, by1, bx2, by2)

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
    main_font = getattr(template, "font_name", "black_han_sans")
    sub_font = getattr(template, "sub_font_name", "pretendard")

    f_black_72 = get_font(main_font, 72)
    f_black_58 = get_font(main_font, 58)
    f_pret_50 = get_font(sub_font, 50)
    f_pret_42 = get_font(sub_font, 42)
    f_pret_36 = get_font(sub_font, 36)
    f_pret_32 = get_font(sub_font, 32)
    f_pret_30 = get_font(sub_font, 30)
    f_pret_28 = get_font(sub_font, 28)
    f_pret_26 = get_font(sub_font, 26)
    f_pret_24 = get_font(sub_font, 24)
    f_pret_22 = get_font(sub_font, 22)
    f_pret_18 = get_font(sub_font, 18)

    line1, line2 = split_hook_headline(highlight.title, highlight.hook_text)
    if not line1:
        line1 = "놓치면 후회하는 핵심 명장면"
    if not line2:
        line2 = f"클립 #{highlight.id} 지금 바로 확인!"

    # =========================================================================
    # 1. NEWS PORTAL (뉴스 포털 & 긴급 속보 템플릿)
    # =========================================================================
    if template.layout_type == "news_portal":
        img = make_vertical_gradient(canvas_w, canvas_h, (248, 250, 254), (236, 240, 248))
        draw = ImageDraw.Draw(img)

        # 1-1. Top Broadcast Red Bar (Zero-collision broadcast header)
        draw.rectangle([0, 0, canvas_w, 136], fill=(215, 25, 38, 255))
        f_news_logo = get_font(FONT_BLACK_HAN_SANS, 48)
        draw.text((70, 68), "SHORTS NEWS", font=f_news_logo, fill=(255, 255, 255), anchor="lm")
        tb_news = f_news_logo.getbbox("SHORTS NEWS")
        news_w = tb_news[2] - tb_news[0]

        # LIVE badge placed directly next to SHORTS NEWS logo with clean clearance
        draw_tag_badge(
            draw, 70 + news_w + 24, 46, "LIVE", font=f_pret_24,
            fill_color=(0, 0, 0, 190), text_color=(255, 255, 255),
            icon_type="dot", icon_color=(255, 60, 60), icon_size=14,
            tag_h=44, radius=22, pad_x=22
        )
        draw.text((canvas_w - 70, 68), "24H 속보 특보", font=f_pret_28, fill=(255, 255, 255), anchor="rm")

        # 1-2. Floating Headline Card with Drop Shadow
        hy = 165
        head_box = [60, hy, canvas_w - 60, hy + 265]
        draw_card_with_shadow(img, head_box, radius=24, fill=(255, 255, 255, 255), outline=(225, 230, 240, 255), shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 40))

        draw = ImageDraw.Draw(img)
        # Red category chip
        draw_tag_badge(draw, 90, hy + 22, "긴급 속보 • 단독 리포트", f_pret_22, fill_color=(255, 235, 238), text_color=(215, 25, 38), outline_color=(255, 180, 190), outline_width=1, tag_h=46, radius=12, pad_x=24)

        # Line 1
        draw.text((90, hy + 102), line1[:28], font=f_pret_36, fill=(20, 25, 35), anchor="lm")

        # Line 2 with Highlighter Marker Tape (Mathematically centered)
        l2_font = f_black_58
        l2_bbox = l2_font.getbbox(line2, anchor="lm")
        if (l2_bbox[2] - l2_bbox[0]) > 860:
            l2_font = get_font(main_font, max(36, int(58 * (860 / (l2_bbox[2] - l2_bbox[0])))))
            l2_bbox = l2_font.getbbox(line2, anchor="lm")
        text_cy = hy + 175
        draw_marker(draw, [90 + l2_bbox[0], text_cy + l2_bbox[1], 90 + l2_bbox[2], text_cy + l2_bbox[3]], color=template.marker_color, pad_x=20)
        draw.text((90, text_cy), line2, font=l2_font, fill=(255, 255, 255) if template.marker_color[0] > 180 else (10, 12, 16), anchor="lm")

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
        draw_tag_badge(draw, vx + 20, vy + 20, "HOT 실시간 제보", f_pret_24, fill_color=(215, 25, 38, 245), text_color=(255, 255, 255), tag_h=46, radius=10, pad_x=22)

        # 1-4. Bottom News Briefing Card with Drop Shadow
        by = vy + vh + 32
        b_box = [60, by, canvas_w - 60, by + 460]
        draw_card_with_shadow(img, b_box, radius=24, fill=(255, 255, 255, 255), outline=(225, 230, 240, 255), shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 40))

        draw = ImageDraw.Draw(img)
        # Card header badge
        draw_tag_badge(draw, b_box[0] + 30, b_box[1] + 25, "SHORTS NEWS 현장 브리핑", f_pret_22, fill_color=(215, 25, 38), text_color=(255, 255, 255), tag_h=44, radius=12, pad_x=24)
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

        # Top Attention Tag (Editorial eyebrow - Dynamic width with generous clearance)
        draw_pill_badge(draw, center_y=106, text=f"TECH GUIDE • TIP {highlight.id:02d}", font=f_pret_28, fill_color=(255, 230, 0), text_color=(10, 12, 16), outline_color=(0, 0, 0), outline_width=2, badge_h=58, pad_x=50)

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

        # Subtitle slot inside macOS window
        sub_box_y = vy + vh + 25
        draw.rounded_rectangle([wx1 + 30, sub_box_y, wx2 - 30, sub_box_y + 130], radius=16, fill=(255, 255, 255), outline=(210, 216, 228), width=1)

        # Window Content Tip Card
        tip_y = sub_box_y + 155
        draw.rounded_rectangle([wx1 + 30, tip_y, wx2 - 30, tip_y + 135], radius=16, fill=(255, 255, 255), outline=(215, 220, 232), width=1)
        draw_vector_check(draw, wx1 + 60, tip_y + 36, size=16, stroke_color=(0, 180, 100), width=3)
        draw.text((wx1 + 80, tip_y + 24), "실전 추천 포인트 & 가이드", font=f_pret_28, fill=(25, 30, 45), anchor="lt")
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
    # 3. NEON MAGAZINE (인포 매거진 템플릿)
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

        # Top Gold Pill Badge (Editorial eyebrow - Dynamic width with generous clearance)
        draw_pill_badge(draw, center_y=106, text=f"TREND REPORT • KEY {highlight.id:02d}", font=f_pret_28, fill_color=(255, 215, 0), text_color=(10, 12, 16), outline_color=(255, 255, 255), outline_width=2, badge_h=58, pad_x=50)

        # 2-line Headline
        draw.text((540, 180), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        l2_font = f_black_72
        l2_bbox = f_black_72.getbbox(line2)
        if (l2_bbox[2] - l2_bbox[0]) > 900:
            l2_font = f_black_58
        draw_neon_glow_text_art(
            img, (540, 255), line2, l2_font,
            neon_color=(0, 255, 230), core_color=(255, 255, 255), glow_radius=18
        )

        # Video container with Glowing Cyan Border
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 6, vy - 6, vx + vw + 6, vy + vh + 6], radius=26, fill=(0, 255, 220, 200))
        draw.rounded_rectangle([vx, vy, vx + vw, vy + vh], radius=22, fill=(0, 0, 0))

        # Warning sticker on top-right corner of video card
        draw_tag_badge(draw, vx + vw - 24, vy + 20, "MUST WATCH • 01", f_pret_22, fill_color=(255, 45, 85, 240), text_color=(255, 255, 255), tag_h=44, radius=12, pad_x=22, align="right")

        # Dedicated Glowing Subtitle Slot
        draw.rounded_rectangle([80, 940, canvas_w - 80, 1095], radius=20, fill=(18, 22, 32, 230), outline=(0, 255, 220, 90), width=2)
        tb = f_pret_22.getbbox("KEY INSIGHT")
        tw = tb[2] - tb[0]
        block_w = 18 + 12 + tw
        start_x = (canvas_w - block_w) // 2
        draw_vector_lightning(draw, start_x + 9, 965, size=18, fill=(0, 255, 220))
        draw.text((start_x + 18 + 12, 965), "KEY INSIGHT", font=f_pret_22, fill=(0, 255, 220), anchor="lm")

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
        draw_vector_chat_bubble(draw, 95, 70, w=28, h=20, fill=(35, 30, 10))
        draw.text((150, 58), "익명 제보자 단톡방", font=f_pret_36, fill=(25, 25, 25), anchor="lm")
        draw.text((150, 95), "참여 1.2만명  •  실시간 썰", font=f_pret_22, fill=(110, 115, 125), anchor="lm")
        draw.line([(0, 140), (canvas_w, 140)], fill=(210, 220, 230), width=2)

        # Top Question Bubble (Yellow - Dynamic Width with ample padding)
        tb1 = f_pret_36.getbbox(line1[:28])
        w1 = tb1[2] - tb1[0]
        bw1 = min(canvas_w - 120, max(260, w1 + 70))
        draw.rounded_rectangle([60, 170, 60 + bw1, 255], radius=20, fill=(254, 229, 0))
        draw.text((95, 212), line1[:28], font=f_pret_36, fill=(25, 25, 25), anchor="lm")

        # Second Bubble (White - Dynamic Width)
        tb2 = f_pret_36.getbbox(line2[:28])
        w2 = tb2[2] - tb2[0]
        bw2 = min(canvas_w - 120, max(260, w2 + 70))
        draw.rounded_rectangle([60, 275, 60 + bw2, 360], radius=20, fill=(255, 255, 255))
        draw.text((95, 317), line2[:28], font=f_pret_36, fill=(25, 25, 25), anchor="lm")

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=24, fill=(255, 255, 255))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Dedicated Subtitle Slot Banner between video and chat
        sub_slot_y = vy + vh + 25
        draw.rounded_rectangle([70, sub_slot_y, canvas_w - 70, sub_slot_y + 125], radius=18, fill=(255, 255, 255, 220), outline=(210, 220, 230), width=1)

        # Bottom Active Chat Conversation (Fills bottom area cleanly)
        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "실시간 꿀팁 인정"]
        chat_y = sub_slot_y + 150

        # Reply 1: User yellow bubble (right-aligned, timestamp cleanly right-aligned to left of bubble)
        p1 = pts[0][:26]
        tbp1 = f_pret_28.getbbox(p1)
        wp1 = tbp1[2] - tbp1[0]
        bwp1 = min(680, max(200, wp1 + 50))
        rx1 = canvas_w - 60 - bwp1
        draw.rounded_rectangle([rx1, chat_y, canvas_w - 60, chat_y + 75], radius=18, fill=(254, 229, 0))
        draw.text((rx1 + 25, chat_y + 37), p1, font=f_pret_28, fill=(25, 25, 25), anchor="lm")
        draw.text((rx1 - 15, chat_y + 60), "오후 2:14", font=f_pret_18, fill=(110, 130, 150), anchor="rm")

        # Reply 2: Participant white bubble (left-aligned with avatar)
        p2 = pts[1][:26] if len(pts) > 1 else "이거 진짜 꿀팁이네 ㅋㅋㅋ"
        draw.ellipse([60, chat_y + 95, 110, chat_y + 145], fill=(255, 255, 255))
        draw_vector_chat_bubble(draw, 85, chat_y + 120, w=20, h=16, fill=(100, 110, 125))
        tbp2 = f_pret_28.getbbox(p2)
        wp2 = tbp2[2] - tbp2[0]
        bwp2 = min(680, max(200, wp2 + 50))
        draw.rounded_rectangle([125, chat_y + 95, 125 + bwp2, chat_y + 170], radius=18, fill=(255, 255, 255))
        draw.text((150, chat_y + 132), p2, font=f_pret_28, fill=(25, 25, 25), anchor="lm")
        draw.text((125 + bwp2 + 15, chat_y + 155), "오후 2:15", font=f_pret_18, fill=(130, 150, 170), anchor="lm")

        # Reply 3: Another participant bubble
        p3 = pts[2][:26] if len(pts) > 2 else "영상 끝까지 보고 저장 완료!"
        tbp3 = f_pret_28.getbbox(p3)
        wp3 = tbp3[2] - tbp3[0]
        bwp3 = min(680, max(200, wp3 + 50))
        draw.rounded_rectangle([125, chat_y + 190, 125 + bwp3, chat_y + 265], radius=18, fill=(255, 255, 255))
        draw.text((150, chat_y + 227), p3, font=f_pret_28, fill=(25, 25, 25), anchor="lm")
        draw.text((125 + bwp3 + 15, chat_y + 250), "오후 2:15", font=f_pret_18, fill=(130, 150, 170), anchor="lm")

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

        # Top Gold Trophy Badge
        draw_pill_badge(
            draw, center_y=106, text=f"TOP RANKING • #{highlight.id:02d}",
            font=f_pret_30, fill_color=(255, 140, 0), text_color=(255, 255, 255),
            outline_color=(255, 220, 100), outline_width=2,
            icon_type="trophy", icon_color=(255, 245, 220), icon_size=22,
            badge_h=60, pad_x=50
        )

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
        draw_tag_badge(
            draw, 100, sc_y + 22, "실시간 1위 선정", f_pret_24,
            fill_color=(255, 140, 0), text_color=(255, 255, 255),
            icon_type="flame", icon_color=(255, 245, 220), icon_size=18,
            tag_h=46, radius=12, pad_x=22
        )

        # Subtitle slot background pill
        draw.rounded_rectangle([95, sc_y + 80, canvas_w - 95, sc_y + 195], radius=16, fill=(18, 15, 26), outline=(255, 140, 0, 80), width=1)

        # Summary bullet points placed below subtitle slot
        pts = highlight.summary_points if highlight.summary_points else [f"{highlight.title} 핵심 포인트", "절대 놓치면 안 되는 이유"]
        draw_vector_star(draw, 115, sc_y + 238, size=12, fill=(255, 215, 0))
        draw.text((135, sc_y + 225), f"선정 이유: {pts[0][:32]}", font=f_pret_28, fill=(245, 245, 255), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw_vector_check(draw, 115, sc_y + 298, size=14, stroke_color=(255, 180, 0), width=3)
        draw.text((135, sc_y + 285), f"체크 포인트: {p2[:32]}", font=f_pret_28, fill=(245, 245, 255), anchor="lt")
        draw.text((100, sc_y + 335), "• 다음 순위 영상은 채널에서 바로 확인 가능합니다", font=f_pret_22, fill=(160, 150, 180), anchor="lt")

    # =========================================================================
    # 6. PRODUCT REVIEW (5성 별점 & 내돈내산 리뷰)
    # =========================================================================
    elif template.layout_type == "product_review":
        img = Image.new("RGBA", (canvas_w, canvas_h), (245, 248, 250, 255))
        draw = ImageDraw.Draw(img)

        # Top Rating Pill (5 Mathematical Vector Stars + Score)
        draw_pill_badge(
            draw, center_y=104, text="VERIFIED • 4.9 / 5.0",
            font=f_pret_28, fill_color=(0, 230, 160), text_color=(10, 30, 25),
            outline_color=(0, 180, 120), outline_width=2,
            stars_count=5, icon_color=(10, 30, 25), icon_size=18,
            badge_h=60, pad_x=52
        )

        # Headline
        draw.text((540, 180), line1, font=f_pret_50, fill=(20, 30, 40), anchor="mm")
        l2_bbox = f_pret_50.getbbox(line2)
        l2_w = l2_bbox[2] - l2_bbox[0]
        l2_h = l2_bbox[3] - l2_bbox[1]
        cx = (canvas_w - l2_w) // 2
        draw.rounded_rectangle([cx - 16, 255 - l2_h // 2 - 8, cx + l2_w + 16, 255 + l2_h // 2 + 10], radius=10, fill=(0, 230, 160, 210))
        draw.text((540, 255), line2, font=f_pret_50, fill=(10, 20, 30), anchor="mm")

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=24, fill=(20, 30, 40))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Pros/Cons Card with Dedicated Subtitle Slot
        sc_y = vy + vh + 35
        draw.rounded_rectangle([70, sc_y, canvas_w - 70, sc_y + 370], radius=24, fill=(255, 255, 255), outline=(210, 225, 235), width=2)
        draw_tag_badge(
            draw, 100, sc_y + 22, "내돈내산 솔직 평가", f_pret_24,
            fill_color=(0, 200, 140), text_color=(255, 255, 255),
            tag_h=46, radius=12, pad_x=22
        )

        # Subtitle slot background pill
        draw.rounded_rectangle([95, sc_y + 80, canvas_w - 95, sc_y + 195], radius=16, fill=(240, 245, 248), outline=(0, 200, 140, 90), width=1)

        # Summary bullet points placed below subtitle slot
        pts = highlight.summary_points if highlight.summary_points else [f"{highlight.title} 실전 장점", "주의할 점 및 추천 대상"]
        draw_vector_check(draw, 115, sc_y + 238, size=14, stroke_color=(0, 180, 120), width=3)
        draw.text((135, sc_y + 225), f"추천 포인트: {pts[0][:32]}", font=f_pret_28, fill=(30, 40, 50), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw_vector_star(draw, 115, sc_y + 298, size=11, fill=(0, 180, 120))
        draw.text((135, sc_y + 285), f"구매 전 체크: {p2[:32]}", font=f_pret_28, fill=(30, 40, 50), anchor="lt")
        draw.text((100, sc_y + 335), "• 실사용자 평점 및 실시간 최저가는 본문 링크 참고", font=f_pret_22, fill=(120, 135, 145), anchor="lt")

    # =========================================================================
    # 7. MOTIVATION QUOTE (명언 & 동기부여 블랙 매거진)
    # =========================================================================
    elif template.layout_type == "motivation_quote":
        img = Image.new("RGBA", (canvas_w, canvas_h), (12, 12, 15, 255))
        draw = ImageDraw.Draw(img)

        # Elegant Quote Pill Badge
        draw_pill_badge(
            draw, center_y=102, text=f"DAILY INSPIRATION • EP.{highlight.id:02d}",
            font=f_pret_28, fill_color=(28, 25, 20), text_color=(245, 200, 80),
            outline_color=(245, 200, 80, 160), outline_width=2,
            badge_h=58, pad_x=50
        )

        # Headline Quotes
        draw.text((540, 175), line1, font=f_pret_50, fill=(240, 240, 245), stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")
        draw_gradient_text_art(
            img, (540, 250), f"\"{line2}\"", f_black_58,
            top_color=(255, 235, 140), bottom_color=(210, 150, 40),
            stroke_color=(15, 15, 20), stroke_width=5
        )

        # Video Frame with Gold Border
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=20, fill=(245, 200, 80, 200))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Wisdom Reflection Card with Dedicated Subtitle Slot
        sc_y = vy + vh + 35
        draw.rounded_rectangle([80, sc_y, canvas_w - 80, sc_y + 370], radius=24, fill=(20, 20, 26), outline=(245, 200, 80, 80), width=1)
        draw.text((540, sc_y + 38), "오늘의 인생 인사이트", font=f_pret_36, fill=(245, 200, 80), anchor="mm")

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
        draw_pill_badge(
            draw, center_y=102, text="BALANCE GAME • VOTE NOW",
            font=f_pret_30, fill_color=(255, 60, 80), text_color=(255, 255, 255),
            outline_color=(255, 255, 255), outline_width=2,
            icon_type="flame", icon_color=(255, 240, 240), icon_size=22,
            badge_h=60, pad_x=50
        )

        # Headline
        draw.text((540, 180), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        draw_3d_text(draw, (540, 260), line2, f_black_72, fill=(255, 230, 0), stroke_fill=(0, 0, 0), stroke_width=8)

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=20, fill=(255, 60, 80))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Dedicated Subtitle Banner Slot directly under video
        draw.rounded_rectangle([70, 1005, canvas_w - 70, 1120], radius=18, fill=(16, 14, 24), outline=(255, 60, 80, 120), width=2)
        tb = f_pret_22.getbbox("COMMUNITY DISCUSSION")
        tw = tb[2] - tb[0]
        block_w = 22 + 12 + tw
        sx = (canvas_w - block_w) // 2
        draw_vector_chat_bubble(draw, sx + 11, 1030, w=22, h=16, fill=(255, 180, 190))
        draw.text((sx + 22 + 12, 1030), "COMMUNITY DISCUSSION", font=f_pret_22, fill=(255, 180, 190), anchor="lm")

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

        # Washi Tape Sticker Badge (Holds episode indicator with authentic tape look)
        draw_pill_badge(
            draw, center_y=105, text=f"DAILY VLOG • EPISODE {highlight.id:02d}",
            font=f_pret_26, fill_color=(225, 205, 175, 230), text_color=(75, 60, 45),
            outline_color=(205, 185, 155), outline_width=2,
            badge_h=52, radius=12, pad_x=44
        )
        draw.text((540, 180), line1, font=f_pret_50, fill=(35, 30, 25), anchor="mm")
        draw.text((540, 250), line2, font=f_pret_36, fill=(80, 70, 60), anchor="mm")

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
    # 10. FACETIME CALL (아이폰 화상통화 / FaceTime UI - 9:16 Overlay)
    # =========================================================================
    elif template.layout_type == "facetime_call":
        # Transparent overlay canvas over 9:16 vertical video
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Top subtle dark gradient vignette
        for y in range(320):
            alpha = int(170 * (1 - y / 320))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Top iOS Status Bar
        draw.text((80, 50), "9:41", font=f_pret_28, fill=(255, 255, 255), anchor="lm")
        draw.text((canvas_w - 80, 50), "5G  85%", font=f_pret_28, fill=(255, 255, 255), anchor="rm")

        # Top Call Status Pill
        draw_pill_badge(
            draw, center_y=120, text="화상 통화 연결 중 • 02:45",
            font=f_pret_26, fill_color=(20, 24, 34, 220), text_color=(255, 255, 255),
            outline_color=(255, 255, 255, 80), outline_width=1,
            icon_type="dot", icon_color=(0, 230, 130), icon_size=14,
            badge_h=54, radius=27, pad_x=48
        )

        # Headline (Caller Name & Topic)
        draw.text((540, 200), line1[:26], font=f_pret_42, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 15, 20), anchor="mm")
        draw.text((540, 255), line2[:28], font=f_pret_30, fill=(0, 255, 180), stroke_width=3, stroke_fill=(10, 15, 20), anchor="mm")

        # Bottom subtle dark gradient vignette
        for y in range(1600, canvas_h):
            alpha = int(180 * ((y - 1600) / (canvas_h - 1600)))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Bottom Frosted Glass Control Capsule (holds Mute, End, Flip buttons)
        by = 1720
        draw.rounded_rectangle([180, by, canvas_w - 180, by + 120], radius=40, fill=(20, 24, 34, 230), outline=(255, 255, 255, 50), width=1)
        # Mute button
        draw.ellipse([240, by + 15, 330, by + 105], fill=(55, 62, 75, 240))
        draw_vector_mic(draw, 285, by + 60, size=22, fill=(255, 255, 255), muted=True)
        # End Call Red Button
        draw.ellipse([495, by + 15, 585, by + 105], fill=(235, 45, 45))
        draw_vector_phone(draw, 540, by + 60, size=24, fill=(255, 255, 255))
        # Flip Camera Button
        draw.ellipse([750, by + 15, 840, by + 105], fill=(55, 62, 75, 240))
        draw_vector_camera(draw, 795, by + 60, size=22, fill=(255, 255, 255))

    # =========================================================================
    # 11. INSTAGRAM REELS (인스타 릴스 & 피드 UI - 9:16 Overlay)
    # =========================================================================
    elif template.layout_type == "instagram_reels":
        # Transparent overlay canvas over 9:16 vertical video
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Top subtle dark gradient vignette
        for y in range(240):
            alpha = int(160 * (1 - y / 240))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Top Bar
        draw.text((70, 70), "Reels", font=f_pret_50, fill=(255, 255, 255), anchor="lt")
        draw_vector_camera(draw, canvas_w - 70, 95, size=26, fill=(255, 255, 255))

        # Right Action Column (Heart, Chat, Share, Save)
        rx = canvas_w - 85
        action_data = [
            ("heart", "2.5만", (255, 65, 85)),
            ("chat", "1,420", (255, 255, 255)),
            ("share", "공유", (255, 255, 255)),
            ("save", "저장", (255, 255, 255)),
        ]
        for idx, (act_type, label, col) in enumerate(action_data):
            ay = 980 + idx * 105
            if act_type == "heart":
                draw_vector_heart(draw, rx, ay - 6, size=26, fill=col)
            elif act_type == "chat":
                draw_vector_chat_bubble(draw, rx, ay - 6, w=28, h=22, fill=col)
            elif act_type == "share":
                draw_vector_paperplane(draw, rx, ay - 6, size=24, fill=col)
            elif act_type == "save":
                draw_vector_bookmark(draw, rx, ay - 6, size=24, fill=col)
            draw.text((rx, ay + 28), label, font=f_pret_22, fill=(245, 245, 250), stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")

        # Bottom subtle dark gradient vignette
        for y in range(1550, canvas_h):
            alpha = int(210 * ((y - 1550) / (canvas_h - 1550)))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Bottom Profile & Caption
        draw.ellipse([65, 1630, 125, 1690], fill=(255, 215, 0))
        draw.text((95, 1660), "S", font=f_pret_28, fill=(20, 20, 25), anchor="mm")
        username = "@shorts_studio"
        draw.text((140, 1660), username, font=f_pret_30, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0), anchor="lm")
        u_bbox = f_pret_30.getbbox(username)
        u_w = u_bbox[2] - u_bbox[0]
        btn_x1 = 140 + u_w + 16
        btn_x2 = btn_x1 + 86
        draw.rounded_rectangle([btn_x1, 1642, btn_x2, 1678], radius=8, fill=(0, 0, 0, 140), outline=(255, 255, 255), width=1)
        draw.text(((btn_x1 + btn_x2) // 2, 1660), "팔로우", font=f_pret_22, fill=(255, 255, 255), anchor="mm")
        draw.text((65, 1720), f"{line1[:30]} #shorts #viral", font=f_pret_28, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0), anchor="lm")
        draw.text((65, 1770), f"🎵 원본 오디오  •  {highlight.title[:22]}", font=f_pret_22, fill=(220, 225, 240), stroke_width=2, stroke_fill=(0, 0, 0), anchor="lm")

    # =========================================================================
    # 12. IPHONE GALLERY (iOS 사진첩 & 미디어 정보 카드)
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
        draw.rounded_rectangle([80, 1290, canvas_w - 80, 1410], radius=18, fill=(235, 238, 245), outline=(210, 215, 225), width=1)

        # Bottom iOS Photos Detail & Highlight Drawer (Clean & Professional)
        dy = 1445
        draw_card_with_shadow(img, [70, dy, canvas_w - 70, dy + 290], radius=24, fill=(255, 255, 255, 255), outline=(220, 225, 235, 255), shadow_blur=16, shadow_offset=(0, 6), shadow_color=(0, 0, 0, 35))
        draw = ImageDraw.Draw(img)

        # Drawer Top Header Tag
        draw_tag_badge(draw, 100, dy + 22, "PHOTOS HIGHLIGHT • 4K HDR", f_pret_22, fill_color=(235, 243, 255), text_color=(0, 122, 255), tag_h=42, radius=10, pad_x=20)
        draw.text((canvas_w - 100, dy + 43), "iCloud 동기화됨", font=f_pret_22, fill=(130, 135, 148), anchor="rm")

        # Media Meta Row
        draw.text((100, dy + 84), "오늘 14:15  •  4K 60fps  •  1080x1920 HDR", font=f_pret_26, fill=(35, 40, 50), anchor="lm")
        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "보관함에 저장된 핵심 클립"]
        draw.text((100, dy + 130), f"• {pts[0][:34]}", font=f_pret_26, fill=(70, 75, 88), anchor="lm")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((100, dy + 172), f"• {p2[:34]}", font=f_pret_22, fill=(115, 120, 135), anchor="lm")

        # iOS Action Bar (Share, Favorite, Bookmark)
        draw.line([(95, dy + 208), (canvas_w - 95, dy + 208)], fill=(235, 238, 245), width=1)
        bar_y = dy + 248
        # Share
        draw_vector_paperplane(draw, 220, bar_y, size=22, fill=(0, 122, 255))
        draw.text((250, bar_y), "공유", font=f_pret_22, fill=(0, 122, 255), anchor="lm")
        # Favorite
        draw_vector_heart(draw, 510, bar_y, size=22, fill=(255, 60, 80))
        draw.text((540, bar_y), "즐겨찾기", font=f_pret_22, fill=(255, 60, 80), anchor="lm")
        # Save
        draw_vector_bookmark(draw, 800, bar_y, size=22, fill=(0, 122, 255))
        draw.text((830, bar_y), "보관함 저장", font=f_pret_22, fill=(0, 122, 255), anchor="lm")

    # =========================================================================
    # 13. MEME CARTOON (웹툰 & 페페 카툰 리액션 템플릿)
    # =========================================================================
    elif template.layout_type == "meme_cartoon":
        img = Image.new("RGBA", (canvas_w, canvas_h), (252, 250, 245, 255))
        draw = ImageDraw.Draw(img)

        # Comic Speech Bubble with downward speech tail
        draw.rounded_rectangle([60, 50, canvas_w - 60, 245], radius=24, fill=(255, 235, 80), outline=(20, 20, 25), width=4)
        # Speech bubble tail pointing down toward video frame
        draw.polygon([(220, 243), (250, 280), (280, 243)], fill=(255, 235, 80))
        draw.line([(220, 243), (250, 280)], fill=(20, 20, 25), width=4)
        draw.line([(250, 280), (280, 243)], fill=(20, 20, 25), width=4)
        draw.line([(222, 243), (278, 243)], fill=(255, 235, 80), width=6)

        comic_title = f"\"{line1}\""
        f_comic = f_black_58
        tb_c = f_comic.getbbox(comic_title)
        tw_c = tb_c[2] - tb_c[0]
        if tw_c > 820:
            f_comic = get_font(main_font, max(36, int(58 * (820 / tw_c))))
        draw_3d_extruded_text_art(
            img, (540, 115), comic_title, f_comic,
            front_color=(255, 230, 0), side_color=(220, 60, 0),
            stroke_color=(20, 20, 25), depth=10, stroke_width=5
        )
        draw.text((540, 185), f"▶ {line2}", font=f_pret_32, fill=(40, 40, 50), anchor="mm")

        # Video Frame with Comic Ink Border
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 6, vy - 6, vx + vw + 6, vy + vh + 6], radius=16, fill=(20, 20, 25))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Webtoon Reaction Deck with Dedicated Subtitle Slot
        by = vy + vh + 30
        deck_h = 520
        draw.rounded_rectangle([60, by, canvas_w - 60, by + deck_h], radius=24, fill=(255, 255, 255), outline=(20, 20, 25), width=4)
        draw_tag_badge(
            draw, 95, by + 22, "실시간 베댓 1위", font=f_pret_26,
            fill_color=(20, 20, 25), text_color=(255, 235, 80),
            icon="chat", icon_color=(255, 235, 80), icon_size=20,
            tag_h=46, radius=12, pad_x=22
        )

        # Subtitle slot background pill
        draw.rounded_rectangle([90, by + 85, canvas_w - 90, by + 205], radius=16, fill=(250, 248, 238), outline=(20, 20, 25), width=2)

        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "ㅋㅋㅋ 댓글 보고 인정함"]
        draw.text((95, by + 235), f"\" {pts[0][:34]} \"", font=f_pret_32, fill=(20, 20, 25), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else "이거 나만 지금 알았냐 ㅋㅋㅋ"
        draw.text((95, by + 295), f"▶ {p2[:36]}", font=f_pret_28, fill=(80, 85, 95), anchor="lt")
        p3 = pts[2] if len(pts) > 2 else "이건 무조건 저장각이다"
        draw.text((95, by + 355), f"• {p3[:36]}", font=f_pret_26, fill=(110, 115, 125), anchor="lt")
        draw.line([(90, by + 420), (canvas_w - 90, by + 420)], fill=(225, 225, 230), width=2)
        draw.text((95, by + 460), "추천 4,820개  •  답글 284개  •  공유 1,230회", font=f_pret_24, fill=(120, 125, 135), anchor="lt")

    # =========================================================================
    # 14. CINEMA PREVIEW (금주 개봉작 시네마틱 필름 티켓)
    # =========================================================================
    elif template.layout_type == "cinema_preview":
        img = Image.new("RGBA", (canvas_w, canvas_h), (14, 15, 20, 255))
        draw = ImageDraw.Draw(img)

        # Top Ticket Strip
        draw.rounded_rectangle([80, 60, canvas_w - 80, 140], radius=18, fill=(28, 30, 40), outline=(245, 210, 110, 120), width=2)
        draw.text((110, 100), "CINEMA PREVIEW • TICKET NO. 0824", font=f_pret_28, fill=(245, 210, 110), anchor="lm")
        start_star_x = canvas_w - 240
        for i in range(5):
            draw_vector_star(draw, start_star_x + i * 22, 100, size=9, fill=(245, 210, 110))
        draw.text((canvas_w - 100, 100), "9.8", font=f_pret_28, fill=(255, 255, 255), anchor="rm")

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
    # 15. PIE CHART REACTION (팬 반응 통계 & 도넛 차트 템플릿)
    # =========================================================================
    elif template.layout_type == "pie_chart_reaction":
        img = Image.new("RGBA", (canvas_w, canvas_h), (18, 20, 30, 255))
        draw = ImageDraw.Draw(img)

        # Top Headline
        draw_pill_badge(
            draw, center_y=100, text="FAN REACTION • 99% POLL",
            font=f_pret_30, fill_color=(255, 60, 60), text_color=(255, 255, 255),
            outline_color=(255, 120, 120), outline_width=2,
            icon_type="flame", icon_color=(255, 255, 255), icon_size=22,
            badge_h=60, pad_x=50
        )
        draw.text((540, 185), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        draw_3d_text(draw, (540, 265), line2, f_black_72, fill=(255, 220, 0), stroke_fill=(0, 0, 0), stroke_width=8)

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 4, vy - 4, vx + vw + 4, vy + vh + 4], radius=20, fill=(255, 70, 70))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Statistics Deck with Dedicated Subtitle Slot
        by = vy + vh + 30
        draw.rounded_rectangle([70, by, canvas_w - 70, by + 400], radius=24, fill=(28, 32, 48), outline=(255, 80, 80, 80), width=2)

        # Authentic Donut Pie Chart Graphic (Top of card)
        chart_cx = 160
        chart_cy = by + 65
        chart_r = 38
        # PIL pieslices: 0 to 360 degrees
        # 45% (0 to 162) - 답답함 (Red)
        draw.pieslice([chart_cx - chart_r, chart_cy - chart_r, chart_cx + chart_r, chart_cy + chart_r], 0, 162, fill=(235, 50, 50))
        # 35% (162 to 288) - 분노 (Orange)
        draw.pieslice([chart_cx - chart_r, chart_cy - chart_r, chart_cx + chart_r, chart_cy + chart_r], 162, 288, fill=(255, 130, 0))
        # 19% (288 to 356) - 화병 (Yellow)
        draw.pieslice([chart_cx - chart_r, chart_cy - chart_r, chart_cx + chart_r, chart_cy + chart_r], 288, 356, fill=(255, 200, 0))
        # 1% (356 to 360) - 이성 (Green)
        draw.pieslice([chart_cx - chart_r, chart_cy - chart_r, chart_cx + chart_r, chart_cy + chart_r], 356, 360, fill=(50, 200, 120))
        # Center hole cutout for modern donut chart look
        hole_r = 20
        draw.ellipse([chart_cx - hole_r, chart_cy - hole_r, chart_cx + hole_r, chart_cy + hole_r], fill=(28, 32, 48))

        # Stats Badges aligned to the right of donut chart
        draw.rounded_rectangle([220, by + 22, 380, by + 64], radius=10, fill=(235, 50, 50))
        draw.text((300, by + 43), "답답함 45%", font=f_pret_24, fill=(255, 255, 255), anchor="mm")

        draw.rounded_rectangle([400, by + 22, 560, by + 64], radius=10, fill=(255, 130, 0))
        draw.text((480, by + 43), "분노 35%", font=f_pret_24, fill=(255, 255, 255), anchor="mm")

        draw.rounded_rectangle([580, by + 22, 740, by + 64], radius=10, fill=(255, 200, 0))
        draw.text((660, by + 43), "화병 19%", font=f_pret_24, fill=(20, 20, 20), anchor="mm")

        draw.rounded_rectangle([760, by + 22, 920, by + 64], radius=10, fill=(50, 200, 120))
        draw.text((840, by + 43), "이성 1%", font=f_pret_24, fill=(20, 20, 20), anchor="mm")

        # Subtitle slot background pill
        draw.rounded_rectangle([95, by + 95, canvas_w - 95, by + 210], radius=16, fill=(18, 20, 32), outline=(255, 80, 80, 60), width=1)

        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "100% 실화... 내 모습인 줄 알았다"]
        draw.text((100, by + 245), f"\" {pts[0][:32]} \"", font=f_pret_36, fill=(255, 255, 255), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else "공감되면 좋아요와 댓글 남겨주세요!"
        draw.text((100, by + 310), f"• {p2[:36]}", font=f_pret_28, fill=(200, 210, 230), anchor="lt")
        draw.text((100, by + 355), "• 공감되면 좋아요와 댓글 남겨주세요!", font=f_pret_22, fill=(150, 160, 180), anchor="lt")

    # =========================================================================
    # 16. CHALLENGE FITNESS (오운완 챌린지 & 운동 루틴 미션)
    # =========================================================================
    # =========================================================================
    # 16. CHALLENGE FITNESS (오운완 챌린지 & 운동 루틴 미션)
    # =========================================================================
    elif template.layout_type == "challenge_fitness":
        img = Image.new("RGBA", (canvas_w, canvas_h), (18, 14, 20, 255))
        draw = ImageDraw.Draw(img)

        # Top Challenge Banner
        draw_pill_badge(
            draw, center_y=100, text="WORKOUT CHALLENGE • D-DAY",
            font=f_pret_30, fill_color=(255, 45, 45), text_color=(255, 255, 255),
            outline_color=(255, 120, 120), outline_width=2,
            icon_type="flame", icon_color=(255, 255, 255), icon_size=22,
            badge_h=60, pad_x=50
        )
        draw.text((540, 185), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        draw_3d_text(draw, (540, 265), line2, f_black_72, fill=(255, 60, 40), stroke_fill=(0, 0, 0), stroke_width=8)

        # Video Frame
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 6, vy - 6, vx + vw + 6, vy + vh + 6], radius=24, fill=(255, 50, 50))
        draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(0, 0, 0))

        # Bottom Mission Checklist Card with Dedicated Subtitle Slot
        by = vy + vh + 30
        draw.rounded_rectangle([70, by, canvas_w - 70, by + 370], radius=24, fill=(30, 22, 32), outline=(255, 60, 60, 100), width=2)
        draw_tag_badge(
            draw, 100, by + 22, "오늘의 루틴 미션", f_pret_24,
            fill_color=(255, 45, 45), text_color=(255, 255, 255),
            tag_h=46, radius=12, pad_x=22
        )

        # Subtitle slot background pill
        draw.rounded_rectangle([95, by + 80, canvas_w - 95, by + 195], radius=16, fill=(18, 14, 22), outline=(255, 60, 60, 70), width=1)

        pts = highlight.summary_points if highlight.summary_points else [f"{highlight.title} 실전 루틴", "매일 꾸준히 반복하기"]
        draw_vector_check(draw, 115, by + 238, size=14, stroke_color=(255, 100, 100), width=3)
        draw.text((135, by + 225), f"미션 1: {pts[0][:32]}", font=f_pret_28, fill=(255, 245, 245), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw_vector_flame(draw, 115, by + 298, size=18, fill=(255, 100, 100))
        draw.text((135, by + 285), f"미션 2: {p2[:32]}", font=f_pret_28, fill=(255, 245, 245), anchor="lt")
        draw.text((100, by + 335), "• 오운완 인증하고 오늘 하루도 갓생 완성!", font=f_pret_22, fill=(200, 170, 180), anchor="lt")

    # =========================================================================
    # 17. MINIMAL EDU (모던 클린 교육 템플릿)
    # =========================================================================
    elif template.layout_type == "minimal_edu":
        img = Image.new("RGBA", (canvas_w, canvas_h), (20, 24, 34, 255))
        draw = ImageDraw.Draw(img)

        # Top Pill (Editorial indicator - Dynamic width!)
        draw_pill_badge(
            draw, center_y=110, text=f"1-MINUTE KNOWLEDGE • LESSON {highlight.id:02d}",
            font=f_pret_28, fill_color=(35, 42, 58), text_color=(255, 255, 255),
            outline_color=(80, 95, 125), outline_width=2,
            badge_h=58, pad_x=50
        )

        # 2-line Headline
        draw.text((540, 185), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0), anchor="mm")
        l2_bbox = f_pret_50.getbbox(line2)
        l2_w = l2_bbox[2] - l2_bbox[0]
        l2_h = l2_bbox[3] - l2_bbox[1]
        cx = (canvas_w - l2_w) // 2
        draw.rounded_rectangle([cx - 16, 260 - l2_h // 2 - 8, cx + l2_w + 16, 260 + l2_h // 2 + 10], radius=10, fill=template.marker_color)
        draw.text((540, 260), line2, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")

        # Video container
        vx, vy, vw, vh = template.video_box
        draw.rounded_rectangle([vx - 3, vy - 3, vx + vw + 3, vy + vh + 3], radius=16, fill=(0, 0, 0))

        # Bottom Knowledge Card with Dedicated Subtitle Slot
        sc_y = 1000
        draw.rounded_rectangle([70, sc_y, canvas_w - 70, sc_y + 370], radius=20, fill=(28, 34, 48), outline=(60, 72, 95), width=2)
        draw.text((110, sc_y + 35), "[SUMMARY] 실전 핵심 지식 요약", font=f_pret_36, fill=(255, 255, 255), anchor="lt")

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
    # 20. VLOG STICKER LIFESTYLE (나를 바꾼 습관 3가지 & 감성 라이프스타일)
    # =========================================================================
    elif template.layout_type == "vlog_sticker_lifestyle":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Soft top dark vignette
        for y in range(480):
            alpha = int(140 * (1 - y / 480))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Top Pastel Wave Badge (Ample clearance, never overlaps text)
        draw_pill_badge(
            draw, center_y=125, text="DAILY ROUTINE • SELF TALK",
            font=f_pret_28, fill_color=(232, 255, 130, 235), text_color=(25, 40, 15),
            outline_color=(255, 255, 255, 220), outline_width=2,
            badge_h=58, pad_x=50
        )

        draw.text((540, 205), line1, font=f_pret_50, fill=(255, 255, 255), stroke_width=4, stroke_fill=(15, 20, 25), anchor="mm")
        draw_sticker_badge_text_art(
            img, (540, 280), line2[:20], f_black_58,
            text_color=(25, 40, 15), sticker_border_color=(232, 255, 130),
            border_width=12, angle_deg=-2.0
        )

        # Top-right corner tag (Cleanly in top margin, completely clear of face/mic)
        draw_tag_badge(draw, canvas_w - 70, 50, "AESTHETIC VLOG", font=f_pret_22, fill_color=(255, 255, 255, 220), text_color=(40, 50, 30), tag_h=42, radius=10, pad_x=20, align="right")

        # Bottom Daily Habit Note Card (Cleanly placed below subtitle at y=1360)
        draw_card_with_shadow(img, [60, 1530, canvas_w - 60, 1750], radius=24, fill=(255, 255, 255, 240), outline=(225, 235, 220, 255), shadow_blur=16, shadow_offset=(0, 6), shadow_color=(0, 0, 0, 40))
        draw = ImageDraw.Draw(img)
        draw_tag_badge(draw, 95, 1555, "TODAY'S HABIT", font=f_pret_22, fill_color=(232, 255, 130), text_color=(25, 40, 15), tag_h=40, radius=10, pad_x=18)
        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "매일 실천하는 나만의 루틴"]
        draw.text((95, 1615), f"• {pts[0][:34]}", font=f_pret_28, fill=(35, 45, 30), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((95, 1665), f"• {p2[:34]}", font=f_pret_24, fill=(90, 105, 85), anchor="lt")

    # =========================================================================
    # 21. VLOG MONEY SALARY (프리랜서 평균 수입 & 테이프 스티커)
    # =========================================================================
    elif template.layout_type == "vlog_money_salary":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Soft top dark vignette
        for y in range(450):
            alpha = int(160 * (1 - y / 450))
            draw.line([(0, y), (canvas_w, y)], fill=(10, 12, 18, alpha))

        # Top Pink Capsule (Dynamic width with generous clearance)
        draw_pill_badge(
            draw, center_y=110, text="FINANCE & SALARY VLOG",
            font=f_pret_30, fill_color=(255, 240, 245), text_color=(220, 40, 100),
            outline_color=(255, 180, 200), outline_width=2,
            badge_h=58, pad_x=50
        )

        # Headline
        f_title = f_pret_50
        tb1 = f_title.getbbox(line1)
        if tb1[2] - tb1[0] > 880:
            f_title = get_font(FONT_PRETENDARD, max(36, int(50 * (880 / (tb1[2] - tb1[0])))))
        draw.text((540, 185), line1, font=f_title, fill=(255, 255, 255), stroke_width=4, stroke_fill=(15, 15, 20), anchor="mm")

        # Dynamic Pastel Highlighter Tape for Line 2
        tb2 = f_pret_42.getbbox(line2)
        w2 = tb2[2] - tb2[0]
        cx = (canvas_w - w2) // 2
        draw.rounded_rectangle([cx - 20, 235, cx + w2 + 20, 288], radius=8, fill=(255, 245, 170, 240), outline=(235, 215, 130), width=2)
        draw.text((540, 260), line2, font=f_pret_42, fill=(90, 70, 10), anchor="mm")

        # Bottom Revenue Proof Card (Cleanly placed below subtitle at y=1420)
        draw_card_with_shadow(img, [60, 1510, canvas_w - 60, 1780], radius=24, fill=(255, 255, 255, 245), outline=(225, 235, 230, 255), shadow_blur=16, shadow_offset=(0, 6), shadow_color=(0, 0, 0, 40))
        draw = ImageDraw.Draw(img)
        # Left tag: 실시간 수익 인증
        draw_tag_badge(
            draw, 95, 1535, "실시간 수익 인증", font=f_pret_22,
            fill_color=(185, 245, 230), text_color=(15, 80, 70),
            icon="star", icon_color=(15, 80, 70), icon_size=16,
            tag_h=40, radius=10, pad_x=18
        )
        # Right tag: $$$ REVENUE
        draw_tag_badge(
            draw, canvas_w - 95, 1535, "$$$ REVENUE", font=f_pret_22,
            fill_color=(255, 235, 120), text_color=(120, 90, 10),
            icon="star", icon_color=(120, 90, 10), icon_size=16,
            tag_h=40, radius=10, pad_x=18, align="right"
        )
        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "실제 통장 입금 내역 공개"]
        draw.text((95, 1610), f"• {pts[0][:34]}", font=f_pret_28, fill=(25, 35, 30), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((95, 1660), f"• {p2[:34]}", font=f_pret_24, fill=(80, 95, 85), anchor="lt")
        draw.line([(95, 1715), (canvas_w - 95, 1715)], fill=(225, 235, 230), width=1)
        draw.text((540, 1745), "@happy.shorts  •  실시간 VLOG 연재 중", font=f_pret_22, fill=(120, 135, 125), anchor="mm")

    # =========================================================================
    # 22. PROMO FITNESS GYM (오운완 챌린지 & 다이나믹 스포츠 HUD)
    # =========================================================================
    elif template.layout_type == "promo_fitness_gym":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Top subtle dark gradient
        for y in range(400):
            alpha = int(170 * (1 - y / 400))
            draw.line([(0, y), (canvas_w, y)], fill=(8, 10, 15, alpha))

        # Top Athletic Pill Badge
        draw_pill_badge(
            draw, center_y=100, text="WORKOUT CHALLENGE • FITNESS",
            font=f_pret_28, fill_color=(235, 25, 45), text_color=(255, 255, 255),
            outline_color=(255, 100, 110), outline_width=2,
            icon_type="flame", icon_color=(255, 255, 255), icon_size=20,
            badge_h=58, pad_x=50
        )

        # Dynamic Headline
        f_title = f_black_58
        tb1 = f_title.getbbox(line1)
        if tb1[2] - tb1[0] > 900:
            f_title = get_font(main_font, max(38, int(58 * (900 / (tb1[2] - tb1[0])))))
        draw.text((540, 175), line1, font=f_title, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 10, 15), anchor="mm")
        draw.text((540, 245), line2, font=f_pret_36, fill=(255, 220, 0), stroke_width=3, stroke_fill=(10, 10, 15), anchor="mm")

        # Bottom Translucent HUD Card (Cleanly encasing all mission points below subtitle at y=1360)
        draw_card_with_shadow(img, [60, 1480, canvas_w - 60, 1830], radius=24, fill=(12, 15, 22, 235), outline=(235, 25, 45, 180), width=2, shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 80))
        draw = ImageDraw.Draw(img)

        # Tag Badge
        draw_tag_badge(
            draw, 90, 1505, "SPORTS HUD • TODAY'S MISSION", font=f_pret_24,
            fill_color=(235, 25, 45), text_color=(255, 255, 255),
            icon="flame", icon_color=(255, 255, 255), icon_size=18,
            tag_h=46, radius=12, pad_x=22
        )

        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "오운완 인증하고 갓생 달성!"]
        draw_vector_check(draw, 105, 1585, size=14, stroke_color=(255, 220, 0), width=3)
        draw.text((130, 1572), f"미션 1: {pts[0][:32]}", font=f_pret_28, fill=(245, 248, 255), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else "루틴 완주 후 인증샷 업로드"
        draw_vector_star(draw, 105, 1645, size=11, fill=(255, 220, 0))
        draw.text((130, 1632), f"미션 2: {p2[:32]}", font=f_pret_28, fill=(245, 248, 255), anchor="lt")
        draw.text((90, 1705), "• 오운완 인증하고 오늘 하루도 갓생 완성!", font=f_pret_22, fill=(180, 190, 210), anchor="lt")

        # Bottom Red Progress Bar inside card
        draw.line([(90, 1775), (canvas_w - 90, 1775)], fill=(50, 55, 68), width=6)
        draw.line([(90, 1775), (460, 1775)], fill=(235, 25, 45), width=6)

    # =========================================================================
    # 23. YOUTH TIPS PICK (핵심 꿀팁 총정리 픽)
    # =========================================================================
    elif template.layout_type == "youth_tips_pick":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Soft top dark vignette
        for y in range(450):
            alpha = int(160 * (1 - y / 450))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Top Pill Badge
        draw_pill_badge(
            draw, center_y=105, text="LIFE HACKS • TIPS PICK",
            font=f_pret_30, fill_color=(20, 24, 32, 230), text_color=(235, 255, 30),
            outline_color=(235, 255, 30, 220), outline_width=2,
            icon_type="star", icon_color=(235, 255, 30), icon_size=20,
            badge_h=58, pad_x=50
        )

        # Main Headline
        f_title = f_pret_50
        tb1 = f_title.getbbox(line1)
        if tb1[2] - tb1[0] > 900:
            f_title = get_font(FONT_PRETENDARD, max(36, int(50 * (900 / (tb1[2] - tb1[0])))))
        draw.text((540, 180), line1, font=f_title, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 10, 15), anchor="mm")

        # Dynamic Neon Yellow Box + Highlight Text for Line 2
        tb2 = f_pret_42.getbbox(line2)
        w2 = tb2[2] - tb2[0]
        cx = (canvas_w - w2) // 2
        draw.rounded_rectangle([cx - 20, 235, cx + w2 + 20, 295], radius=8, fill=(235, 255, 30))
        draw.text((540, 265), line2, font=f_pret_42, fill=(15, 20, 25), anchor="mm")

        # Bottom Translucent Card (Enclosing all tips below subtitle at y=1360)
        draw_card_with_shadow(img, [60, 1480, canvas_w - 60, 1830], radius=24, fill=(15, 18, 26, 235), outline=(235, 255, 30, 160), width=2, shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 80))
        draw = ImageDraw.Draw(img)

        # Tag Badge
        draw_tag_badge(
            draw, 90, 1505, "PICK! 핵심 꿀팁", font=f_pret_26,
            fill_color=(235, 255, 30), text_color=(15, 20, 25),
            icon="star", icon_color=(15, 20, 25), icon_size=18,
            tag_h=46, radius=12, pad_x=22
        )
        pts = highlight.summary_points if highlight.summary_points else [highlight.title]
        draw.text((90, 1575), f"• {pts[0][:34]}", font=f_pret_28, fill=(255, 255, 255), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else "놓치면 아까운 실전 활용법"
        draw.text((90, 1635), f"• {p2[:34]}", font=f_pret_26, fill=(235, 240, 250), anchor="lt")

        # Disclaimer
        draw.line([(90, 1715), (canvas_w - 90, 1715)], fill=(50, 55, 70), width=1)
        draw.text((90, 1750), "* 상세 꿀팁 정보는 본문 링크 및 커뮤니티에서 확인 가능", font=f_pret_22, fill=(180, 190, 210), anchor="lt")

    # =========================================================================
    # 24. DRAMA WEEKLY PREVIEW (이번 주 가장 많이 본 명장면 다시보기)
    # =========================================================================
    elif template.layout_type == "drama_weekly_preview":
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Soft top dark vignette
        for y in range(400):
            alpha = int(170 * (1 - y / 400))
            draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

        # Top Pill Badge
        draw_pill_badge(
            draw, center_y=110, text="WEEKLY DRAMA • BEST SCENE",
            font=f_pret_28, fill_color=(225, 25, 40), text_color=(255, 255, 255),
            outline_color=(255, 80, 90), outline_width=2,
            icon_type="trophy", icon_color=(255, 255, 255), icon_size=18,
            badge_h=58, pad_x=50
        )

        # Center Expressive Calligraphy Splash Headline
        f_title = get_font("nanum_brush", 68)
        draw_brush_splash_text_art(
            img, (540, 180), line1, f_title,
            text_color=(255, 255, 255),
            brush_bg_color=(215, 25, 40, 240)
        )
        draw.text((540, 255), f"《 {line2} 》", font=f_pret_36, fill=(255, 220, 100), stroke_width=3, stroke_fill=(10, 10, 15), anchor="mm")

        # Bottom Translucent Cinematic Card (Non-blocking, below subtitle at y=1360)
        draw.rounded_rectangle([60, 1490, canvas_w - 60, 1820], radius=24, fill=(18, 20, 28, 235), outline=(225, 25, 40), width=2)
        draw_tag_badge(
            draw, 90, 1515, "명장면 프리뷰", font=f_pret_26,
            fill_color=(225, 25, 40), text_color=(255, 255, 255),
            icon="flame", icon_color=(255, 255, 255), icon_size=18,
            tag_h=46, radius=12, pad_x=22
        )
        pts = highlight.summary_points if highlight.summary_points else [highlight.title, "놓치면 안 될 명장면"]
        draw.text((90, 1585), f"• 감상 포인트: {pts[0][:32]}", font=f_pret_28, fill=(240, 245, 255), anchor="lt")
        p2 = pts[1] if len(pts) > 1 else highlight.title
        draw.text((90, 1645), f"• 주요 특징: {p2[:32]}", font=f_pret_28, fill=(200, 210, 225), anchor="lt")
        draw.line([(90, 1710), (canvas_w - 90, 1710)], fill=(60, 70, 85), width=1)
        draw.text((90, 1745), "▶ 풀버전은 고정 댓글 링크에서 확인하실 수 있습니다.", font=f_pret_22, fill=(255, 200, 210), anchor="lt")

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

        # Row 1 (y = 52):
        # Left: Tesla Red Brand
        draw_tesla_t(draw, 75, 52)
        draw.text((115, 52), "TESLA", font=f_pret_36, fill=(255, 255, 255), anchor="lm")

        # Center: Drive Mode
        draw.text((540, 52), "P   R   N   D*", font=f_pret_28, fill=(140, 150, 170), anchor="mm")

        # Right: Speedometer & Speed Limit Sign
        draw.text((canvas_w - 180, 52), "105", font=f_black_72, fill=(255, 255, 255), anchor="rm")
        draw.text((canvas_w - 172, 58), "km/h", font=f_pret_22, fill=(170, 185, 205), anchor="lm")
        sl_cx, sl_cy = canvas_w - 110, 52
        draw.ellipse([sl_cx - 24, sl_cy - 24, sl_cx + 24, sl_cy + 24], fill=(255, 255, 255), outline=(235, 25, 45), width=5)
        draw.text((sl_cx, sl_cy), "100", font=f_pret_18, fill=(10, 10, 10), anchor="mm")

        # Row 2 (y = 116):
        # Center: FSD Active Pill Badge (hero element)
        draw_pill_badge(
            draw, center_y=116, text="FSD AUTOPILOT ACTIVE",
            font=f_pret_22, fill_color=(12, 38, 28, 230), text_color=(0, 245, 160),
            outline_color=(0, 230, 140), outline_width=2,
            icon_type="dot", icon_color=(0, 245, 160), icon_size=12,
            badge_h=46, radius=16, pad_x=28
        )
        # Left: Clean FSD version
        draw.text((75, 116), "FSD v13.2", font=f_pret_22, fill=(150, 165, 185), anchor="lm")

        # Right: Battery Status
        draw_vector_lightning(draw, canvas_w - 190, 116, size=16, fill=(0, 230, 140))
        draw.text((canvas_w - 75, 116), "88%  432km", font=f_pret_22, fill=(0, 230, 140), anchor="rm")

        # 2. Bottom Control Dock with Frosted Glass Drop Shadow
        dock_box = [60, 1680, canvas_w - 60, 1860]
        draw_card_with_shadow(img, dock_box, radius=28, fill=(14, 18, 26, 235), outline=(50, 65, 85, 200), width=2, shadow_blur=16, shadow_offset=(0, 8), shadow_color=(0, 0, 0, 100))

        draw = ImageDraw.Draw(img)
        # Controls
        draw.text((110, 1745), "21.5°C AUTO", font=f_pret_28, fill=(255, 255, 255), anchor="lm")
        draw.text((110, 1795), "SEAT HEATER LV.2", font=f_pret_22, fill=(150, 165, 185), anchor="lm")

        # Media & Nav
        draw.text((540, 1735), "SPOTIFY • AMBIENT DRIVING", font=f_pret_28, fill=(255, 255, 255), anchor="mm")
        draw.rounded_rectangle([360, 1762, 720, 1768], radius=3, fill=(45, 55, 75))
        draw.rounded_rectangle([360, 1762, 530, 1768], radius=3, fill=(0, 230, 140))
        nav_dest = highlight.title[:22] if highlight.title else "판교 테크노밸리"
        draw.text((540, 1805), f"NAV: {nav_dest}", font=f_pret_22, fill=(160, 175, 195), anchor="mm")

        # Right Status
        draw.text((canvas_w - 110, 1745), "BATTERY AUTO", font=f_pret_28, fill=(0, 230, 140), anchor="rm")
        draw.text((canvas_w - 110, 1795), "LIGHTS AUTO", font=f_pret_22, fill=(150, 165, 185), anchor="rm")

    elif template.layout_type in ["smart_crop", "source_pure"]:
        # Transparent background for 9:16 full-bleed video
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        if template.layout_type == "smart_crop":
            # Subtle top & bottom shadow gradient for text legibility
            for y in range(420):
                alpha = int(160 * (1 - y / 420))
                draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))
            for y in range(canvas_h - 380, canvas_h):
                alpha = int(160 * ((y - (canvas_h - 380)) / 380))
                draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

            # Top category eyebrow pill badge
            badge_title = "REAL TALK • INTERVIEW"
            draw_pill_badge(
                draw, center_y=115,
                text=badge_title,
                font=f_pret_26, fill_color=(20, 24, 34, 230),
                text_color=(255, 230, 0), outline_color=(255, 230, 0, 220),
                outline_width=2, badge_h=52, pad_x=48
            )

            # Prominent 2-line Headline below the badge
            f_title = f_black_58
            tb1 = f_title.getbbox(line1)
            if tb1[2] - tb1[0] > 900:
                f_title = get_font(main_font, max(36, int(58 * (900 / (tb1[2] - tb1[0])))))
            draw.text((540, 190), line1, font=f_title, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 15, 20), anchor="mm")
            draw.text((540, 260), f"《 {line2} 》", font=f_pret_36, fill=(255, 230, 0), stroke_width=3, stroke_fill=(10, 15, 20), anchor="mm")

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
    """Renders intro hook header and pill badge for smart_crop layout."""
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_black_58 = get_font(FONT_BLACK_HAN_SANS, 58)
    f_pret_36 = get_font(FONT_PRETENDARD, 36)
    f_pret_26 = get_font(FONT_PRETENDARD, 26)

    line1, line2 = split_hook_headline(title, hook_text)
    if not line1:
        line1 = title if title else "놓치면 후회하는 핵심 명장면"
    if not line2:
        line2 = hook_text if hook_text else f"클립 #{clip_idx:02d} 지금 바로 확인!"

    # 1. Top subtle shadow gradient
    for y in range(380):
        alpha = int(150 * (1 - y / 380))
        draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, alpha))

    # 2. Eyebrow Category Pill Badge
    badge_title = f"INTERVIEW • CLIP #{clip_idx:02d}"
    if badge_style == "red_pill":
        fill_col = (180, 20, 30, 240)
        text_col = (255, 255, 255)
        out_col = (255, 80, 90, 220)
    elif badge_style == "minimal_pill":
        fill_col = (30, 35, 45, 240)
        text_col = (255, 255, 255)
        out_col = (100, 115, 135, 200)
    else:
        fill_col = (20, 24, 34, 230)
        text_col = (255, 230, 0)
        out_col = (255, 230, 0, 220)

    draw_pill_badge(
        draw, center_y=115, text=badge_title,
        font=f_pret_26, fill_color=fill_col, text_color=text_col,
        outline_color=out_col, outline_width=2, badge_h=52, pad_x=48
    )

    # 3. 2-line Bold Headline below badge
    f_t = f_black_58
    tb = f_t.getbbox(line1)
    if tb[2] - tb[0] > 900:
        f_t = get_font(FONT_BLACK_HAN_SANS, max(36, int(58 * (900 / (tb[2] - tb[0])))))
    draw.text((540, 190), line1, font=f_t, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 15, 20), anchor="mm")
    draw.text((540, 260), f"《 {line2} 》", font=f_pret_36, fill=(255, 230, 0), stroke_width=3, stroke_fill=(10, 15, 20), anchor="mm")

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

    chosen_font_path = resolve_font_path(font_name)
    font_key = str(font_name).lower().strip()

    is_landscape = (canvas_w > canvas_h)
    if "dongle" in font_key:
        base_size = (72 if is_landscape else 88) if style != "clean_minimal" else (64 if is_landscape else 78)
    elif "song" in font_key or "gowun" in font_key:
        base_size = (54 if is_landscape else 68) if style != "clean_minimal" else (46 if is_landscape else 60)
    elif style == "clean_minimal" or "pret" in font_key:
        base_size = 52 if is_landscape else 64
    else:
        base_size = 56 if is_landscape else 72

    active_font = get_font(chosen_font_path, base_size)
    normal_font = get_font(chosen_font_path, int(base_size * 0.88))
    stroke_w = 8 if (style == "clean_minimal" or "pret" in font_key or "gowun" in font_key or "song" in font_key) else 9

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

KOREAN_FILLER_WORDS = {
    "네", "예", "어", "음", "아", "저", "에", "으", "으음", "어어",
    "네네", "어머", "글쎄", "어라", "아이구", "아이고", "어휴", "음음"
}

def is_filler_word(
    word: Word,
    prev_word: Optional[Word] = None,
    next_word: Optional[Word] = None
) -> bool:
    """
    Determines if a word is a conversational filler/hesitation (e.g. '네,', '어..', '음..', '아,')
    rather than substantive speech content.
    """
    clean = re.sub(r'[^가-힣a-zA-Z0-9]', '', word.word).strip()
    if clean not in KOREAN_FILLER_WORDS:
        return False

    has_trailing_pause = any(word.word.endswith(p) for p in [",", "..", "...", "~"])
    prev_ended = prev_word is None or any(prev_word.word.endswith(p) for p in [".", "?", "!", "~"])
    prev_gap = (word.start - prev_word.end) if prev_word else 999.0
    next_gap = (next_word.start - word.end) if next_word else 999.0

    # 1. At start of clip or sentence, or after speech pause (> 0.35s)
    if prev_ended or prev_gap > 0.35:
        return True

    # 2. Marked with comma or ellipsis as an interjection/hesitation (e.g. '네,', '어..', '음..')
    if has_trailing_pause:
        return True

    # 3. Isolated with pauses before or after (> 0.25s)
    if prev_gap > 0.25 or next_gap > 0.25:
        return True

    # 4. Followed by another filler word (e.g. '어.. 음.. 네..')
    if next_word:
        next_clean = re.sub(r'[^가-힣a-zA-Z0-9]', '', next_word.word).strip()
        if next_clean in KOREAN_FILLER_WORDS:
            return True

    # 5. Very short utterance pause (< 0.35s)
    if (word.end - word.start) < 0.35:
        return True

    return False

def filter_filler_words(words: List[Word]) -> List[Word]:
    """
    Filters out conversational filler interjections and verbal hesitations (e.g. '네,', '어..', '음..', '아,')
    to prevent awkward, flash-in-the-pan single-word subtitles in viral Shorts.
    """
    if not words:
        return []

    filtered: List[Word] = []
    for i, w in enumerate(words):
        prev_w = words[i - 1] if i > 0 else None
        next_w = words[i + 1] if i + 1 < len(words) else None
        if not is_filler_word(w, prev_w, next_w):
            filtered.append(w)

    return filtered if filtered else words

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
    canvas_w: int = 1080,
    canvas_h: int = 1920,
    y_center: int = 1360,
    filter_fillers: bool = True
) -> Tuple[str, str]:
    """
    Generate timed PNG sequence and an ffconcat descriptor file.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    blank_png = str(out_dir / "blank.png")
    blank_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    blank_img.save(blank_png, "PNG")

    if filter_fillers:
        words = filter_filler_words(words)

    if not words or style == "none":
        concat_file = str(out_dir / "subtitles.txt")
        with open(concat_file, "w", encoding="utf-8") as f:
            f.write("ffconcat version 1.0\n")
            f.write("file blank.png\n")
            f.write(f"duration {clip_duration:.2f}\n")
            f.write("file blank.png\n")
        return concat_file, blank_png

    # Group words into 2~4 word chunks
    groups: List[List[Word]] = []
    current_grp: List[Word] = []

    for w_idx, w in enumerate(words):
        current_grp.append(w)
        ends_sentence = any(w.word.endswith(p) for p in [".", "?", "!", "~"])
        clause_break = w.word.endswith(",") and len(current_grp) >= 2

        has_pause = False
        if len(current_grp) > 1 and w_idx + 1 < len(words):
            next_w = words[w_idx + 1]
            if next_w.start - w.end > 0.35:
                has_pause = True

        if len(current_grp) >= max_words_per_group or ends_sentence or clause_break or has_pause:
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
                canvas_w=canvas_w,
                canvas_h=canvas_h,
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
