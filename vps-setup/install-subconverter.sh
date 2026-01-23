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

# 连通性自测
PUBLIC_IP=$(curl -s4 ip.sb 2>/dev/null || curl -s4 ifconfig.me 2>/dev/null)
print_info "正在进行 Subconverter 服务自检..."
sleep 2
TEST_SC=$(curl -s --connect-timeout 2 http://localhost:25500/version > /dev/null && echo -e "${GREEN}正常${NC}" || echo -e "${RED}启动失败/端口被占用${NC}")

echo ""
echo -e "${CYAN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${CYAN}┃                🔋 订阅中心 (Subconverter) 部署完成           ┃${NC}"
echo -e "${CYAN}┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫${NC}"
echo -e "${CYAN}┃${NC}  🌐 【服务端信息】"
echo -e "${CYAN}┃${NC}  - 转换中心地址: ${YELLOW}http://${PUBLIC_IP}:25500${NC}"
echo -e "${CYAN}┃${NC}  - 服务状态:     $TEST_SC"
echo -e "${CYAN}┃${NC}"
echo -e "${CYAN}┃${NC}  📝 【使用指南】"
echo -e "${CYAN}┃${NC}  1. 请在您的 [配置生成器] 网页中输入上述 IP"
echo -e "${CYAN}┃${NC}  2. 若服务状态显示异常，请通过 'systemctl status subconverter' 检查"
echo -e "${CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo ""
