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
from src.templates import TEMPLATES, get_template, ShortsTemplate

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
        "스텝 2/5. 생성할 쇼츠(하이라이트) 개수를 선택하세요:",
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

    # Step 3: 디자인 템플릿 선택 (미리캔버스 / 캔바 / 알파컷 스타일)
    tpl_choice = questionary.select(
        "스텝 3/5. 적용할 쇼츠 디자인 템플릿을 선택하세요 (미리캔버스·캔바·알파컷 기반):",
        choices=[
            "💻 1) [정보·리뷰·테크] 인터넷창 / macOS 브라우저 창 썸네일형 (트래픽라이트 🔴🟡🟢 + 3D 폰트 + 해시태그)",
            "🚨 2) [뉴스·속보·이슈] 미리캔버스 뉴스 포털 & 긴급 속보형 (Clean 화이트 + 방송 레드 헤더 + 형광펜 헤드라인)",
            "✨ 3) [매거진·인포·네온] 캔바 & 알파컷 인포 매거진 템플릿 (다크 슬레이트 + 네온 사이언 보더 + 요약 카드)",
            "💡 4) [교육·강의·미니멀] 캔바 모던 클린 템플릿 (모던 슬레이트 + 프리텐다드 서체 자막)",
            "👤 5) [인터뷰·토크] 9:16 인물 추적 풀스크린 (호르모지 스타일)",
            "🎞 6) [순정 원본 보존] 자체 자막 유지 템플릿 (영상 원본 100% 보존, 추가 자막 없음)",
            "🎨 7) [세부 맞춤 설정] 레이아웃, 자막 스타일 직접 세부 설정"
        ]
    ).ask()

    if not tpl_choice:
        sys.exit(0)

    template = get_template("browser_window")

    if "뉴스" in tpl_choice or "속보" in tpl_choice:
        template = get_template("news_portal")
    elif "매거진" in tpl_choice or "네온" in tpl_choice:
        template = get_template("neon_magazine")
    elif "인터넷창" in tpl_choice or "브라우저" in tpl_choice:
        template = get_template("browser_window")
    elif "인터뷰" in tpl_choice:
        template = get_template("interview_talk")
    elif "교육" in tpl_choice:
        template = get_template("minimal_edu")
    elif "순정" in tpl_choice:
        template = get_template("source_pure")
    elif "맞춤 설정" in tpl_choice:
        # Custom fine-tuning
        layout_choice = questionary.select(
            "👉 레이아웃 선택:",
            choices=["인터넷창 / 맥OS 브라우저형", "뉴스 포털 & 긴급 속보형", "스마트 인물 크롭 (9:16)", "블러 배경"]
        ).ask()
        layout_mode = "browser_window" if "브라우저" in layout_choice else ("news_portal" if "뉴스" in layout_choice else ("smart_crop" if "스마트" in layout_choice else "blur_background"))

        show_badge = questionary.confirm("👉 상단 3초 인트로 훅 뱃지 노출 여부:", default=True).ask()

        template = ShortsTemplate(
            id="custom",
            name="사용자 지정 커스텀",
            category="커스텀",
            description="사용자가 직접 구성한 스타일",
            layout_type=layout_mode,
            badge_style="gold_pill" if show_badge else "none",
            badge_prefix="🔥",
            subtitle_style="viral_pop",
            active_color=(255, 230, 0),
            normal_color=(255, 255, 255),
            marker_color=(0, 255, 180, 200),
            font_name="black_han_sans",
            video_box=(70, 435, 940, 528),
            subtitle_y=1120
        )

    # Step 4: 자막(캡션) 생성 여부 및 스타일 선택
    default_sub_idx = 0
    if template.subtitle_style == "none":
        default_sub_idx = 2
    elif template.subtitle_style == "clean_minimal":
        default_sub_idx = 1

    sub_choices = [
        "🔥 1) 바이럴 키네틱 팝 자막 (단어별 형광펜 하이라이트 + 굵은 외곽선 / 추천)",
        "💬 2) 클린 미니멀 자막 (깔끔하고 단정한 프리텐다드 서체 자막)",
        "🚫 3) 자막 생성 안 함 (영상 원본 자체 자막 유지 또는 자막 없이 생성)"
    ]

    sub_choice = questionary.select(
        "스텝 4/5. 자막(캡션) 생성 여부 및 스타일을 선택하세요:",
        choices=sub_choices,
        default=sub_choices[default_sub_idx]
    ).ask()

    if not sub_choice:
        sys.exit(0)

    if "바이럴" in sub_choice:
        show_subtitles = True
        sub_style = "viral_pop"
    elif "클린" in sub_choice:
        show_subtitles = True
        sub_style = "clean_minimal"
    else:
        show_subtitles = False
        sub_style = "none"

    template.subtitle_style = sub_style

    # Step 5: 쇼츠 목표 길이
    dur_choice = questionary.select(
        "스텝 5/5. 쇼츠 목표 길이를 선택하세요:",
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

    sub_desc = "바이럴 키네틱 자막" if sub_style == "viral_pop" else ("클린 미니멀 자막" if sub_style == "clean_minimal" else "자막 생성 안 함")
    console.print(f"\n[bold green]✔ [{template.name}] 템플릿 & [{sub_desc}] 설정 완료! 쇼츠 생성을 시작합니다.[/bold green]\n")

    # 실행
    run_with_progress(
        source=source,
        clips_count=clips_count,
        template=template,
        target_dur=target_dur,
        show_subtitles=show_subtitles,
        subtitle_style=sub_style
    )

def run_with_progress(
    source: str,
    clips_count: int,
    template: ShortsTemplate,
    target_dur: tuple[int, int],
    show_subtitles: bool = True,
    subtitle_style: str = "viral_pop"
):
    pipeline = ShortsPipeline(
        whisper_model="small",
        llm_model="qwen2.5:7b",
        template=template,
        layout_mode=template.layout_type,
        show_badge=template.badge_style != "none",
        badge_style=template.badge_style,
        badge_prefix=template.badge_prefix,
        show_subtitles=show_subtitles,
        subtitle_style=subtitle_style,
        active_color=template.active_color,
        normal_color=template.normal_color,
        font_name=template.font_name,
        show_progress_bar=False,
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
    parser.add_argument("-t", "--template", choices=list(TEMPLATES.keys()), default="tech_review", help="디자인 템플릿")
    parser.add_argument("-l", "--layout", choices=["studio_card", "smart_crop", "blur_background", "center_crop"], default=None, help="레이아웃 오버라이드")
    parser.add_argument("-w", "--whisper", default="small", choices=["base", "small", "medium", "large-v3-turbo"])
    parser.add_argument("-m", "--llm", default="qwen2.5:7b", help="Ollama 로컬 모델")
    parser.add_argument("--no-badge", action="store_true", help="상단 훅 뱃지 끄기")
    parser.add_argument("--no-subtitles", action="store_true", help="자막(캡션) 생성 끄기")
    parser.add_argument("--subtitle-style", choices=["viral_pop", "clean_minimal", "none"], default=None, help="자막 스타일 오버라이드")
    parser.add_argument("--min-dur", type=int, default=30)
    parser.add_argument("--max-dur", type=int, default=50)

    return parser.parse_args()

def main():
    args = parse_args()
    source = args.source or args.source_opt

    if not source:
        try:
            interactive_wizard()
        except KeyboardInterrupt:
            console.print("\n[yellow]작업이 취소되었습니다.[/yellow]")
            sys.exit(0)
        return

    tpl = get_template(args.template)
    layout_mode = args.layout or tpl.layout_type
    show_badge = not args.no_badge and tpl.badge_style != "none"
    show_subtitles = not args.no_subtitles and (args.subtitle_style != "none" if args.subtitle_style else tpl.subtitle_style != "none")
    sub_style = args.subtitle_style or tpl.subtitle_style

    pipeline = ShortsPipeline(
        whisper_model=args.whisper,
        llm_model=args.llm,
        template=tpl,
        layout_mode=layout_mode,
        show_badge=show_badge,
        badge_style=tpl.badge_style,
        badge_prefix=tpl.badge_prefix,
        show_subtitles=show_subtitles,
        subtitle_style=sub_style,
        active_color=tpl.active_color,
        normal_color=tpl.normal_color,
        font_name=tpl.font_name,
        show_progress_bar=False,
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
