#!/bin/bash
# ============================================================
# VLESS 链接转 Clash 配置 - Shell 版本 (无需 Python)
# 使用方法: bash convert.sh "vless://..." 
# ============================================================

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 解析 VLESS 链接
parse_vless() {
    local link="$1"
    
    # 移除 vless:// 前缀
    link="${link#vless://}"
    
    # 提取名称 (# 后面的部分)
    if [[ "$link" == *"#"* ]]; then
        local name="${link##*#}"
        name=$(echo "$name" | sed 's/%20/ /g' | sed 's/%2F/\//g')  # URL 解码
        link="${link%#*}"
    else
        local name="VLESS"
    fi
    
    # 分离参数
    local params=""
    if [[ "$link" == *"?"* ]]; then
        params="${link##*\?}"
        link="${link%\?*}"
    fi
    
    # 解析 uuid@server:port
    local uuid="${link%@*}"
    local server_port="${link#*@}"
    local server="${server_port%:*}"
    local port="${server_port#*:}"
    
    # 解析参数
    local security=$(echo "$params" | grep -oP 'security=\K[^&]+' || echo "none")
    local sni=$(echo "$params" | grep -oP 'sni=\K[^&]+' || echo "")
    local pbk=$(echo "$params" | grep -oP 'pbk=\K[^&]+' || echo "")
    local sid=$(echo "$params" | grep -oP 'sid=\K[^&]+' || echo "")
    local fp=$(echo "$params" | grep -oP 'fp=\K[^&]+' || echo "chrome")
    local flow=$(echo "$params" | grep -oP 'flow=\K[^&]+' || echo "")
    local type=$(echo "$params" | grep -oP 'type=\K[^&]+' || echo "tcp")
    
    # 生成 YAML
    echo "  - name: $name"
    echo "    type: vless"
    echo "    server: $server"
    echo "    port: $port"
    echo "    uuid: $uuid"
    
    if [[ -n "$flow" ]]; then
        echo "    flow: $flow"
    fi
    
    if [[ "$security" == "reality" ]]; then
        echo "    tls: true"
        echo "    servername: $sni"
        echo "    client-fingerprint: $fp"
        echo "    network: $type"
        echo "    reality-opts:"
        echo "      public-key: $pbk"
        echo "      short-id: \"$sid\""
    elif [[ "$security" == "tls" ]]; then
        echo "    tls: true"
        echo "    servername: $sni"
        echo "    client-fingerprint: $fp"
        echo "    network: $type"
    else
        echo "    network: $type"
    fi
}

# 主函数
main() {
    if [[ $# -eq 0 ]]; then
        echo "使用方法: $0 \"vless://...\""
        echo ""
        echo "示例:"
        echo "  $0 \"vless://uuid@server:port?...#名称\""
        exit 1
    fi
    
    local link="$1"
    
    echo -e "${CYAN}# 生成的 Clash 节点配置${NC}"
    echo "# 复制以下内容到配置文件的 proxies 部分"
    echo ""
    
    if [[ "$link" == vless://* ]]; then
        parse_vless "$link"
    else
        echo "错误: 目前仅支持 VLESS 链接"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}# 转换完成!${NC}"
}

main "$@"
