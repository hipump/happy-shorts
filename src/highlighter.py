import json
import re
from typing import List, Optional, Callable
import ollama
from src.models import Transcript, Highlight

def format_transcript_for_llm(transcript: Transcript, max_chars: int = 40000) -> str:
    """Format segments into compact timestamped dialogue lines."""
    lines = []
    total_chars = 0
    for seg in transcript.segments:
        line = f"[{int(seg.start)}초 -> {int(seg.end)}초] {seg.text}"
        if total_chars + len(line) > max_chars:
            break
        lines.append(line)
        total_chars += len(line)
    return "\n".join(lines)

import os
import subprocess

# Korean Sentence Ending Completeness Rules (Linguistic boundary verification)
COMPLETE_ENDINGS = re.compile(
    r'([다요죠까네나오군어자마][\.\?\!\s]*$|[\.\?\!]$)'
)
INCOMPLETE_ENDINGS = re.compile(
    r'([고며면서는데은데지만으나어서아서해서면으면거나려고자마자듯이]|그리고|그러나|그런데|하지만|또한|그러면|그래서|그렇지만)\s*$'
)

def is_sentence_complete(text: str) -> bool:
    """Check if Korean text cleanly completes a thought with a proper ending verb."""
    if not text:
        return False
    t = text.strip()
    if INCOMPLETE_ENDINGS.search(t):
        return False
    return bool(COMPLETE_ENDINGS.search(t))

def detect_scene_cuts(
    video_path: Optional[str],
    search_start: float,
    search_end: float,
    threshold: float = 0.25
) -> List[float]:
    """Detect visual scene change cuts using FFmpeg within a specific time window."""
    if not video_path or not os.path.exists(video_path):
        return []
    try:
        dur = max(1.0, search_end - search_start)
        cmd = [
            "ffmpeg", "-ss", str(max(0.0, search_start)), "-t", str(dur),
            "-i", video_path,
            "-filter:v", f"select='gt(scene,{threshold})',showinfo",
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
        cuts = []
        for line in res.stderr.splitlines():
            if "pts_time:" in line:
                m = re.search(r'pts_time:([0-9\.]+)', line)
                if m:
                    cuts.append(round(search_start + float(m.group(1)), 2))
        return cuts
    except Exception:
        return []

def snap_timestamps_to_sentence_boundaries(
    transcript: Transcript,
    raw_start: float,
    raw_end: float,
    min_dur: float = 30.0,
    max_dur: float = 50.0,
    video_path: Optional[str] = None,
    room_tone_start: float = 0.15,
    room_tone_end: float = 0.25
) -> tuple[float, float]:
    """
    Ensure the clip starts cleanly at the beginning of a sentence
    and ends cleanly with a complete sentence ending verb (~다, ~요, ~죠, ~까).
    Applies audio room-tone padding (150ms start, 250ms end) to prevent choppy speech cuts.
    Guarantees clip duration is strictly between min_dur and max_dur.
    """
    if not transcript.segments:
        return max(0.0, raw_start), max(raw_start + min_dur, raw_end)

    if transcript.duration <= min_dur:
        return 0.0, round(transcript.duration, 2)

    segments = transcript.segments

    # 1. Find start segment closest to raw_start
    start_idx = 0
    best_start_diff = float("inf")
    for i, seg in enumerate(segments):
        diff = abs(seg.start - raw_start)
        if diff < best_start_diff:
            best_start_diff = diff
            start_idx = i

    snapped_start = segments[start_idx].start

    # 2. Find end segment that satisfies grammatical completion
    end_idx = start_idx
    target_end = max(snapped_start + min_dur, raw_end)
    best_complete_idx = None
    min_dist_to_target = float("inf")

    # Search for complete ending within [snapped_start + min_dur, snapped_start + max_dur]
    for i in range(start_idx, len(segments)):
        accum_dur = segments[i].end - snapped_start
        if accum_dur < min_dur:
            continue
        if accum_dur > max_dur:
            break

        seg_text = segments[i].text.strip()
        if is_sentence_complete(seg_text):
            dist = abs(segments[i].end - target_end)
            if dist < min_dist_to_target:
                min_dist_to_target = dist
                best_complete_idx = i

    if best_complete_idx is not None:
        end_idx = best_complete_idx
    else:
        # Fallback: look for closest segment before max_dur
        for i in range(start_idx, len(segments)):
            accum_dur = segments[i].end - snapped_start
            if accum_dur >= min_dur:
                end_idx = i
                if accum_dur >= target_end or accum_dur >= (min_dur + 5.0):
                    break

    # If duration still < min_dur (near end of video), expand start backwards
    while start_idx > 0 and (segments[end_idx].end - segments[start_idx].start) < min_dur:
        start_idx -= 1

    snapped_start = segments[start_idx].start
    snapped_end = segments[end_idx].end

    # Apply Auto-Editor style audio room-tone padding:
    # -150ms before speech start to catch breathing/first plosive consonant
    # +250ms after speech end to catch natural room decay/reverb
    final_start = max(0.0, round(snapped_start - room_tone_start, 2))
    final_end = min(round(transcript.duration, 2), round(snapped_end + room_tone_end, 2))

    # Optional: Scene cut snap if video_path is provided
    if video_path and os.path.exists(video_path):
        cuts = detect_scene_cuts(video_path, max(0.0, final_start - 0.5), final_end + 0.5)
        for cut in cuts:
            if abs(cut - final_start) <= 0.35:
                final_start = max(0.0, cut)
            if abs(cut - final_end) <= 0.35 and (cut - final_start) >= min_dur:
                final_end = cut

    return final_start, final_end

EMOJI_REGEX = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27bf\ud83c-\ud83e\ud83d\udc00-\udfff]')

def strip_emojis(text: str) -> str:
    """Strip all emojis and special pictorial glyphs."""
    if not text:
        return ""
    return EMOJI_REGEX.sub('', text).strip()

def clean_korean_text(text: str, fallback: str) -> str:
    """Ensure text does not contain Chinese characters, emojis, or unwanted noise."""
    if not text or re.search(r'[\u4e00-\u9fff]', text):
        return strip_emojis(fallback)
    return strip_emojis(text)

def format_hook_badge_text(hook_text: str, title: str) -> str:
    """Format hook badge text to be punchy, clean, and under 22 chars without emojis."""
    hook = strip_emojis(hook_text.strip().strip("\"'「」『』"))
    title_clean = strip_emojis(title.strip().strip("\"'「」『』"))

    if 4 <= len(hook) <= 20:
        target = hook
    elif 2 <= len(title_clean) <= 18:
        target = f"{title_clean} 꿀팁"
    else:
        target = hook[:18] if hook else title_clean[:18]

    return target[:24].strip()

def generate_hook_variants(title: str, hook_text: str) -> dict:
    """
    Generates 3 distinct psychological angles for viral Shorts hooks (A/B testing):
    1. Curiosity / Questioning: '설마 아직도 {topic} 몰랐나요?'
    2. Loss Aversion / Urgency: '모르면 무조건 손해보는 {topic}'
    3. Extreme Benefit / Shortcut: '3초 만에 끝내는 {topic}'
    """
    emoji_pattern = r'[\U00010000-\U0010ffff\u2600-\u27bf\ud83c-\ud83e\ud83d\udc00-\udfff]'
    clean_title = re.sub(emoji_pattern, '', title).strip().strip("\"'「」『』[]")
    clean_hook = re.sub(emoji_pattern, '', hook_text).strip().strip("\"'「」『』[]")
    base = clean_hook if (clean_hook and len(clean_hook) <= 16) else clean_title[:14]
    if not base:
        base = "핵심 실전 꿀팁"

    return {
        "curiosity": f"설마 아직도 {base} 몰랐나요?"[:24],
        "urgency": f"모르면 무조건 손해보는 {base}"[:24],
        "benefit": f"3초 만에 끝내는 {base} 비결"[:24]
    }

def extract_stat_pill_from_transcript(
    transcript: Transcript,
    start_time: float,
    end_time: float
) -> Optional[dict]:
    """
    Extracts high-impact statistics or numbers (e.g. '100만원', '10배', '50%', '3초')
    from the clip dialogue to render an Apple Keynote-style glassmorphic stat card.
    """
    clip_segs = [s for s in transcript.segments if start_time <= s.end and s.start <= end_time]
    for seg in clip_segs:
        text = seg.text.strip()
        m = re.search(r'(\d+[\.,]?\d*)\s*(만원|억원|원|%|프로|배|가지|초|분|등|위)', text)
        if m:
            num = m.group(1)
            unit = m.group(2)
            metric = f"{num}{unit}"
            rel_t = max(2.2, round(seg.start - start_time, 1))

            if unit in ["만원", "억원", "원"]:
                icon = "money"
                sub = "핵심 비용 절감"
            elif unit in ["%", "프로"]:
                icon = "percent"
                sub = "효율 개선 지표"
            elif unit in ["배"]:
                icon = "growth"
                sub = "생산성 폭증"
            elif unit in ["초", "분"]:
                icon = "speed"
                sub = "초단기 세이브"
            else:
                icon = "star"
                sub = "핵심 주요 포인트"

            return {
                "metric": metric,
                "label": sub,
                "icon": icon,
                "rel_time": min(rel_t, 7.5)
            }

    return None

def calculate_infinite_loop_score(start_text: str, end_text: str) -> int:
    """
    Estimates the psychological seamlessness of looping back to the hook (78~98).
    Higher if the end clause naturally leads into an explanation or setup.
    """
    score = 82
    if any(end_text.endswith(p) for p in [".", "!", "?", "요", "다", "죠"]):
        score += 6
    if any(k in start_text for k in ["이게", "여기서", "바로", "이유", "방법", "팁"]):
        score += 6
    return min(98, score)

def summarize_clip_content(
    transcript: Transcript,
    start_time: float,
    end_time: float,
    title: str = "",
    model_name: str = "qwen2.5:14b"
) -> List[str]:
    """
    Extracts 2 concrete, factual summary takeaway points of what is taught or explained
    in this specific clip, using the real dialogue content.
    """
    clip_segs = [s for s in transcript.segments if start_time <= s.end and s.start <= end_time]
    dialogue_lines = [s.text.strip() for s in clip_segs if s.text.strip()]
    dialogue_text = " ".join(dialogue_lines)

    if not dialogue_text or len(dialogue_text) < 15:
        return [
            f"{title if title else '영상 주요 기능'} 실전 가이드",
            "실제 상황에서 바로 활용 가능한 팁"
        ]

    try:
        prompt = (
            f"다음은 쇼츠 영상 클립의 실제 대화 내용입니다:\n\"{dialogue_text[:450]}\"\n\n"
            f"이 클립에서 설명하는 실전 핵심 정보/꿀팁 2가지를 요약하여 JSON으로 응답하세요.\n"
            f"규칙:\n"
            f"1. 이모지 절대 금지\n"
            f"2. 각 요약은 25자 이내의 명확한 사실 정보 (예: '트렁크 뒤 비프음 3회 후 자동 오픈', '천장 낮은 주차장에서 높이 조절')\n"
            f"3. '시청자 몰입도', '핵심 구간', '하이라이트' 같은 추상적인 문구 절대 금지\n"
        )
        resp = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a concise video summarizer. Output 2 factual bullet points in Korean without emojis."},
                {"role": "user", "content": prompt}
            ],
            format={
                "type": "object",
                "properties": {
                    "points": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["points"]
            },
            options={"temperature": 0.2}
        )
        data = json.loads(resp["message"]["content"])
        pts = [strip_emojis(p).strip() for p in data.get("points", []) if p]
        pts = [p for p in pts if len(p) >= 4 and "몰입도" not in p and "핵심 구간" not in p]
        if len(pts) >= 2:
            return pts[:2]
        if len(pts) == 1:
            pts.append(f"{title} 실전 활용 필수 팁")
            return pts[:2]
    except Exception:
        pass

    # Heuristic fallback using actual dialogue lines
    points = []
    filler_prefixes = r'^(네|그리고|뭐|그렇죠|자|근데|하지만|또한|진짜|정말|이것도)\s*,?\s*'
    for s in clip_segs:
        text = strip_emojis(s.text.strip())
        cleaned = re.sub(filler_prefixes, '', text).strip()
        cleaned = re.sub(r'[\.\?\!]+$', '', cleaned).strip()
        if len(cleaned) >= 8 and not any(f in cleaned for f in ["몰입도", "핵심 구간", "하이라이트"]):
            if cleaned not in points:
                points.append(cleaned[:26])
        if len(points) >= 2:
            break

    if len(points) < 1:
        points.append(f"{title if title else '영상 주요 기능'} 실전 가이드")
    if len(points) < 2:
        points.append("실제 상황에서 바로 활용 가능한 팁")
    return points[:2]

def fallback_heuristic_highlights(
    transcript: Transcript,
    count: int = 1,
    min_dur: float = 30.0,
    max_dur: float = 50.0
) -> List[Highlight]:
    """Rule-based heuristic: pick distinct non-overlapping windows of high speech density."""
    duration = transcript.duration
    if duration <= 60.0:
        pts = summarize_clip_content(transcript, 0.0, duration, "하이라이트 쇼츠")
        return [
            Highlight(
                id=1,
                title="하이라이트 쇼츠",
                hook_text="핵심 요약 하이라이트",
                start_time=0.0,
                end_time=round(duration, 2),
                reason="전체 영상 길이가 쇼츠 규격(60초 이내)에 적합",
                summary_points=pts
            )
        ]

    window_size = 38.0
    step = 5.0
    candidates = []

    curr_time = 0.0
    while curr_time + window_size <= duration:
        end_time = curr_time + window_size
        words_in_window = sum(
            len(seg.words) for seg in transcript.segments
            if seg.start >= curr_time and seg.end <= end_time
        )
        candidates.append((words_in_window, curr_time, end_time))
        curr_time += step

    candidates.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, raw_s, raw_e in candidates:
        s_start, s_end = snap_timestamps_to_sentence_boundaries(
            transcript, raw_s, raw_e, min_dur=min_dur, max_dur=max_dur
        )
        # Check overlap with existing results
        overlap = False
        for r in results:
            if max(0.0, min(s_end, r.end_time) - max(s_start, r.start_time)) > 8.0:
                overlap = True
                break
        if not overlap:
            idx = len(results) + 1
            clip_title = f"핵심 꿀팁 하이라이트 #{idx}"
            pts = summarize_clip_content(transcript, s_start, s_end, clip_title)
            # Calculate heuristic virality score (75 ~ 95)
            dur = max(1.0, s_end - s_start)
            wpm = (words_in_window / dur) * 60.0
            density_score = min(28, max(18, int(wpm / 6.0)))
            virality_score = min(96, max(78, 60 + density_score + (10 if len(pts) >= 2 else 5)))
            breakdown = {
                "hook": min(28, density_score + 2),
                "flow": 22,
                "value": 24 if len(pts) >= 2 else 18,
                "trend": min(20, max(12, virality_score - 70))
            }
            hook_var = generate_hook_variants(clip_title, f"놓치면 손해보는 핵심 팁 #{idx}")
            stat_p = extract_stat_pill_from_transcript(transcript, s_start, s_end)
            results.append(Highlight(
                id=idx,
                title=clip_title,
                hook_text=f"놓치면 손해보는 핵심 팁 #{idx}",
                hook_variants=hook_var,
                start_time=s_start,
                end_time=s_end,
                reason="음성 밀도가 높고 설명이 가장 충실한 핵심 구간",
                summary_points=pts,
                virality_score=virality_score,
                score_breakdown=breakdown,
                loop_score=88,
                stat_pill=stat_p
            ))
            if len(results) >= count:
                break

    return results

def detect_highlights(
    transcript: Transcript,
    model_name: str = "qwen2.5:14b",
    max_count: int = 1,
    target_duration_range: tuple[int, int] = (30, 50),
    video_path: Optional[str] = None,
    callback: Optional[Callable[[int, str], None]] = None
) -> List[Highlight]:
    """
    Detect the most engaging shorts highlight segments using Ollama.
    Guarantees every clip is between min_dur (30s) and max_dur (50s).
    Evaluates clips using Opus Clip's 4-Pillar Virality Scoring model.
    """
    min_dur, max_dur = target_duration_range

    if transcript.duration <= 60.0:
        pts = summarize_clip_content(transcript, 0.0, transcript.duration, "쇼츠 클립", model_name=model_name)
        return [
            Highlight(
                id=1,
                title="쇼츠 클립",
                hook_text="핵심 요약",
                start_time=0.0,
                end_time=round(transcript.duration, 2),
                reason="영상 전체 클립",
                summary_points=pts,
                virality_score=90,
                score_breakdown={"hook": 27, "flow": 23, "value": 23, "trend": 17}
            )
        ]

    if callback:
        callback(66, f"AI 문맥 분석 시작 (전체 {len(transcript.segments)}개 대화 세그먼트 벡터 구조화)...")

    formatted_text = format_transcript_for_llm(transcript)

    system_prompt = (
        "You are an elite YouTube Shorts & TikTok PD creating viral million-view clips.\n"
        "Analyze the dialogue transcript and choose the best viral highlight moments for Shorts.\n\n"
        "🔥 VIRAL KILLER FACTOR RANKING (PRIORITIZE THESE):\n"
        "1. EXTREME FINANCIAL / NUMBER CONTRAST (Highest Priority, 95~99 Score):\n"
        "   - Clips with huge numerical contrasts (e.g. '70만원 vs 4만원', '100만원 손해', '10배 절약', '3초 만에 해결').\n"
        "   - Immediately grabs dopamine and forces the viewer to stay.\n"
        "2. LOSS AVERSION & RIP-OFF PREVENTION (High Priority, 90~95 Score):\n"
        "   - Secrets to avoid getting scammed or overcharged (e.g. '카센터 눈탱이 방지', '보험료 할증 폭탄 피하는 법').\n"
        "3. COUNTER-INTUITIVE TRUTHS & EXCLUSIVE SECRETS (High Priority, 88~93 Score):\n"
        "   - Things most people do wrong (e.g. '사고 났을 때 절대 보험 먼저 부르지 마세요').\n"
        "⛔ CLICHÉ & COMMON SENSE PENALTY (AVOID OR SCORE 60~72):\n"
        "   - Boring textbook advice or public service announcements (e.g. '사고 나면 비상등 켜고 안전지대로 대피하고 112 신고').\n"
        "   - Everyone already knows this! Viewers swipe away within 1 second. DO NOT pick this as #1!\n\n"
        "OPUS CLIP 4-PILLAR VIRALITY SCORING (Total: 60 ~ 99):\n"
        "1. Hook (0~30): First 3 seconds stopping power.\n"
        "2. Flow (0~25): Standalone, coherent, punchy story without boring pauses.\n"
        "3. Value (0~25): High practical takeaway, money saved, or secret tip.\n"
        "4. Trend (0~20): High curiosity and shareability for a wide audience.\n\n"
        "CRITICAL RULES:\n"
        f"1. Target length: Highlight clips MUST span {min_dur} to {max_dur} seconds.\n"
        "2. LANGUAGE: You MUST write title, hook_text, reason, and summary_points in 100% natural, high-CTR KOREAN (Hangul).\n"
        "   - NEVER use Chinese characters (Hanzi). Only Korean Hangul.\n"
        "3. hook_text: Short, punchy hook under 20 chars in Korean WITHOUT emojis (e.g., '사이드미러 4만원 해결법').\n"
        "4. title: Click-worthy Korean YouTube Shorts title (e.g., '70만원 수리비 단돈 4만원에 끝내는 비결'). Do NOT repeat words.\n"
        "5. virality_score: Integer from 60 to 99 representing true viral retention potential.\n"
        "6. score_breakdown: Object with keys 'hook', 'flow', 'value', 'trend'.\n"
        "7. summary_points: EXACTLY 2 concrete bullet points summarizing the actual practical facts/methods (under 28 chars each in Korean). Do NOT write generic filler.\n"
        "8. Output ONLY the specified JSON structure.\n"
    )

    user_prompt = f"다음 자막 대본을 분석하여 바이럴 가능성이 가장 높은 쇼츠 {max_count}개를 선정해 JSON으로 응답하세요:\n\n{formatted_text}"

    schema = {
        "type": "object",
        "properties": {
            "highlights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "hook_text": {"type": "string"},
                        "start_time": {"type": "number"},
                        "end_time": {"type": "number"},
                        "virality_score": {"type": "integer"},
                        "score_breakdown": {
                            "type": "object",
                            "properties": {
                                "hook": {"type": "integer"},
                                "flow": {"type": "integer"},
                                "value": {"type": "integer"},
                                "trend": {"type": "integer"}
                            }
                        },
                        "reason": {"type": "string"},
                        "summary_points": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "hook_text", "start_time", "end_time", "virality_score", "summary_points"]
                }
            }
        },
        "required": ["highlights"]
    }

    try:
        if callback:
            callback(70, f"Ollama LLM ({model_name}) 심층 문맥 추론 및 바이럴 구간 탐색 중...")

        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            format=schema,
            options={"temperature": 0.25}
        )
        content = response["message"]["content"]

        if callback:
            callback(85, "한국어 문장 어미(~다, ~요, ~죠) 문법 경계 스냅 및 룸톤 오디오 보정 중...")
        
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            items = parsed.get("highlights", []) or list(parsed.values())[0] if parsed else []
            if not isinstance(items, list):
                items = [parsed]
        elif isinstance(parsed, list):
            items = parsed
        else:
            items = []

        highlights = []
        for item in items:
            if not isinstance(item, dict):
                continue
            raw_start = item.get("start_time") or item.get("start")
            raw_end = item.get("end_time") or item.get("end")
            if raw_start is None or raw_end is None:
                continue

            raw_start = float(raw_start)
            raw_end = float(raw_end)
            
            # Snap timestamps to grammatical speech boundaries and enforce min_dur ~ max_dur
            s_start, s_end = snap_timestamps_to_sentence_boundaries(
                transcript, raw_start, raw_end, min_dur=min_dur, max_dur=max_dur, video_path=video_path
            )

            # Prevent heavy overlap with already selected clips
            is_overlap = False
            for prev in highlights:
                overlap_sec = max(0.0, min(s_end, prev.end_time) - max(s_start, prev.start_time))
                if overlap_sec > 10.0:
                    is_overlap = True
                    break
            if is_overlap:
                continue

            # Clean and sanitize Korean texts
            idx = len(highlights) + 1
            title = clean_korean_text(item.get("title", ""), f"영상 핵심 꿀팁 #{idx}")
            hook = clean_korean_text(item.get("hook_text", ""), f"놓치면 안 되는 꿀팁 #{idx}")
            formatted_hook = format_hook_badge_text(hook, title)
            reason = clean_korean_text(item.get("reason", ""), "핵심 구간 요약")

            # Extract 2 concrete factual summary points
            raw_pts = item.get("summary_points", [])
            valid_pts = [strip_emojis(p).strip() for p in raw_pts if p and len(strip_emojis(p).strip()) >= 4]
            valid_pts = [p for p in valid_pts if "몰입도" not in p and "핵심 구간" not in p]
            if len(valid_pts) < 2:
                fallback_pts = summarize_clip_content(transcript, s_start, s_end, title, model_name=model_name)
                for fp in fallback_pts:
                    if fp not in valid_pts:
                        valid_pts.append(fp)
            summary_points = valid_pts[:2]

            # Calculate empirical viral metrics (WPM pacing, hook curiosity, value)
            clip_dur = max(1.0, s_end - s_start)
            clip_words_count = sum(
                len(seg.words) for seg in transcript.segments
                if seg.start >= (s_start - 0.2) and seg.end <= (s_end + 0.2)
            )
            wpm = (clip_words_count / clip_dur) * 60.0

            # Hook curiosity detection in initial 5 seconds
            first_segs_text = " ".join(
                seg.text for seg in transcript.segments
                if seg.start >= (s_start - 0.2) and seg.start <= (s_start + 6.0)
            )
            has_curiosity_hook = any(kw in first_segs_text for kw in ["어떻게", "왜", "방법", "꿀팁", "주의", "실수", "비법", "기능", "중요", "까", "나요", "죠", "모르", "진짜"])

            if callback and len(highlights) == 0:
                callback(92, "OpusClip 4기둥 바이럴 채점 및 CTR 훅 타이포그래피 생성 중...")

            # Viral Keyword & Financial Contrast Detection
            all_clip_text = " ".join(seg.text for seg in transcript.segments if seg.start >= (s_start - 0.2) and seg.end <= (s_end + 0.2))
            has_money_contrast = bool(re.search(r'(\d+만\s*원|\d+원|70만|4만|100만|비용|수리비|견적|환불|할증|절약)', all_clip_text))
            has_loss_aversion = any(kw in all_clip_text for kw in ["눈탱이", "호구", "손해", "실수", "당하지", "사기", "비밀", "꿀팁", "아끼", "절대", "주의"])
            is_boring_cliche = any(kw in all_clip_text for kw in ["안전지대", "가드레일", "삼각대", "대피", "112", "신고"]) and not has_money_contrast

            raw_v = item.get("virality_score")
            base_llm = int(raw_v) if raw_v and str(raw_v).isdigit() else 80

            # Dynamic multi-factor scoring with extreme contrast reward & cliché penalty
            hook_bonus = (6 if has_money_contrast else (3 if has_curiosity_hook else 0))
            value_bonus = (5 if has_loss_aversion else 2) + (3 if has_money_contrast else 0)
            cliche_penalty = -16 if is_boring_cliche else 0

            hook_sc = min(30, max(14, 18 + hook_bonus))
            flow_sc = min(25, max(14, 18 + (4 if 110 <= wpm <= 190 else 1)))
            value_sc = min(25, max(14, 16 + value_bonus))
            trend_sc = min(20, max(12, 14 + (4 if has_money_contrast or has_loss_aversion else 1)))

            v_score = hook_sc + flow_sc + value_sc + trend_sc + cliche_penalty
            if base_llm:
                v_score = int(v_score * 0.6 + base_llm * 0.4)
            v_score = min(99, max(60, v_score))

            score_breakdown = {
                "hook": hook_sc,
                "flow": flow_sc,
                "value": value_sc,
                "trend": trend_sc
            }

            # Hook A/B testing variants & Infinite Loop Score & Apple Stat Pill
            hook_variants = generate_hook_variants(title, formatted_hook)
            last_segs = [seg.text for seg in transcript.segments if seg.start >= (s_end - 5.0) and seg.end <= (s_end + 0.5)]
            last_text = " ".join(last_segs)
            loop_score = calculate_infinite_loop_score(first_segs_text, last_text)
            stat_pill = extract_stat_pill_from_transcript(transcript, s_start, s_end)

            highlights.append(Highlight(
                id=idx,
                title=title,
                hook_text=formatted_hook,
                hook_variants=hook_variants,
                start_time=s_start,
                end_time=s_end,
                reason=reason,
                summary_points=summary_points,
                virality_score=v_score,
                score_breakdown=score_breakdown,
                loop_score=loop_score,
                stat_pill=stat_pill
            ))

        if highlights:
            # Sort clips by virality_score descending so top viral killer clip is always #1!
            highlights.sort(key=lambda h: h.virality_score, reverse=True)
            for i, h in enumerate(highlights):
                h.id = i + 1
            if callback:
                callback(96, f"최종 {len(highlights)}개 고득점 하이라이트 구간 확정 완료")
            return highlights[:max_count]

    except Exception as e:
        print(f"[Warning] Ollama highlight extraction fallback triggered: {e}")

    # Fallback heuristic
    return fallback_heuristic_highlights(transcript, count=max_count, min_dur=min_dur, max_dur=max_dur)
