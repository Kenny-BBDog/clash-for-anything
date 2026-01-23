#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VLESS/VMess 链接转 Clash 配置工具
项目地址: https://github.com/Kenny-BBDog/clash-for-anything

使用方法:
    python convert.py "vless://..." --output node.yaml
    python convert.py "vless://..." --merge existing_config.yaml
"""

import sys
import re
import json
import base64
import argparse
from urllib.parse import urlparse, parse_qs, unquote
from typing import Dict, Optional, List
import yaml


class ProxyParser:
    """代理链接解析器"""
    
    @staticmethod
    def parse_vless(link: str) -> Dict:
        """
        解析 VLESS 链接
        格式: vless://uuid@server:port?params#name
        """
        # 移除 vless:// 前缀
        link = link.replace('vless://', '')
        
        # 分离名称
        if '#' in link:
            link, name = link.rsplit('#', 1)
            name = unquote(name)
        else:
            name = 'VLESS'
        
        # 分离参数
        if '?' in link:
            main_part, params_str = link.split('?', 1)
            params = dict(parse_qs(params_str))
            # parse_qs 返回列表，取第一个值
            params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}
        else:
            main_part = link
            params = {}
        
        # 解析 uuid@server:port
        match = re.match(r'([^@]+)@([^:]+):(\d+)', main_part)
        if not match:
            raise ValueError(f"无法解析 VLESS 链接: {main_part}")
        
        uuid, server, port = match.groups()
        
        # 构建 Clash 节点配置
        node = {
            'name': name,
            'type': 'vless',
            'server': server,
            'port': int(port),
            'uuid': uuid,
        }
        
        # 处理传输方式
        transport_type = params.get('type', 'tcp')
        node['network'] = transport_type
        
        # 处理 TLS/Reality
        security = params.get('security', 'none')
        if security == 'reality':
            node['tls'] = True
            node['servername'] = params.get('sni', '')
            node['client-fingerprint'] = params.get('fp', 'chrome')
            node['reality-opts'] = {
                'public-key': params.get('pbk', ''),
                'short-id': params.get('sid', ''),
            }
        elif security == 'tls':
            node['tls'] = True
            node['servername'] = params.get('sni', '')
            if params.get('fp'):
                node['client-fingerprint'] = params.get('fp')
        
        # 处理 flow (xtls-rprx-vision)
        if params.get('flow'):
            node['flow'] = params.get('flow')
        
        # 处理 WebSocket
        if transport_type == 'ws':
            node['ws-opts'] = {}
            if params.get('path'):
                node['ws-opts']['path'] = params.get('path')
            if params.get('host'):
                node['ws-opts']['headers'] = {'Host': params.get('host')}
        
        # 处理 gRPC
        if transport_type == 'grpc':
            node['grpc-opts'] = {}
            if params.get('serviceName'):
                node['grpc-opts']['grpc-service-name'] = params.get('serviceName')
        
        return node
    
    @staticmethod
    def parse_vmess(link: str) -> Dict:
        """
        解析 VMess 链接
        格式: vmess://base64_encoded_json
        """
        # 移除 vmess:// 前缀
        link = link.replace('vmess://', '')
        
        # Base64 解码
        try:
            decoded = base64.b64decode(link + '==').decode('utf-8')
            config = json.loads(decoded)
        except Exception as e:
            raise ValueError(f"无法解析 VMess 链接: {e}")
        
        # 构建 Clash 节点配置
        node = {
            'name': config.get('ps', 'VMess'),
            'type': 'vmess',
            'server': config.get('add', ''),
            'port': int(config.get('port', 443)),
            'uuid': config.get('id', ''),
            'alterId': int(config.get('aid', 0)),
            'cipher': config.get('scy', 'auto'),
        }
        
        # 传输方式
        net = config.get('net', 'tcp')
        node['network'] = net
        
        # TLS
        if config.get('tls') == 'tls':
            node['tls'] = True
            if config.get('sni'):
                node['servername'] = config.get('sni')
        
        # WebSocket
        if net == 'ws':
            node['ws-opts'] = {}
            if config.get('path'):
                node['ws-opts']['path'] = config.get('path')
            if config.get('host'):
                node['ws-opts']['headers'] = {'Host': config.get('host')}
        
        return node
    
    @staticmethod
    def parse_ss(link: str) -> Dict:
        """
        解析 Shadowsocks 链接
        格式: ss://base64(method:password)@server:port#name
        """
        link = link.replace('ss://', '')
        
        # 分离名称
        if '#' in link:
            link, name = link.rsplit('#', 1)
            name = unquote(name)
        else:
            name = 'Shadowsocks'
        
        # 分离认证信息和服务器
        if '@' in link:
            auth_part, server_part = link.rsplit('@', 1)
            try:
                auth = base64.b64decode(auth_part + '==').decode('utf-8')
                method, password = auth.split(':', 1)
            except:
                raise ValueError("无法解析 SS 认证信息")
        else:
            # 整体 base64 编码的情况
            try:
                decoded = base64.b64decode(link + '==').decode('utf-8')
                match = re.match(r'([^:]+):([^@]+)@([^:]+):(\d+)', decoded)
                if match:
                    method, password, server, port = match.groups()
                    return {
                        'name': name,
                        'type': 'ss',
                        'server': server,
                        'port': int(port),
                        'cipher': method,
                        'password': password,
                    }
            except:
                pass
            raise ValueError("无法解析 SS 链接")
        
        server, port = server_part.rsplit(':', 1)
        
        return {
            'name': name,
            'type': 'ss',
            'server': server,
            'port': int(port),
            'cipher': method,
            'password': password,
        }
    
    @classmethod
    def parse(cls, link: str) -> Dict:
        """自动识别并解析代理链接"""
        link = link.strip()
        
        if link.startswith('vless://'):
            return cls.parse_vless(link)
        elif link.startswith('vmess://'):
            return cls.parse_vmess(link)
        elif link.startswith('ss://'):
            return cls.parse_ss(link)
        else:
            raise ValueError(f"不支持的链接类型: {link[:20]}...")


class ClashConfigGenerator:
    """Clash 配置生成器"""
    
    def __init__(self):
        self.nodes: List[Dict] = []
    
    def add_node(self, node: Dict):
        """添加节点"""
        self.nodes.append(node)
    
    def generate_node_yaml(self) -> str:
        """生成节点 YAML 配置"""
        output = "# 生成的 Clash 节点配置\n"
        output += "# 可直接复制到 proxies 部分\n\n"
        
        for node in self.nodes:
            output += yaml.dump([node], allow_unicode=True, default_flow_style=False, sort_keys=False)
            output += "\n"
        
        return output
    
    def merge_to_config(self, config_path: str, output_path: Optional[str] = None) -> str:
        """将节点合并到现有配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 获取现有节点名称
        existing_names = {p['name'] for p in config.get('proxies', [])}
        
        # 添加新节点
        for node in self.nodes:
            if node['name'] in existing_names:
                print(f"警告: 节点 '{node['name']}' 已存在，跳过")
                continue
            
            if 'proxies' not in config:
                config['proxies'] = []
            config['proxies'].append(node)
            
            # 添加到代理组
            for group in config.get('proxy-groups', []):
                if group.get('type') == 'select':
                    if 'proxies' in group and node['name'] not in group['proxies']:
                        # 在 DIRECT 之前插入
                        if 'DIRECT' in group['proxies']:
                            idx = group['proxies'].index('DIRECT')
                            group['proxies'].insert(idx, node['name'])
                        else:
                            group['proxies'].append(node['name'])
            
            print(f"已添加节点: {node['name']}")
        
        # 输出
        output_path = output_path or config_path
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description='VLESS/VMess 链接转 Clash 配置工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python convert.py "vless://xxx...#节点名称"
  python convert.py "vless://xxx..." --output node.yaml
  python convert.py "vless://xxx..." --merge config.yaml
  python convert.py "vless://...#节点1" "vmess://...#节点2" --merge config.yaml
        '''
    )
    
    parser.add_argument('links', nargs='+', help='代理链接 (支持 vless://, vmess://, ss://)')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-m', '--merge', help='合并到现有配置文件')
    
    args = parser.parse_args()
    
    generator = ClashConfigGenerator()
    
    # 解析所有链接
    for link in args.links:
        try:
            node = ProxyParser.parse(link)
            generator.add_node(node)
            print(f"解析成功: {node['name']} ({node['type']})")
        except Exception as e:
            print(f"解析失败: {e}")
            continue
    
    if not generator.nodes:
        print("没有成功解析的节点")
        sys.exit(1)
    
    # 输出
    if args.merge:
        output_path = generator.merge_to_config(args.merge)
        print(f"\n已合并到: {output_path}")
    elif args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(generator.generate_node_yaml())
        print(f"\n已保存到: {args.output}")
    else:
        print("\n" + "=" * 50)
        print(generator.generate_node_yaml())


if __name__ == '__main__':
    main()
