import sqlite3
import json

def compare_settings():
    # 1. Get Sub Hub Config
    try:
        with open('/etc/x-ui/clash/config.json', 'r') as f:
            subhub_config = json.load(f)
            us_node = next(n for n in subhub_config['nodes'] if n['name'] == 'DMIT_us')
            print(f"Sub Hub US Node Link: {us_node['url']}")
    except Exception as e:
        print(f"Error reading Sub Hub config: {e}")

    # 2. Get 3x-ui Database Settings
    conn = sqlite3.connect('/etc/x-ui/x-ui.db')
    c = conn.cursor()
    c.execute('SELECT protocol, settings, stream_settings FROM inbounds WHERE port=4887')
    row = c.fetchone()
    if row:
        print("\n--- 3x-ui Inbound (Port 4887) ---")
        print(f"Protocol: {row[0]}")
        settings = json.loads(row[1])
        print(f"Settings: {json.dumps(settings, indent=2)}")
        stream = json.loads(row[2])
        print(f"Stream Settings: {json.dumps(stream, indent=2)}")
    else:
        print("\n3x-ui Inbound 4887 not found!")
    conn.close()

if __name__ == "__main__":
    compare_settings()
