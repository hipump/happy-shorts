import os
import re
import json
import subprocess
from pathlib import Path
from typing import Tuple, Optional
import yt_dlp
from src.models import VideoMetadata

DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

def extract_youtube_id(source: str) -> Optional[str]:
    """
    Extract 11-character YouTube video ID handling shell escapes, file paths, and various URL formats.
    """
    clean = source.strip().strip("'\"")
    for ch in ["?", "=", "&", "#", "%"]:
        clean = clean.replace(f"\\{ch}", ch)

    candidates = [clean, Path(clean).stem]
    patterns = [
        r'(?:v=|\/v\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for c in candidates:
        for p in patterns:
            m = re.search(p, c)
            if m:
                return m.group(1)
    return None

def is_youtube_url(source: str) -> bool:
    return extract_youtube_id(source) is not None

def get_video_info_ffprobe(file_path: str) -> Tuple[float, int, int, float]:
    """Extract duration, width, height, fps using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration:format=duration",
        "-of", "json",
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    data = json.loads(result.stdout)
    
    stream = data.get("streams", [{}])[0]
    fmt = data.get("format", {})
    
    duration = float(stream.get("duration") or fmt.get("duration") or 0.0)
    width = int(stream.get("width", 1920))
    height = int(stream.get("height", 1080))
    
    r_frame_rate = stream.get("r_frame_rate", "30/1")
    if "/" in r_frame_rate:
        num, den = r_frame_rate.split("/")
        fps = float(num) / max(float(den), 1.0)
    else:
        fps = float(r_frame_rate) if r_frame_rate else 30.0
        
    return duration, width, height, fps

def prepare_source(source: str) -> VideoMetadata:
    """Download video if URL or validate local file, returning VideoMetadata."""
    video_id = extract_youtube_id(source)

    if video_id:
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
        expected_mp4 = DOWNLOADS_DIR / f"{video_id}.mp4"

        # Check if already downloaded
        title = f"YouTube_{video_id}"
        if expected_mp4.exists() and expected_mp4.stat().st_size > 1024:
            local_path = str(expected_mp4)
        else:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                'outtmpl': str(DOWNLOADS_DIR / f'{video_id}.%(ext)s'),
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'quiet': False,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                title = info.get('title', title)

            local_path = str(expected_mp4)
            # If for some reason extension is not mp4, check folder
            if not os.path.exists(local_path):
                candidates = list(DOWNLOADS_DIR.glob(f"{video_id}.*"))
                if candidates:
                    local_path = str(candidates[0])

        duration, width, height, fps = get_video_info_ffprobe(local_path)

        return VideoMetadata(
            source=clean_url,
            is_url=True,
            title=title,
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            local_path=local_path
        )
    else:
        clean_path = source.strip().strip("'\"")
        local_path = os.path.abspath(clean_path)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"로컬 비디오 파일을 찾을 수 없습니다: {local_path}")
            
        title = Path(local_path).stem
        duration, width, height, fps = get_video_info_ffprobe(local_path)
        
        return VideoMetadata(
            source=source,
            is_url=False,
            title=title,
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            local_path=local_path
        )
