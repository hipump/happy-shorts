from dataclasses import dataclass
from typing import Tuple, Dict, Optional

@dataclass
class ShortsTemplate:
    id: str
    name: str
    category: str
    description: str
    layout_type: str              # "news_portal", "browser_window", "neon_magazine", "minimal_edu", "smart_crop", "source_pure", "messenger_chat", "ranking_chart", "product_review", "motivation_quote", "quiz_balance", "vlog_polaroid"
    badge_style: str              # "gold_pill", "red_pill", "minimal_pill", "none"
    badge_prefix: str             # "[TIP]", "[속보]", "[KEY]", "[NOTE]", "[CHAT]", "[TOP 1]", "[리뷰]", "[명언]", "[QUIZ]", "[VLOG]"
    subtitle_style: str           # "viral_pop", "clean_minimal", "none"
    active_color: Tuple[int, int, int]
    normal_color: Tuple[int, int, int]
    marker_color: Tuple[int, int, int, int] # RGBA highlighter marker tape
    font_name: str                # "black_han_sans", "pretendard"
    video_box: Tuple[int, int, int, int]    # (x, y, w, h)
    subtitle_y: int

TEMPLATES: Dict[str, ShortsTemplate] = {
    # 1. 뉴스 & 속보
    "news_portal": ShortsTemplate(
        id="news_portal",
        name="[뉴스·속보] 미리캔버스 뉴스 포털 & 긴급 속보 템플릿",
        category="뉴스 및 이슈",
        description="Clean 화이트 포털 + 레드 방송 LIVE 헤더 + 형광펜 헤드라인 + 뉴스 브리핑 덱",
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

    # 2. 브라우저 창
    "browser_window": ShortsTemplate(
        id="browser_window",
        name="[정보·리뷰·테크] 인터넷창 / macOS 브라우저 창 썸네일형",
        category="정보 및 리뷰",
        description="다크 네이비 메쉬 데스크 + 맥OS 윈도우 프레임 🔴🟡🟢 + 3D 폰트 + 해시태그 칩스",
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

    # 3. 네온 매거진
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

    # 4. 모던 클린 교육
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

    # 5. 카카오톡 / 메신저 대화 (NEW)
    "messenger_chat": ShortsTemplate(
        id="messenger_chat",
        name="[메신저·카톡·썰] 미리캔버스 메신저 채팅 대화 템플릿",
        category="메신저 및 대화",
        description="모바일 채팅방 프로필 + 카톡 옐로우 말풍선 + 질문 & 답변 스토리형 템플릿",
        layout_type="messenger_chat",
        badge_style="gold_pill",
        badge_prefix="[CHAT]",
        subtitle_style="viral_pop",
        active_color=(254, 229, 0),        # Kakao Yellow
        normal_color=(255, 255, 255),
        marker_color=(254, 229, 0, 220),
        font_name="pretendard",
        video_box=(60, 450, 960, 540),
        subtitle_y=1160
    ),

    # 6. 랭킹 TOP 5 차트 (NEW)
    "ranking_chart": ShortsTemplate(
        id="ranking_chart",
        name="[랭킹·차트·순위] 100만 유튜버 추천 랭킹 TOP 템플릿",
        category="랭킹 및 퀴즈",
        description="골드 트로피 🏆 뱃지 + TOP 순위 인포그래픽 바 + 오렌지 불꽃 헤드라인",
        layout_type="ranking_chart",
        badge_style="gold_pill",
        badge_prefix="[TOP 1]",
        subtitle_style="viral_pop",
        active_color=(255, 130, 0),        # Vivid Orange
        normal_color=(255, 255, 255),
        marker_color=(255, 160, 0, 220),
        font_name="black_han_sans",
        video_box=(70, 430, 940, 528),
        subtitle_y=1130
    ),

    # 7. 내돈내산 상품 리뷰 & 별점 (NEW)
    "product_review": ShortsTemplate(
        id="product_review",
        name="[리뷰·쇼핑·추천] 5성 별점 ★★★★★ 내돈내산 솔직 리뷰",
        category="상품 및 리뷰",
        description="별점 레이팅 뱃지 + 장점/단점 큐레이션 박스 + 민트 & 화이트 클린 프레임",
        layout_type="product_review",
        badge_style="gold_pill",
        badge_prefix="[리뷰]",
        subtitle_style="viral_pop",
        active_color=(0, 230, 160),        # Mint Green
        normal_color=(255, 255, 255),
        marker_color=(0, 230, 160, 210),
        font_name="pretendard",
        video_box=(60, 420, 960, 540),
        subtitle_y=1120
    ),

    # 8. 동기부여 & 명언 매거진 (NEW)
    "motivation_quote": ShortsTemplate(
        id="motivation_quote",
        name="[동기부여·명언·책] 감성 블랙 & 골드 타이포 매거진",
        category="동기부여 및 명언",
        description="럭셔리 매트 블랙 + 골드 따옴표 인용구 + 감성 서체 + 1분 인생 교훈 카드",
        layout_type="motivation_quote",
        badge_style="gold_pill",
        badge_prefix="[명언]",
        subtitle_style="clean_minimal",
        active_color=(245, 200, 80),       # Luxury Gold
        normal_color=(230, 235, 245),
        marker_color=(245, 200, 80, 190),
        font_name="pretendard",
        video_box=(70, 460, 940, 528),
        subtitle_y=1150
    ),

    # 9. 밸런스 게임 & 퀴즈 (NEW)
    "quiz_balance": ShortsTemplate(
        id="quiz_balance",
        name="[퀴즈·게임·질문] 당신의 선택은? 밸런스 게임 쇼츠",
        category="랭킹 및 퀴즈",
        description="A vs B 대비 스플릿 박스 + 긴장감 넘치는 질문 덱 + 인터랙티브 투표 룩",
        layout_type="quiz_balance",
        badge_style="red_pill",
        badge_prefix="[QUIZ]",
        subtitle_style="viral_pop",
        active_color=(255, 70, 85),        # Coral Red
        normal_color=(255, 255, 255),
        marker_color=(255, 70, 85, 210),
        font_name="black_han_sans",
        video_box=(60, 440, 960, 540),
        subtitle_y=1150
    ),

    # 10. 감성 브이로그 & 일상 폴라로이드 (NEW)
    "vlog_polaroid": ShortsTemplate(
        id="vlog_polaroid",
        name="[브이로그·일상·여행] 인스타 감성 폴라로이드 템플릿",
        category="브이로그 및 일상",
        description="아날로그 필름 테두리 + 마스킹 테이프 스티커 + 감성 일기 기록 박스",
        layout_type="vlog_polaroid",
        badge_style="minimal_pill",
        badge_prefix="[VLOG]",
        subtitle_style="clean_minimal",
        active_color=(255, 245, 220),
        normal_color=(220, 225, 230),
        marker_color=(240, 210, 170, 200),
        font_name="pretendard",
        video_box=(70, 400, 940, 528),
        subtitle_y=1120
    ),

    # 11. 인터뷰 9:16 인물 풀스크린
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

    # 12. 원본 순정 보존
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

    # 13. 화상통화 / FaceTime (MiriCanvas 인기)
    "facetime_call": ShortsTemplate(
        id="facetime_call",
        name="[화상통화·페이스타임] 화상미팅 / FaceTime 영상통화 UI",
        category="SNS 및 통화",
        description="아이폰 영상통화 화면 + 통화종료 🔴 버튼 & 카메라 아이콘 + 상단 배터리/시간 바",
        layout_type="facetime_call",
        badge_style="minimal_pill",
        badge_prefix="[CALL]",
        subtitle_style="viral_pop",
        active_color=(0, 255, 180),
        normal_color=(255, 255, 255),
        marker_color=(0, 255, 180, 210),
        font_name="pretendard",
        video_box=(0, 180, 1080, 1480),
        subtitle_y=1380
    ),

    # 14. 인스타그램 릴스 & 피드 (MiriCanvas 인기)
    "instagram_reels": ShortsTemplate(
        id="instagram_reels",
        name="[SNS·인스타] 인스타그램 릴스 & 피드 인터페이스",
        category="SNS 및 통화",
        description="인스타 우측 좋아요 ❤️ 2.5만, 댓글 💬, 공유 ✈️ + 계정 프로필 바 + 깔끔한 자막 덱",
        layout_type="instagram_reels",
        badge_style="gold_pill",
        badge_prefix="[REELS]",
        subtitle_style="viral_pop",
        active_color=(255, 230, 0),
        normal_color=(255, 255, 255),
        marker_color=(255, 45, 85, 210),
        font_name="pretendard",
        video_box=(0, 140, 1080, 1540),
        subtitle_y=1400
    ),

    # 15. 아이폰 갤러리 & 삭제 팝업 밈 (MiriCanvas 인기)
    "iphone_gallery": ShortsTemplate(
        id="iphone_gallery",
        name="[아이폰·갤러리] iOS 사진첩 & 삭제 경고 밈 템플릿",
        category="밈 및 썰",
        description="아이폰 갤러리 상단 네비게이션 + '이 사진이 모든 기기에서 삭제됩니다' 알림 팝업 밈",
        layout_type="iphone_gallery",
        badge_style="red_pill",
        badge_prefix="[MEME]",
        subtitle_style="viral_pop",
        active_color=(255, 59, 48),
        normal_color=(255, 255, 255),
        marker_color=(255, 59, 48, 210),
        font_name="pretendard",
        video_box=(60, 320, 960, 960),
        subtitle_y=1400
    ),

    # 16. 페페 & 카툰 컷분할 리액션 (MiriCanvas 인기)
    "meme_cartoon": ShortsTemplate(
        id="meme_cartoon",
        name="[밈·웹툰·리액션] 페페 & 카툰 컷 분할 리액션 템플릿",
        category="밈 및 썰",
        description="웹툰 볼드 컷 분할 프레임 + 만화 대사 말풍선 + 페페/밈 리액션 스티커",
        layout_type="meme_cartoon",
        badge_style="gold_pill",
        badge_prefix="[CARTOON]",
        subtitle_style="viral_pop",
        active_color=(255, 220, 0),
        normal_color=(255, 255, 255),
        marker_color=(255, 220, 0, 220),
        font_name="black_han_sans",
        video_box=(60, 420, 960, 640),
        subtitle_y=1180
    ),

    # 17. 금주 개봉작 시네마틱 필름 티켓 (MiriCanvas 인기)
    "cinema_preview": ShortsTemplate(
        id="cinema_preview",
        name="[영화·드라마·프리뷰] 금주 개봉작 시네마틱 필름 티켓",
        category="영화 및 리뷰",
        description="클래식 필름 레터박스 + 상단 티켓 바코드/날짜 + 5성 평점 + 감성 시네마틱 프레임",
        layout_type="cinema_preview",
        badge_style="gold_pill",
        badge_prefix="[FILM]",
        subtitle_style="clean_minimal",
        active_color=(245, 210, 110),
        normal_color=(230, 235, 245),
        marker_color=(245, 210, 110, 190),
        font_name="pretendard",
        video_box=(50, 420, 980, 551),
        subtitle_y=1120
    ),

    # 18. 흔한 팬의 일상 원형 차트 (MiriCanvas 인기)
    "pie_chart_reaction": ShortsTemplate(
        id="pie_chart_reaction",
        name="[공감·차트·썰] 흔한 팬의 일상.. 분노·답답함 99% 원형 차트",
        category="랭킹 및 퀴즈",
        description="공감 100% 원형 그래프 인포그래픽 + 팩트 폭격 헤드라인 + 감정 통계 덱",
        layout_type="pie_chart_reaction",
        badge_style="red_pill",
        badge_prefix="[공감]",
        subtitle_style="viral_pop",
        active_color=(255, 80, 70),
        normal_color=(255, 255, 255),
        marker_color=(255, 80, 70, 210),
        font_name="black_han_sans",
        video_box=(60, 400, 960, 540),
        subtitle_y=1120
    ),

    # 19. 오운완 챌린지 & 운동 미션 (MiriCanvas 인기)
    "challenge_fitness": ShortsTemplate(
        id="challenge_fitness",
        name="[운동·챌린지·동기부여] 오운완 챌린지 & D-Day 미션",
        category="동기부여 및 명언",
        description="열정 레드 & 네온 에너지 보더 + D-Day 카운트다운 뱃지 + 루틴 미션 체크리스트",
        layout_type="challenge_fitness",
        badge_style="red_pill",
        badge_prefix="[챌린지]",
        subtitle_style="viral_pop",
        active_color=(255, 60, 40),
        normal_color=(255, 255, 255),
        marker_color=(255, 60, 40, 220),
        font_name="black_han_sans",
        video_box=(60, 420, 960, 600),
        subtitle_y=1140
    ),

    # 20. 감성 습관 & 라이프스타일 3D 스티커 (MiriCanvas 인기)
    "vlog_sticker_lifestyle": ShortsTemplate(
        id="vlog_sticker_lifestyle",
        name="[감성·습관·브이로그] 나를 바꾼 습관 3가지 & 감성 3D 스티커",
        category="브이로그 및 감성",
        description="9:16 풀스크린 + SELF TALK 물결 태그 + 나를 바꾼 습관 감성 타이포 + ☕ 커피잔 / 🧘‍♀️ 요가 / 🌿 나무 스티커",
        layout_type="vlog_sticker_lifestyle",
        badge_style="minimal_pill",
        badge_prefix="[습관]",
        subtitle_style="clean_minimal",
        active_color=(232, 255, 130),       # Lime Yellow
        normal_color=(255, 255, 255),
        marker_color=(232, 255, 130, 200),
        font_name="pretendard",
        video_box=(0, 0, 1080, 1920),
        subtitle_y=1500
    ),

    # 21. 직장인 썰 & 머니 테이프 스티커 (MiriCanvas 인기)
    "vlog_money_salary": ShortsTemplate(
        id="vlog_money_salary",
        name="[직장인·머니·수입] 프리랜서 평균 수입 & 테이프 스티커",
        category="브이로그 및 감성",
        description="9:16 풀스크린 + 핑크 VLOG 캡슐 + 명조 타이틀 + '진짜 월 1000만원?' 민트 테이프 & 날아다니는 돈 💸 스티커",
        layout_type="vlog_money_salary",
        badge_style="minimal_pill",
        badge_prefix="[VLOG]",
        subtitle_style="viral_pop",
        active_color=(0, 255, 200),         # Mint Green
        normal_color=(255, 255, 255),
        marker_color=(0, 255, 200, 210),
        font_name="pretendard",
        video_box=(0, 0, 1080, 1920),
        subtitle_y=1480
    ),

    # 22. 미리짐 오운완 챌린지 & 이벤트 CTA (MiriCanvas 인기)
    "promo_fitness_gym": ShortsTemplate(
        id="promo_fitness_gym",
        name="[이벤트·프로모션] 미리짐 오운완 챌린지 & 참여방법 CTA",
        category="챌린지 및 프로모션",
        description="9:16 풀스크린 + MIRIGYM 상단 로고 + 볼드 타이포 + '▶ 참여방법' 레드 CTA 버튼 + 이벤트 혜택 안내",
        layout_type="promo_fitness_gym",
        badge_style="red_pill",
        badge_prefix="[EVENT]",
        subtitle_style="viral_pop",
        active_color=(255, 50, 60),         # Vivid Red
        normal_color=(255, 255, 255),
        marker_color=(255, 50, 60, 220),
        font_name="black_han_sans",
        video_box=(0, 0, 1080, 1920),
        subtitle_y=1420
    ),

    # 23. 모르면 손해보는 청년혜택 총정리 (MiriCanvas 인기)
    "youth_tips_pick": ShortsTemplate(
        id="youth_tips_pick",
        name="[꿀팁·정보·PICK] 모르면 손해보는 청년혜택 총정리",
        category="정보 및 리뷰",
        description="9:16 풀스크린 + '놓치면 진짜 아까워요!' 감성 서브헤드 + [청년혜택] 형광 옐로우 박스 + 좌하단 PICK! 강조 스티커",
        layout_type="youth_tips_pick",
        badge_style="gold_pill",
        badge_prefix="[꿀팁]",
        subtitle_style="viral_pop",
        active_color=(255, 235, 0),         # Neon Yellow
        normal_color=(255, 255, 255),
        marker_color=(255, 235, 0, 220),
        font_name="black_han_sans",
        video_box=(0, 0, 1080, 1920),
        subtitle_y=1400
    ),

    # 24. 이번 주 짧은 드라마 명장면 다시보기 (MiriCanvas 인기)
    "drama_weekly_preview": ShortsTemplate(
        id="drama_weekly_preview",
        name="[드라마·영화·큐레이션] 이번 주 가장 많이 본 명장면 다시보기",
        category="영화 및 리뷰",
        description="9:16 풀스크린 + 상단 레드 '▶ 이번 주 짧은 드라마' 뱃지 + '가장 많이 본 장면' 다시 보기 + WEEKLY PREVIEW 카드",
        layout_type="drama_weekly_preview",
        badge_style="red_pill",
        badge_prefix="[명장면]",
        subtitle_style="viral_pop",
        active_color=(255, 60, 60),
        normal_color=(255, 255, 255),
        marker_color=(255, 60, 60, 220),
        font_name="black_han_sans",
        video_box=(0, 0, 1080, 1920),
        subtitle_y=1380
    ),

    # 25. 테슬라 FSD v13.2 자율주행 대시보드 (사용자 요청 테슬라 테마)
    "tesla_fsd_vision": ShortsTemplate(
        id="tesla_fsd_vision",
        name="[테크·테슬라·HUD] 테슬라 FSD v13.2 자율주행 대시보드",
        category="테슬라 및 테크",
        description="테슬라 특유의 사이버 감성 UI + 상단 레드 T 로고 & FSD v13.2 자율주행 HUD + 105km/h 계기판 + 하단 차량 제어 독",
        layout_type="tesla_fsd_vision",
        badge_style="red_pill",
        badge_prefix="[TESLA]",
        subtitle_style="viral_pop",
        active_color=(235, 25, 45),         # Tesla Red
        normal_color=(255, 255, 255),
        marker_color=(235, 25, 45, 220),
        font_name="pretendard",
        video_box=(0, 0, 1080, 1920),
        subtitle_y=1440
    ),
}

# Aliases for backward compatibility
TEMPLATES["breaking_news"] = TEMPLATES["news_portal"]
TEMPLATES["tech_review"] = TEMPLATES["browser_window"]

def get_template(template_id: str) -> ShortsTemplate:
    return TEMPLATES.get(template_id, TEMPLATES["browser_window"])
