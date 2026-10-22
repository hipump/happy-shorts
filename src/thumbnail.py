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
        elif style == "gold_gloss":
            r = int(255 - ratio * 35)
            g = int(235 - ratio * 110)
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

def add_atmospheric_fx(canvas_rgba: Image.Image, banner_y1: int) -> Image.Image:
    """
    Adds cinematic floating ember sparks and warm light rays.
    """
    w, h = canvas_rgba.size
    embers = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    edraw = ImageDraw.Draw(embers)
    random.seed(42)
    for _ in range(60):
        ex = random.randint(0, w)
        ey = random.randint(max(0, banner_y1 - 120), h - 80)
        er = random.randint(2, 5)
        col = random.choice([(255, 205, 50), (255, 125, 30), (255, 60, 20), (255, 255, 220)])
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
    **kwargs,
) -> str:
    """
    3D Blockbuster Viral Thumbnail Renderer:
    - 3-Layer Architecture:
      1. Cinematic background (AI or graded bokeh video frame)
      2. Automated subject cutout (u2net) with multi-layer neon rim glow
      3. 3D Extruded Blockbuster Typography with -3.5° dynamic slant & red splatter banner
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
        # Fallback to frame 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError(f"Failed to capture frame at {sample_time}s from {target_video}")

    raw_frame_rgb = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # 3. Create Layer 1: Background
    if ai_bg_path and Path(ai_bg_path).exists():
        ai_bg = Image.open(ai_bg_path).convert("RGBA").resize((target_w, target_h), Image.Resampling.LANCZOS)
        # Apply slight contrast enhance and lower vignette
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

    # 4. Create Layer 2: Subject Cutout & Rim Light
    cutout = extract_subject_cutout(raw_frame_rgb)
    if cutout is not None:
        if aspect_ratio == "16:9":
            # In 16:9, scale subject to 65% height, align to right-center
            scale = (target_h * 0.90) / cutout.height
            nw = int(cutout.width * scale)
            nh = int(cutout.height * scale)
            cutout_resized = cutout.resize((nw, nh), Image.Resampling.LANCZOS)
            px = target_w - nw - 40
            py = target_h - nh
        else:
            # In 9:16, scale subject to fill upper body (1.62x width), center horizontally
            scale = (target_w * 1.62) / cutout.width
            nw = int(cutout.width * scale)
            nh = int(cutout.height * scale)
            cutout_resized = cutout.resize((nw, nh), Image.Resampling.LANCZOS)
            px = (target_w - nw) // 2
            py = 310

        rim_color = (60, 200, 255) if (virality_score or 0) >= 80 else (255, 180, 50)
        canvas = apply_rim_light(canvas, cutout_resized, px, py, rim_color=rim_color)

    # 5. Create Layer 3: Crimson Grunge Slash Banner & Atmospheric Sparks
    if aspect_ratio == "16:9":
        by1 = target_h - 220
        by2 = target_h - 30
        banner = draw_grunge_slash_banner(target_w, target_h, by1, by2, color=(190, 10, 20), angle_offset=30)
    else:
        by1 = 1010
        by2 = 1490
        banner = draw_grunge_slash_banner(target_w, target_h, by1, by2, color=(195, 15, 28), angle_offset=45)

    canvas = Image.alpha_composite(canvas, banner)
    canvas = add_atmospheric_fx(canvas, by1)

    # 6. Create Layer 4: 3D Blockbuster Typography
    part1, part2 = parse_blockbuster_phrases(title, hook_text)

    font_size_1 = 92 if aspect_ratio == "16:9" else 125
    font_size_2 = 82 if aspect_ratio == "16:9" else 115
    font1 = get_thumbnail_font(font_size_1, prefer_black_han=True)
    font2 = get_thumbnail_font(font_size_2, prefer_black_han=True)

    txt_canvas_w = target_w + 350
    txt_canvas_h = 350 if aspect_ratio == "16:9" else 550
    txt_img = Image.new("RGBA", (txt_canvas_w, txt_canvas_h), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(txt_img)

    if aspect_ratio == "16:9":
        # 16:9 Layout: Horizontal side-by-side
        bbox1 = tdraw.textbbox((0, 0), part1, font=font1)
        w1 = bbox1[2] - bbox1[0]
        bbox2 = tdraw.textbbox((0, 0), f" {part2}", font=font2)
        w2 = bbox2[2] - bbox2[0]
        total_w = w1 + w2

        sx = (txt_canvas_w - total_w) // 2
        sy = 70
        # Part 1: Ruby Metallic Gloss with White Inner Stroke
        render_graphic_text_block(txt_img, part1, font1, sx, sy, style="ruby_gloss", depth=18, inner_stroke_color=(255, 255, 255))
        # Part 2: Distressed Concrete Weathered
        render_graphic_text_block(txt_img, f" {part2}", font2, sx + w1 + 10, sy, style="concrete_weathered", depth=18, inner_stroke_color=(20, 20, 20))
    else:
        # 9:16 Layout: Two stacked lines
        bbox1 = tdraw.textbbox((0, 0), part1, font=font1)
        w1 = bbox1[2] - bbox1[0]
        sx1 = (txt_canvas_w - w1) // 2
        # Line 1: Gold Metallic Gloss with White Inner Stroke
        render_graphic_text_block(txt_img, part1, font1, sx1, 40, style="gold_gloss", depth=22, inner_stroke_color=(255, 255, 255))

        bbox2 = tdraw.textbbox((0, 0), part2, font=font2)
        w2 = bbox2[2] - bbox2[0]
        sx2 = (txt_canvas_w - w2) // 2
        # Line 2: Distressed Concrete Weathered with Black 3D
        render_graphic_text_block(txt_img, part2, font2, sx2, 220, style="concrete_weathered", depth=22, inner_stroke_color=(20, 20, 20))

    # Rotate text canvas by -3.5 degrees (positive angle for clockwise tilt)
    rotated_txt = txt_img.rotate(3.5, resample=Image.Resampling.BICUBIC, expand=True)

    tx = (target_w - rotated_txt.width) // 2
    if aspect_ratio == "16:9":
        ty = target_h - rotated_txt.height + 40
    else:
        ty = by1 - 10

    canvas.paste(rotated_txt, (tx, ty), rotated_txt)

    # 7. Final Polish & Save
    final_rgb = canvas.convert("RGB")
    final_rgb.save(str(out_p), format="JPEG", quality=95, subsampling=0)
    return str(out_p)

# Backward-compatibility alias
generate_pro_thumbnail = generate_creator_thumbnail
