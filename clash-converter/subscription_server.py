#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash 配置订阅服务器
提供订阅链接功能，客户端可自动更新配置

使用方法:
    python subscription_server.py --port 8080

客户端订阅地址:
    http://your-server:8080/clash/config.yaml
"""

import os
import sys
import json
import yaml
import hashlib
import argparse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional

# 配置文件路径
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
NODES_FILE = os.path.join(CONFIG_DIR, 'nodes.json')
TEMPLATE_FILE = os.path.join(CONFIG_DIR, 'templates', 'base-rules.yaml')


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.nodes: List[Dict] = []
        self.load_nodes()
    
    def load_nodes(self):
        """加载节点配置"""
        if os.path.exists(NODES_FILE):
            with open(NODES_FILE, 'r', encoding='utf-8') as f:
                self.nodes = json.load(f)
    
    def save_nodes(self):
        """保存节点配置"""
        with open(NODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.nodes, f, ensure_ascii=False, indent=2)
    
    def add_node(self, node: Dict):
        """添加节点"""
        # 检查是否已存在
        for i, n in enumerate(self.nodes):
            if n['name'] == node['name']:
                self.nodes[i] = node
                self.save_nodes()
                return
        self.nodes.append(node)
        self.save_nodes()
    
    def remove_node(self, name: str) -> bool:
        """删除节点"""
        for i, n in enumerate(self.nodes):
            if n['name'] == name:
                del self.nodes[i]
                self.save_nodes()
                return True
        return False
    
    def list_nodes(self) -> List[Dict]:
        """列出所有节点"""
        return self.nodes
    
    def generate_config(self, platform: str = 'windows') -> str:
        """生成完整 Clash 配置"""
        
        # 基础配置
        config = {
            'port': 7890,
            'socks-port': 7891,
            'mixed-port': 7892,
            'allow-lan': True,
            'bind-address': '*',
            'mode': 'rule',
            'log-level': 'warning',
            'ipv6': False,
            'external-controller': '127.0.0.1:9090',
            'unified-delay': True,
            'tcp-concurrent': True,
        }
        
        # 平台特定配置
        if platform == 'windows':
            config['geodata-mode'] = True
            config['geodata-loader'] = 'memconservative'
            config['geo-auto-update'] = True
            config['geo-update-interval'] = 24
            config['global-client-fingerprint'] = 'chrome'
            
            # Sniffer
            config['sniffer'] = {
                'enable': True,
                'force-dns-mapping': True,
                'parse-pure-ip': True,
                'override-destination': True,
                'sniff': {
                    'HTTP': {'ports': [80, '8080-8880'], 'override-destination': True},
                    'TLS': {'ports': [443, 8443]},
                    'QUIC': {'ports': [443, 8443]},
                },
            }
            
            # TUN
            config['tun'] = {
                'enable': True,
                'stack': 'mixed',
                'dns-hijack': ['any:53'],
                'auto-route': True,
                'auto-detect-interface': True,
                'strict-route': True,
                'mtu': 9000,
            }
        else:
            # Android 简化配置
            config['geodata-mode'] = False
        
        # DNS 配置
        config['dns'] = {
            'enable': True,
            'listen': '0.0.0.0:1053',
            'ipv6': False,
            'enhanced-mode': 'fake-ip',
            'fake-ip-range': '198.18.0.1/16',
            'fake-ip-filter': [
                '*.lan', '*.local', '*.localhost',
                'time.*.com', 'ntp.*.com',
                'localhost.ptlogin2.qq.com',
            ],
            'default-nameserver': ['119.29.29.29', '223.5.5.5'],
            'nameserver': [
                'https://doh.pub/dns-query',
                'https://dns.alidns.com/dns-query',
            ],
            'fallback': [
                'https://dns.google/dns-query',
                'https://cloudflare-dns.com/dns-query',
            ],
            'fallback-filter': {
                'geoip': platform == 'windows',
                'ipcidr': ['240.0.0.0/4', '0.0.0.0/32'],
            },
        }
        
        # 代理节点
        config['proxies'] = self.nodes
        
        # 代理组
        proxy_names = [n['name'] for n in self.nodes]
        config['proxy-groups'] = [
            {
                'name': '🚀 代理选择',
                'type': 'select',
                'proxies': proxy_names + ['DIRECT'],
            },
        ]
        
        # 检查是否有住宅 IP 节点
        if '住宅IP' in proxy_names:
            config['proxy-groups'].insert(0, {
                'name': '住宅IP',
                'type': 'select',
                'proxies': ['住宅IP'],
            })
        
        # 加载规则模板
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                rules_config = yaml.safe_load(f)
                config['rules'] = rules_config.get('rules', [])
        else:
            config['rules'] = ['MATCH,🚀 代理选择']
        
        return yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    def health_check(self) -> Dict:
        """节点健康检查"""
        import socket
        import ssl
        
        results = {}
        for node in self.nodes:
            name = node['name']
            server = node.get('server', '')
            port = node.get('port', 443)
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                start = datetime.now()
                sock.connect((server, port))
                latency = (datetime.now() - start).total_seconds() * 1000
                sock.close()
                results[name] = {'status': 'ok', 'latency': f'{latency:.0f}ms'}
            except Exception as e:
                results[name] = {'status': 'fail', 'error': str(e)}
        
        return results


class SubscriptionHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    config_manager = ConfigManager()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == '/clash/config.yaml' or path == '/clash/windows':
            self.send_config('windows')
        elif path == '/clash/android':
            self.send_config('android')
        elif path == '/nodes':
            self.send_json(self.config_manager.list_nodes())
        elif path == '/health':
            self.send_json(self.config_manager.health_check())
        else:
            self.send_error(404, 'Not Found')
    
    def send_config(self, platform: str):
        config = self.config_manager.generate_config(platform)
        self.send_response(200)
        self.send_header('Content-Type', 'text/yaml; charset=utf-8')
        self.send_header('Content-Disposition', f'attachment; filename="clash_{platform}.yaml"')
        self.send_header('Profile-Update-Interval', '24')
        self.end_headers()
        self.wfile.write(config.encode('utf-8'))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")


def main():
    parser = argparse.ArgumentParser(description='Clash 配置订阅服务器')
    parser.add_argument('-p', '--port', type=int, default=8080, help='监听端口')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    args = parser.parse_args()
    
    server = HTTPServer((args.host, args.port), SubscriptionHandler)
    print(f"""
╔════════════════════════════════════════════════════════════╗
║         Clash 配置订阅服务器已启动                           ║
╚════════════════════════════════════════════════════════════╝

订阅地址:
  Windows: http://your-server:{args.port}/clash/windows
  Android: http://your-server:{args.port}/clash/android
  
API 接口:
  节点列表: http://your-server:{args.port}/nodes
  健康检查: http://your-server:{args.port}/health

按 Ctrl+C 停止服务...
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
