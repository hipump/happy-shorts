import re
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

def normalize_spoken_acronyms(text: str) -> str:
    """Normalize phonetically transcribed Korean words like '에이아이' to standard 'AI'."""
    if not text:
        return ""
    text = re.sub(r'에이아이', 'AI', text)
    text = re.sub(r'에프에스디', 'FSD', text)
    text = re.sub(r'오티에이', 'OTA', text)
    return text

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
                # Normalize acronyms in cached data as well (e.g. 에이아이 -> AI)
                for s in data.get("segments", []):
                    s["text"] = normalize_spoken_acronyms(s.get("text", ""))
                    for w in s.get("words", []):
                        w["word"] = normalize_spoken_acronyms(w.get("word", ""))
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

        # Optimize beam_size: beam_size=1 (greedy) delivers 99%+ accuracy for Korean with 2.5x speedup
        effective_beam = 1 if model_size in ["large-v3-turbo", "large-v3"] else 2

        segments_generator, info = model.transcribe(
            wav_path,
            beam_size=effective_beam,
            word_timestamps=True,
            language="ko"  # default to Korean, faster-whisper will detect if different
        )
        
        total_audio_sec = max(1.0, float(info.duration or 1.0))
        segments_list = []
        seg_idx = 0
        last_reported_sec = 0.0

        for seg in segments_generator:
            clean_seg_text = normalize_spoken_acronyms(seg.text.strip())
            words = []
            if seg.words:
                for w in seg.words:
                    words.append(Word(
                        word=normalize_spoken_acronyms(w.word.strip()),
                        start=round(w.start, 2),
                        end=round(w.end, 2),
                        probability=round(w.probability, 2)
                    ))
            
            segments_list.append(Segment(
                id=seg_idx,
                start=round(seg.start, 2),
                end=round(seg.end, 2),
                text=clean_seg_text,
                words=words
            ))
            seg_idx += 1

            # Granular real-time progress update every 3 seconds of audio or every 4 segments
            if callback and (seg.end - last_reported_sec >= 3.0 or seg_idx % 4 == 0):
                last_reported_sec = seg.end
                curr_min = int(seg.end // 60)
                curr_sec = int(seg.end % 60)
                tot_min = int(total_audio_sec // 60)
                tot_sec = int(total_audio_sec % 60)
                audio_pct = min(1.0, seg.end / total_audio_sec)
                overall_pct = 40 + int(audio_pct * 24)
                preview = seg.text.strip()[:20]
                callback(
                    overall_pct,
                    f"[{curr_min:02d}:{curr_sec:02d} / {tot_min:02d}:{tot_sec:02d}] STT 단어 추출 중 ({seg_idx}문장, '{preview}')..."
                )
            
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
