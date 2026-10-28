#!/usr/bin/env bash
# ==============================================================================
# Happy Shorts AI Studio - macOS 올인원 설치 & 환경 구성 스크립트
# 지원 환경: macOS 13+ (Apple Silicon M1/M2/M3/M4 및 Intel Mac)
# ==============================================================================

set -eo pipefail

# Homebrew 무인 자동 설치 환경변수 설정 (대화형 프롬프트 대기 방지)
export NONINTERACTIVE=1
export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_NO_ENV_HINTS=1
export HOMEBREW_NO_INSTALL_CLEANUP=1

# 터미널 컬러 서식
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

log_step() {
    echo -e "\n${CYAN}${BOLD}[$1]${NC} ${BOLD}$2${NC}"
}
log_success() {
    echo -e "   ${GREEN}✔ $1${NC}"
}
log_warn() {
    echo -e "   ${YELLOW}⚠ $1${NC}"
}
log_info() {
    echo -e "   ${BLUE}ℹ $1${NC}"
}
log_error() {
    echo -e "   ${RED}✖ $1${NC}"
}

echo -e "${PURPLE}${BOLD}"
echo "================================================================="
echo "   🎬 Happy Shorts AI Studio - macOS 통합 원클릭 설치 스크립트"
echo "   100% 로컬 무료 구동 | Qwen2.5-14B & Whisper Large-v3-Turbo"
echo "================================================================="
echo -e "${NC}"

# ------------------------------------------------------------------------------
# 1. macOS 하드웨어 및 운영체제 환경 감지
# ------------------------------------------------------------------------------
log_step "1/8" "macOS 하드웨어 및 시스템 사양 감지"

OS_NAME="$(uname -s)"
if [ "$OS_NAME" != "Darwin" ]; then
    log_error "본 스크립트는 macOS 환경 전용입니다. (현재 OS: $OS_NAME)"
    exit 1
fi

ARCH="$(uname -m)"
OS_VER="$(sw_vers -productVersion)"
RAM_BYTES="$(sysctl -n hw.memsize 2>/dev/null || echo 0)"
RAM_GB=$((RAM_BYTES / 1024 / 1024 / 1024))

log_info "macOS 버전: ${OS_VER} (${ARCH})"
log_info "시스템 메모리: ${RAM_GB}GB RAM"
if [ "$ARCH" = "arm64" ]; then
    log_success "Apple Silicon (M시리즈) 가속 환경 감지됨"
else
    log_info "Intel x86_64 Mac 감지됨"
fi

# ------------------------------------------------------------------------------
# 2. Homebrew 패키지 관리자 확인 및 설정
# ------------------------------------------------------------------------------
log_step "2/8" "Homebrew 패키지 관리자 환경 검증"

# 기존 Homebrew 셸 환경 로드 (Apple Silicon & Intel 경로)
if [ -x "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x "/usr/local/bin/brew" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

if ! command -v brew &>/dev/null; then
    log_warn "Homebrew가 설치되어 있지 않습니다. 설치를 시작합니다..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    if [ -x "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -x "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    log_success "Homebrew 설치 및 셸 환경 설정 완료"
else
    log_success "Homebrew 설치 확인: $(brew --prefix)"
fi

# 차후 새 터미널 창에서도 brew가 유지되도록 ~/.zprofile 등록 확인
ZPROFILE="$HOME/.zprofile"
if [ -x "/opt/homebrew/bin/brew" ]; then
    if ! grep -qs "/opt/homebrew/bin/brew shellenv" "$ZPROFILE" 2>/dev/null; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$ZPROFILE"
    fi
elif [ -x "/usr/local/bin/brew" ]; then
    if ! grep -qs "/usr/local/bin/brew shellenv" "$ZPROFILE" 2>/dev/null; then
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> "$ZPROFILE"
    fi
fi

# ------------------------------------------------------------------------------
# 3. 필수 시스템 도구 설치 (git, ffmpeg, node, python, ollama)
# ------------------------------------------------------------------------------
log_step "3/8" "필수 시스템 도구 설치 및 최신화"

# Git (소스코드 및 모델 허브 통신)
if ! command -v git &>/dev/null; then
    log_info "Git이 감지되지 않아 Homebrew로 설치합니다 (brew install git)..."
    brew install git
    log_success "Git 설치 완료 ($(git --version))"
else
    log_success "Git 확인: $(git --version)"
fi

# FFmpeg (영상/오디오 처리 핵심 엔진)
if ! command -v ffmpeg &>/dev/null; then
    log_info "FFmpeg 초고속 설치 중 (의존성 컴파일 없는 완제품 네이티브 바이너리)..."
    INSTALLED_FFMPEG=0

    # 1순위: Apple Silicon(M시리즈) 초고속 완제품 바이너리 다운로드 (3초 완료)
    if [ "$ARCH" = "arm64" ]; then
        TMP_FF="/tmp/ffmpeg_dl_$$"
        mkdir -p "$TMP_FF"
        if curl -fsSL "https://github.com/Tyrrrz/FFmpegBin/releases/latest/download/ffmpeg-osx-arm64.zip" -o "$TMP_FF/ff.zip"; then
            unzip -q -o "$TMP_FF/ff.zip" -d "$TMP_FF"
            TARGET_BIN_DIR="/opt/homebrew/bin"
            [ ! -d "$TARGET_BIN_DIR" ] && TARGET_BIN_DIR="/usr/local/bin"
            [ ! -d "$TARGET_BIN_DIR" ] && TARGET_BIN_DIR="$HOME/.local/bin"
            mkdir -p "$TARGET_BIN_DIR"
            cp -f "$TMP_FF/ffmpeg" "$TMP_FF/ffprobe" "$TARGET_BIN_DIR/" 2>/dev/null || sudo cp -f "$TMP_FF/ffmpeg" "$TMP_FF/ffprobe" "$TARGET_BIN_DIR/"
            chmod +x "$TARGET_BIN_DIR/ffmpeg" "$TARGET_BIN_DIR/ffprobe"
            xattr -dr com.apple.quarantine "$TARGET_BIN_DIR/ffmpeg" "$TARGET_BIN_DIR/ffprobe" 2>/dev/null || true
            if command -v ffmpeg &>/dev/null; then
                INSTALLED_FFMPEG=1
                log_success "Apple Silicon FFmpeg 네이티브 바이너리 설치 완료 ($TARGET_BIN_DIR)"
            fi
        fi
        rm -rf "$TMP_FF"
    fi

    # 2순위: Intel Mac 또는 다운로드 실패 시 Homebrew 백업
    if [ "$INSTALLED_FFMPEG" -eq 0 ]; then
        log_info "Homebrew를 통해 FFmpeg 패키지를 설치합니다..."
        NONINTERACTIVE=1 brew install ffmpeg || true
    fi

    if command -v ffmpeg &>/dev/null; then
        log_success "FFmpeg 준비 완료 ($(ffmpeg -version | head -n1 | cut -d' ' -f3))"
    else
        log_error "FFmpeg 설치에 실패했습니다."
        exit 1
    fi
else
    log_success "FFmpeg 확인: $(ffmpeg -version | head -n1 | cut -d' ' -f3)"
fi

# Node.js & npm (Next.js 웹 UI 구동)
if ! command -v node &>/dev/null || ! command -v npm &>/dev/null; then
    log_info "Node.js 초고속 설치 중 (공식 네이티브 완제품 바이너리)..."
    INSTALLED_NODE=0

    # 1순위: Apple Silicon(M시리즈) 공식 완제품 바이너리 (의존성 컴파일 없는 3초 설치)
    if [ "$ARCH" = "arm64" ]; then
        TMP_NODE="/tmp/node_dl_$$"
        mkdir -p "$TMP_NODE"
        if curl -fsSL "https://nodejs.org/dist/v22.11.0/node-v22.11.0-darwin-arm64.tar.gz" -o "$TMP_NODE/node.tar.gz"; then
            mkdir -p "$TMP_NODE/pkg"
            tar -xzf "$TMP_NODE/node.tar.gz" -C "$TMP_NODE/pkg" --strip-components=1
            TARGET_BIN_DIR="/opt/homebrew/bin"
            [ ! -d "$TARGET_BIN_DIR" ] && TARGET_BIN_DIR="/usr/local/bin"
            [ ! -d "$TARGET_BIN_DIR" ] && TARGET_BIN_DIR="$HOME/.local/bin"
            mkdir -p "$TARGET_BIN_DIR"
            cp -rf "$TMP_NODE/pkg/bin/"* "$TARGET_BIN_DIR/" 2>/dev/null || sudo cp -rf "$TMP_NODE/pkg/bin/"* "$TARGET_BIN_DIR/"
            if [ -d "$TMP_NODE/pkg/lib" ]; then
                TARGET_LIB_DIR="/opt/homebrew/lib"
                [ ! -d "$TARGET_LIB_DIR" ] && TARGET_LIB_DIR="/usr/local/lib"
                [ ! -d "$TARGET_LIB_DIR" ] && TARGET_LIB_DIR="$HOME/.local/lib"
                mkdir -p "$TARGET_LIB_DIR"
                cp -rf "$TMP_NODE/pkg/lib/"* "$TARGET_LIB_DIR/" 2>/dev/null || sudo cp -rf "$TMP_NODE/pkg/lib/"* "$TARGET_LIB_DIR/"
            fi
            if command -v node &>/dev/null; then
                INSTALLED_NODE=1
                log_success "Node.js 공식 네이티브 바이너리 설치 완료 ($(node -v) / npm $(npm -v))"
            fi
        fi
        rm -rf "$TMP_NODE"
    fi

    # 2순위: Intel Mac 또는 다운로드 실패 시 Homebrew 백업
    if [ "$INSTALLED_NODE" -eq 0 ]; then
        log_info "Homebrew를 통해 Node.js 패키지를 설치합니다..."
        NONINTERACTIVE=1 brew install node || true
    fi

    if command -v node &>/dev/null; then
        log_success "Node.js 준비 완료 ($(node -v) / npm $(npm -v))"
    else
        log_error "Node.js 설치에 실패했습니다."
        exit 1
    fi
else
    log_success "Node.js 확인: $(node -v) / npm $(npm -v)"
fi

# Python 3.10+ 버전 확인 및 설치
PYTHON_BIN=""
for cmd in python3.11 python3.12 python3.10 python3; do
    if command -v "$cmd" &>/dev/null; then
        if "$cmd" -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
            PYTHON_BIN="$(command -v "$cmd")"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    log_warn "Python 3.10 이상 버전이 필요합니다. Homebrew로 python@3.11을 설치합니다..."
    brew install python@3.11
    if [ -x "/opt/homebrew/opt/python@3.11/bin/python3.11" ]; then
        PYTHON_BIN="/opt/homebrew/opt/python@3.11/bin/python3.11"
    elif [ -x "/usr/local/opt/python@3.11/bin/python3.11" ]; then
        PYTHON_BIN="/usr/local/opt/python@3.11/bin/python3.11"
    else
        PYTHON_BIN="$(command -v python3.11 || command -v python3)"
    fi
fi
log_success "Python 인터프리터 확인: $PYTHON_BIN ($("$PYTHON_BIN" --version))"

# Ollama (로컬 LLM 인퍼런스 엔진)
if ! command -v ollama &>/dev/null; then
    log_info "Ollama 설치 중 (brew install ollama)..."
    brew install ollama
    log_success "Ollama 설치 완료"
else
    log_success "Ollama 확인: $(ollama --version 2>/dev/null || echo 'installed')"
fi

# ------------------------------------------------------------------------------
# 4. Python 가상환경(.venv) 구축 및 의존성 라이브러리 설치
# ------------------------------------------------------------------------------
log_step "4/8" "Python 가상환경(.venv) 및 의존성 라이브러리 설치"

if [ -d ".venv" ]; then
    # 기존 가상환경의 파이썬 실행 가능 여부 및 버전 체크
    if ! .venv/bin/python -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
        log_warn "기존 .venv가 손상되었거나 Python 3.10 미만입니다. 가상환경을 깨끗하게 재생성합니다..."
        rm -rf .venv
        "$PYTHON_BIN" -m venv .venv
        log_success ".venv 가상환경 재생성 완료"
    else
        log_success "기존 정상 .venv 가상환경 감지됨"
    fi
else
    log_info "새로운 가상환경(.venv)을 생성합니다..."
    "$PYTHON_BIN" -m venv .venv
    log_success ".venv 가상환경 생성 완료"
fi

source .venv/bin/activate

log_info "pip 패키지 매니저 최신화..."
pip install --upgrade pip setuptools wheel --quiet

log_info "파이썬 패키지 의존성 설치 중 (requirements.txt)..."
pip install -r requirements.txt --quiet
log_success "Python 라이브러리 전체 설치 완료"

# ------------------------------------------------------------------------------
# 5. 웹 프론트엔드(Next.js) 의존성 설치
# ------------------------------------------------------------------------------
log_step "5/8" "Next.js 웹 프론트엔드 환경 구축"

cd web
if [ ! -d "node_modules" ]; then
    log_info "npm 패키지 의존성 설치 중 (npm install)..."
    npm install --quiet
    log_success "웹 프론트엔드 npm 의존성 설치 완료"
else
    log_success "웹 프론트엔드 node_modules 확인 완료"
fi
cd ..

# ------------------------------------------------------------------------------
# 6. 로컬 AI 모델 다운로드 (Ollama Qwen2.5)
# ------------------------------------------------------------------------------
log_step "6/8" "로컬 LLM 모델(Qwen2.5) 다운로드 및 백그라운드 서비스 점검"

# Ollama 백그라운드 서비스 구동 확인
if ! curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
    log_info "Ollama 백그라운드 데몬을 기동합니다..."
    ollama serve >/dev/null 2>&1 &
    
    # 서비스 준비 대기 (최대 15초)
    for i in {1..15}; do
        if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
            break
        fi
        sleep 1
    done
fi

if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
    log_success "Ollama 서비스 통신 연결 확인됨"
else
    log_warn "Ollama 서비스 기동에 시간이 걸리고 있습니다. 계속 진행합니다."
fi

# 시스템 RAM에 맞춘 최적 모델 선정
if [ "$RAM_GB" -ge 16 ]; then
    TARGET_MODEL="qwen2.5:14b"
    log_info "💡 고성능 시스템 (${RAM_GB}GB RAM): 기본 플래그십 모델 '$TARGET_MODEL'을 준비합니다."
else
    TARGET_MODEL="qwen2.5:7b"
    log_info "💡 경량 최적화 (${RAM_GB}GB RAM): 빠른 처리를 위해 '$TARGET_MODEL'을 준비합니다."
fi

EXISTING_MODELS="$(ollama list 2>/dev/null || true)"
if [[ "$EXISTING_MODELS" == *"$TARGET_MODEL"* ]]; then
    log_success "Ollama 모델 '$TARGET_MODEL' 이미 설치됨"
else
    log_info "Ollama 모델 '$TARGET_MODEL' 다운로드를 시작합니다 (네트워크 속도에 따라 수 분 소요)..."
    ollama pull "$TARGET_MODEL"
    log_success "Ollama 모델 '$TARGET_MODEL' 다운로드 완료"
fi

# ------------------------------------------------------------------------------
# 7. 음성인식 및 딥러닝 인페인팅 모델 사전 캐싱
# ------------------------------------------------------------------------------
log_step "7/8" "음성인식(Whisper) 및 AI 자막 제거(LaMa) 모델 검증"

# Whisper Large-v3-Turbo 사전 캐싱
log_info "Whisper Large-v3-Turbo 모델 검증 및 사전 캐싱 중..."
python -c "
import sys
try:
    from faster_whisper import WhisperModel
    print('   캐시 검증 및 다운로드 확인 (약 1.6GB)...')
    WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')
    print('   ✔ Whisper Large-v3-Turbo 모델 로드 준비 완료')
except Exception as e:
    print(f'   ⚠ Whisper 사전 로딩 안내 (첫 분석 실행 시 자동 다운로드됩니다): {e}')
"

# LaMa Inpainting ONNX 모델 검증 및 자동 다운로드
LAMA_MODEL="assets/models/lama_fp32.onnx"
if [ -f "$LAMA_MODEL" ] && [ "$(stat -f%z "$LAMA_MODEL" 2>/dev/null || echo 0)" -gt 150000000 ]; then
    log_success "LaMa AI 딥러닝 자막 제거 모델 확인 완료 ($(ls -lh "$LAMA_MODEL" | awk '{print $5}'))"
else
    log_info "LaMa ONNX 모델이 없어 공식 원격 가중치를 다운로드합니다 (약 198MB)..."
    mkdir -p assets/models
    curl -L "https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx" -o "$LAMA_MODEL" --progress-bar
    log_success "LaMa AI 딥러닝 자막 제거 모델 다운로드 완료 ($(ls -lh "$LAMA_MODEL" | awk '{print $5}'))"
fi

# ------------------------------------------------------------------------------
# 8. 런타임 디렉토리 생성 및 권한 점검
# ------------------------------------------------------------------------------
log_step "8/8" "런타임 디렉토리 및 에셋 구조 검증"

mkdir -p downloads output temp cache assets/models assets/fonts assets/audio
log_success "작업 폴더 준비 완료 (downloads, output, temp, cache)"

echo -e "\n${GREEN}${BOLD}================================================================="
echo "   🎉 Happy Shorts AI Studio 설치 및 환경 설정이 완료되었습니다!"
echo -e "=================================================================${NC}"
echo -e "이제 아래 명령어로 스튜디오를 언제든지 실행할 수 있습니다:\n"
echo -e "   ${CYAN}${BOLD}./start.sh${NC}   (또는 ${CYAN}./run_web.sh${NC})\n"

if [ "$1" = "--run" ] || [ "$1" = "-r" ]; then
    echo -e "${YELLOW}🚀 즉시 스튜디오 실행 모드로 전환합니다...${NC}"
    exec ./start.sh
fi
