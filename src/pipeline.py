import os
import re
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table

from src.models import VideoMetadata, Transcript, Highlight
from src.downloader import prepare_source
from src.transcriber import transcribe_video
from src.highlighter import detect_highlights
from src.renderer import render_short

console = Console()
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>| ]', "_", name)
    return cleaned[:40].strip("_")

class ShortsPipeline:
    def __init__(
        self,
        whisper_model: str = "small",
        llm_model: str = "qwen2.5:7b",
        layout_mode: str = "blur_background",
        show_badge: bool = True,
        show_progress_bar: bool = True,
        normalize_audio: bool = True
    ):
        self.whisper_model = whisper_model
        self.llm_model = llm_model
        self.layout_mode = layout_mode
        self.show_badge = show_badge
        self.show_progress_bar = show_progress_bar
        self.normalize_audio = normalize_audio

    def run(
        self,
        source: str,
        max_clips: int = 1,
        target_duration: tuple[int, int] = (30, 55),
        callback=None
    ) -> List[dict]:
        """
        Execute full pipeline from source to final Shorts MP4 files.
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

        # 3. Detect Highlights
        if callback:
            callback(55.0, f"AI 하이라이트 구간 분석 중 (모델: {self.llm_model})...")
            highlights = detect_highlights(
                transcript,
                model_name=self.llm_model,
                max_count=max_clips,
                target_duration_range=target_duration
            )
            callback(70.0, f"하이라이트 {len(highlights)}개 구간 선정 완료")
        else:
            with console.status(f"[bold green]3/4. AI 하이라이트 분석 및 숏폼 구간 선정 (모델: {self.llm_model})...[/bold green]"):
                highlights = detect_highlights(
                    transcript,
                    model_name=self.llm_model,
                    max_count=max_clips,
                    target_duration_range=target_duration
                )
            console.print(f"  [green]✔[/green] 하이라이트 구간 [bold]{len(highlights)}개[/bold] 선정 완료!")

        # 4. Render Shorts
        results = []
        safe_title = sanitize_filename(metadata.title)
        num_hl = len(highlights)

        for idx, h in enumerate(highlights):
            m_s, s_s = divmod(int(h.start_time), 60)
            m_e, s_e = divmod(int(h.end_time), 60)
            time_str = f"{m_s:02d}:{s_s:02d} ~ {m_e:02d}:{s_e:02d}"

            output_filename = f"short_{safe_title}_{h.id}.mp4"
            output_path = str(OUTPUT_DIR / output_filename)

            if callback:
                render_pct = 70.0 + (idx / max(1, num_hl)) * 28.0
                callback(render_pct, f"클립 #{h.id} 9:16 + 팝업자막 + 효과 렌더링 중...")
                render_short(
                    metadata=metadata,
                    highlight=h,
                    transcript=transcript,
                    output_path=output_path,
                    layout_mode=self.layout_mode,
                    show_badge=self.show_badge,
                    show_progress_bar=self.show_progress_bar,
                    normalize_audio=self.normalize_audio
                )
            else:
                console.print(f"\n[bold yellow]👉 [클립 #{h.id}] {h.title}[/bold yellow] ({time_str}, {h.duration:.1f}초)")
                console.print(f"   • 훅 타이틀: [bold cyan]{h.hook_text}[/bold cyan]")
                console.print(f"   • 선정 이유: {h.reason}")
                with console.status(f"[bold magenta]4/4. 9:16 비디오 + 팝업 자막 + 효과 렌더링 중...[/bold magenta]"):
                    render_short(
                        metadata=metadata,
                        highlight=h,
                        transcript=transcript,
                        output_path=output_path,
                        layout_mode=self.layout_mode,
                        show_badge=self.show_badge,
                        show_progress_bar=self.show_progress_bar,
                        normalize_audio=self.normalize_audio
                    )
                console.print(f"  [bold green]✔ 쇼츠 생성 완료:[/bold green] {output_path}")

            results.append({
                "id": h.id,
                "title": h.title,
                "hook_text": h.hook_text,
                "duration": h.duration,
                "time_range": time_str,
                "output_path": output_path
            })

        if callback:
            callback(100.0, "모든 쇼츠 생성이 완료되었습니다!")

        # Summary Table
        table = Table(title="🎉 생성된 쇼츠 결과 목록", show_header=True, header_style="bold magenta")
        table.add_column("번호", width=6)
        table.add_column("제목", style="cyan")
        table.add_column("훅 헤드라인", style="yellow")
        table.add_column("구간", justify="center")
        table.add_column("길이", justify="center")
        table.add_column("저장 경로", style="green")

        for r in results:
            table.add_row(
                str(r["id"]),
                r["title"],
                r["hook_text"],
                r["time_range"],
                f"{r['duration']:.1f}초",
                r["output_path"]
            )

        console.print("\n")
        console.print(table)
        console.print("\n[bold green]✨ 모든 쇼츠 생성이 성공적으로 완료되었습니다![/bold green]\n")

        return results
