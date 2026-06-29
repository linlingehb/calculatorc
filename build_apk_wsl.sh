#!/bin/bash
# Buildozer APK 打包脚本（WSL 环境）
# 使用方式：在 WSL 终端中 cd 到项目目录后执行：
#   chmod +x build_apk_wsl.sh
#   ./build_apk_wsl.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================================
# 请修改为你的项目路径
WINDOWS_PROJECT_DIR="/mnt/c/Users/Lenovo/WorkBuddy/2026-06-29-14-35-10"
BUILD_DIR="$HOME/.buildozer_builds/sci_calculator"
# ============================================================

check_proxy_working() {
    local proxy_url="$1"
    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" -x "$proxy_url" --max-time 8 https://github.com 2>/dev/null || echo "000")
    [[ "$status" == "200" || "$status" == "301" || "$status" == "302" ]]
}

get_windows_host_ips() {
    local ips=""
    if [[ -n "$WSL_HOST_IP" ]]; then
        ips="$WSL_HOST_IP"
    fi
    local gateway
    gateway=$(ip route 2>/dev/null | awk '/^default/ {print $3; exit}')
    if [[ -n "$gateway" ]] && [[ "$gateway" != "$ips" ]]; then
        [[ -n "$ips" ]] && ips="$ips $gateway" || ips="$gateway"
    fi
    local ns
    ns=$(grep -m1 nameserver /etc/resolv.conf 2>/dev/null | awk '{print $2}')
    if [[ -n "$ns" ]] && [[ "$ns" != "$ips" ]]; then
        [[ -n "$ips" ]] && ips="$ips $ns" || ips="$ns"
    fi
    echo "$ips"
}

detect_and_fix_proxy() {
    local common_port="${PROXY_PORT:-7890}"
    local proxy_set=""
    local original_proxy="${https_proxy:-${http_proxy:-}}"

    if [[ -n "$FORCE_PROXY" ]]; then
        echo -e "${YELLOW}>>> 使用强制代理: $FORCE_PROXY${NC}"
        proxy_set="$FORCE_PROXY"
    fi

    if [[ -z "$proxy_set" ]] && [[ -n "$original_proxy" ]]; then
        echo -e "${YELLOW}>>> 检测到代理: $original_proxy${NC}"
        if check_proxy_working "$original_proxy"; then
            echo -e "${GREEN}>>> 代理可用。${NC}"
            proxy_set="$original_proxy"
        else
            echo -e "${RED}警告：代理 $original_proxy 无法访问 GitHub。${NC}"
        fi
    fi

    if [[ -z "$proxy_set" ]]; then
        echo -e "${YELLOW}>>> 尝试自动发现 Windows 代理（端口 $common_port）...${NC}"
        local windows_ip
        for windows_ip in $(get_windows_host_ips); do
            if check_proxy_working "http://$windows_ip:$common_port"; then
                echo -e "${GREEN}>>> 发现代理: http://$windows_ip:$common_port${NC}"
                proxy_set="http://$windows_ip:$common_port"
                break
            fi
        done
    fi

    if [[ -n "$proxy_set" ]]; then
        export http_proxy="$proxy_set"
        export https_proxy="$proxy_set"
        export HTTP_PROXY="$proxy_set"
        export HTTPS_PROXY="$proxy_set"
        git config --global http.proxy "$proxy_set" 2>/dev/null || true
        git config --global https.proxy "$proxy_set" 2>/dev/null || true
        return 0
    fi

    echo -e "${YELLOW}>>> 未找到可用代理，直接构建（可能需要 VPN）。${NC}"
}

echo -e "${GREEN}=== 科学计算器 APK 打包 ===${NC}"
echo "Windows 项目: $WINDOWS_PROJECT_DIR"
echo "WSL 构建:     $BUILD_DIR"

detect_and_fix_proxy

echo -e "${YELLOW}>>> 准备 WSL 构建目录...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo -e "${YELLOW}>>> 复制项目文件...${NC}"
cp -a "$WINDOWS_PROJECT_DIR/main.py" "$BUILD_DIR/" 2>/dev/null || true
cp -a "$WINDOWS_PROJECT_DIR/"*.kv "$BUILD_DIR/" 2>/dev/null || true
cp -a "$WINDOWS_PROJECT_DIR/"*.png "$BUILD_DIR/" 2>/dev/null || true
cp -a "$WINDOWS_PROJECT_DIR/"*.jpg "$BUILD_DIR/" 2>/dev/null || true
cp -a "$WINDOWS_PROJECT_DIR/"data "$BUILD_DIR/" 2>/dev/null || true
cp -a "$WINDOWS_PROJECT_DIR/buildozer.spec" "$BUILD_DIR/"

cd "$BUILD_DIR"

ORIG_GIT_HTTP_PROXY=$(git config --global http.proxy 2>/dev/null || true)
ORIG_GIT_HTTPS_PROXY=$(git config --global https.proxy 2>/dev/null || true)
restore_git_proxy() {
    [[ -n "$ORIG_GIT_HTTP_PROXY" ]] && git config --global http.proxy "$ORIG_GIT_HTTP_PROXY"
    [[ -n "$ORIG_GIT_HTTPS_PROXY" ]] && git config --global https.proxy "$ORIG_GIT_HTTPS_PROXY"
}
trap restore_git_proxy EXIT
git config --global --unset http.proxy 2>/dev/null || true
git config --global --unset https.proxy 2>/dev/null || true

echo -e "${YELLOW}>>> 安装系统依赖...${NC}"
sudo apt-get update -y
sudo apt-get install -y \
    python3-pip python3-venv build-essential git zip unzip \
    openjdk-17-jdk autoconf automake libtool libtool-bin pkg-config \
    zlib1g-dev libncurses-dev libtinfo6 libffi-dev libssl-dev \
    libsqlite3-dev libbz2-dev libreadline-dev libgdbm-dev \
    libgdbm-compat-dev llvm liblzma-dev xclip python3-virtualenv

VENV_DIR="$BUILD_DIR/.venv"
echo -e "${YELLOW}>>> 创建虚拟环境: $VENV_DIR${NC}"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo -e "${YELLOW}>>> 安装 buildozer...${NC}"
pip install --upgrade pip setuptools wheel
pip install --upgrade buildozer cython

rm -rf .buildozer bin

echo -e "${GREEN}>>> 开始构建 APK...${NC}"
echo -e "${YELLOW}注意：首次构建可能需 30 分钟以上。${NC}"
buildozer -v android debug

APK_FILE=$(find "$BUILD_DIR/bin" -name '*.apk' -print -quit)
if [[ -z "$APK_FILE" ]]; then
    echo -e "${RED}错误：未找到 APK。${NC}"
    exit 1
fi

mkdir -p "$WINDOWS_PROJECT_DIR/bin"
cp -a "$APK_FILE" "$WINDOWS_PROJECT_DIR/bin/"
echo -e "${GREEN}>>> APK 已复制到: $WINDOWS_PROJECT_DIR/bin/${NC}"
