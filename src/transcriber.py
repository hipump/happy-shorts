import os
import json
import hashlib
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel
from src.models import Transcript, Segment, Word

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def get_audio_cache_key(file_path: str) -> str:
    stat = os.stat(file_path)
    content = f"{file_path}_{stat.st_size}_{stat.st_mtime}"
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def extract_audio(video_path: str, output_wav: str) -> str:
    """Extract 16kHz mono WAV audio from video using FFmpeg."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_wav

def transcribe_video(
    video_path: str,
    model_size: str = "large-v3-turbo",
    device: str = "cpu",
    compute_type: str = "int8",
    callback=None
) -> Transcript:
    """
    Transcribe video using faster-whisper with word-level timestamps.
    Results are cached to disk so re-runs are instantaneous.
    """
    cache_key = get_audio_cache_key(video_path)
    cache_file = CACHE_DIR / f"{cache_key}_{model_size}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if callback:
                    callback(62, f"기존 음성 인식(STT) 캐시 불러오기 완료 ({len(data.get('segments', []))}개 발화)")
                return Transcript(**data)
        except Exception:
            pass

    # Extract audio
    if callback:
        callback(32, "고음질 16kHz 모노 오디오 트랙 추출 중...")
    wav_path = str(TEMP_DIR / f"{cache_key}.wav")
    extract_audio(video_path, wav_path)

    try:
        # Load faster-whisper model
        if callback:
            callback(36, f"Faster-Whisper ({model_size}) 음성 모델 로드 중...")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        if callback:
            callback(40, "단어 단위 정밀 타임스탬프 추출 시작...")

        segments_generator, info = model.transcribe(
            wav_path,
            beam_size=5,
            word_timestamps=True,
            language="ko"  # default to Korean, faster-whisper will detect if different
        )
        
        total_audio_sec = max(1.0, float(info.duration or 1.0))
        segments_list = []
        seg_idx = 0
        last_pct = 40

        for seg in segments_generator:
            words = []
            if seg.words:
                for w in seg.words:
                    words.append(Word(
                        word=w.word.strip(),
                        start=round(w.start, 2),
                        end=round(w.end, 2),
                        probability=round(w.probability, 2)
                    ))
            
            segments_list.append(Segment(
                id=seg_idx,
                start=round(seg.start, 2),
                end=round(seg.end, 2),
                text=seg.text.strip(),
                words=words
            ))
            seg_idx += 1
            
        transcript = Transcript(
            language=info.language,
            duration=round(info.duration, 2),
            segments=segments_list
        )
        
        # Save cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)

        return transcript
    finally:
        # Clean up temp wav
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass
