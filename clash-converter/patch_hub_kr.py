import json, os
p = '/etc/x-ui/clash/config.json'
with open(p, 'r', encoding='utf-8') as f:
    c = json.load(f)

# Add KR node to nodes list if not exists
kr_node = {
    'id': '1770051088',
    'name': 'KR_VPS',
    'url': 'vless://8ad88d98-fca4-469e-89c8-580d6d05a967@203.231.242.78:2083?type=tcp&security=reality&flow=xtls-rprx-vision&sni=www.yahoo.com&fp=chrome&pbk=Y3aLQPKK0-ipROME3uCO4ivyTgBS1zbuANRDyTmfi2A&sid=e6a80cfca7e1#KR_Reality',
    'limit_gb': 500,
    'used_bytes': 0,
    'expiry': None,
    'chain_with': None
}

if not any(n['id'] == kr_node['id'] for n in c['nodes']):
    c['nodes'].append(kr_node)
    print(f"Node {kr_node['name']} added.")
else:
    # Update existing node URL/config just in case
    for n in c['nodes']:
        if n['id'] == kr_node['id']:
            n['url'] = kr_node['url']
            print(f"Node {kr_node['name']} updated.")

# Add KR node ID to '二狗' subscription
for s in c['subscriptions']:
    if s.get('id') == '1770060416' or s.get('name') == '二狗':
        if kr_node['id'] not in s['node_ids']:
            s['node_ids'].append(kr_node['id'])
            print(f"Node {kr_node['id']} added to subscription {s['name']}.")
        if 'traffic_base' in s and kr_node['id'] not in s['traffic_base']:
            s['traffic_base'][kr_node['id']] = 0

with open(p, 'w', encoding='utf-8') as f:
    json.dump(c, f, indent=4, ensure_ascii=False)
print("Configuration patched successfully.")
