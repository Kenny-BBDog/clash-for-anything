import json
import urllib.request

# Get the subscription ID
config = json.load(open('/etc/x-ui/clash/config.json'))
sub = next((s for s in config['subscriptions'] if '社媒运营' in s.get('name', '')), None)

if sub:
    sub_id = sub['id']
    # Update subscription to remove external_proxy
    data = {
        'name': sub['name'],
        'node_ids': sub['node_ids'],
        'limit_gb': sub.get('limit_gb', 0),
        'expiry': sub.get('expiry'),
        'external_proxy': None  # Remove external proxy
    }
    req = urllib.request.Request(
        f'http://localhost:8080/api/subscriptions?id={sub_id}',
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    print(urllib.request.urlopen(req).read().decode())
    print(f"Updated subscription {sub['name']} - removed external_proxy")
else:
    print('Subscription not found')
