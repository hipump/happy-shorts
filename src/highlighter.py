import json
import re
from typing import List, Optional
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

def snap_timestamps_to_sentence_boundaries(
    transcript: Transcript,
    raw_start: float,
    raw_end: float,
    min_dur: float = 30.0,
    max_dur: float = 50.0
) -> tuple[float, float]:
    """
    Ensure the clip starts cleanly at the beginning of a sentence
    and ends cleanly at the end of a sentence.
    Guarantees clip duration is strictly between min_dur (30s) and max_dur (50s).
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

    # 2. Find end segment
    end_idx = start_idx
    if (raw_end - raw_start) >= min_dur:
        best_end_diff = float("inf")
        for i in range(start_idx, len(segments)):
            diff = abs(segments[i].end - raw_end)
            if diff < best_end_diff:
                best_end_diff = diff
                end_idx = i
    else:
        # LLM gave a short span (e.g. 1-2 sentences). Expand forward until accumulated duration >= min_dur
        for i in range(start_idx, len(segments)):
            end_idx = i
            if (segments[i].end - snapped_start) >= min_dur:
                break

    # 3. If near the end of video and duration is still < min_dur, expand start backwards
    while start_idx > 0 and (segments[end_idx].end - segments[start_idx].start) < min_dur:
        start_idx -= 1
    snapped_start = segments[start_idx].start

    # 4. If duration exceeds max_dur, clamp end_idx
    while end_idx > start_idx and (segments[end_idx].end - snapped_start) > max_dur:
        if (segments[end_idx - 1].end - snapped_start) >= min_dur:
            end_idx -= 1
        else:
            break

    snapped_end = segments[end_idx].end

    # Fallback sanity check
    if (snapped_end - snapped_start) < min_dur:
        snapped_end = min(transcript.duration, snapped_start + min_dur)

    return max(0.0, round(snapped_start, 2)), min(round(transcript.duration, 2), round(snapped_end, 2))

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

def summarize_clip_content(
    transcript: Transcript,
    start_time: float,
    end_time: float,
    title: str = "",
    model_name: str = "qwen2.5:7b"
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
            results.append(Highlight(
                id=idx,
                title=clip_title,
                hook_text=f"놓치면 손해보는 핵심 팁 #{idx}",
                start_time=s_start,
                end_time=s_end,
                reason="음성 밀도가 높고 설명이 가장 충실한 핵심 구간",
                summary_points=pts
            ))
            if len(results) >= count:
                break

    return results

def detect_highlights(
    transcript: Transcript,
    model_name: str = "qwen2.5:7b",
    max_count: int = 1,
    target_duration_range: tuple[int, int] = (30, 50)
) -> List[Highlight]:
    """
    Detect the most engaging shorts highlight segments using Ollama.
    Guarantees every clip is between min_dur (30s) and max_dur (50s).
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
                summary_points=pts
            )
        ]

    formatted_text = format_transcript_for_llm(transcript)

    system_prompt = (
        "You are a top-tier Korean YouTube Shorts & TikTok PD creating viral million-view clips.\n"
        "Analyze the dialogue transcript and choose the best viral highlight moments for Shorts.\n\n"
        "SELECTION CRITERIA (Hook - Story - Payoff):\n"
        "1. Hook (First 3s): Starts with an intriguing question or statement that stops viewers from swiping.\n"
        "2. Story (25~35s): Delivers practical, useful tip or entertaining revelation.\n"
        "3. Payoff (End): Wraps up with clear conclusion or summary without cutting off.\n\n"
        "CRITICAL RULES:\n"
        f"1. Target length: Highlight clips MUST span {min_dur} to {max_dur} seconds.\n"
        "2. LANGUAGE: You MUST write title, hook_text, reason, and summary_points in 100% natural, high-CTR KOREAN (Hangul).\n"
        "   - NEVER use Chinese characters (Hanzi). Only Korean Hangul.\n"
        "3. hook_text: Short, punchy hook under 20 chars in Korean WITHOUT emojis (e.g., '테슬라 차주 필수 꿀팁'). Do NOT include emojis.\n"
        "4. title: Click-worthy Korean YouTube Shorts title (e.g., '트렁크 오토락 숨겨진 기능'). Do NOT include emojis.\n"
        "5. summary_points: EXACTLY 2 concrete bullet points summarizing the actual practical facts/methods explained in this clip (under 28 chars each in Korean, e.g. ['트렁크 뒤 비프음 3회 후 자동 오픈', '천장 낮은 주차장에서 높이 조절']). Do NOT write generic filler like '시청자 몰입도가 높음'.\n"
        "6. Output ONLY the specified JSON structure.\n"
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
                        "reason": {"type": "string"},
                        "summary_points": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "hook_text", "start_time", "end_time", "summary_points"]
                }
            }
        },
        "required": ["highlights"]
    }

    try:
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
            
            # Snap timestamps to speech boundaries and enforce min_dur ~ max_dur
            s_start, s_end = snap_timestamps_to_sentence_boundaries(
                transcript, raw_start, raw_end, min_dur=min_dur, max_dur=max_dur
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

            highlights.append(Highlight(
                id=idx,
                title=title,
                hook_text=formatted_hook,
                start_time=s_start,
                end_time=s_end,
                reason=reason,
                summary_points=summary_points
            ))

            if len(highlights) >= max_count:
                break
            
        if highlights:
            return highlights

    except Exception as e:
        print(f"[Warning] Ollama highlight extraction fallback triggered: {e}")

    # Fallback heuristic
    return fallback_heuristic_highlights(transcript, count=max_count, min_dur=min_dur, max_dur=max_dur)
