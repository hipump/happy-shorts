import os
from pathlib import Path
from typing import Tuple, Optional

CASCADE_PATH = Path("assets/models/haarcascade_frontalface_default.xml")
YUNET_PATH = Path("assets/models/face_detection_yunet_2023mar.onnx")

def detect_face_center_x(
    video_path: str,
    start_time: float,
    end_time: float,
    sample_interval: float = 1.0
) -> Optional[int]:
    """
    Sample video frames within [start_time, end_time] and find the
    dominant face horizontal center coordinate using YuNet (OpenCV DNN) or Haar Cascade fallback.
    """
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    centers_x = []

    try:
        # Priority 1: YuNet Deep Learning Detector (Fast & High Accuracy)
        if YUNET_PATH.exists() and hasattr(cv2, "FaceDetectorYN"):
            try:
                detector = cv2.FaceDetectorYN.create(
                    str(YUNET_PATH), "", (640, 360), score_threshold=0.6
                )
                curr_time = start_time
                while curr_time <= end_time:
                    frame_idx = int(curr_time * fps)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    if not ret:
                        break

                    h, w, _ = frame.shape
                    detector.setInputSize((w, h))
                    _, faces = detector.detect(frame)
                    if faces is not None and len(faces) > 0:
                        largest = max(faces, key=lambda f: f[2] * f[3])
                        fx, fy, fw, fh = largest[0:4].astype(int)
                        centers_x.append(fx + fw // 2)

                    curr_time += sample_interval

                if centers_x:
                    return int(np.median(centers_x))
            except Exception:
                pass

        # Priority 2: Haar Cascade Fallback
        if CASCADE_PATH.exists() and hasattr(cv2, "CascadeClassifier"):
            try:
                face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
                curr_time = start_time
                while curr_time <= end_time:
                    frame_idx = int(curr_time * fps)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    if not ret:
                        break

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
                    )
                    if len(faces) > 0:
                        largest_face = max(faces, key=lambda f: f[2] * f[3])
                        fx, fy, fw, fh = largest_face
                        centers_x.append(fx + fw // 2)

                    curr_time += sample_interval

                if centers_x:
                    return int(np.median(centers_x))
            except Exception:
                pass
    finally:
        if cap.isOpened():
            cap.release()

    return None

OVERLAY_LAYOUTS = {
    "vlog_sticker_lifestyle",
    "vlog_money_salary",
    "promo_fitness_gym",
    "youth_tips_pick",
    "drama_weekly_preview",
    "tesla_fsd_vision",
    "instagram_reels",
    "facetime_call"
}

COLOR_GRADE_PROFILES = {
    # 2026 YouTube Shorts Algorithmic Color Grading Presets (Skin-tone Protected & Crisp)
    "vibrant_tech": "eq=contrast=1.07:brightness=0.01:saturation=1.15,colorbalance=rs=0.012:gs=0.012:bs=-0.008:rm=0.012:gm=0.008:bm=0.015,unsharp=5:5:0.70:5:5:0.25",
    "warm_clean": "eq=contrast=1.05:brightness=0.02:saturation=1.08,colorbalance=rs=0.035:gs=0.012:bs=-0.020:rm=0.025:gm=0.008:bm=-0.015,unsharp=5:5:0.60:5:5:0.20",
    "film_contrast": "eq=contrast=1.12:brightness=-0.015:saturation=1.02,colorbalance=rs=-0.015:gs=0.008:bs=0.030:rh=0.025:gh=0.008:bh=-0.025,unsharp=5:5:0.65:5:5:0.25",
    # Backward compatible aliases
    "vibrant": "eq=contrast=1.07:brightness=0.01:saturation=1.15,colorbalance=rs=0.012:gs=0.012:bs=-0.008:rm=0.012:gm=0.008:bm=0.015,unsharp=5:5:0.70:5:5:0.25",
    "cinematic": "eq=contrast=1.12:brightness=-0.015:saturation=1.02,colorbalance=rs=-0.015:gs=0.008:bs=0.030:rh=0.025:gh=0.008:bh=-0.025,unsharp=5:5:0.65:5:5:0.25",
    "clean": "unsharp=5:5:0.65:5:5:0.22",
    "none": "",
}

def build_framing_filter(
    layout_mode: str,
    orig_width: int,
    orig_height: int,
    video_path: str,
    start_time: float,
    end_time: float,
    video_box: Optional[Tuple[int, int, int, int]] = None,
    bg_input_idx: int = 1,
    enable_punch_in_zoom: bool = True,
    aspect_ratio: str = "9:16",
    remove_subtitles: bool = False,
    color_grade: str = "vibrant"
) -> Tuple[str, str]:
    """
    Build FFmpeg video filtergraph string for 9:16 or 16:9 layout.
    Supports:
    - Aspect Ratio: "9:16" (1080x1920) or "16:9" (1920x1080)
    - Face tracking center adjustment for horizontal (16:9) sources converted to 9:16
    - Source burned-in subtitle removal via spatial delogo inpainting
    - Studio Color Grading & Sharpening (Vibrant, Cinematic, Clean)
    - Dynamic Punch-in Zoom (Submagic-style 1.10x focal zoom during middle explanation)
    - Graphic template placement (video_box: vx, vy, vw, vh onto template background)
    - Fullscreen Overlay templates (video smart-cropped with transparent HUD/Stickers overlay)
    - smart_crop (AI face tracking)
    - blur_background (box-blurred video backdrop)
    - studio_card (floating card fallback)
    Returns: (filter_str, final_label)
    """
    dur = max(1.0, end_time - start_time)
    z_start = round(min(4.5, dur * 0.22), 2)
    z_end = round(max(z_start + 3.0, dur * 0.70), 2)

    # 1. Source burned-in subtitle removal (delogo inpainting filter)
    delogo_prefix = ""
    v_in = "[0:v]"
    if remove_subtitles:
        if orig_width > orig_height:
            # Horizontal source: subtitle band is typically at bottom 16% (y: 78% ~ 94%)
            sub_x = int(orig_width * 0.10)
            sub_w = int(orig_width * 0.80)
            sub_y = int(orig_height * 0.78)
            sub_h = int(orig_height * 0.16)
        else:
            # Vertical source: subtitle band is typically at y: 72% ~ 87%
            sub_x = int(orig_width * 0.06)
            sub_w = int(orig_width * 0.88)
            sub_y = int(orig_height * 0.72)
            sub_h = int(orig_height * 0.15)

        # Ensure even coordinates for YUV chroma alignment
        sub_x = max(0, sub_x - (sub_x % 2))
        sub_y = max(0, sub_y - (sub_y % 2))
        sub_w = max(10, min(orig_width - sub_x, sub_w - (sub_w % 2)))
        sub_h = max(10, min(orig_height - sub_y, sub_h - (sub_h % 2)))

        delogo_prefix = f"[0:v]delogo=x={sub_x}:y={sub_y}:w={sub_w}:h={sub_h}[v_nosub];"
        v_in = "[v_nosub]"

    # 2. Studio Color Grading & Crisp Sharpening
    cg_prefix = ""
    cg_filter = COLOR_GRADE_PROFILES.get(str(color_grade).lower().strip(), "")
    if cg_filter:
        cg_prefix = f"{v_in}{cg_filter}[v_graded];"
        v_in = "[v_graded]"

    filter_prep = f"{delogo_prefix}{cg_prefix}"

    # 3. Dynamic Rhythmic Punch-in Zoom (CapCut/Submagic-style rhythmic focus cuts)
    zoom_filter = ""
    if enable_punch_in_zoom and dur >= 6.5:
        if dur >= 15.0:
            # Multi-beat dynamic rhythm: alternates between normal and 1.09x focal punch
            p1_end = round(min(7.5, dur * 0.32), 2)
            p2_start = round(max(p1_end + 3.5, dur * 0.44), 2)
            p2_end = round(min(p2_start + 6.0, dur * 0.72), 2)
            p3_start = round(max(p2_end + 3.5, dur * 0.80), 2)
            p3_end = round(max(p3_start + 3.0, dur - 0.5), 2)

            zoom_cond = f"(between(t,2.2,{p1_end})+between(t,{p2_start},{p2_end})"
            if dur >= 26.0:
                zoom_cond += f"+between(t,{p3_start},{p3_end})"
            zoom_cond += ")"
            zoom_filter = f"crop='if(gt({zoom_cond},0),2*trunc(iw/2.18),iw)':'if(gt({zoom_cond},0),2*trunc(ih/2.18),ih)':(iw-ow)/2:(ih-oh)/2,"
        else:
            z_start = round(min(3.5, dur * 0.22), 2)
            z_end = round(max(z_start + 3.0, dur * 0.75), 2)
            zoom_filter = f"crop='if(between(t,{z_start},{z_end}),2*trunc(iw/2.18),iw)':'if(between(t,{z_start},{z_end}),2*trunc(ih/2.18),ih)':(iw-ow)/2:(ih-oh)/2,"

    # 3. 16:9 Landscape Video Canvas (1920x1080)
    if aspect_ratio == "16:9":
        if orig_width >= orig_height:
            # Source is already horizontal: scale directly to 1920x1080 without cutting sides
            vf = (
                f"{filter_prep}"
                f"{v_in}{zoom_filter}scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black[base]"
            )
            return vf, "base"
        else:
            # Source is vertical (9:16): center vertical video on blurred 1920x1080 background
            vf = (
                f"{filter_prep}"
                f"{v_in}scale=1920:1080:force_original_aspect_ratio=increase,"
                f"crop=1920:1080,boxblur=30:8,eq=brightness=-0.16:contrast=1.06[bg];"
                f"{v_in}{zoom_filter}scale=-2:1080:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:0[base]"
            )
            return vf, "base"

    # 4. 9:16 Vertical Shorts Canvas (1080x1920)
    # Fullscreen Overlay Templates (9:16 Smart Crop Video + Floating Stickers/HUD on top)
    if layout_mode in OVERLAY_LAYOUTS:
        face_x = detect_face_center_x(video_path, start_time, end_time)
        crop_w = int(orig_height * 9 / 16)
        crop_w = min(crop_w, orig_width)

        if face_x is not None:
            x = int(face_x - crop_w / 2)
            x = max(0, min(orig_width - crop_w, x))
        else:
            x = (orig_width - crop_w) // 2

        vf = (
            f"{filter_prep}"
            f"{v_in}{zoom_filter}crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[v_base];"
            f"[v_base][{bg_input_idx}:v]overlay=0:0[base]"
        )
        return vf, "base"

    # Boxed Window Templates (Video placed into a specified canvas coordinate)
    if video_box is not None and layout_mode not in ["smart_crop", "blur_background"]:
        vx, vy, vw, vh = video_box
        vf = (
            f"{filter_prep}"
            f"{v_in}{zoom_filter}scale={vw}:{vh}:force_original_aspect_ratio=decrease,"
            f"pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:color=black,format=rgba[fg];"
            f"[{bg_input_idx}:v][fg]overlay={vx}:{vy}[base]"
        )
        return vf, "base"

    if layout_mode == "smart_crop":
        face_x = detect_face_center_x(video_path, start_time, end_time)
        crop_w = int(orig_height * 9 / 16)
        crop_w = min(crop_w, orig_width)

        if face_x is not None:
            x = int(face_x - crop_w / 2)
            x = max(0, min(orig_width - crop_w, x))
        else:
            x = (orig_width - crop_w) // 2

        vf = f"{filter_prep}{v_in}{zoom_filter}crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[base]"
        return vf, "base"

    elif layout_mode == "blur_background":
        vf = (
            f"{filter_prep}"
            f"{v_in}scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,boxblur=30:8,eq=brightness=-0.16:contrast=1.06[bg];"
            f"{v_in}{zoom_filter}scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
        )
        return vf, "base"

    elif layout_mode == "studio_card":
        card_w = 1000
        card_h = int(card_w * 9 / 16)  # 562
        vf = (
            f"{filter_prep}"
            f"color=c=0x0B0D14:s=1080x1920[canvas];"
            f"{v_in}scale={card_w}:{card_h}:force_original_aspect_ratio=decrease,format=rgba[fg];"
            f"[canvas][fg]overlay=(W-w)/2:520[base]"
        )
        return vf, "base"

    else:
        # Default fallback: smart crop centering on face if horizontal source
        face_x = detect_face_center_x(video_path, start_time, end_time)
        crop_w = int(orig_height * 9 / 16)
        crop_w = min(crop_w, orig_width)
        if face_x is not None:
            x = int(face_x - crop_w / 2)
            x = max(0, min(orig_width - crop_w, x))
        else:
            x = (orig_width - crop_w) // 2

        vf = f"{filter_prep}{v_in}{zoom_filter}crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[base]"
        return vf, "base"


