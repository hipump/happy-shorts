import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.templates import TEMPLATES, get_template
from src.models import Highlight, VideoMetadata
from src.effects import (
    render_template_background,
    get_font,
    FONT_BLACK_HAN_SANS,
    FONT_PRETENDARD,
)
from src.framing import OVERLAY_LAYOUTS

OUTPUT_DIR = Path("web/public/templates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = Path("assets/templates")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = Path("temp/preview_gen")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_FRAME_PATH = Path("assets/source_frame_16x9.jpg")

SAMPLE_HIGHLIGHT = Highlight(
    id=1,
    title="테슬라 오너 7년차가 알려주는 필수 세팅",
    hook_text="출고 전 필수 세팅 10가지 총정리!",
    start_time=15.0,
    end_time=30.0,
    viral_score=94,
    summary_points=[
        "테슬라 모델Y/3 인도 전 필수 확인 설정",
        "비프음 3번 대기 후 트렁크 높이 조절 가이드",
        "핸즈프리 워크어웨이 도어락 세팅 팁"
    ]
)

SAMPLE_METADATA = VideoMetadata(
    video_id="WiFTZW0cp8g",
    title="테슬라 백과사전 출고 꿀팁",
    duration=600,
    width=1920,
    height=1080,
    local_path=str(SOURCE_FRAME_PATH),
    source="YouTube",
    is_url=True
)

def generate_wysiwyg_preview(template_id: str):
    tmpl = get_template(template_id)
    canvas_w, canvas_h = 1080, 1920

    # 1. Render true pipeline template background
    bg_path = str(TEMP_DIR / f"{template_id}_bg.png")
    render_template_background(
        template=tmpl,
        highlight=SAMPLE_HIGHLIGHT,
        metadata=SAMPLE_METADATA,
        output_path=bg_path,
        canvas_w=canvas_w,
        canvas_h=canvas_h
    )

    bg_img = Image.open(bg_path).convert("RGBA")
    src_img = Image.open(str(SOURCE_FRAME_PATH)).convert("RGBA")

    # 2. Composite video frame according to framing rules
    if tmpl.layout_type in OVERLAY_LAYOUTS or tmpl.layout_type in ["smart_crop", "interview_talk"]:
        # 9:16 Center Crop of source video
        sw, sh = src_img.size
        cw = int(sh * 9 / 16)
        cx = max(0, (sw - cw) // 2)
        crop_v = src_img.crop((cx, 0, cx + cw, sh)).resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        # Overlay template graphic on top of 9:16 video
        final_canvas = Image.alpha_composite(crop_v, bg_img)

    elif tmpl.layout_type == "blur_background":
        # Blurred background + center video
        blurred_bg = src_img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(30))
        # Center 16:9
        vw = 1080
        vh = int(vw * 9 / 16)
        scaled_v = src_img.resize((vw, vh), Image.Resampling.LANCZOS)
        final_canvas = blurred_bg
        vy = (canvas_h - vh) // 2
        final_canvas.paste(scaled_v, (0, vy))
        final_canvas = Image.alpha_composite(final_canvas, bg_img)

    else:
        # Boxed frame templates (news_portal, browser_window, ranking_chart, etc.)
        final_canvas = bg_img
        vx, vy, vw, vh = tmpl.video_box
        scaled_v = src_img.resize((vw, vh), Image.Resampling.LANCZOS)
        final_canvas.paste(scaled_v, (vx, vy))

        # Add crisp border around video box
        draw = ImageDraw.Draw(final_canvas)
        draw.rounded_rectangle([vx - 2, vy - 2, vx + vw + 2, vy + vh + 2], radius=14, outline=(25, 30, 40), width=3)

    # 3. Render Sample Subtitles if template supports subtitles
    if tmpl.subtitle_y > 0 and tmpl.subtitle_style != "none":
        sub_font_file = FONT_BLACK_HAN_SANS if tmpl.font_name == "black_han_sans" else FONT_PRETENDARD
        f_sub = get_font(sub_font_file, 40)
        draw = ImageDraw.Draw(final_canvas)
        sub_text = "출고 앞두신 분들, 이 설정 꼭 하세요!"
        sy = tmpl.subtitle_y

        # Subtitle pill badge
        tb = f_sub.getbbox(sub_text)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        pad_x = 28
        pad_y = 16

        # In overlay layouts, draw a semi-transparent dark pill background for readability
        if tmpl.layout_type in OVERLAY_LAYOUTS or tmpl.layout_type == "smart_crop":
            draw.rounded_rectangle(
                [540 - tw // 2 - pad_x, sy - th // 2 - pad_y, 540 + tw // 2 + pad_x, sy + th // 2 + pad_y],
                radius=18,
                fill=(12, 16, 22, 220),
                outline=(50, 60, 80, 180),
                width=2
            )

        # Kinetic highlighted word simulation
        draw.text(
            (540, sy),
            sub_text,
            font=f_sub,
            fill=tmpl.active_color,
            stroke_width=4,
            stroke_fill=(0, 0, 0),
            anchor="mm"
        )

    # 4. Save 100% WYSIWYG image to web/public and assets
    out_jpg = OUTPUT_DIR / f"{template_id}.jpg"
    final_canvas.convert("RGB").save(str(out_jpg), "JPEG", quality=92)

    asset_jpg = ASSETS_DIR / f"{template_id}.jpg"
    shutil.copy(str(out_jpg), str(asset_jpg))
    print(f"✅ Generated 100% WYSIWYG preview for: {template_id}")

def main():
    print(f"🚀 Generating 100% WYSIWYG pipeline previews for {len(TEMPLATES)} templates...")
    for t_id in TEMPLATES.keys():
        generate_wysiwyg_preview(t_id)
    print("✨ All previews generated successfully!")

if __name__ == "__main__":
    main()
