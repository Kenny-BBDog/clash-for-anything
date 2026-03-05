#!/usr/bin/env python3
import sqlite3
import json
import time
import random
import string
import base64
import os
import sys

# --- Configuration ---
DB_PATH = '/etc/x-ui/x-ui.db'  # Default 3x-ui database path
PROTOCOL = 'shadowsocks'
METHOD = 'aes-256-gcm'

def generate_random_string(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_public_ip():
    import urllib.request
    try:
        return urllib.request.urlopen('http://v4.ident.me').read().decode('utf8')
    except:
        return 'your_vps_ip'

def add_guest_inbound(duration_hours=0.5, total_gb=0):
    if not os.path.exists(DB_PATH):
        print(f"Error: 3x-ui database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Generate credentials
    guest_id = generate_random_string(8)
    remark = f"Guest-{duration_hours}h-{guest_id}"
    port = random.randint(30000, 60000)
    password = generate_random_string(16)
    
    # Calculate expiry (milliseconds)
    expiry_time = int((time.time() + (duration_hours * 3600)) * 1000)
    
    # Total bytes
    total_bytes = int(total_gb * (1024**3))

    # Prepare settings JSON
    settings = {
        "method": METHOD,
        "password": password,
        "udp": True,
        "clients": []
    }
    
    # Basic stream settings
    stream_settings = {
        "network": "tcp",
        "security": "none",
        "tcpSettings": {
            "header": {
                "type": "none"
            }
        }
    }

    try:
        # Insert into 3x-ui database
        cursor.execute("""
            INSERT INTO inbounds (user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 0, 0, total_bytes, remark, 1, expiry_time, "", port, PROTOCOL, json.dumps(settings), json.dumps(stream_settings), f"inbound-{port}"))
        
        conn.commit()
        
        # Construct SS link
        user_pass = f"{METHOD}:{password}"
        user_pass_encoded = base64.b64encode(user_pass.encode()).decode()
        ip = get_public_ip()
        ss_link = f"ss://{user_pass_encoded}@{ip}:{port}#{remark}"

        if "--json" in sys.argv:
            print(json.dumps({
                "status": "success",
                "link": ss_link,
                "remark": remark,
                "port": port,
                "password": password,
                "method": METHOD,
                "ip": ip,
                "expiry": expiry_time,
                "limit_gb": total_gb
            }))
        else:
            print(f"SUCCESS")
            print(f"LINK: {ss_link}")
            print(f"REMARK: {remark}")
            print(f"EXPIRY: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry_time/1000))}")
            if total_gb > 0:
                print(f"LIMIT: {total_gb} GB")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    duration = 0.5
    total_gb = 0
    if len(sys.argv) > 1:
        try: duration = float(sys.argv[1])
        except: pass
    if len(sys.argv) > 2:
        try: total_gb = float(sys.argv[2])
        except: pass
    add_guest_inbound(duration, total_gb)
