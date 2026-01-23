#!/bin/bash
# ============================================================
# VPS 一键部署脚本 - 科学上网环境快速搭建
# 项目地址: https://github.com/Kenny-BBDog/clash-for-anything
# 使用方法: bash <(curl -Ls https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/vps-setup/setup.sh)
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
show_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         VPS 一键部署脚本 v1.0                               ║"
    echo "║         GitHub: Kenny-BBDog/clash-for-anything             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检测系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        print_error "无法检测操作系统类型"
        exit 1
    fi
    print_info "检测到系统: $OS $VERSION"
}

# 检测是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用 root 用户运行此脚本"
        exit 1
    fi
}

# 创建 SWAP
create_swap() {
    print_info "检查 SWAP 配置..."
    
    if [ $(swapon --show | wc -l) -eq 0 ]; then
        print_info "正在创建 1GB SWAP..."
        
        # 根据可用空间决定 SWAP 大小
        TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
        if [ $TOTAL_MEM -lt 1024 ]; then
            SWAP_SIZE="1G"
        else
            SWAP_SIZE="2G"
        fi
        
        fallocate -l $SWAP_SIZE /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=1024
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        
        # 持久化
        if ! grep -q "/swapfile" /etc/fstab; then
            echo '/swapfile none swap sw 0 0' >> /etc/fstab
        fi
        
        print_success "SWAP 创建完成 ($SWAP_SIZE)"
    else
        print_success "SWAP 已存在，跳过"
    fi
}

# BBR 优化
configure_bbr() {
    print_info "配置 BBR 和 TCP 深度优化参数 (2026 极致调优版)..."
    
    cat > /etc/sysctl.d/99-bbr-optimize.conf << 'EOF'
# ============================================================
# BBR 及 TCP 深度优化参数 (极致跨海传输调优)
# ============================================================

# 核心 BBR 开启
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# TCP Fast Open (加速握手)
net.ipv4.tcp_fastopen = 3

# 网络缓冲区优化 (适配 190ms+ 高延迟 & 1Gbps+ 高带宽)
net.core.rmem_max = 67108864
net.core.wmem_max = 67108864
net.core.rmem_default = 1048576
net.core.wmem_default = 1048576
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
net.ipv4.tcp_mem = 65536 131072 262144

# 传输效率优化
net.ipv4.tcp_sack = 1
net.ipv4.tcp_fack = 1
net.ipv4.tcp_recovery = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_adv_win_scale = -2
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_ecn = 0

# 减少延迟 (Lower Latency)
net.ipv4.tcp_notsent_lowat = 16384
net.ipv4.tcp_frto = 0
net.ipv4.tcp_mtu_probing = 0

# 挥手与超时优化
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_rfc1337 = 1

# 连接队列与突发流量处理
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_max_tw_buckets = 65535
net.ipv4.tcp_tw_reuse = 1

# 文件描述符限制
fs.file-max = 1000000
EOF

    sysctl -p /etc/sysctl.d/99-bbr-optimize.conf > /dev/null 2>&1
    
    # 验证 BBR
    if lsmod | grep -q bbr; then
        print_success "BBR 已成功启动并完成极致调优"
    else
        print_warning "BBR 模块未在 lsmod 中发现，可能需要重启系统生效"
    fi
}

# 安装基础工具
install_tools() {
    print_info "安装基础工具..."
    
    case $OS in
        ubuntu|debian)
            apt update -qq
            apt install -y -qq curl socat wget htop vim net-tools unzip jq
            ;;
        centos|rhel|fedora)
            yum install -y -q curl socat wget htop vim net-tools unzip jq epel-release
            ;;
        *)
            print_warning "未知系统，尝试使用 apt..."
            apt update -qq && apt install -y -qq curl socat wget htop vim net-tools unzip jq
            ;;
    esac
    
    print_success "基础工具安装完成"
}

# 安装 3x-ui 面板
install_3xui() {
    print_info "安装 3x-ui 面板..."
    
    # 检查是否已安装
    if systemctl is-active --quiet x-ui 2>/dev/null; then
        print_success "3x-ui 已安装并运行中"
        return
    fi
    
    bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/master/install.sh)
    
    print_success "3x-ui 安装完成"
}

# 安装 NextTrace (路由测试)
# 安装私有订阅转换引擎 (Subconverter) - [已移至独立脚本]

# 配置防火墙
configure_firewall() {
    print_info "配置防火墙..."
    
    # 常用端口 + Subconverter 端口
    PORTS="22 80 443 2053 2083 2087 2096 8443 666 25500"
    
    if command -v ufw &> /dev/null; then
        ufw --force enable
        for port in $PORTS; do
            ufw allow $port/tcp > /dev/null 2>&1
            ufw allow $port/udp > /dev/null 2>&1
        done
        print_success "UFW 防火墙配置完成"
    elif command -v firewall-cmd &> /dev/null; then
        systemctl start firewalld
        for port in $PORTS; do
            firewall-cmd --permanent --add-port=$port/tcp > /dev/null 2>&1
            firewall-cmd --permanent --add-port=$port/udp > /dev/null 2>&1
        done
        firewall-cmd --reload
        print_success "Firewalld 配置完成"
    else
        print_warning "未检测到防火墙，跳过配置"
    fi
}

# 显示安装报告
show_report() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    安装完成报告                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 系统信息
    echo -e "${YELLOW}【系统信息】${NC}"
    echo "  操作系统: $OS $VERSION"
    echo "  内核版本: $(uname -r)"
    echo "  CPU: $(grep -c processor /proc/cpuinfo) 核"
    echo "  内存: $(free -h | awk '/^Mem:/{print $2}')"
    echo "  SWAP: $(free -h | awk '/^Swap:/{print $2}')"
    echo ""
    
    # BBR 状态
    echo -e "${YELLOW}【网络优化】${NC}"
    if sysctl net.ipv4.tcp_congestion_control 2>/dev/null | grep -q bbr; then
        echo -e "  BBR: ${GREEN}已启用${NC}"
    else
        echo -e "  BBR: ${RED}未启用${NC}"
    fi
    echo ""
    
    # 服务状态
    echo -e "${YELLOW}【服务状态】${NC}"
    if systemctl is-active --quiet x-ui 2>/dev/null; then
        X_UI_PORT=$(grep -oP '"port":\s*\K\d+' /usr/local/x-ui/db/x-ui.db 2>/dev/null || echo "2053")
        echo -e "  3x-ui: ${GREEN}运行中${NC} (端口: $X_UI_PORT)"
    else
        echo -e "  3x-ui: ${RED}未运行${NC}"
    fi
    echo ""
    
    # IP 信息
    echo -e "${YELLOW}【网络信息】${NC}"
    PUBLIC_IP=$(curl -s4 ip.sb 2>/dev/null || curl -s4 ifconfig.me 2>/dev/null)
    echo "  公网 IP: $PUBLIC_IP"
    echo ""
    
    # 使用提示
    echo -e "${YELLOW}【下一步】${NC}"
    echo "  1. 访问 3x-ui 面板: http://$PUBLIC_IP:2053"
    echo "  2. 默认用户名密码: admin / admin (请立即修改!)"
    echo "  3. 创建入站后，使用以下命令生成 Clash 配置:"
    echo ""
    echo -e "     ${GREEN}bash <(curl -Ls https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/convert.sh) \"vless://...\"${NC}"
    echo ""
}

# 主函数
main() {
    show_banner
    check_root
    detect_os
    
    echo ""
    print_info "开始 VPS 初始化..."
    echo ""
    
    create_swap
    configure_bbr
    install_tools
    configure_firewall
    install_nexttrace
    install_3xui
    
    show_report
}

# 运行
main "$@"
