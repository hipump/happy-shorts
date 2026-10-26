import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from rich.console import Console
from rich.table import Table

from src.models import VideoMetadata, Transcript, Highlight
from src.templates import ShortsTemplate, get_template
from src.downloader import prepare_source
from src.transcriber import transcribe_video
from src.highlighter import detect_highlights
from src.renderer import render_short
from src.thumbnail import generate_pro_thumbnail

console = Console()
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>| ]', "_", name)
    return cleaned[:40].strip("_")

def get_unique_output_paths(output_dir: Path, safe_title: str, clip_id: int) -> Tuple[str, str, str]:
    """
    Generate unique non-colliding output paths for MP4, cover thumbnail JPG, and metadata TXT.
    Prevents overwriting previous runs by incorporating timestamp and duplicate check.
    """
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_key = f"{safe_title}_{clip_id}_{now_str}"

    counter = 1
    cand_key = base_key
    while (output_dir / f"short_{cand_key}.mp4").exists():
        cand_key = f"{base_key}_{counter}"
        counter += 1

    out_video = str(output_dir / f"short_{cand_key}.mp4")
    out_cover = str(output_dir / f"cover_{cand_key}.jpg")
    out_meta = str(output_dir / f"shorts_info_{cand_key}.txt")
    return out_video, out_cover, out_meta

def generate_youtube_metadata_file(
    output_txt_path: str,
    highlight: Highlight,
    metadata: VideoMetadata,
    output_video_path: str
):
    """Generates 2026 YouTube Shorts SEO-optimized metadata package (titles, description, hashtags)."""
    title_clean = highlight.title.strip()
    hook_clean = highlight.hook_text.strip()

    t1 = f"{title_clean} - {hook_clean}"[:58]
    t2 = f"몰랐으면 후회할 {title_clean}"[:58]
    t3 = f"실전 핵심 꿀팁! {title_clean}"[:58]

    summary_lines = "\n".join(f"- {p}" for p in highlight.summary_points) if highlight.summary_points else f"- {title_clean} 실전 가이드"

    tags = ["#Shorts", "#유튜브쇼츠"]
    words = [re.sub(r'[^가-힣a-zA-Z0-9]', '', w) for w in title_clean.split() if len(w) >= 2]
    for w in words[:3]:
        if w and f"#{w}" not in tags:
            tags.append(f"#{w}")
    tags_str = " ".join(tags[:5])

    b = highlight.score_breakdown
    breakdown_str = f"Hook: {b.get('hook', 26)}/30, Flow: {b.get('flow', 22)}/25, Value: {b.get('value', 22)}/25, Trend: {b.get('trend', 18)}/20"

    # Viral hook variants & loop strategy
    hook_vars = getattr(highlight, "hook_variants", {}) or {}
    curiosity_h = hook_vars.get("curiosity", hook_clean)
    urgency_h = hook_vars.get("urgency", f"지금 안 보면 손해 보는 {title_clean}")
    benefit_h = hook_vars.get("benefit", f"단 30초 만에 끝내는 {title_clean}")
    loop_sc = getattr(highlight, "loop_score", 85)
    stat_p = getattr(highlight, "stat_pill", None)
    stat_desc = f"감지됨 [{stat_p.get('metric', '')} - {stat_p.get('label', '')}] (3.8초경 팝업)" if stat_p else "미감지 (일반 자막 모드)"

    content = f"""================================================================================
🎬 유튜브 쇼츠 업로드 가이드 (2026 알고리즘 최적화)
파일: {os.path.basename(output_video_path)}
바이럴 종합 점수: {highlight.virality_score}점 ({breakdown_str})
🔁 무한 루프 싱크 지수: {loop_sc}점 / 100점 (끝문장-첫문장 자연 순환 설계)
📊 키노트 수치 카드: {stat_desc}
================================================================================

🎯 [훅 A/B 테스트 추천 헤드라인 3종]
• [호기심 자극형] {curiosity_h}
• [손실 회피형]   {urgency_h}
• [극대 이득형]   {benefit_h}

📌 [추천 업로드 제목 (CTR 최적화 - 55~60자 이내)]
1안: {t1}
2안: {t2}
3안: {t3}

📝 [본문 설명란 (복사하여 붙여넣기)]
{title_clean}의 실전 핵심 내용을 빠르게 정리했습니다!
{summary_lines}

영상 끝까지 시청해주셔서 감사합니다! 구독과 좋아요는 큰 힘이 됩니다.
{tags_str}

🏷️ [추천 해시태그 (3~5개 엄선)]
{tags_str}
================================================================================
"""
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(content)

class ShortsPipeline:
    def __init__(
        self,
        whisper_model: str = "large-v3-turbo",
        llm_model: str = "qwen2.5:14b",
        template: Optional[ShortsTemplate] = None,
        template_id: str = "browser_window",
        layout_mode: Optional[str] = None,
        show_badge: bool = True,
        badge_style: str = "gold_pill",
        badge_prefix: str = "[TIP]",
        show_subtitles: bool = True,
        subtitle_style: Optional[str] = None,
        active_color: tuple = (255, 230, 0),
        normal_color: tuple = (255, 255, 255),
        font_name: str = "black_han_sans",
        show_progress_bar: bool = False,
        normalize_audio: bool = True,
        aspect_ratio: str = "9:16",
        remove_subtitles: bool = False,
        filter_fillers: bool = True,
        bgm_track: str = "auto",
        enable_sfx: bool = True,
        color_grade: str = "vibrant_tech",
        dynamic_zoom: bool = True,
        smart_keywords: bool = True,
        bounce_animation: bool = True,
        hook_variant_type: str = "default",
        enable_stat_pill: bool = True,
        seamless_loop: bool = True
    ):
        self.whisper_model = whisper_model
        from src.highlighter import resolve_optimal_llm
        self.llm_model = resolve_optimal_llm(llm_model)
        self.template = template if template else get_template(template_id)
        self.layout_mode = layout_mode or self.template.layout_type
        self.show_badge = show_badge
        self.badge_style = badge_style
        self.badge_prefix = badge_prefix
        self.show_subtitles = show_subtitles
        self.subtitle_style = subtitle_style or self.template.subtitle_style
        self.active_color = active_color
        self.normal_color = normal_color
        self.font_name = font_name
        self.show_progress_bar = show_progress_bar
        self.normalize_audio = normalize_audio
        self.aspect_ratio = aspect_ratio
        self.remove_subtitles = remove_subtitles
        self.filter_fillers = filter_fillers
        self.bgm_track = bgm_track
        self.enable_sfx = enable_sfx
        self.color_grade = color_grade
        self.dynamic_zoom = dynamic_zoom
        self.smart_keywords = smart_keywords
        self.bounce_animation = bounce_animation
        self.hook_variant_type = hook_variant_type
        self.enable_stat_pill = enable_stat_pill
        self.seamless_loop = seamless_loop

    def run(
        self,
        source: str,
        max_clips: int = 1,
        target_duration: tuple[int, int] = (30, 55),
        callback=None,
        interactive_preview: bool = False
    ) -> List[dict]:
        """
        Execute full pipeline from source to final Shorts MP4 files.
        Supports interactive candidate preview selection mode with OpusClip Virality Scores.
        """
        if callback:
            callback(5.0, "영상 소스 분석 및 준비 중...")
        else:
            console.rule("[bold cyan]🎬 유튜브/로컬 영상 -> 쇼츠 변환 파이프라인 시작[/bold cyan]")

        # 1. Prepare Source
        if not callback:
            with console.status("[bold green]1/4. 영상 소스 준비 중 (다운로드/검증)...[/bold green]"):
                metadata = prepare_source(source)
            console.print(f"  [green]✔[/green] 원본 영상: [bold]{metadata.title}[/bold] (길이: {metadata.duration:.1f}초, 해상도: {metadata.width}x{metadata.height})")
        else:
            metadata = prepare_source(source)
            callback(25.0, f"영상 준비 완료 ({metadata.title[:20]}...)")

        # 2. Transcribe Audio
        if callback:
            callback(30.0, f"음성 인식 및 자막 추출 중 (Whisper: {self.whisper_model})...")
            transcript = transcribe_video(
                metadata.local_path,
                model_size=self.whisper_model
            )
            callback(50.0, f"음성 인식 완료 ({len(transcript.segments)}개 문장)")
        else:
            with console.status(f"[bold green]2/4. 음성 인식 및 단어 단위 자막 추출 (Whisper: {self.whisper_model})...[/bold green]"):
                transcript = transcribe_video(
                    metadata.local_path,
                    model_size=self.whisper_model
                )
            total_words = sum(len(seg.words) for seg in transcript.segments)
            console.print(f"  [green]✔[/green] STT 완료: 총 {len(transcript.segments)}개 문장, {total_words}개 단어 감지됨 (언어: {transcript.language})")

        # 3. Detect Highlights with OpusClip 4-Pillar Virality Scoring
        detect_count = max(3, max_clips) if interactive_preview else max_clips
        if callback:
            callback(55.0, f"AI 하이라이트 구간 분석 및 바이럴 채점 중 (모델: {self.llm_model})...")
            highlights = detect_highlights(
                transcript,
                model_name=self.llm_model,
                max_count=detect_count,
                target_duration_range=target_duration,
                video_path=metadata.local_path
            )
            callback(70.0, f"하이라이트 {len(highlights)}개 구간 선정 완료")
        else:
            with console.status(f"[bold green]3/4. AI 하이라이트 분석 및 바이럴 채점 중 (모델: {self.llm_model})...[/bold green]"):
                highlights = detect_highlights(
                    transcript,
                    model_name=self.llm_model,
                    max_count=detect_count,
                    target_duration_range=target_duration,
                    video_path=metadata.local_path
                )
            console.print(f"  [green]✔[/green] AI 하이라이트 분석 완료: 총 [bold]{len(highlights)}개[/bold] 후보 구간 감지됨!")

        # Sort candidates by virality score descending
        highlights.sort(key=lambda h: h.virality_score, reverse=True)
        for i, h in enumerate(highlights, 1):
            h.id = i

        # Interactive Candidate Preview Mode
        if interactive_preview and len(highlights) > 1:
            import questionary

            c_table = Table(title="🏆 AI 하이라이트 후보 분석 결과 (OpusClip 바이럴 점수 순)", show_header=True, header_style="bold magenta")
            c_table.add_column("후보", width=6, justify="center")
            c_table.add_column("바이럴 점수", justify="center", style="bold red")
            c_table.add_column("쇼츠 제목 & 후킹 화두", style="cyan")
            c_table.add_column("구간", justify="center", style="yellow")
            c_table.add_column("길이", justify="center")
            c_table.add_column("실전 핵심 꿀팁", style="green")

            for h in highlights:
                m_s, s_s = divmod(int(h.start_time), 60)
                m_e, s_e = divmod(int(h.end_time), 60)
                t_str = f"{m_s:02d}:{s_s:02d} ~ {m_e:02d}:{s_e:02d}"
                summary_txt = " • " + " / ".join(h.summary_points) if h.summary_points else h.reason[:30]
                badge = "🔥" if h.virality_score >= 90 else ("✨" if h.virality_score >= 80 else "💡")
                b = h.score_breakdown
                score_str = f"{badge} {h.virality_score}점 (H:{b.get('hook', 20)} F:{b.get('flow', 20)} V:{b.get('value', 20)} T:{b.get('trend', 15)})"
                c_table.add_row(
                    f"#{h.id}",
                    score_str,
                    f"{h.title}\n[dim]{h.hook_text}[/dim]",
                    t_str,
                    f"{h.duration:.1f}초",
                    summary_txt
                )

            console.print("\n")
            console.print(c_table)
            console.print("\n")

            choices = []
            for h in highlights:
                rec_tag = " (강력 추천)" if h.id == 1 else ""
                choices.append(f"{h.id}번 후보) [{h.virality_score}점] {h.title}{rec_tag}")
            
            if 1 < max_clips < len(highlights):
                choices.append(f"상위 {max_clips}개 후보 일괄 생성 (1번 ~ {max_clips}번)")
            choices.append(f"전체 후보 모두 생성 (총 {len(highlights)}개 클립)")

            try:
                sel = questionary.select(
                    "👉 최종 렌더링할 하이라이트 후보를 선택하세요:",
                    choices=choices
                ).ask()
            except Exception:
                sel = None

            if not sel or "모두" in sel:
                # All candidates selected
                pass
            elif "일괄" in sel:
                highlights = highlights[:max_clips]
            elif "번 후보)" in sel:
                chosen_num = int(sel.split("번 후보)")[0].strip())
                highlights = [h for h in highlights if h.id == chosen_num]
                highlights[0].id = 1
            else:
                highlights = highlights[:max_clips]
        else:
            highlights = highlights[:max_clips]

        # 4. Render Shorts
        results = []
        safe_title = sanitize_filename(metadata.title)
        num_hl = len(highlights)

        for idx, h in enumerate(highlights):
            m_s, s_s = divmod(int(h.start_time), 60)
            m_e, s_e = divmod(int(h.end_time), 60)
            time_str = f"{m_s:02d}:{s_s:02d} ~ {m_e:02d}:{s_e:02d}"

            output_path, cover_path, meta_txt_path = get_unique_output_paths(OUTPUT_DIR, safe_title, h.id)
            output_filename = os.path.basename(output_path)

            if callback:
                render_pct = 70.0 + (idx / max(1, num_hl)) * 28.0
                callback(render_pct, f"클립 #{h.id} (바이럴 {h.virality_score}점) 렌더링 중...")
                render_short(
                    metadata=metadata,
                    highlight=h,
                    transcript=transcript,
                    output_path=output_path,
                    template=self.template,
                    layout_mode=self.layout_mode,
                    show_badge=self.show_badge,
                    badge_style=self.badge_style,
                    badge_prefix=self.badge_prefix,
                    show_subtitles=self.show_subtitles,
                    subtitle_style=self.subtitle_style,
                    active_color=self.active_color,
                    normal_color=self.normal_color,
                    font_name=self.font_name,
                    show_progress_bar=self.show_progress_bar,
                    normalize_audio=self.normalize_audio,
                    aspect_ratio=self.aspect_ratio,
                    remove_subtitles=self.remove_subtitles,
                    filter_fillers=self.filter_fillers,
                    bgm_track=self.bgm_track,
                    enable_sfx=self.enable_sfx,
                    color_grade=self.color_grade,
                    dynamic_zoom=self.dynamic_zoom,
                    smart_keywords=self.smart_keywords,
                    bounce_animation=self.bounce_animation,
                    hook_variant_type=self.hook_variant_type,
                    enable_stat_pill=self.enable_stat_pill,
                    seamless_loop=self.seamless_loop
                )
            else:
                ratio_label = "16:9 가로" if self.aspect_ratio == "16:9" else "9:16 세로"
                sub_label = " (원본 자막 AI 제거 적용)" if self.remove_subtitles else ""
                console.print(f"\n[bold yellow]👉 [클립 #{h.id}] {h.title}[/bold yellow] ({time_str}, {h.duration:.1f}초, [bold red]바이럴 {h.virality_score}점[/bold red])")
                console.print(f"   • 화면 비율: [bold cyan]{ratio_label}[/bold cyan]{sub_label}")
                console.print(f"   • 훅 헤드라인: [bold cyan]{h.hook_text}[/bold cyan]")
                console.print(f"   • 선정 이유: {h.reason}")
                with console.status(f"[bold magenta]4/4. {ratio_label} 비디오 + 팝업 자막 + 효과 렌더링 중...[/bold magenta]"):
                    render_short(
                        metadata=metadata,
                        highlight=h,
                        transcript=transcript,
                        output_path=output_path,
                        template=self.template,
                        layout_mode=self.layout_mode,
                        show_badge=self.show_badge,
                        badge_style=self.badge_style,
                        badge_prefix=self.badge_prefix,
                        show_subtitles=self.show_subtitles,
                        subtitle_style=self.subtitle_style,
                        active_color=self.active_color,
                        normal_color=self.normal_color,
                        font_name=self.font_name,
                        show_progress_bar=self.show_progress_bar,
                        normalize_audio=self.normalize_audio,
                        aspect_ratio=self.aspect_ratio,
                        remove_subtitles=self.remove_subtitles,
                        filter_fillers=self.filter_fillers,
                        bgm_track=self.bgm_track,
                        enable_sfx=self.enable_sfx,
                        color_grade=self.color_grade,
                        dynamic_zoom=self.dynamic_zoom,
                        smart_keywords=self.smart_keywords,
                        bounce_animation=self.bounce_animation,
                        hook_variant_type=self.hook_variant_type,
                        enable_stat_pill=self.enable_stat_pill,
                        seamless_loop=self.seamless_loop
                    )
                console.print(f"  [bold green]✔ 쇼츠 생성 완료:[/bold green] {output_path}")

            # Extract high-res viral pro thumbnail
            try:
                console.print(f"  [bold cyan]🎨 2026 고화질 3D 크리에이터 썸네일 합성 중...[/bold cyan]")
                generate_pro_thumbnail(
                    video_path=output_path,
                    output_cover_path=cover_path,
                    title=h.title,
                    hook_text=h.hook_text,
                    badge_type="warning" if h.virality_score and h.virality_score >= 85 else "tip",
                    badge_label="긴급 대처법" if h.virality_score and h.virality_score >= 85 else "핵심 꿀팁",
                    headline_style="yellow_on_black",
                    punchline_style="white_on_black",
                    aspect_ratio=self.aspect_ratio,
                    source_video_path=str(metadata.local_path) if metadata and metadata.local_path else None,
                    start_time=h.start_time,
                    duration=h.duration,
                    virality_score=h.virality_score,
                )
                console.print(f"  [bold green]✔ 크리에이터 썸네일 완성:[/bold green] {cover_path}")
            except Exception as e:
                console.print(f"  [yellow]⚠ 프로 썸네일 생성 실패, 기본 캡처로 대체: {e}[/yellow]")
                try:
                    subprocess.run([
                        "ffmpeg", "-y", "-ss", "00:00:01.5", "-i", output_path,
                        "-vframes", "1", "-q:v", "2", cover_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                except Exception:
                    pass

            # Generate YouTube SEO Metadata Package
            generate_youtube_metadata_file(meta_txt_path, h, metadata, output_path)

            results.append({
                "id": h.id,
                "title": h.title,
                "hook_text": h.hook_text,
                "duration": h.duration,
                "time_range": time_str,
                "output_path": output_path,
                "cover_path": cover_path,
                "meta_txt_path": meta_txt_path,
                "virality_score": h.virality_score
            })

        if callback:
            callback(100.0, "모든 쇼츠 생성이 완료되었습니다!")

        # Summary Table
        table = Table(title="🎉 생성된 쇼츠 결과 목록", show_header=True, header_style="bold magenta")
        table.add_column("번호", width=6)
        table.add_column("바이럴 점수", justify="center", style="bold red")
        table.add_column("제목", style="cyan")
        table.add_column("구간", justify="center")
        table.add_column("길이", justify="center")
        table.add_column("저장 경로", style="green")

        for r in results:
            table.add_row(
                str(r["id"]),
                f"🔥 {r['virality_score']}점",
                r["title"],
                r["time_range"],
                f"{r['duration']:.1f}초",
                r["output_path"]
            )

        console.print("\n")
        console.print(table)
        console.print("\n[bold green]✨ 모든 쇼츠 생성 및 유튜브 업로드 가이드(shorts_info.txt + 커버 썸네일) 패키징이 완료되었습니다![/bold green]\n")

        return results
