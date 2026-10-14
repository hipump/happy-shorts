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

            cap.release()
            if centers_x:
                return int(np.median(centers_x))
            return None
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

            cap.release()
            if centers_x:
                return int(np.median(centers_x))
        except Exception:
            pass

    if cap.isOpened():
        cap.release()
    return None

OVERLAY_LAYOUTS = {
    "vlog_sticker_lifestyle",
    "vlog_money_salary",
    "promo_fitness_gym",
    "youth_tips_pick",
    "drama_weekly_preview",
    "tesla_fsd_vision"
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
    enable_punch_in_zoom: bool = True
) -> Tuple[str, str]:
    """
    Build FFmpeg video filtergraph string for 9:16 layout.
    Supports:
    - Graphic template placement (video_box: vx, vy, vw, vh onto template background)
    - Fullscreen Overlay templates (video smart-cropped to 9:16 with transparent HUD/Stickers overlay)
    - Dynamic Punch-in Zoom (Submagic-style 1.10x focal zoom during middle explanation)
    - smart_crop (AI face tracking 9:16)
    - blur_background (box-blurred video backdrop)
    - studio_card (floating card fallback)
    Returns: (filter_str, final_label)
    """
    dur = max(1.0, end_time - start_time)
    z_start = round(dur * 0.25, 1)
    z_end = round(dur * 0.65, 1)
    # 1.10x center punch-in zoom during middle climax (if enabled and clip >= 15s)
    zoom_filter = ""
    if enable_punch_in_zoom and dur >= 15.0:
        zoom_filter = f"crop='if(between(t,{z_start},{z_end}),iw/1.10,iw)':'if(between(t,{z_start},{z_end}),ih/1.10,ih)':(iw-ow)/2:(ih-oh)/2,"

    # 1. Fullscreen Overlay Templates (9:16 Smart Crop Video + Floating Stickers/HUD on top)
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
            f"[0:v]{zoom_filter}crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[v_base];"
            f"[v_base][{bg_input_idx}:v]overlay=0:0[base]"
        )
        return vf, "base"

    # 2. Boxed Window Templates (Video placed into a specified canvas coordinate)
    if video_box is not None and layout_mode not in ["smart_crop", "blur_background"]:
        vx, vy, vw, vh = video_box
        # Scale to fit box preserving aspect ratio, pad with black if needed
        vf = (
            f"[0:v]{zoom_filter}scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:color=black,format=rgba[fg];"
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

        vf = f"[0:v]{zoom_filter}crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[base]"
        return vf, "base"

    elif layout_mode == "blur_background":
        vf = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=30:8,eq=brightness=-0.16:contrast=1.06[bg];"
            f"[0:v]{zoom_filter}scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
        )
        return vf, "base"

    elif layout_mode == "studio_card":
        card_w = 1000
        card_h = int(card_w * 9 / 16)  # 562
        vf = (
            f"color=c=0x0B0D14:s=1080x1920[canvas];"
            f"[0:v]scale={card_w}:{card_h}:force_original_aspect_ratio=decrease,format=rgba[fg];"
            f"[canvas][fg]overlay=(W-w)/2:520[base]"
        )
        return vf, "base"

    else:
        # Default fallback to center crop
        crop_w = int(orig_height * 9 / 16)
        crop_w = min(crop_w, orig_width)
        x = (orig_width - crop_w) // 2
        vf = f"[0:v]{zoom_filter}crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[base]"
        return vf, "base"


