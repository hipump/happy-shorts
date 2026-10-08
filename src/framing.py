import os
from pathlib import Path
from typing import Tuple, Optional

CASCADE_PATH = Path("assets/models/haarcascade_frontalface_default.xml")

def detect_face_center_x(
    video_path: str,
    start_time: float,
    end_time: float,
    sample_interval: float = 1.0
) -> Optional[int]:
    """
    Sample video frames within [start_time, end_time] and find the
    dominant face horizontal center coordinate.
    """
    if not CASCADE_PATH.exists():
        return None

    import cv2
    import numpy as np

    face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    centers_x = []

    curr_time = start_time
    while curr_time <= end_time:
        frame_idx = int(curr_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        if len(faces) > 0:
            # Pick largest face
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            fx, fy, fw, fh = largest_face
            centers_x.append(fx + fw // 2)

        curr_time += sample_interval

    cap.release()

    if centers_x:
        return int(np.median(centers_x))
    return None

def build_framing_filter(
    layout_mode: str,
    orig_width: int,
    orig_height: int,
    video_path: str,
    start_time: float,
    end_time: float
) -> Tuple[str, str]:
    """
    Build FFmpeg video filtergraph string for 9:16 layout.
    Returns: (filter_str, final_label)
    """
    if layout_mode == "blur_background":
        # Professional standard: Blurred 9:16 background + sharp centered 16:9 foreground
        vf = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=25:5,eq=brightness=-0.12[bg];"
            "[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
        )
        return vf, "base"

    elif layout_mode == "smart_crop":
        # Compute face center
        face_x = detect_face_center_x(video_path, start_time, end_time)
        crop_w = int(orig_height * 9 / 16)
        crop_w = min(crop_w, orig_width)

        if face_x is not None:
            x = int(face_x - crop_w / 2)
            x = max(0, min(orig_width - crop_w, x))
        else:
            x = (orig_width - crop_w) // 2

        vf = f"[0:v]crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[base]"
        return vf, "base"

    elif layout_mode == "center_crop":
        crop_w = int(orig_height * 9 / 16)
        crop_w = min(crop_w, orig_width)
        x = (orig_width - crop_w) // 2
        vf = f"[0:v]crop={crop_w}:{orig_height}:{x}:0,scale=1080:1920[base]"
        return vf, "base"

    else:
        # Default to blur_background
        return build_framing_filter("blur_background", orig_width, orig_height, video_path, start_time, end_time)
