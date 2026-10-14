#!/usr/bin/env bash
# Happy Shorts AI Studio - 웹 GUI 원클릭 실행 스크립트
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. 가상환경 확인
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ 가상환경(.venv)이 존재하지 않습니다."
    exit 1
fi

echo "🎬 ================================================================"
echo "   Happy Shorts AI Studio (웹 GUI 대시보드)"
echo "   100% 로컬 무료 구동 | Qwen2.5-14B & Whisper Large-v3-Turbo"
echo "================================================================"

# 종료 시 백엔드와 프론트엔드 프로세스 동시 종료
cleanup() {
    echo ""
    echo "🛑 서버를 안전하게 종료합니다..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

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
