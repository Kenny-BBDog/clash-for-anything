# Independent Egress Chaining Maintenance Guide

This guide documents the "Independent Egress Chaining" feature, which allows different nodes in a single Clash subscription to have independent landing IPs (e.g., US nodes land on US residential IPs and Japan nodes land on Japan residential IPs).

## 1. Configuration (`config.json`)

Subscriptions now support a `chains` list. Each item in the list represents a chained proxy (landing IP) that will be injected into the Clash configuration.

### Data Format
```json
{
    "id": "1770060416",
    "name": "二狗",
    "chains": [
        {
            "name": "🇺🇸 运营专线 (美国静态)",
            "type": "socks5",
            "server": "isp.decodo.com",
            "port": 10003,
            "username": "...",
            "password": "...",
            "dialer_name": "DMIT_us"
        },
        {
            "name": "🇯🇵 运营专线 (日本静态)",
            "type": "socks5",
            "server": "isp.decodo.com",
            "port": 10010,
            "username": "...",
            "password": "...",
            "dialer_name": "JP_IIJ"
        }
    ]
}
```

### Fields
- **name**: Display name in Clash.
- **type**: Protocol (always `socks5` for residential proxies).
- **server/port**: Landing IP provider gateway.
- **username/password**: Credentials for the SOCKS5 proxy.
- **dialer_name**: (Critical) A keyword to match the bottom node. The script will search for this string in the node names to find the dialer.
- **dialer_id**: (Optional) Explicit ID of the bottom node for better stability.

## 2. Server Logic (`sub_bridge.py`)

The server uses the `chains` list to:
1.  **Prioritize Grouping**: External landing IPs are placed at the beginning of the `select` and `url-test` proxy groups.
2.  **Order Persistence**: The landing IPs appear at the top of the proxy list.
3.  **Automatic Dialer Association**: The script automatically links the SOCKS5 proxy to the correct physical node based on `dialer_name`.

## 3. VPS Maintenance & Updates

If the logic needs updating or the egress IPs change, follow these steps:

### Update Code & Templates
```bash
cd /etc/x-ui/clash
curl -o sub_bridge.py https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/sub_bridge.py
mkdir -p templates
curl -o templates/social-media-rules.yaml https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/templates/social-media-rules.yaml
```

### Safe Configuration Patching
Avoid overwriting `config.json` directly as it contains unique tokens and traffic data. Use a Python one-liner to patch the `chains`:

```bash
python3 -c "
import json
p = 'config.json'
with open(p, 'r') as f: c = json.load(f)
for s in c['subscriptions']:
    if s['id'] == '1770060416': # Target 二狗
        s['chains'] = [...] # New configuration
with open(p, 'w') as f: json.dump(c, f, indent=4)
"
```

### Restart Service
```bash
pkill -9 -f sub_bridge.py
nohup python3 sub_bridge.py > sub_bridge.log 2>&1 &
```

## 4. Troubleshooting

- **Timeout**: Check SOCKS5 credentials and firewall. Use the diagnostic script to verify `isp.decodo.com` reachability.
- **Node Missing**: Ensure `dialer_name` correctly matches one of the nodes in the subscription.
- **Clash Error**: Ensure `geosite:cn` and `geosite:google` are used. Avoid non-standard categories like `gplay`.
