import json
import urllib.request
import sys

TOKEN_TARGET = "tFhmRkkhMFpScsow"
TOKEN_DUPE = "Nlwz1qTgRZ45djcs"

NEW_PROXY = {
    'type': 'socks5',
    'server': 'isp.decodo.com',
    'port': 10003,
    'username': 'spc8vh23z1',
    'password': '8q8dgJWfJc3br8~Zaq'
}

def clean_and_update():
    config = json.load(open('/etc/x-ui/clash/config.json'))
    
    # 1. Delete Duplicate
    dupe = next((s for s in config['subscriptions'] if s['token'] == TOKEN_DUPE), None)
    if dupe:
        print(f"Deleting duplicate sub: {dupe['name']} ({dupe['token']})")
        try:
            req = urllib.request.Request(f"http://localhost:8080/api/subscriptions?id={dupe['id']}", method='DELETE')
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"Error deleting dupe: {e}")

    # 2. Update Target
    sub = next((s for s in config['subscriptions'] if s['token'] == TOKEN_TARGET), None)
    if not sub:
        print("Target sub not found")
        sys.exit(1)

    print(f"Updating target sub: {sub['name']} ({sub['token']})")
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
        method='PUT' # CORRECT METHOD
    )
    
    try:
        res = urllib.request.urlopen(req)
        print(res.read().decode())
        print("✅ Target Updated Successfully!")
    except Exception as e:
        print(f"❌ Error updating target: {e}")

if __name__ == "__main__":
    clean_and_update()
