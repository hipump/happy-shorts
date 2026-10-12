from dataclasses import dataclass
from typing import Tuple, Dict, Optional

@dataclass
class ShortsTemplate:
    id: str
    name: str
    category: str
    description: str
    layout_type: str              # "news_portal", "browser_window", "neon_magazine", "minimal_edu", "smart_crop", "source_pure"
    badge_style: str              # "gold_pill", "red_pill", "minimal_pill", "none"
    badge_prefix: str             # "[TIP]", "[속보]", "[KEY]", "[NOTE]"
    subtitle_style: str           # "viral_pop", "clean_minimal", "none"
    active_color: Tuple[int, int, int]
    normal_color: Tuple[int, int, int]
    marker_color: Tuple[int, int, int, int] # RGBA highlighter marker tape
    font_name: str                # "black_han_sans", "pretendard"
    video_box: Tuple[int, int, int, int]    # (x, y, w, h)
    subtitle_y: int

TEMPLATES: Dict[str, ShortsTemplate] = {
    "news_portal": ShortsTemplate(
        id="news_portal",
        name="[뉴스·속보·이슈] 미리캔버스 뉴스 포털 & 긴급 속보 템플릿",
        category="뉴스 및 이슈",
        description="Clean 화이트 포털 + 레드 방송 헤더 + 형광펜 2단 헤드라인 + 뉴스 브리핑 자막 덱",
        layout_type="news_portal",
        badge_style="red_pill",
        badge_prefix="[속보]",
        subtitle_style="viral_pop",
        active_color=(255, 230, 0),        # Broadcast Yellow
        normal_color=(255, 255, 255),      # Crisp White
        marker_color=(215, 25, 35, 220),   # Broadcast Red Marker Strip
        font_name="black_han_sans",
        video_box=(70, 460, 940, 528),
        subtitle_y=1188
    ),
    "browser_window": ShortsTemplate(
        id="browser_window",
        name="[정보·리뷰·테크] 인터넷창 / macOS 브라우저 창 썸네일형",
        category="정보 및 리뷰",
        description="다크 네이비 메쉬 데스크 + 맥OS 윈도우 프레임 + 3D 폰트 + 해시태그 칩스",
        layout_type="browser_window",
        badge_style="gold_pill",
        badge_prefix="[TIP]",
        subtitle_style="viral_pop",
        active_color=(255, 230, 0),        # Cyber Yellow
        normal_color=(255, 255, 255),      # White
        marker_color=(0, 255, 180, 210),   # Cyber Mint
        font_name="black_han_sans",
        video_box=(70, 435, 940, 528),
        subtitle_y=1120
    ),
    "neon_magazine": ShortsTemplate(
        id="neon_magazine",
        name="[매거진·인포·네온] 캔바 & 알파컷 인포 매거진 템플릿",
        category="인포 매거진",
        description="럭셔리 다크 슬레이트 + 네온 사이언 발광 보더 + 형광펜 하이라이트 + 핵심 요약 카드",
        layout_type="neon_magazine",
        badge_style="gold_pill",
        badge_prefix="[KEY]",
        subtitle_style="viral_pop",
        active_color=(0, 255, 220),        # Neon Cyan
        normal_color=(255, 255, 255),      # White
        marker_color=(255, 230, 0, 220),   # Marker Yellow
        font_name="black_han_sans",
        video_box=(50, 350, 980, 551),
        subtitle_y=1040
    ),
    "minimal_edu": ShortsTemplate(
        id="minimal_edu",
        name="[교육·강의·미니멀] 캔바 모던 클린 템플릿",
        category="교육 및 강의",
        description="모던 슬레이트 캔버스 + 깔끔한 1분 지식 카드 + 프리텐다드 클린 자막",
        layout_type="minimal_edu",
        badge_style="minimal_pill",
        badge_prefix="[NOTE]",
        subtitle_style="clean_minimal",
        active_color=(255, 255, 255),
        normal_color=(200, 210, 225),
        marker_color=(50, 130, 255, 180),
        font_name="pretendard",
        video_box=(70, 440, 940, 528),
        subtitle_y=1140
    ),
    "interview_talk": ShortsTemplate(
        id="interview_talk",
        name="[인터뷰·토크] 9:16 인물 추적 풀스크린 (호르모지 스타일)",
        category="인터뷰 및 토크",
        description="9:16 스마트 인물 추적 + 상단 인트로 훅 글래스 카드 + 팝업 키네틱 자막",
        layout_type="smart_crop",
        badge_style="gold_pill",
        badge_prefix="[TALK]",
        subtitle_style="viral_pop",
        active_color=(255, 230, 0),
        normal_color=(255, 255, 255),
        marker_color=(255, 230, 0, 210),
        font_name="black_han_sans",
        video_box=(0, 0, 1080, 1920),
        subtitle_y=1320
    ),
    "source_pure": ShortsTemplate(
        id="source_pure",
        name="[순정 원본 보존] 자체 자막 유지 템플릿",
        category="자체 자막 영상",
        description="화면 공유/강의/자체 자막이 이미 있는 영상용 (새 자막 없이 영상 100% 보존)",
        layout_type="source_pure",
        badge_style="gold_pill",
        badge_prefix="[CLIP]",
        subtitle_style="none",
        active_color=(255, 230, 0),
        normal_color=(255, 255, 255),
        marker_color=(255, 230, 0, 210),
        font_name="black_han_sans",
        video_box=(70, 450, 940, 528),
        subtitle_y=0
    ),
}

# Aliases for backward compatibility
TEMPLATES["breaking_news"] = TEMPLATES["news_portal"]
TEMPLATES["tech_review"] = TEMPLATES["browser_window"]

def get_template(template_id: str) -> ShortsTemplate:
    return TEMPLATES.get(template_id, TEMPLATES["browser_window"])

