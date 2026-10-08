#!/usr/bin/env bash
# Happy Shorts 대화형 실행 스크립트
set -e

# 프로젝트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 가상환경 확인 및 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ 가상환경(.venv)이 존재하지 않습니다."
    exit 1
fi

# 메인 프로그램 실행 (인자가 없으면 대화형 보기 선택 모드로 자동 진입)
python main.py "$@"
