import os
import sys
import re
import argparse
import subprocess
from pathlib import Path
from typing import Tuple

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn, TimeElapsedColumn

from src.pipeline import ShortsPipeline

console = Console()

def print_banner():
    banner_text = (
        "[bold yellow]🎬 Happy Shorts - AI 유튜브/로컬 영상 쇼츠 자동 변환기[/bold yellow]\n"
        "[dim]100% 로컬 무료 구동 | Qwen2.5 AI 하이라이트 | 단어별 팝업 자막 | 9:16 비주얼 리프레임[/dim]"
    )
    console.print(Panel(banner_text, border_style="bold cyan", expand=False))

def interactive_wizard():
    print_banner()

    # Step 1: 입력 소스 선택
    recent_videos = [
        f for f in Path("downloads").glob("*.mp4")
        if f.stat().st_size > 1024
    ]

    choices = []
    if recent_videos:
        choices.append(f"⚡ 1) 이전에 작업했던 영상 목록에서 선택 ({len(recent_videos)}개 보유 - 즉시 재사용)")
        choices.append("🌐 2) 새로운 유튜브 영상 URL (자동 다운로드)")
        choices.append("📁 3) 내 PC의 로컬 영상 파일 (.mp4, .mov 등)")
    else:
        choices.append("🌐 1) 유튜브 영상 URL (자동 다운로드)")
        choices.append("📁 2) 내 PC의 로컬 영상 파일 (.mp4, .mov 등)")

    source_type = questionary.select(
        "스텝 1/4. 영상을 어떻게 입력하시겠습니까?",
        choices=choices
    ).ask()

    if not source_type:
        sys.exit(0)

    if "이전에 작업했던 영상" in source_type:
        video_items = [
            f"{f.name} ({f.stat().st_size / (1024 * 1024):.1f} MB)"
            for f in sorted(recent_videos, key=lambda x: x.stat().st_mtime, reverse=True)
        ]
        chosen = questionary.select(
            "👉 재사용할 영상을 선택하세요 (재다운로드/음성인식 없이 즉시 생성):",
            choices=video_items
        ).ask()
        if not chosen:
            sys.exit(0)
        selected_file = chosen.split(" ")[0]
        source = str(Path("downloads") / selected_file)
        console.print(f"  [green]✔ 이전 영상 선택됨:[/green] [bold]{selected_file}[/bold] (캐시 자동 재사용)")
    elif "유튜브" in source_type:
        while True:
            raw_url = questionary.text(
                "👉 유튜브 영상 URL 또는 영상 ID를 입력하세요 (이미 작업했던 영상은 캐시 자동 재사용):"
            ).ask()
            if not raw_url:
                sys.exit(0)
            cleaned_url = raw_url.strip().strip("'\"")
            for ch in ["?", "=", "&", "#", "%"]:
                cleaned_url = cleaned_url.replace(f"\\{ch}", ch)
            if "youtube.com" in cleaned_url or "youtu.be" in cleaned_url or re.match(r'^[a-zA-Z0-9_-]{11}$', cleaned_url):
                source = cleaned_url
                break
            console.print("[bold red]⚠ 올바른 유튜브 URL 형식이 아닙니다. 다시 입력해주세요.[/bold red]")
    else:
        while True:
            raw_path = questionary.text(
                "👉 로컬 영상 파일 경로를 입력하세요 (터미널로 드래그앤드롭 가능):"
            ).ask()
            if not raw_path:
                sys.exit(0)
            clean_path = raw_path.strip().strip("'\"")
            clean_path = clean_path.replace("\\ ", " ")
            if os.path.exists(clean_path):
                source = clean_path
                break
            console.print(f"[bold red]⚠ 파일을 찾을 수 없습니다: {clean_path}[/bold red]")

    # Step 2: 영상 몇 개 생성할 것인가
    clips_choice = questionary.select(
        "스텝 2/4. 생성할 쇼츠(하이라이트) 개수를 선택하세요:",
        choices=[
            "1개 (가장 추천하는 핵심 하이라이트)",
            "2개 (서로 다른 2개 구간 추출)",
            "3개 (3가지 베스트 명장면 추출)",
            "직접 입력"
        ]
    ).ask()

    if not clips_choice:
        sys.exit(0)

    if "1개" in clips_choice:
        clips_count = 1
    elif "2개" in clips_choice:
        clips_count = 2
    elif "3개" in clips_choice:
        clips_count = 3
    else:
        custom_c = questionary.text("원하는 개수를 숫자로 입력하세요:", default="1").ask()
        clips_count = int(custom_c) if custom_c and custom_c.isdigit() else 1

    # Step 3: 옵션 선택
    opt_mode = questionary.select(
        "스텝 3/4. 숏폼 스타일 및 효과 옵션을 선택하세요:",
        choices=[
            "⚡ [빠른 추천] 기본 최적 옵션 (블러 배경 + 훅 뱃지 + 프로그레스 바 + 30~50초)",
            "🎨 [맞춤 설정] 화면 레이아웃, 길이, 효과 직접 변경"
        ]
    ).ask()

    if not opt_mode:
        sys.exit(0)

    layout_mode = "blur_background"
    show_badge = True
    show_progress_bar = True
    target_dur = (30, 50)

    if "맞춤 설정" in opt_mode:
        # 3-1. 화면 레이아웃 모드
        layout_choice = questionary.select(
            "👉 9:16 세로 화면 연출 모드를 선택하세요:",
            choices=[
                "🌟 1) 블러 배경 모드 (추천: 상하단 은은한 블러 + 중앙 원본 유지)",
                "👤 2) 스마트 얼굴 추적 (AI가 화자 얼굴을 따라 9:16 중앙 패닝)",
                "🎯 3) 단순 중앙 크롭 (가운데 9:16 영역만 잘라내기)"
            ]
        ).ask()
        if "블러" in layout_choice:
            layout_mode = "blur_background"
        elif "스마트" in layout_choice:
            layout_mode = "smart_crop"
        else:
            layout_mode = "center_crop"

        # 3-2. 쇼츠 길이
        dur_choice = questionary.select(
            "👉 쇼츠 목표 길이를 선택하세요:",
            choices=[
                "⏱ 1) 30초 ~ 50초 (유튜브 쇼츠 표준 추천)",
                "⚡ 2) 20초 ~ 35초 (짧고 빠른 템포)",
                "📖 3) 45초 ~ 60초 (풍부한 스토리 완결형)"
            ]
        ).ask()
        if "20초" in dur_choice:
            target_dur = (20, 35)
        elif "45초" in dur_choice:
            target_dur = (45, 60)
        else:
            target_dur = (30, 50)

        # 3-3. 효과 여부
        show_badge = questionary.confirm("👉 상단 훅(Hook) 타이틀 뱃지를 넣으시겠습니까?", default=True).ask()
        show_progress_bar = questionary.confirm("👉 하단 다이내믹 프로그레스 바를 넣으시겠습니까?", default=True).ask()

    console.print("\n[bold green]✔ 모든 설정이 완료되었습니다! 쇼츠 생성을 시작합니다.[/bold green]\n")

    # Step 4: 생성 > 진행 과정 안내 문구 및 진행 퍼센트 게이지 노출
    run_with_progress(
        source=source,
        clips_count=clips_count,
        layout_mode=layout_mode,
        show_badge=show_badge,
        show_progress_bar=show_progress_bar,
        target_dur=target_dur
    )

def run_with_progress(
    source: str,
    clips_count: int,
    layout_mode: str,
    show_badge: bool,
    show_progress_bar: bool,
    target_dur: tuple[int, int]
):
    pipeline = ShortsPipeline(
        whisper_model="small",
        llm_model="qwen2.5:7b",
        layout_mode=layout_mode,
        show_badge=show_badge,
        show_progress_bar=show_progress_bar,
        normalize_audio=True
    )

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, style="bright_black", complete_style="bold yellow"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        expand=False
    ) as progress:
        task_id = progress.add_task("[1/4] 파이프라인 초기화 중...", total=100)

        def on_progress(pct: float, message: str):
            progress.update(task_id, completed=pct, description=message)

        results = pipeline.run(
            source=source,
            max_clips=clips_count,
            target_duration=target_dur,
            callback=on_progress
        )
        progress.update(task_id, completed=100, description="[bold green]🎉 모든 쇼츠 생성 완료![/bold green]")

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
    console.print("\n[bold green]✨ 모든 작업이 성공적으로 끝났습니다![/bold green]\n")

    # Ask to open in Finder
    try:
        open_finder = questionary.confirm("📂 생성된 쇼츠 폴더(output)를 Finder에서 여시겠습니까?", default=True).ask()
        if open_finder:
            subprocess.run(["open", "output"])
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(
        description="🎬 유튜브/로컬 영상 -> 9:16 쇼츠 자동 변환기",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("source", nargs="?", help="유튜브 URL 또는 파일 경로 (생략 시 대화형 마법사 실행)")
    parser.add_argument("-s", "--source-opt", dest="source_opt", help="소스 지정")
    parser.add_argument("-c", "--clips", type=int, default=1, help="생성할 쇼츠 개수")
    parser.add_argument("-l", "--layout", choices=["blur_background", "smart_crop", "center_crop"], default="blur_background")
    parser.add_argument("-w", "--whisper", default="small", choices=["base", "small", "medium", "large-v3-turbo"])
    parser.add_argument("-m", "--llm", default="qwen2.5:7b", help="Ollama 로컬 모델")
    parser.add_argument("--no-badge", action="store_true", help="상단 훅 뱃지 끄기")
    parser.add_argument("--no-progress", action="store_true", help="하단 프로그레스 바 끄기")
    parser.add_argument("--min-dur", type=int, default=30)
    parser.add_argument("--max-dur", type=int, default=50)

    return parser.parse_args()

def main():
    args = parse_args()
    source = args.source or args.source_opt

    # If no arguments given, run the interactive wizard!
    if not source:
        try:
            interactive_wizard()
        except KeyboardInterrupt:
            console.print("\n[yellow]작업이 취소되었습니다.[/yellow]")
            sys.exit(0)
        return

    # Otherwise run directly in CLI mode
    pipeline = ShortsPipeline(
        whisper_model=args.whisper,
        llm_model=args.llm,
        layout_mode=args.layout,
        show_badge=not args.no_badge,
        show_progress_bar=not args.no_progress,
        normalize_audio=True
    )

    try:
        pipeline.run(
            source=source,
            max_clips=args.clips,
            target_duration=(args.min_dur, args.max_dur)
        )
    except Exception as e:
        console.print(f"\n[bold red]❌ 실행 중 오류 발생:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
