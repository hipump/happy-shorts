#!/usr/bin/env bash
# ==============================================================================
# Happy Shorts AI Studio - 올인원 원클릭 실행 스크립트 (start.sh)
# 미설치 상태일 경우 setup.sh 자동 감지 및 설치 후 실행
# ==============================================================================

set -eo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Homebrew 경로 로드 (Apple Silicon & Intel)
if [ -x "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x "/usr/local/bin/brew" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

echo -e "${PURPLE}${BOLD}"
echo "================================================================="
echo "   🎬 Happy Shorts AI Studio 구동기"
echo "   100% 로컬 무료 구동 | Qwen2.5-14B & Whisper Large-v3-Turbo"
echo -e "=================================================================${NC}"

# 1. 필수 환경 미설치 시 setup.sh 자동 실행
if [ ! -d ".venv" ] || [ ! -d "web/node_modules" ] || ! command -v ffmpeg &>/dev/null || ! command -v ollama &>/dev/null; then
    echo -e "${YELLOW}⚡ 시스템에 아직 설치되지 않은 필수 요소가 감지되었습니다.${NC}"
    echo -e "${CYAN}👉 올인원 자동 설치 스크립트(setup.sh)를 먼저 실행합니다...${NC}\n"
    chmod +x ./setup.sh
    ./setup.sh
    
    # setup.sh 실행 후 Homebrew 환경 다시 로드
    if [ -x "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -x "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

source .venv/bin/activate

# 2. Ollama 백그라운드 데몬 구동 확인
if ! curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
    echo -e "${BLUE}ℹ Ollama 백그라운드 데몬을 기동합니다...${NC}"
    ollama serve >/dev/null 2>&1 &
    
    for i in {1..15}; do
        if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
            break
        fi
        sleep 1
    done
fi

# 3. 포트 충돌 방지 및 기존 좀비 프로세스 정리 함수
check_and_free_port() {
    local port=$1
    local pids=$(lsof -ti :"$port" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        kill -9 $pids 2>/dev/null || true
        sleep 0.3
    fi
}

# 4. 종료 시 모든 하위 프로세스(백엔드, 프론트엔드) 안전 종료
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 스튜디오 서비스를 안전하게 종료합니다...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    check_and_free_port 8000
    check_and_free_port 3000
    exit 0
}
trap cleanup SIGINT SIGTERM

# 기동 전 기존 포트 충돌 정리
check_and_free_port 8000
check_and_free_port 3000
mkdir -p temp

# 5. FastAPI 백엔드 서버 시작 (포트 8000)
echo -e "${CYAN}🚀 1/2. Python FastAPI 백엔드 서버 기동 중 (http://127.0.0.1:8000)...${NC}"
python -m uvicorn server:app --host 127.0.0.1 --port 8000 > temp/backend.log 2>&1 &
BACKEND_PID=$!

# 6. Next.js 프론트엔드 서버 시작 (포트 3000)
echo -e "${CYAN}🌐 2/2. Next.js 웹 대시보드 기동 중 (http://localhost:3000)...${NC}"
cd web
npm run dev > ../temp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# 7. 서비스 헬스체크 및 조기 실패 감지
echo -e "${BLUE}⏳ 서버 기동 대기 중...${NC}"
for i in {1..35}; do
    # 조기 충돌 감지
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${RED}✖ 백엔드 서버가 시작 도중 종료되었습니다. (오류 로그 확인):${NC}"
        tail -n 25 temp/backend.log
        cleanup
    fi
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${RED}✖ 웹 대시보드가 시작 도중 종료되었습니다. (오류 로그 확인):${NC}"
        tail -n 25 temp/frontend.log
        cleanup
    fi

    if curl -s http://127.0.0.1:8000/api/status &>/dev/null && curl -s http://localhost:3000 &>/dev/null; then
        break
    fi
    sleep 0.8
done

echo ""
echo -e "${GREEN}${BOLD}================================================================="
echo "   ✨ Happy Shorts AI Studio가 성공적으로 실행되었습니다!"
echo "   🌐 웹 대시보드 URL: http://localhost:3000"
echo "   🔌 백엔드 API URL: http://127.0.0.1:8000"
echo -e "=================================================================${NC}"
echo -e "💡 팁: 서비스를 종료하려면 언제든지 터미널에서 ${YELLOW}${BOLD}Ctrl + C${NC} 를 누르세요.\n"

# 브라우저 자동 오픈
open "http://localhost:3000" 2>/dev/null || true

# 프로세스 유지 대기
wait
