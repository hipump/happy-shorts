#!/usr/bin/env bash
# Happy Shorts AI Studio - 웹 GUI 원클릭 실행 스크립트
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export NONINTERACTIVE=1
export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_NO_ENV_HINTS=1
export HOMEBREW_NO_INSTALL_CLEANUP=1

# Homebrew 경로 로드 (Apple Silicon & Intel)
if [ -x "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x "/usr/local/bin/brew" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

echo "🎬 ================================================================"
echo "   Happy Shorts AI Studio (웹 GUI 대시보드)"
echo "   100% 로컬 무료 구동 | Qwen2.5-14B & Whisper Large-v3-Turbo"
echo "================================================================"

# 1. 필수 환경 미설치 시 setup.sh 자동 실행
if [ ! -d ".venv" ] || [ ! -d "web/node_modules" ] || ! command -v ffmpeg &>/dev/null || ! command -v ollama &>/dev/null; then
    echo "⚡ 필수 구동 환경(.venv, npm 모듈, ffmpeg, ollama 등)이 감지되지 않았습니다."
    echo "👉 올인원 원클릭 설치 스크립트(setup.sh)를 자동으로 먼저 실행합니다..."
    echo ""
    chmod +x ./setup.sh
    ./setup.sh
    
    if [ -x "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -x "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

# 가상환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 2. Ollama 백그라운드 데몬 구동 확인
if ! curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
    echo "ℹ️ Ollama 로컬 LLM 백그라운드 서비스를 시작합니다..."
    ollama serve >/dev/null 2>&1 &
    
    for i in {1..15}; do
        if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
            break
        fi
        sleep 1
    done
fi

# 기동 전 및 종료 시 포트 정리 함수
free_port() {
    local port=$1
    local pids=$(lsof -ti :"$port" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        kill -9 $pids 2>/dev/null || true
    fi
}

# 종료 시 백엔드와 프론트엔드 프로세스 동시 종료
cleanup() {
    echo ""
    echo "🛑 서버를 안전하게 종료합니다..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    free_port 8000
    free_port 3000
    exit 0
}
trap cleanup SIGINT SIGTERM

# 기동 전 기존에 남아있는 좀비 포트 정리
free_port 8000
free_port 3000

# 2. FastAPI 백엔드 서버 시작 (포트 8000)
echo "🚀 1/2. Python FastAPI 백엔드 기동 중 (http://127.0.0.1:8000)..."
python -m uvicorn server:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# 백엔드 기동 대기
sleep 1.5

# 3. Next.js 프론트엔드 서버 시작 (포트 3000)
echo "🌐 2/2. Next.js 프론트엔드 기동 중 (http://localhost:3000)..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

# 4. 브라우저 자동 오픈
sleep 2.5
echo ""
echo "✨ 준비 완료! 웹 브라우저를 엽니다: http://localhost:3000"
echo "👉 서버를 종료하려면 터미널에서 Ctrl + C 를 누르세요."
echo ""
open "http://localhost:3000" 2>/dev/null || true

# 프로세스 대기
wait
