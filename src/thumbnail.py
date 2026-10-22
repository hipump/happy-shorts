"""
Creator-Grade 3D Blockbuster Viral Thumbnail Engine.
Inspired by top-tier viral YouTube thumbnails:
- Layer 1: Cinematic Full-Bleed Background (AI-generated or graded video frame with bokeh/vignette)
- Layer 2: Subject Cutout (rembg u2net) with Multi-Layer Neon Rim Lighting / Outer Glow
- Layer 3: 3D Blockbuster Multi-Stroke Typography (BlackHanSans, -3.5° dynamic tilt, deep extrusion)
- Layer 4: Distressed Crimson Grunge / Splatter Slash Banner
- 100% Local, runs in < 1 second on Apple Silicon
- Supports both 9:16 (Shorts/Reels/TikTok) and 16:9 (YouTube Standard)
"""

import os
import math
import random
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT_DIR = Path("assets/fonts")

# Global rembg session cache for ultra-fast (sub-second) inference
_REMBG_SESSION = None

def get_rembg_session():
    """Lazily loads local u2net rembg session once."""
    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        try:
            import rembg
            _REMBG_SESSION = rembg.new_session("u2net")
        except Exception:
            _REMBG_SESSION = False
    return _REMBG_SESSION

def get_thumbnail_font(size: int, prefer_black_han: bool = True) -> ImageFont.FreeTypeFont:
    """Finds best available bold Korean font for 3D blockbuster thumbnails."""
    candidates = []
    if prefer_black_han:
        candidates.append(FONT_DIR / "BlackHanSans-Regular.ttf")
    candidates.extend([
        FONT_DIR / "Pretendard-ExtraBold.ttf",
        FONT_DIR / "GasoekOne-Regular.ttf",
        FONT_DIR / "BagelFatOne-Regular.ttf",
        FONT_DIR / "DoHyeon-Regular.ttf",
        Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
    ])
    for fp in candidates:
        if fp.exists():
            try:
                return ImageFont.truetype(str(fp), size)
            except Exception:
                continue
    return ImageFont.load_default()

def get_preset_font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    """Loads a specific font from assets/fonts/ with graceful fallback."""
    fp = FONT_DIR / filename
    if fp.exists():
        try:
            return ImageFont.truetype(str(fp), int(size))
        except Exception:
            pass
    return get_thumbnail_font(int(size))

# ==============================================================================
# YouTube Master Typography 8-Presets Suite
# Each preset defines a unique font, graphic shaders, strokes, and color palette
# ==============================================================================
TYPOGRAPHY_PRESETS: Dict[str, Dict] = {
    "blockbuster_3d": {
        "id": "blockbuster_3d",
        "name": "3D 돌출 & 베벨 메탈",
        "category": "정통 이슈/바이럴/충격",
        "font_file": "BlackHanSans-Regular.ttf",
        "font_size_mult": 1.0,
        "tilt": -3.5,
        "banner_style": "slash",
        "banner_color": (195, 12, 25),
        "rim_color": (255, 215, 0),
        "p_colors": [(255, 230, 50), (255, 140, 20), (255, 255, 200)],
        "style1": "ruby_gloss",
        "style2": "concrete_weathered",
    },
    "jelly_pop": {
        "id": "jelly_pop",
        "name": "젤리 버블 팝 스티커",
        "category": "맛집/먹방/일상/디저트",
        "font_file": "BagelFatOne-Regular.ttf",
        "font_size_mult": 0.95,
        "tilt": 2.5,
        "banner_style": "soft_pill",
        "banner_color": (255, 105, 180),
        "rim_color": (255, 150, 200),
        "p_colors": [(255, 120, 180), (255, 225, 50), (255, 255, 255)],
    },
    "ink_splatter": {
        "id": "ink_splatter",
        "name": "거친 캘리 잉크 스플래터",
        "category": "재난/격투/실화/사고",
        "font_file": "EastSeaDokdo-Regular.ttf",
        "font_size_mult": 1.35,
        "tilt": -2.5,
        "banner_style": "slash",
        "banner_color": (180, 10, 25),
        "rim_color": (60, 200, 255),
        "p_colors": [(220, 20, 30), (160, 10, 20), (255, 200, 200)],
    },
    "cyber_neon": {
        "id": "cyber_neon",
        "name": "각진 메탈 & 네온 튜브",
        "category": "테크/자동차/AI/IT",
        "font_file": "GasoekOne-Regular.ttf",
        "font_size_mult": 0.95,
        "tilt": 3.0,
        "banner_style": "cyber_lines",
        "banner_color": (10, 35, 80),
        "rim_color": (0, 235, 255),
        "p_colors": [(0, 240, 255), (60, 150, 255), (220, 250, 255)],
    },
    "gold_luxury": {
        "id": "gold_luxury",
        "name": "골드 럭셔리 엠보싱",
        "category": "주식/코인/재테크/부자",
        "font_file": "DoHyeon-Regular.ttf",
        "font_size_mult": 1.0,
        "tilt": 2.0,
        "banner_style": "slash",
        "banner_color": (15, 18, 25),
        "rim_color": (255, 215, 0),
        "p_colors": [(255, 215, 0), (255, 245, 180), (255, 255, 255)],
    },
    "spooky_ghost": {
        "id": "spooky_ghost",
        "name": "오싹한 스푸키 고스트",
        "category": "괴담/공포/미스터리/심령",
        "font_file": "KirangHaerang-Regular.ttf",
        "font_size_mult": 1.25,
        "tilt": -3.5,
        "banner_style": "shadow_smoke",
        "banner_color": (15, 30, 20),
        "rim_color": (50, 255, 120),
        "p_colors": [(50, 255, 120), (180, 255, 210), (240, 70, 70)],
    },
    "variety_show": {
        "id": "variety_show",
        "name": "방송 예능 버라이어티",
        "category": "예능/썰/코미디/인터뷰",
        "font_file": "Jua-Regular.ttf",
        "font_size_mult": 0.98,
        "tilt": 1.5,
        "banner_style": "plates",
        "banner_color": (240, 140, 10),
        "rim_color": (255, 235, 20),
        "p_colors": [(255, 220, 30), (255, 160, 20), (255, 255, 255)],
    },
    "washi_vlog": {
        "id": "washi_vlog",
        "name": "감성 테이프 손글씨",
        "category": "감성 브이로그/여행/힐링",
        "font_file": "NanumPenScript-Regular.ttf",
        "font_size_mult": 1.30,
        "tilt": -1.5,
        "banner_style": "washi_tape",
        "banner_color": (60, 50, 45),
        "rim_color": (255, 210, 140),
        "p_colors": [(255, 240, 210), (255, 200, 150), (240, 220, 190)],
    },
}


def parse_blockbuster_phrases(title: str, hook_text: str) -> Tuple[str, str]:
    """
    Extracts 2 high-impact, punchy phrases from title and hook without repetition.
    Part 1: The trigger word (4~8 chars, quoted)
    Part 2: The outcome / consequence (4~10 chars)
    """
    clean_t = (title or "").strip().replace("에이아이", "AI").split("#")[0].strip()
    clean_h = (hook_text or "").strip().replace("에이아이", "AI").split("#")[0].strip()

    if clean_h:
        part1 = clean_h
        remainder = clean_t
        # Clean overlapping words or prefixes
        for word in clean_h.split():
            if len(word) >= 2:
                remainder = remainder.replace(f"{word} 속", "").replace(f"{word} 시", "").replace(f"{word} 때", "").replace(word, "").strip()
        part2 = remainder if remainder else "100% 필수 시청"
    elif clean_t:
        words = clean_t.split()
        if len(words) >= 2:
            part1 = " ".join(words[:2])
            part2 = " ".join(words[2:]) if len(words) > 2 else words[1]
        else:
            part1 = clean_t
            part2 = "100% 필수 시청"
    else:
        part1 = "긴급 대처법"
        part2 = "모르면 손해"

    # Enforce character limits
    part1 = part1[:10].strip()
    part2 = part2[:12].strip()

    # Wrap part1 in quotes if not present
    if not (part1.startswith("“") or part1.startswith('"') or part1.startswith("'")):
        part1 = f"“{part1}”"

    return part1, part2

def render_graphic_text_block(
    dest_canvas: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    pos_x: int,
    pos_y: int,
    style: str = "gold_gloss",
    depth: int = 20,
    inner_stroke_color: Tuple[int, int, int] = (255, 255, 255),
    outer_shadow_color: Tuple[int, int, int] = (0, 0, 0)
):
    """
    Photoshop-Grade Procedural Graphic Typography Shader:
    - 3D Extruded Bevel with directional decay shading
    - Multi-layer stroke outline
    - Procedural gradient + micro-textured surface (Ruby gloss, Gold gloss, or Weathered stone)
    - Specular top rim highlight (embossed bevel light)
    """
    tdraw = ImageDraw.Draw(dest_canvas)
    w, h = dest_canvas.size

    # 1. 3D Extrusion slices (directional down-right)
    for d in range(depth, 0, -1):
        shade = int(22 * (1.0 - d / depth))
        tdraw.text(
            (pos_x + d // 2, pos_y + d),
            text,
            font=font,
            fill=(shade, shade, shade, 255),
            stroke_width=7,
            stroke_fill=(0, 0, 0, 255)
        )

    # 2. Outer dark silhouette stroke
    tdraw.text((pos_x, pos_y), text, font=font, fill=inner_stroke_color, stroke_width=15, stroke_fill=outer_shadow_color)

    # 3. Inner contrast stroke
    if inner_stroke_color:
        tdraw.text((pos_x, pos_y), text, font=font, fill=(0, 0, 0, 0), stroke_width=6, stroke_fill=inner_stroke_color)

    # 4. Measure text bounds for procedural shader
    bbox = tdraw.textbbox((pos_x, pos_y), text, font=font)
    tw, th = max(1, bbox[2] - bbox[0]), max(1, bbox[3] - bbox[1])

    # Isolated alpha mask
    mask_layer = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask_layer)
    mdraw.text((pos_x, pos_y), text, font=font, fill=255)

    # 5. Gradient Shading Face
    grad_np = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(pos_y, min(h, pos_y + th + 15)):
        ratio = max(0.0, min(1.0, (y - pos_y) / max(1, th)))
        if style == "ruby_gloss":
            r = int(255 * (1.0 - ratio * 0.55))
            g = int(65 * (1.0 - ratio * 0.9))
            b = int(65 * (1.0 - ratio * 0.8))
        elif style == "cyber_cyan":
            r = int(0 + ratio * 30)
            g = int(235 - ratio * 90)
            b = int(255 - ratio * 20)
        elif style == "warm_sunset":
            r = int(255 - ratio * 10)
            g = int(150 - ratio * 80)
            b = int(40 + ratio * 30)
        elif style == "gold_gloss":
            r = int(255 - ratio * 30)
            g = int(235 - ratio * 105)
            b = int(20 + ratio * 10)
        else:  # concrete_weathered
            val = int(252 - ratio * 55)
            r = g = b = val
        grad_np[y, :] = [r, g, b]

    face_img = Image.fromarray(grad_np, "RGB")

    # 6. Procedural Texture / Weathering Noise
    noise_sigma = 65 if style == "concrete_weathered" else 40
    noise = np.random.normal(128, noise_sigma, (h, w)).clip(0, 255).astype(np.uint8)
    noise_img = Image.fromarray(noise, "L").filter(ImageFilter.GaussianBlur(1.0))
    face_np = np.array(face_img, dtype=np.float32)
    noise_np = np.array(noise_img, dtype=np.float32) / 255.0

    mult = (0.6 + 0.7 * noise_np[:, :, np.newaxis]) if style == "concrete_weathered" else (0.75 + 0.5 * noise_np[:, :, np.newaxis])
    face_textured = Image.fromarray(np.clip(face_np * mult, 0, 255).astype(np.uint8), "RGB")

    # 7. Specular Top Bevel Edge (Light reflection)
    mask_arr = np.array(mask_layer, dtype=np.float32)
    shift_down = np.roll(mask_arr, 4, axis=0)
    shift_down[:4, :] = 0
    top_edge = np.clip(mask_arr - shift_down, 0, 255).astype(np.uint8)
    top_edge_img = Image.fromarray(top_edge, "L").filter(ImageFilter.GaussianBlur(1.5))

    highlight_rgba = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    highlight_rgba.putalpha(top_edge_img)

    # 8. Alpha composite graphic face onto canvas
    face_rgba = face_textured.convert("RGBA")
    face_rgba.putalpha(mask_layer)
    final_face = Image.alpha_composite(face_rgba, highlight_rgba)

    dest_canvas.paste(final_face, (0, 0), final_face)

draw_3d_text = render_graphic_text_block

def draw_grunge_slash_banner(
    w: int,
    h: int,
    by1: int,
    by2: int,
    color: Tuple[int, int, int] = (195, 15, 28),
    angle_offset: int = 40
) -> Image.Image:
    """
    Renders an organic, aggressive torn brush banner with jagged edges and dripping splatter.
    """
    banner = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(banner)
    base_pts = [
        (-20, by1 + angle_offset),
        (w + 20, by1 - (angle_offset // 2)),
        (w + 20, by2),
        (-20, by2 + (angle_offset // 2))
    ]
    bdraw.polygon(base_pts, fill=(*color, 245))

    random.seed(999)
    step_x = max(6, w // 130)
    # Jagged brush top edge
    for x in range(0, w + 20, step_x):
        y_top = int(by1 + angle_offset - ((angle_offset * 1.5) * x / w) + random.randint(-16, 16))
        brush_len = random.randint(15, 45)
        bdraw.line([(x, y_top), (x + random.randint(-4, 4), y_top + brush_len)], fill=(*color, 245), width=random.randint(6, 14))

    # Jagged dripping bottom edge
    darker_color = (max(0, color[0] - 35), max(0, color[1] - 8), max(0, color[2] - 10))
    for x in range(0, w + 20, step_x + 2):
        y_bot = int(by2 + (angle_offset // 2) - ((angle_offset // 2) * x / w) + random.randint(-12, 12))
        drip_len = random.randint(10, 55)
        bdraw.line([(x, y_bot), (x, y_bot + drip_len)], fill=(*darker_color, 235), width=random.randint(4, 10))

    # Splatter droplets
    for _ in range(160):
        sx = random.randint(0, w)
        sy = random.randint(by1 - 40, by2 + 70)
        sr = random.randint(2, 8)
        dark_shade = max(0, color[0] - 80)
        bdraw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(dark_shade, 0, 10, random.randint(160, 255)))

    return banner.filter(ImageFilter.GaussianBlur(1.2))

def detect_content_mood(title: str, hook_text: str = "") -> Dict:
    """
    Analyzes video title and hook semantics to dynamically select the best typography preset:
    - spooky_ghost: horror, ghost, mystery, abandoned
    - ink_splatter: flood, disaster, fight, accident, real story
    - cyber_neon: AI, Tesla, Apple, EV, tech, coding, gadgets
    - gold_luxury: bitcoin, stock, crypto, money, wealth, luxury
    - jelly_pop: food, mukbang, cafe, bagel, dessert, recipe
    - washi_vlog: vlog, travel, healing, jeju, alone, quiet
    - variety_show: talk, confession, comedy, funny, secret, dating
    - blockbuster_3d: default high-CTR shock, viral, warning
    """
    text = f"{title} {hook_text}".lower()

    # 1. Horror / Ghost / Mystery
    if any(k in text for k in ["괴담", "공포", "흉가", "미스터리", "심령", "폐병원", "귀신", "악마", "저주", "오싹", "무서운", "심야"]):
        return TYPOGRAPHY_PRESETS["spooky_ghost"]

    # 2. Disaster / Blood / Combat / Emergency
    if any(k in text for k in ["폭우", "침수", "방전", "긴급", "위험", "경고", "사망", "체포", "폭망", "파산", "화재", "사고", "실화", "탈출", "생존", "갇힘", "고립", "대피", "비상", "격투", "살인"]):
        return TYPOGRAPHY_PRESETS["ink_splatter"]

    # 3. Stock / Crypto / Wealth / Finance
    if any(k in text for k in ["주식", "코인", "비트코인", "이더리움", "10억", "재테크", "부자", "월급", "수익", "투자", "명품", "연봉", "슈퍼카", "매출", "상승", "폭등"]):
        return TYPOGRAPHY_PRESETS["gold_luxury"]

    # 4. Tech / AI / Cyber / Gadgets
    if any(k in text for k in ["스마트폰", "ai", "테슬라", "애플", "전기차", "로봇", "반도체", "미래", "과학", "팁", "꿀팁", "알고리즘", "세팅", "기능", "업데이트", "아이폰", "갤럭시", "컴퓨터", "비전프로", "chatgpt", "출시", "개발", "코딩"]):
        return TYPOGRAPHY_PRESETS["cyber_neon"]

    # 5. Food / Mukbang / Cafe / Dessert
    if any(k in text for k in ["맛집", "베이글", "카페", "요리", "먹방", "디저트", "빵", "존맛", "케이크", "식당", "레시피", "꿀조합", "고기", "치킨", "라면"]):
        return TYPOGRAPHY_PRESETS["jelly_pop"]

    # 6. Vlog / Travel / Healing
    if any(k in text for k in ["브이로그", "여행", "힐링", "제주", "혼자", "감성", "다이어리", "산책", "숙소", "조용한", "호캉스", "휴식"]):
        return TYPOGRAPHY_PRESETS["washi_vlog"]

    # 7. Variety Show / Talk / Comedy / Dating
    if any(k in text for k in ["썰", "고백", "비밀", "코미디", "폭소", "개그", "웃긴", "친구", "연애", "환승", "남친", "여친", "인터뷰", "충격 고백"]):
        return TYPOGRAPHY_PRESETS["variety_show"]

    # 8. Default High-CTR Viral Blockbuster
    return TYPOGRAPHY_PRESETS["blockbuster_3d"]

def draw_preset_banner(
    w: int,
    h: int,
    by1: int,
    by2: int,
    preset: Dict,
    aspect_ratio: str = "9:16"
) -> Image.Image:
    """
    Renders a style-matched background banner for the typography preset:
    - slash: organic distressed torn banner with splatter
    - cyber_lines: dark cyber banner with neon laser borders
    - shadow_smoke: dark eerie smoke fog
    - soft_pill: gentle dark plate with pastel neon halo
    - plates / washi_tape: clean soft vignette (label plates provide contrast)
    """
    style = preset.get("banner_style", "slash")
    color = preset.get("banner_color", (195, 12, 25))

    if style == "slash":
        offset = 45 if aspect_ratio == "9:16" else 30
        return draw_grunge_slash_banner(w, h, by1, by2, color=color, angle_offset=offset)

    banner = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(banner)

    if style == "cyber_lines":
        pad_y = 30
        bdraw.rectangle([(0, by1 - pad_y), (w, by2 + pad_y)], fill=(*color, 230))
        rim = preset.get("rim_color", (0, 235, 255))
        bdraw.line([(0, by1 - pad_y), (w, by1 - pad_y)], fill=(*rim, 240), width=4)
        bdraw.line([(0, by2 + pad_y), (w, by2 + pad_y)], fill=(*rim, 240), width=4)
        return banner.filter(ImageFilter.GaussianBlur(1.0))

    elif style == "shadow_smoke":
        for y in range(max(0, by1 - 100), min(h, by2 + 120)):
            factor = 1.0 - abs(y - (by1 + by2) // 2) / ((by2 - by1) // 2 + 100)
            alpha = int(240 * max(0.0, factor))
            bdraw.line([(0, y), (w, y)], fill=(*color, alpha))
        return banner.filter(ImageFilter.GaussianBlur(12.0))

    elif style == "soft_pill":
        pad_x = 40
        bdraw.rounded_rectangle(
            [pad_x, by1 - 20, w - pad_x, by2 + 30],
            radius=32,
            fill=(18, 16, 22, 220),
            outline=(*color, 180),
            width=3
        )
        return banner.filter(ImageFilter.GaussianBlur(2.0))

    else:  # plates or washi_tape (soft shadow backing for maximum readability)
        for y in range(max(0, by1 - 40), min(h, by2 + 60)):
            factor = 1.0 - abs(y - (by1 + by2) // 2) / ((by2 - by1) // 2 + 50)
            alpha = int(140 * max(0.0, factor))
            bdraw.line([(0, y), (w, y)], fill=(10, 10, 14, alpha))
        return banner.filter(ImageFilter.GaussianBlur(16.0))

def render_preset_typography(
    txt_canvas: Image.Image,
    part1: str,
    part2: str,
    preset: Dict,
    aspect_ratio: str = "9:16"
):
    """
    Renders professional creator typography tailored to the selected preset.
    Supports all 8 distinct image font styles with custom shaders and plate geometry.
    """
    p_id = preset.get("id", "blockbuster_3d")
    font_file = preset.get("font_file", "BlackHanSans-Regular.ttf")
    mult = preset.get("font_size_mult", 1.0)

    if aspect_ratio == "16:9":
        base_s1, base_s2 = int(92 * mult), int(82 * mult)
    else:
        base_s1, base_s2 = int(125 * mult), int(115 * mult)

    font1 = get_preset_font(font_file, base_s1)
    font2 = get_preset_font(font_file, base_s2)

    cw, ch = txt_canvas.size
    tdraw = ImageDraw.Draw(txt_canvas)

    # 1. 3D Blockbuster
    if p_id == "blockbuster_3d":
        style1 = preset.get("style1", "ruby_gloss")
        style2 = preset.get("style2", "concrete_weathered")
        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2)) // 2
            sy = 70
            render_graphic_text_block(txt_canvas, part1, font1, sx, sy, style=style1, depth=18, inner_stroke_color=(255, 255, 255))
            render_graphic_text_block(txt_canvas, f" {part2}", font2, sx + w1 + 10, sy, style=style2, depth=18, inner_stroke_color=(20, 20, 20))
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            sx1 = (cw - (bb1[2] - bb1[0])) // 2
            render_graphic_text_block(txt_canvas, part1, font1, sx1, 40, style=style1, depth=22, inner_stroke_color=(255, 255, 255))
            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            sx2 = (cw - (bb2[2] - bb2[0])) // 2
            render_graphic_text_block(txt_canvas, part2, font2, sx2, 220, style=style2, depth=22, inner_stroke_color=(20, 20, 20))

    # 2. Jelly Pop Bubble Sticker (BagelFatOne)
    elif p_id == "jelly_pop":
        def draw_jelly_line(x, y, text, f, fill_color):
            tdraw.text((x, y), text, font=f, fill=(20, 15, 25), stroke_width=20, stroke_fill=(20, 15, 25))
            tdraw.text((x, y), text, font=f, fill=(255, 255, 255), stroke_width=12, stroke_fill=(255, 255, 255))
            tdraw.text((x, y), text, font=f, fill=fill_color)

        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2)) // 2
            draw_jelly_line(sx, 70, part1, font1, (255, 65, 130))
            draw_jelly_line(sx + w1 + 15, 70, f" {part2}", font2, (255, 220, 0))
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            sx1 = (cw - (bb1[2] - bb1[0])) // 2
            draw_jelly_line(sx1, 40, part1, font1, (255, 65, 130))
            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            sx2 = (cw - (bb2[2] - bb2[0])) // 2
            draw_jelly_line(sx2, 220, part2, font2, (255, 220, 0))

    # 3. Ink Splatter Calligraphy (EastSeaDokdo)
    elif p_id == "ink_splatter":
        def draw_ink_line(x, y, text, f, fill_color, stroke_col=(0, 0, 0)):
            tdraw.text((x, y), text, font=f, fill=stroke_col, stroke_width=16, stroke_fill=stroke_col)
            tdraw.text((x, y), text, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(255, 255, 255))
            tdraw.text((x, y), text, font=f, fill=fill_color)

        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2)) // 2
            draw_ink_line(sx, 60, part1, font1, (230, 20, 30))
            draw_ink_line(sx + w1 + 15, 60, f" {part2}", font2, (240, 240, 240))
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            sx1 = (cw - (bb1[2] - bb1[0])) // 2
            draw_ink_line(sx1, 30, part1, font1, (230, 20, 30))
            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            sx2 = (cw - (bb2[2] - bb2[0])) // 2
            draw_ink_line(sx2, 220, part2, font2, (240, 240, 240))

        # Dynamic Splatter Drops around text
        random.seed(77)
        for _ in range(60):
            ix = random.randint(100, cw - 100)
            iy = random.randint(20, ch - 40)
            ir = random.randint(2, 6)
            tdraw.ellipse([ix - ir, iy - ir, ix + ir, iy + ir], fill=(180, 10, 20, random.randint(180, 255)))

    # 4. Cyber Neon Tube (GasoekOne)
    elif p_id == "cyber_neon":
        glow_layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)

        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2)) // 2
            gdraw.text((sx, 65), part1, font=font1, fill=(0, 230, 255, 255), stroke_width=18, stroke_fill=(0, 230, 255, 255))
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(12))
            txt_canvas.paste(glow_layer, (0, 0), glow_layer)

            tdraw.text((sx, 65), part1, font=font1, fill=(255, 255, 255), stroke_width=8, stroke_fill=(10, 30, 60))
            tdraw.text((sx, 65), part1, font=font1, fill=(0, 245, 255))

            tdraw.text((sx + w1 + 15, 65), f" {part2}", font=font2, fill=(0, 0, 0), stroke_width=12, stroke_fill=(0, 0, 0))
            tdraw.text((sx + w1 + 15, 65), f" {part2}", font=font2, fill=(235, 245, 255))
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            sx1 = (cw - (bb1[2] - bb1[0])) // 2
            gdraw.text((sx1, 40), part1, font=font1, fill=(0, 230, 255, 255), stroke_width=20, stroke_fill=(0, 230, 255, 255))
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(14))
            txt_canvas.paste(glow_layer, (0, 0), glow_layer)

            tdraw.text((sx1, 40), part1, font=font1, fill=(255, 255, 255), stroke_width=8, stroke_fill=(10, 30, 60))
            tdraw.text((sx1, 40), part1, font=font1, fill=(0, 245, 255))

            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            sx2 = (cw - (bb2[2] - bb2[0])) // 2
            tdraw.text((sx2, 220), part2, font=font2, fill=(0, 0, 0), stroke_width=14, stroke_fill=(0, 0, 0))
            tdraw.text((sx2, 220), part2, font=font2, fill=(235, 245, 255))

    # 5. Gold Luxury Emboss (DoHyeon)
    elif p_id == "gold_luxury":
        def draw_gold_line(x, y, text, f, is_gold=True):
            tdraw.text((x, y), text, font=f, fill=(0, 0, 0), stroke_width=16, stroke_fill=(0, 0, 0))
            if is_gold:
                tdraw.text((x, y), text, font=f, fill=(255, 240, 160), stroke_width=8, stroke_fill=(180, 130, 20))
                tdraw.text((x, y), text, font=f, fill=(255, 215, 0))
            else:
                tdraw.text((x, y), text, font=f, fill=(255, 255, 255))

        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2)) // 2
            draw_gold_line(sx, 70, part1, font1, is_gold=True)
            draw_gold_line(sx + w1 + 15, 70, f" {part2}", font2, is_gold=False)
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            sx1 = (cw - (bb1[2] - bb1[0])) // 2
            draw_gold_line(sx1, 40, part1, font1, is_gold=True)
            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            sx2 = (cw - (bb2[2] - bb2[0])) // 2
            draw_gold_line(sx2, 220, part2, font2, is_gold=False)

            # Sparkle glints
            for gx, gy in [(sx1 + 30, 50), (sx1 + (bb1[2] - bb1[0]) - 30, 60), (sx2 + 50, 235)]:
                tdraw.line([(gx - 10, gy), (gx + 10, gy)], fill=(255, 255, 255), width=3)
                tdraw.line([(gx, gy - 10), (gx, gy + 10)], fill=(255, 255, 255), width=3)
                tdraw.ellipse([gx - 4, gy - 4, gx + 4, gy + 4], fill=(255, 255, 255))

    # 6. Spooky Ghost Ectoplasm (KirangHaerang)
    elif p_id == "spooky_ghost":
        glow_layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)

        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2)) // 2
            gdraw.text((sx, 55), part1, font=font1, fill=(50, 255, 120, 255), stroke_width=20, stroke_fill=(50, 255, 120, 255))
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(16))
            txt_canvas.paste(glow_layer, (0, 0), glow_layer)

            tdraw.text((sx, 55), part1, font=font1, fill=(0, 0, 0), stroke_width=12, stroke_fill=(0, 0, 0))
            tdraw.text((sx, 55), part1, font=font1, fill=(180, 255, 210))

            tdraw.text((sx + w1 + 15, 55), f" {part2}", font=font2, fill=(0, 0, 0), stroke_width=14, stroke_fill=(0, 0, 0))
            tdraw.text((sx + w1 + 15, 55), f" {part2}", font=font2, fill=(240, 80, 80))
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            sx1 = (cw - (bb1[2] - bb1[0])) // 2
            gdraw.text((sx1, 25), part1, font=font1, fill=(50, 255, 120, 255), stroke_width=22, stroke_fill=(50, 255, 120, 255))
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(16))
            txt_canvas.paste(glow_layer, (0, 0), glow_layer)

            tdraw.text((sx1, 25), part1, font=font1, fill=(0, 0, 0), stroke_width=12, stroke_fill=(0, 0, 0))
            tdraw.text((sx1, 25), part1, font=font1, fill=(180, 255, 210))

            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            sx2 = (cw - (bb2[2] - bb2[0])) // 2
            tdraw.text((sx2, 210), part2, font=font2, fill=(0, 0, 0), stroke_width=14, stroke_fill=(0, 0, 0))
            tdraw.text((sx2, 210), part2, font=font2, fill=(240, 80, 80))

    # 7. Variety Show Television Caption Plates (Jua)
    elif p_id == "variety_show":
        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2 + 60)) // 2

            tdraw.rounded_rectangle([sx, 60, sx + w1 + 24, 150], radius=14, fill=(255, 225, 0), outline=(20, 20, 20), width=4)
            tdraw.text((sx + 12, 68), part1, font=font1, fill=(20, 20, 20))

            tdraw.rounded_rectangle([sx + w1 + 35, 60, sx + w1 + w2 + 55, 150], radius=14, fill=(20, 20, 20), outline=(255, 255, 255), width=3)
            tdraw.text((sx + w1 + 45, 68), f" {part2}", font=font2, fill=(255, 255, 255))
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            sx1 = (cw - (w1 + 36)) // 2
            tdraw.rounded_rectangle([sx1, 40, sx1 + w1 + 36, 175], radius=18, fill=(255, 225, 0), outline=(20, 20, 20), width=5)
            tdraw.text((sx1 + 18, 52), part1, font=font1, fill=(20, 20, 20))

            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            w2 = bb2[2] - bb2[0]
            sx2 = (cw - (w2 + 36)) // 2
            tdraw.rounded_rectangle([sx2, 220, sx2 + w2 + 36, 350], radius=18, fill=(20, 20, 20), outline=(255, 255, 255), width=4)
            tdraw.text((sx2 + 18, 230), part2, font=font2, fill=(255, 255, 255))

    # 8. Washi Vlog Masking Tape (NanumPenScript)
    elif p_id == "washi_vlog":
        if aspect_ratio == "16:9":
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            bb2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
            w2 = bb2[2] - bb2[0]
            sx = (cw - (w1 + w2 + 50)) // 2

            tdraw.rounded_rectangle([sx, 55, sx + w1 + 25, 155], radius=8, fill=(255, 245, 225, 240), outline=(220, 200, 180), width=2)
            tdraw.text((sx + 12, 52), part1, font=font1, fill=(45, 40, 35))

            tdraw.rounded_rectangle([sx + w1 + 35, 55, sx + w1 + w2 + 55, 155], radius=8, fill=(40, 35, 30, 230), outline=(180, 160, 140), width=2)
            tdraw.text((sx + w1 + 45, 52), f" {part2}", font=font2, fill=(255, 248, 235))
        else:
            bb1 = tdraw.textbbox((0, 0), part1, font=font1)
            w1 = bb1[2] - bb1[0]
            sx1 = (cw - (w1 + 40)) // 2
            tdraw.rounded_rectangle([sx1, 35, sx1 + w1 + 40, 175], radius=10, fill=(255, 245, 225, 240), outline=(220, 200, 180), width=3)
            tdraw.text((sx1 + 20, 32), part1, font=font1, fill=(45, 40, 35))

            bb2 = tdraw.textbbox((0, 0), part2, font=font2)
            w2 = bb2[2] - bb2[0]
            sx2 = (cw - (w2 + 40)) // 2
            tdraw.rounded_rectangle([sx2, 220, sx2 + w2 + 40, 360], radius=10, fill=(40, 35, 30, 230), outline=(180, 160, 140), width=3)
            tdraw.text((sx2 + 20, 215), part2, font=font2, fill=(255, 248, 235))


def add_atmospheric_fx(
    canvas_rgba: Image.Image,
    banner_y1: int,
    p_colors: Optional[List[Tuple[int, int, int]]] = None
) -> Image.Image:
    """
    Adds cinematic floating sparks/particles matching the content theme.
    """
    w, h = canvas_rgba.size
    embers = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    edraw = ImageDraw.Draw(embers)
    random.seed(42)
    colors = p_colors or [(255, 205, 50), (255, 125, 30), (255, 60, 20), (255, 255, 220)]
    for _ in range(70):
        ex = random.randint(0, w)
        ey = random.randint(max(0, banner_y1 - 120), h - 80)
        er = random.randint(2, 6)
        col = random.choice(colors)
        edraw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(*col, random.randint(180, 255)))
    embers = embers.filter(ImageFilter.GaussianBlur(1.0))
    return Image.alpha_composite(canvas_rgba, embers)

def extract_subject_cutout(pil_img: Image.Image) -> Optional[Image.Image]:
    """
    Extracts foreground subject (face/person/object) using local rembg (u2net).
    Runs in < 1 second.
    Applies facial clarity, sharpness, and vibrant skin tone punch.
    """
    try:
        session = get_rembg_session()
        if session is False:
            return None
        import rembg
        # Resize temporarily if huge to ensure instant inference
        max_dim = 960
        orig_w, orig_h = pil_img.size
        working_img = pil_img.copy()
        if max(orig_w, orig_h) > max_dim:
            working_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        cutout = rembg.remove(working_img, session=session)
        if cutout.size != (orig_w, orig_h):
            cutout = cutout.resize((orig_w, orig_h), Image.Resampling.LANCZOS)

        # Enhance subject punch (face clarity, contrast, skin vibrance)
        r, g, b, a = cutout.split()
        rgb_c = Image.merge("RGB", (r, g, b))
        rgb_c = ImageEnhance.Sharpness(rgb_c).enhance(1.6)
        rgb_c = ImageEnhance.Contrast(rgb_c).enhance(1.22)
        rgb_c = ImageEnhance.Color(rgb_c).enhance(1.25)
        return Image.merge("RGBA", (*rgb_c.split(), a))
    except Exception as e:
        print(f"rembg cutout skipped: {e}")
        return None

def apply_rim_light(
    bg_rgba: Image.Image,
    cutout_rgba: Image.Image,
    pos_x: int,
    pos_y: int,
    rim_color: Tuple[int, int, int] = (60, 200, 255),
    outer_blur: int = 32,
    sharp_blur: int = 8
) -> Image.Image:
    """
    Applies multi-layer neon rim lighting around the subject cutout.
    Layer 1: Soft diffuse glow aura
    Layer 2: Sharp high-intensity white rim edge
    """
    w, h = bg_rgba.size
    mask = cutout_rgba.split()[3]

    # Soft diffuse aura
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_color = Image.new("RGBA", cutout_rgba.size, (*rim_color, 240))
    glow.paste(glow_color, (pos_x, pos_y), mask)
    glow = glow.filter(ImageFilter.GaussianBlur(outer_blur))

    # Sharp rim edge
    sharp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sharp.paste(Image.new("RGBA", cutout_rgba.size, (255, 255, 255, 255)), (pos_x, pos_y), mask)
    sharp = sharp.filter(ImageFilter.GaussianBlur(sharp_blur))

    res = Image.alpha_composite(bg_rgba, glow)
    res = Image.alpha_composite(res, sharp)
    res.paste(cutout_rgba, (pos_x, pos_y), cutout_rgba)
    return res

def create_cinematic_bg(
    raw_frame_rgb: Image.Image,
    target_w: int,
    target_h: int
) -> Image.Image:
    """
    Transforms a raw video frame into a rich, contrasty, bokeh background.
    """
    rw, rh = raw_frame_rgb.size
    # Crop to target aspect ratio
    target_ratio = target_w / target_h
    raw_ratio = rw / rh

    if raw_ratio > target_ratio:
        cw = int(rh * target_ratio)
        x1 = (rw - cw) // 2
        cropped = raw_frame_rgb.crop((x1, 0, x1 + cw, rh))
    else:
        ch = int(rw / target_ratio)
        y1 = (rh - ch) // 2
        cropped = raw_frame_rgb.crop((0, y1, rw, y1 + ch))

    bg = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    bg = ImageEnhance.Contrast(bg).enhance(1.25)
    bg = ImageEnhance.Color(bg).enhance(1.3)
    bg = bg.filter(ImageFilter.GaussianBlur(22))

    # Top & bottom vignette
    vignette = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for y in range(target_h):
        if y < int(target_h * 0.2):
            a = int(190 * (1.0 - y / (target_h * 0.2)))
        elif y > int(target_h * 0.5):
            a = int(230 * ((y - target_h * 0.5) / (target_h * 0.5)))
        else:
            a = 70
        vdraw.line([(0, y), (target_w, y)], fill=(5, 5, 12, a))

    return Image.alpha_composite(bg.convert("RGBA"), vignette)

def extract_thumbnail_candidates(
    video_path: str,
    source_video_path: Optional[str] = None,
    start_time: float = 0.0,
    duration: float = 30.0,
    count: int = 4,
    output_dir: str = "temp/candidates"
) -> List[Dict]:
    """
    Extracts multiple candidate face-centered 9:16 frames across the clip timeline.
    Returns preview paths and timestamps for interactive user selection.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    target_video = source_video_path if (source_video_path and Path(source_video_path).exists()) else video_path
    is_source = (target_video == source_video_path)

    cap = cv2.VideoCapture(target_video)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1000)
    video_dur = total_frames / fps

    effective_dur = min(duration, video_dur - (start_time if is_source else 0.0))
    if effective_dur <= 2.0:
        rel_offsets = [0.5, 1.0]
    else:
        rel_offsets = [effective_dur * ratio for ratio in [0.15, 0.35, 0.60, 0.82]][:count]

    candidates = []
    base_name = Path(video_path).stem

    for idx, offset in enumerate(rel_offsets):
        target_sec = (start_time + offset) if is_source else offset
        f_idx = int(target_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(rgb)
        rw, rh = pil_frame.size
        cw = int(rh * 9 / 16)
        x1 = max(0, min(rw - cw, (rw - cw) // 2))
        cropped = pil_frame.crop((x1, 0, x1 + cw, rh)).resize((540, 960), Image.Resampling.LANCZOS)

        cand_filename = f"cand_{base_name}_{idx}.jpg"
        cand_path = out_dir / cand_filename
        cropped.save(str(cand_path), quality=90)

        candidates.append({
            "index": idx,
            "timestamp": round(target_sec, 2),
            "offset_sec": round(offset, 2),
            "file_path": str(cand_path),
            "preview_url": f"/media/temp/candidates/{cand_filename}"
        })

    cap.release()
    return candidates

def generate_creator_thumbnail(
    video_path: str,
    output_cover_path: str,
    title: str = "",
    hook_text: str = "",
    badge_type: str = "warning",
    badge_label: Optional[str] = None,
    headline_style: str = "yellow_on_black",
    punchline_style: str = "white_on_black",
    aspect_ratio: str = "9:16",
    source_video_path: Optional[str] = None,
    start_time: Optional[float] = None,
    duration: Optional[float] = None,
    target_time: Optional[float] = None,
    virality_score: Optional[int] = None,
    ai_bg_path: Optional[str] = None,
    style_preset: Optional[str] = None,
    **kwargs,
) -> str:
    """
    3D Blockbuster & Stylized Image-Font Viral Thumbnail Engine:
    - 4-Layer Architecture:
      1. Layer 1: Cinematic bokeh background (AI-generated or graded video frame with vignette)
      2. Layer 2: Subject Cutout (rembg u2net) with Multi-Layer Neon Rim Glow matching preset
      3. Layer 3: Preset-tailored Banner / Backplate (Slash splatter, Cyber neon lines, Eerie fog, etc.)
      4. Layer 4: Multi-Style Graphic Typography (8 distinct presets: Jelly Pop, Calli Ink, Cyber Neon,
         3D Blockbuster, 24K Gold Luxury, Spooky Ghost, TV Variety Show, Washi Vlog)
    - 100% Local Apple Silicon, sub-second inference.
    - Saves 1080x1920 (9:16) or 1280x720 (16:9) high-CTR JPEG.
    """
    out_p = Path(output_cover_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # 1. Target dimensions
    if aspect_ratio == "16:9":
        target_w, target_h = 1280, 720
    else:  # Default 9:16 Shorts
        target_w, target_h = 1080, 1920

    # 2. Extract best video frame
    target_video = source_video_path if (source_video_path and Path(source_video_path).exists()) else video_path
    is_source = (target_video == source_video_path)
    base_time = (start_time or 0.0) if is_source else 0.0
    clip_dur = duration or 30.0
    sample_time = target_time if target_time is not None else (base_time + min(clip_dur * 0.25, 4.0))

    cap = cv2.VideoCapture(target_video)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video for thumbnail: {target_video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    video_dur = total_frames / fps if fps > 0 else 0.0

    if video_dur > 0:
        sample_time = max(0.0, min(sample_time, video_dur - 0.1))

    cap.set(cv2.CAP_PROP_POS_FRAMES, int(sample_time * fps))
    ret, frame = cap.read()
    if not ret or frame is None:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError(f"Failed to capture frame at {sample_time}s from {target_video}")

    raw_frame_rgb = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # 3. Create Layer 1: Background
    if ai_bg_path and Path(ai_bg_path).exists():
        ai_bg = Image.open(ai_bg_path).convert("RGBA").resize((target_w, target_h), Image.Resampling.LANCZOS)
        canvas = ImageEnhance.Contrast(ai_bg).enhance(1.15)
        vignette = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        vdraw = ImageDraw.Draw(vignette)
        for y in range(int(target_h * 0.45), target_h):
            factor = (y - target_h * 0.45) / (target_h * 0.55)
            alpha = int(220 * (factor ** 1.3))
            vdraw.line([(0, y), (target_w, y)], fill=(0, 0, 0, alpha))
        canvas = Image.alpha_composite(canvas, vignette)
    else:
        canvas = create_cinematic_bg(raw_frame_rgb, target_w, target_h)

    # 4. Resolve Typography Preset (Explicit user selection or AI content analysis)
    if style_preset and style_preset in TYPOGRAPHY_PRESETS:
        preset = TYPOGRAPHY_PRESETS[style_preset]
    else:
        preset = detect_content_mood(title, hook_text)

    # Subtle mood wash
    banner_color = preset.get("banner_color", (195, 12, 25))
    wash = Image.new("RGBA", (target_w, target_h), (*banner_color, 35))
    canvas = Image.alpha_composite(canvas, wash)

    # 5. Create Layer 2: Subject Cutout & Themed Rim Light
    cutout = extract_subject_cutout(raw_frame_rgb)
    if cutout is not None:
        if aspect_ratio == "16:9":
            scale = (target_h * 0.90) / cutout.height
            nw = int(cutout.width * scale)
            nh = int(cutout.height * scale)
            cutout_resized = cutout.resize((nw, nh), Image.Resampling.LANCZOS)
            px = target_w - nw - 40
            py = target_h - nh
        else:
            scale = (target_w * 1.62) / cutout.width
            nw = int(cutout.width * scale)
            nh = int(cutout.height * scale)
            cutout_resized = cutout.resize((nw, nh), Image.Resampling.LANCZOS)
            px = (target_w - nw) // 2
            py = 310

        rim_col = preset.get("rim_color", (60, 200, 255))
        canvas = apply_rim_light(canvas, cutout_resized, px, py, rim_color=rim_col)

    # 6. Create Layer 3: Preset-Tailored Banner & Atmospheric FX
    if aspect_ratio == "16:9":
        by1 = target_h - 220
        by2 = target_h - 30
    else:
        by1 = 1010
        by2 = 1490

    banner = draw_preset_banner(target_w, target_h, by1, by2, preset=preset, aspect_ratio=aspect_ratio)
    canvas = Image.alpha_composite(canvas, banner)
    canvas = add_atmospheric_fx(canvas, by1, p_colors=preset.get("p_colors"))

    # 7. Create Layer 4: Stylized Typography (Rendered with preset image font & shaders)
    part1, part2 = parse_blockbuster_phrases(title, hook_text)

    txt_canvas_w = target_w + 350
    txt_canvas_h = 350 if aspect_ratio == "16:9" else 550
    txt_img = Image.new("RGBA", (txt_canvas_w, txt_canvas_h), (0, 0, 0, 0))

    render_preset_typography(txt_img, part1, part2, preset=preset, aspect_ratio=aspect_ratio)

    # Apply preset dynamic tilt
    tilt_deg = -float(preset.get("tilt", -3.5))
    rotated_txt = txt_img.rotate(tilt_deg, resample=Image.Resampling.BICUBIC, expand=True)

    tx = (target_w - rotated_txt.width) // 2
    if aspect_ratio == "16:9":
        ty = target_h - rotated_txt.height + 40
    else:
        ty = by1 - 10

    canvas.paste(rotated_txt, (tx, ty), rotated_txt)

    # 8. Final Polish & Save
    final_rgb = canvas.convert("RGB")
    final_rgb.save(str(out_p), format="JPEG", quality=95, subsampling=0)
    return str(out_p)

# Backward-compatibility alias
generate_pro_thumbnail = generate_creator_thumbnail
