#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sub Hub v2 - Advanced Proxy Manager
Supports card-based UI, node metadata (limit, expiry, chaining), 
and traffic reporting headers for Clash.
"""

import os
import sys
import json
import base64
import urllib.request
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import yaml
from urllib.parse import urlparse, parse_qs
import random
import string

def generate_random_string(length=16):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# Import project-specific converter logic
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from convert import ProxyParser, ClashConfigGenerator
except ImportError:
    print("Error: convert.py not found in the same directory.")
    sys.exit(1)

# --- Configuration ---
PORT = 8080
SECRET_PATH = "my-stable-sub"
CONFIG_FILE = os.path.join(script_dir, 'config.json')
LOCAL_TEMPLATE = os.path.join(script_dir, 'templates', 'base-rules.yaml')
DASHBOARD_FILE = os.path.join(script_dir, 'dashboard.html')

import threading
CONFIG_LOCK = threading.Lock()

def get_public_ip():
    """获取 VPS 公网 IP"""
    try:
        for url in ['http://v4.ident.me', 'http://ifconfig.me/ip', 'http://ip.sb']:
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    return response.read().decode('utf8').strip()
            except:
                continue
        return 'your_vps_ip'
    except:
        return 'your_vps_ip'

XUI_DB = '/etc/x-ui/x-ui.db'

def sync_traffic(nodes):
    """Sync nodes usage from 3x-ui database."""
    if not os.path.exists(XUI_DB):
        return nodes
    
    try:
        import sqlite3
        conn = sqlite3.connect(XUI_DB)
        c = conn.cursor()
        c.execute('SELECT port, up, down FROM inbounds')
        db_stats = {str(row[0]): (row[1] + row[2]) for row in c.fetchall()}
        conn.close()
        
        for node in nodes:
            # Extract port from URL (e.g., :443)
            try:
                from urllib.parse import urlparse
                # For vless/vmess/ss urls
                u = urlparse(node['url'])
                port = str(u.port)
                if port in db_stats:
                    node['used_bytes'] = db_stats[port]
            except: pass
    except Exception as e:
        print(f"Traffic sync error: {e}")
    return nodes

def load_config():
    with CONFIG_LOCK:
        default_config = {"nodes": [], "subscriptions": []}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list): # Migrate from v1
                        data = {"nodes": [{"id": str(i), "name": f"Node {i+1}", "url": u, "limit_gb": 0, "used_bytes": 0, "expiry": None, "chain_with": None} for i, u in enumerate(data)], "subscriptions": []}
                    if isinstance(data, dict):
                        if "nodes" not in data: data["nodes"] = []
                        if "subscriptions" not in data: data["subscriptions"] = []
                        # Ensure all nodes/subs have necessary traffic fields
                        for n in data["nodes"]:
                            if 'used_bytes' not in n: n['used_bytes'] = 0
                            if 'limit_gb' not in n: n['limit_gb'] = 0
                        for s in data["subscriptions"]:
                            if 'used_bytes' not in s: s['used_bytes'] = 0
                            if 'limit_gb' not in s: s['limit_gb'] = 0
                            if 'traffic_base' not in s: s['traffic_base'] = {} # map node_id -> base_bytes
                        return data
            except Exception as e:
                print(f"Error loading config: {e}")
        return default_config

def save_config(config):
    with CONFIG_LOCK:
        # Use a temporary file for atomic write if possible, or just lock
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

class SubBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            
            if path == SECRET_PATH:
                # Default stable sub (legacy)
                self.generate_and_send_config()
            elif path.startswith("sub/"):
                # Professional Sub (v3)
                token = path.split("/")[-1]
                self.generate_and_send_config(token=token)
            elif path == "dashboard" or path == "":
                self.serve_dashboard()
            elif path == "api/nodes":
                config = load_config()
                config["nodes"] = sync_traffic(config["nodes"])
                self.send_json(config["nodes"])
            elif path == "api/subscriptions":
                config = load_config()
                config["nodes"] = sync_traffic(config["nodes"])
                # Calculate live subscription usage
                nodes_map = {n['id']: n['used_bytes'] for n in config["nodes"]}
                for s in config["subscriptions"]:
                    total_usage = 0
                    for nid in s.get('node_ids', []):
                        if nid in nodes_map:
                            base = s.get('traffic_base', {}).get(nid, 0)
                            current = nodes_map[nid]
                            # If current < base, node might have been reset, we treat it as 0 delta or handle reset?
                            # Simplest: just current if reset, else current - base
                            delta = max(0, current - base)
                            total_usage += delta
                    s['used_bytes'] = total_usage
                self.send_json(config.get("subscriptions", []))
            elif path == "health":
                self.send_response(200)
                self.send_header('Content-Length', '2')
                self.end_headers()
                try:
                    self.wfile.write(b"OK")
                    self.wfile.flush()
                except: pass
            elif path == "favicon.ico":
                self.send_response(204)
                self.end_headers()
            else:
                # Try to serve static file if it exists (e.g. css, js, fonts)
                file_path = os.path.join(os.path.dirname(__file__), path)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    if path.endswith('.css'): self.send_header('Content-Type', 'text/css')
                    elif path.endswith('.js'): self.send_header('Content-Type', 'application/javascript')
                    elif path.endswith('.woff2'): self.send_header('Content-Type', 'font/woff2')
                    else: self.send_header('Content-Type', 'application/octet-stream')
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_error(404, "Not Found")
        except Exception as e:
            print(f"Handler error (GET {self.path}): {e}")
            self.send_error(500, str(e))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        parsed = urlparse(self.path)
        path = parsed.path.strip('/')

        if path == "api/nodes":
            try:
                data = json.loads(body)
                url = data.get('url')
                if url:
                    config = load_config()
                    # Determine name
                    name = data.get('name')
                    if not name:
                        name = "新节点"
                        if '://' in url:
                            try:
                                temp_node = ProxyParser.parse(url)
                                name = temp_node.get('name', '新节点')
                            except: pass
                    
                    new_node = {
                        "id": str(int(time.time())),
                        "name": name,
                        "url": url,
                        "limit_gb": data.get('limit_gb', 0),
                        "used_bytes": 0,
                        "expiry": data.get('expiry'),
                        "chain_with": data.get('chain_with')
                    }
                    config["nodes"].append(new_node)
                    save_config(config)
                    self.send_json({"status": "ok"})
                else:
                    self.send_error(400, "Missing URL")
            except Exception as e:
                self.send_error(500, str(e))
        
        elif path == "api/subscriptions":
            try:
                data = json.loads(body)
                config = load_config()
                config["nodes"] = sync_traffic(config["nodes"])
                
                import random, string
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                
                # Record current node traffic as base for this subscription
                node_ids = data.get('node_ids', [])
                traffic_base = {}
                for n in config["nodes"]:
                    if n['id'] in node_ids:
                        traffic_base[n['id']] = n.get('used_bytes', 0)
                
                new_sub = {
                    "id": str(int(time.time())),
                    "name": data.get('name', '未命名订阅'),
                    "token": token,
                    "node_ids": node_ids,
                    "traffic_base": traffic_base,
                    "limit_gb": data.get('limit_gb', 0),
                    "used_bytes": 0,
                    "expiry": data.get('expiry'),
                    "status": "active"
                }
                # Support external proxy for chain
                if data.get('external_proxy'):
                    new_sub['external_proxy'] = data['external_proxy']
                if data.get('template'):
                    new_sub['template'] = data['template']
                config["subscriptions"].append(new_sub)
                save_config(config)
                self.send_json({"status": "ok", "token": token})
            except Exception as e:
                self.send_error(500, str(e))

        elif path == "api/guest-pass":
            try:
                data = json.loads(body)
                selected_node_ids = data.get('node_ids', [])
                duration_hours = float(data.get('duration_hours', 0.5))
                total_gb = float(data.get('limit_gb', 0))
                output_format = data.get('format', 'ss')  # 'ss' or 'clash'
                
                if output_format == 'clash':
                    # Generate a temporary Sub Hub subscription for selected nodes
                    config = load_config()
                    token = generate_random_string(16)
                    expiry_date = time.strftime('%Y-%m-%d', time.localtime(time.time() + duration_hours * 3600))
                    
                    # Calculate traffic base for delta tracking
                    traffic_base = {}
                    for nid in selected_node_ids:
                        node = next((n for n in config["nodes"] if n["id"] == nid), None)
                        if node:
                            traffic_base[nid] = node.get('used_bytes', 0)
                    
                    guest_name = data.get('name') or f"Guest-{duration_hours}h"
                    guest_sub = {
                        "id": str(int(time.time() * 1000)),
                        "name": guest_name,
                        "token": token,
                        "node_ids": selected_node_ids,
                        "limit_gb": total_gb,
                        "used_bytes": 0,
                        "expiry": expiry_date,
                        "status": "active",
                        "is_guest": True,
                        "traffic_base": traffic_base
                    }
                    config["subscriptions"].append(guest_sub)
                    save_config(config)
                    
                    public_ip = get_public_ip()
                    clash_url = f"http://{public_ip}:{PORT}/sub/{token}"
                    self.send_json({"status": "ok", "link": clash_url, "format": "clash", "expiry": expiry_date})
                else:
                    # Original SS link via guest_pass.py
                    cmd = [sys.executable, os.path.join(script_dir, 'guest_pass.py'), str(duration_hours), str(total_gb)]
                    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8')
                    
                    import re
                    match = re.search(r'(ss://[^\s]+)', result)
                    if match:
                        self.send_json({"status": "ok", "link": match.group(1), "format": "ss"})
                    else:
                        self.send_error(500, "Failed to parse guest link from output")
            except Exception as e:
                self.send_error(500, f"Error generating guest pass: {e}")
        elif path == "api/subscriptions/reset":
            try:
                sub_id = params.get('id', [None])[0]
                config = load_config()
                config["nodes"] = sync_traffic(config["nodes"])
                
                found = False
                for s in config["subscriptions"]:
                    if s["id"] == sub_id:
                        # Update traffic_base to current node traffic
                        new_base = {}
                        for n in config["nodes"]:
                            if n['id'] in s.get('node_ids', []):
                                new_base[n['id']] = n.get('used_bytes', 0)
                        s['traffic_base'] = new_base
                        s['used_bytes'] = 0
                        found = True
                        break
                
                if found:
                    save_config(config)
                    self.send_json({"status": "ok"})
                else:
                    self.send_error(404, "Subscription not found")
            except Exception as e:
                self.send_error(500, str(e))
        elif path == "api/subscriptions/extend":
            try:
                data = json.loads(body)
                sub_id = data.get('id')
                extend_hours = float(data.get('extend_hours', 24))
                
                config = load_config()
                found = False
                for s in config["subscriptions"]:
                    if s["id"] == sub_id:
                        # Calculate new expiry
                        current_expiry = s.get('expiry')
                        if current_expiry:
                            try:
                                expire_date = time.strptime(current_expiry, "%Y-%m-%d")
                                expire_ts = time.mktime(expire_date)
                            except:
                                expire_ts = time.time()
                        else:
                            expire_ts = time.time()
                        
                        # Add extension hours
                        new_expire_ts = expire_ts + (extend_hours * 3600)
                        s['expiry'] = time.strftime("%Y-%m-%d", time.localtime(new_expire_ts))
                        found = True
                        break
                
                if found:
                    save_config(config)
                    self.send_json({"status": "ok", "new_expiry": s['expiry']})
                else:
                    self.send_error(404, "Subscription not found")
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip('/')
        params = parse_qs(parsed.query)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        if path == "api/nodes":
            try:
                index = int(params.get('index', [-1])[0])
                config = load_config()
                if 0 <= index < len(config["nodes"]):
                    data = json.loads(body)
                    node = config["nodes"][index]
                    node["name"] = data.get("name", node["name"])
                    node["url"] = data.get("url", node["url"])
                    node["limit_gb"] = data.get("limit_gb", node["limit_gb"])
                    node["expiry"] = data.get("expiry", node["expiry"])
                    node["chain_with"] = data.get("chain_with", node["chain_with"])
                    save_config(config)
                    self.send_json({"status": "ok"})
                else:
                    self.send_error(400, "Invalid index")
            except Exception as e:
                self.send_error(500, str(e))
        
        elif path == "api/subscriptions":
            try:
                sub_id = params.get('id', [None])[0]
                config = load_config()
                found = False
                for s in config["subscriptions"]:
                    if s["id"] == sub_id:
                        data = json.loads(body)
                        s["name"] = data.get("name", s["name"])
                        s["node_ids"] = data.get("node_ids", s["node_ids"])
                        s["limit_gb"] = data.get("limit_gb", s.get("limit_gb", 0))
                        s["expiry"] = data.get("expiry", s.get("expiry"))
                        s["status"] = data.get("status", s.get("status", "active"))
                        # Support external proxy for chain
                        if "external_proxy" in data:
                            s["external_proxy"] = data["external_proxy"]
                        if "chains" in data:
                            s["chains"] = data["chains"]
                        if "dialer_id" in data:
                            s["dialer_id"] = data["dialer_id"]
                        if "dialer_name" in data:
                            s["dialer_name"] = data["dialer_name"]
                        if "template" in data:
                            s["template"] = data["template"]
                        found = True
                        break
                if found:
                    save_config(config)
                    self.send_json({"status": "ok"})
                else:
                    self.send_error(404, "Subscription not found")
            except Exception as e:
                self.send_error(500, str(e))

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip('/')
        params = parse_qs(parsed.query)

        if path == "api/nodes":
            try:
                index = int(params.get('index', [-1])[0])
                config = load_config()
                if 0 <= index < len(config["nodes"]):
                    config["nodes"].pop(index)
                    save_config(config)
                    self.send_json({"status": "ok"})
                else:
                    self.send_error(400, "Invalid index")
            except Exception as e:
                self.send_error(500, str(e))
                
        elif path == "api/subscriptions":
            try:
                sub_id = params.get('id', [None])[0]
                config = load_config()
                config["subscriptions"] = [s for s in config["subscriptions"] if s["id"] != sub_id]
                save_config(config)
                self.send_json({"status": "ok"})
            except Exception as e:
                self.send_error(500, str(e))

    def serve_dashboard(self):
        if os.path.exists(DASHBOARD_FILE):
            with open(DASHBOARD_FILE, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            try:
                self.wfile.write(content)
                self.wfile.flush()
            except BrokenPipeError:
                pass
        else:
            self.send_error(404, "Dashboard file not found")

    def send_json(self, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        try:
            self.wfile.write(body)
            self.wfile.flush()
        except BrokenPipeError:
            pass

    def fetch_all_nodes(self, node_ids_filter=None):
        """Fetches and parses all configured nodes, optionally filtering by ID."""
        all_parsed_nodes = []
        config = load_config()
        public_ip = get_public_ip()
        
        for node_conf in config.get("nodes", []):
            if node_ids_filter is not None and node_conf["id"] not in node_ids_filter:
                continue
                
            sub_url = node_conf["url"]
            try:
                # 1. Direct Node Link
                if sub_url.startswith(('vless://', 'vmess://', 'ss://')):
                    node = ProxyParser.parse(sub_url)
                    node['name'] = node_conf.get('name', node.get('name', 'node'))
                    node['managed_id'] = node_conf['id']
                    node['chain_with'] = node_conf.get('chain_with')
                    if node.get('server') == '127.0.0.1': node['server'] = public_ip
                    all_parsed_nodes.append(node)
                    continue

                # 2. Subscription URL
                with urllib.request.urlopen(sub_url, timeout=10) as response:
                    content = response.read().decode('utf-8')
                    try:
                        decoded = base64.b64decode(content + '==').decode('utf-8')
                        links = decoded.strip().split('\n')
                    except:
                        links = content.strip().split('\n')
                    
                    for link in links:
                        if '://' in link.strip():
                            try:
                                node = ProxyParser.parse(link.strip())
                                node['managed_id'] = node_conf['id']
                                node['chain_with'] = node_conf.get('chain_with')
                                if node.get('server') == '127.0.0.1': node['server'] = public_ip
                                all_parsed_nodes.append(node)
                            except: pass
            except Exception as e:
                print(f"Error fetching source {sub_url}: {e}")
        return all_parsed_nodes

    def generate_and_send_config(self, token=None):
        try:
            config = load_config()
            node_ids_filter = None
            current_sub = None
            
            if token:
                # Find the subscription
                for s in config.get("subscriptions", []):
                    if s["token"] == token:
                        current_sub = s
                        node_ids_filter = s.get("node_ids", [])
                        break
                
                if not current_sub:
                    self.send_error(403, "Invalid subscription token.")
                    return
                
                # Check Expiry
                if current_sub.get("expiry"):
                    expire_ts = int(time.mktime(time.strptime(current_sub['expiry'], "%Y-%m-%d")))
                    if time.time() > expire_ts + 86400: # Allow the full day
                        self.send_error(403, "Subscription expired.")
                        return
                        
                # Check Traffic Limit (Plan level)
                if current_sub.get("limit_gb", 0) > 0:
                    # Calculate live usage for this sub
                    nodes_map = {n['id']: n['used_bytes'] for n in config["nodes"]}
                    sub_usage = 0
                    for nid in current_sub.get('node_ids', []):
                        if nid in nodes_map:
                            base = current_sub.get('traffic_base', {}).get(nid, 0)
                            sub_usage += max(0, nodes_map[nid] - base)
                    if sub_usage >= current_sub["limit_gb"] * (1024**3):
                        self.send_error(403, "Subscription traffic limit exceeded.")
                        return

            nodes = self.fetch_all_nodes(node_ids_filter=node_ids_filter)
            if not nodes:
                self.send_error(500, "No nodes available for this subscription.")
                return

            from socketserver import ThreadingMixIn
            # Load template
            template_name = current_sub.get('template', 'base-rules.yaml') if current_sub else 'base-rules.yaml'
            template_path = os.path.join(script_dir, 'templates', template_name)
            if not os.path.exists(template_path):
                template_path = LOCAL_TEMPLATE

            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    config_yaml = yaml.safe_load(f)
            else:
                config_yaml = {
                    "port": 7890, "socks-port": 7891, "mode": "rule",
                    "dns": {"enable": True, "enhanced-mode": "fake-ip", "nameserver": ["119.29.29.29"]},
                    "proxy-groups": [{"name": "🚀 代理选择", "type": "select", "proxies": []}],
                    "rules": ["MATCH,🚀 代理选择"]
                }

            # Injected Managed Proxies
            config_yaml['proxies'] = nodes
            
            # Support both legacy 'external_proxy' and new 'chains' list
            chains_data = []
            if current_sub:
                if current_sub.get('chains'):
                    chains_data = current_sub['chains']
                elif current_sub.get('external_proxy'):
                    # Convert legacy format to chains list
                    legacy_ext = current_sub['external_proxy']
                    if 'name' not in legacy_ext:
                        legacy_ext['name'] = "🇺🇸 运营专线 (美国静态)"
                    if 'dialer_id' not in legacy_ext:
                        legacy_ext['dialer_id'] = current_sub.get('dialer_id')
                    if 'dialer_name' not in legacy_ext:
                        legacy_ext['dialer_name'] = current_sub.get('dialer_name')
                    chains_data = [legacy_ext]
            
            for chain_conf in reversed(chains_data):
                if chain_conf.get('server') and chain_conf.get('port'):
                    # Find the dialer node
                    dialer_node_name = None
                    
                    # 1. Check for explicit dialer_id in chain or sub
                    target_dialer_id = chain_conf.get('dialer_id') or current_sub.get('dialer_id')
                    if target_dialer_id:
                        for node in nodes:
                            if node.get('managed_id') == target_dialer_id:
                                dialer_node_name = node['name']
                                break
                    
                    # 2. Check for explicit dialer_name in chain or sub
                    target_dialer_name = chain_conf.get('dialer_name') or current_sub.get('dialer_name')
                    if not dialer_node_name and target_dialer_name:
                        for node in nodes:
                            if target_dialer_name.lower() in node['name'].lower():
                                dialer_node_name = node['name']
                                break

                    # 3. Fallback to DMIT (legacy behavior)
                    if not dialer_node_name:
                        for node in nodes:
                            if 'DMIT' in node['name']:
                                dialer_node_name = node['name']
                                break
                    
                    # 4. Final fallback to first node
                    if not dialer_node_name and nodes:
                        dialer_node_name = nodes[0]['name']

                    ext_proxy = {
                        "name": chain_conf.get('name', "🛸 运营专线"),
                        "type": chain_conf.get('type', 'socks5'),
                        "server": chain_conf['server'],
                        "port": int(chain_conf['port']),
                    }
                    if chain_conf.get('username'):
                        ext_proxy['username'] = chain_conf['username']
                        ext_proxy['password'] = chain_conf.get('password', '')
                    
                    # Chain: Client -> Dialer -> External IP -> Target
                    if dialer_node_name:
                        ext_proxy['dialer-proxy'] = dialer_node_name
                        
                    config_yaml['proxies'].insert(0, ext_proxy)
            
            # Handle Relay / Chaining
            external_proxy_names = [p['name'] for p in config_yaml['proxies'] if p['name'] not in [n['name'] for n in nodes]]
            managed_node_names = [n['name'] for n in nodes]
            relay_names = []
            relays = []
            for node in nodes:
                if node.get('chain_with'):
                    target_name = node['chain_with']
                    if target_name in managed_node_names:
                        relay_name = f"🔗 {node['name']} -> {target_name}"
                        relays.append({
                            "name": relay_name,
                            "type": "relay",
                            "proxies": [target_name, node['name']]
                        })
            
            if relays:
                if 'proxy-groups' not in config_yaml: config_yaml['proxy-groups'] = []
                config_yaml['proxy-groups'].extend(relays)
            
            # Update ALL proxy-groups
            relay_names = [r['name'] for r in relays]
            select_proxies = managed_node_names + relay_names + external_proxy_names
            for group in config_yaml.get('proxy-groups', []):
                group_type = group.get('type', '')
                if group_type == 'url-test':
                    current = group.get('proxies', [])
                    for name in managed_node_names:
                        if name not in current: current.append(name)
                    group['proxies'] = [p for p in current if p in managed_node_names]
                elif group_type == 'select':
                    current = group.get('proxies', [])
                    for name in select_proxies:
                        if name not in current:
                            if 'DIRECT' in current: current.insert(current.index('DIRECT'), name)
                            else: current.append(name)
                    group['proxies'] = [p for p in current if p in select_proxies or p in ['DIRECT', 'REJECT']]

            # Calculate User-Info Header
            total_limit_bytes = 0
            used_bytes = 0
            earliest_expiry = 0
            
            if current_sub:
                # Use Plan-specific stats for header
                nodes_map = {n['id']: n['used_bytes'] for n in config["nodes"]}
                used_bytes = 0
                for nid in node_ids_filter:
                    if nid in nodes_map:
                        base = current_sub.get('traffic_base', {}).get(nid, 0)
                        used_bytes += max(0, nodes_map[nid] - base)
                total_limit_bytes = int(current_sub.get('limit_gb', 0) * (1024**3))
            else:
                # Aggregate from nodes (fallback)
                filtered_node_confs = [n for n in config["nodes"] if node_ids_filter is None or n["id"] in node_ids_filter]
                for n in filtered_node_confs:
                    total_limit_bytes += (n.get('limit_gb', 0) * (1024**3))
                    used_bytes += n.get('used_bytes', 0)
                    if n.get('expiry'):
                        try:
                            ts = int(time.mktime(time.strptime(n['expiry'], "%Y-%m-%d")))
                            if earliest_expiry == 0 or ts < earliest_expiry: earliest_expiry = ts
                        except: pass
            
            if current_sub and current_sub.get("expiry"):
                sub_ts = int(time.mktime(time.strptime(current_sub['expiry'], "%Y-%m-%d")))
                if earliest_expiry == 0 or sub_ts < earliest_expiry: earliest_expiry = sub_ts
            
            user_info = f"upload=0; download={used_bytes}; total={total_limit_bytes}; expire={earliest_expiry}"

            # Finalize YAML
            yaml_content = yaml.dump(config_yaml, allow_unicode=True, default_flow_style=False, sort_keys=False)
            body = yaml_content.encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/yaml; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Subscription-Userinfo', user_info)
            self.send_header('Content-Disposition', 'attachment; filename="sub_hub.yaml"')
            self.end_headers()
            try:
                self.wfile.write(body)
                self.wfile.flush()
            except BrokenPipeError:
                pass

        except Exception as e:
            self.send_error(500, f"Internal Error: {e}")

    def log_message(self, format, *args): pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads for concurrent browser access."""
    daemon_threads = True

def run_server():
    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, SubBridgeHandler)
    ip = get_public_ip()
    print(f"Sub Hub v2 running at http://{ip}:{PORT}/dashboard")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
