import json
import urllib.request
import sys

TOKEN = "tFhmRkkhMFpScsow"
NEW_PROXY = {
    'type': 'socks5',
    'server': 'isp.decodo.com',
    'port': 10003,
    'username': 'spc8vh23z1',
    'password': '8q8dgJWfJc3br8~Zaq'
}

def update_sub():
    # 1. Get ID
    config = json.load(open('/etc/x-ui/clash/config.json'))
    sub = next((s for s in config['subscriptions'] if s['token'] == TOKEN), None)
    
    if not sub:
        print("Sub not found")
        sys.exit(1)

    print(f"Updating sub: {sub['name']} ({sub['id']})")

    # 2. Update via API
    data = {
        'name': sub['name'],
        'node_ids': ["1770050962"], # Enforce DMIT only for chaining
        'template': 'social-media-rules.yaml', # Enforce simplified UI
        'external_proxy': NEW_PROXY
    }
    
    req = urllib.request.Request(
        f"http://localhost:8080/api/subscriptions?id={sub['id']}",
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST' # Handler uses POST for updates too based on id param logic, or we can use the PUT logic if preferred, but previous script used POST to /api/subscriptions?id=... which goes to do_POST or do_PUT? 
        # Wait, usually POST is create. PUT is update. 
        # Let's check sub_bridge.py logic again. 
        # POST /api/subscriptions with ?id=... updates existing.
    )
    
    try:
        res = urllib.request.urlopen(req)
        print(res.read().decode())
        print("✅ Update success!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_sub()
