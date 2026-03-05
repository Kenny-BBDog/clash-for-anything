#!/usr/bin/env python3
import json

# Load config
config = json.load(open('/etc/x-ui/clash/config.json', 'r'))

# Deduplicate by URL
seen_urls = set()
new_nodes = []
for n in config.get('nodes', []):
    if n['url'] not in seen_urls:
        seen_urls.add(n['url'])
        new_nodes.append(n)
    else:
        print(f"Removing duplicate: {n['name']}")

config['nodes'] = new_nodes
json.dump(config, open('/etc/x-ui/clash/config.json', 'w'), indent=4)
print(f"Final nodes: {len(new_nodes)}")
