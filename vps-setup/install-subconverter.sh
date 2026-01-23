#!/bin/bash
# ============================================================
# 私有订阅转换引擎 (Subconverter) 安装脚本
# 项目地址: https://github.com/Kenny-BBDog/clash-for-anything
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
    print_error "请使用 root 用户运行此脚本"
    exit 1
fi

print_info "正在安装私有订阅转换引擎 (Subconverter)..."

if [ -d "/usr/local/subconverter" ]; then
    print_success "Subconverter 已安装，正在尝试重启..."
    systemctl restart subconverter
    exit 0
fi

# 获取架构
ARCH="linux64"
if [[ "$(uname -m)" == "aarch64" ]]; then ARCH="aarch64"; fi

# 下载
wget -qO /tmp/subconverter.tar.gz https://github.com/tindy2013/subconverter/releases/latest/download/subconverter_${ARCH}.tar.gz
tar -xzf /tmp/subconverter.tar.gz -C /usr/local/
rm /tmp/subconverter.tar.gz

# 创建服务
cat > /etc/systemd/system/subconverter.service << EOF
[Unit]
Description=Subconverter Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/usr/local/subconverter
ExecStart=/usr/local/subconverter/subconverter
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable subconverter
systemctl start subconverter

# 放行端口 (尝试检测防火墙)
if command -v ufw &> /dev/null; then
    ufw allow 25500/tcp > /dev/null 2>&1
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=25500/tcp > /dev/null 2>&1
    firewall-cmd --reload > /dev/null 2>&1
fi

print_success "Subconverter 安装成功！"
print_info "服务端口: 25500"
print_info "现在你可以在在线工具中使用此服务器 IP 生成订阅链接了。"
