import json
import urllib.request
import time

# Target Subscription Info
SUB_NAME = "客户-社媒运营专用"
NODE_IDS = ["1770050962"] # DMIT_us Only
LIMIT_GB = 500
EXPIRY = "2026-03-05"
TEMPLATE = "social-media-rules.yaml"

def delete_existing_subs():
    try:
        config = json.load(open('/etc/x-ui/clash/config.json'))
        for s in config.get('subscriptions', []):
            if '客户' in s.get('name', '') or 'Twitter' in s.get('name', ''):
                print(f"Deleting older sub: {s.get('name')} ({s.get('token')})")
                req = urllib.request.Request(f"http://localhost:8080/api/subscriptions?id={s['id']}", method='DELETE')
                urllib.request.urlopen(req)
    except Exception as e:
        print(f"Error during cleanup: {e}")

def create_fresh_sub():
    data = {
        'name': SUB_NAME,
        'node_ids': NODE_IDS,
        'limit_gb': LIMIT_GB,
        'expiry': EXPIRY,
        'template': TEMPLATE,
        'external_proxy': {
            'type': 'socks5',
            'server': 'isp.decodo.com',
            'port': 10001,
            'username': 'spc8vh23z1',
            'password': '8q8dgJWfJc3br8~Zaq'
        }
    }
    req = urllib.request.Request(
        'http://localhost:8080/api/subscriptions',
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    res = json.loads(urllib.request.urlopen(req).read().decode())
    print(f"\n✅ Created fresh subscription: {SUB_NAME}")
    print(f"✅ Token: {res['token']}")
    print(f"✅ Final Link: http://64.186.234.15:8080/sub/{res['token']}")
    return res['token']

if __name__ == "__main__":
    delete_existing_subs()
    time.sleep(1) # Wait for cleanup to persist
    create_fresh_sub()
