import sqlite3
import json

def get_detailed_info():
    conn = sqlite3.connect('/etc/x-ui/x-ui.db')
    c = conn.cursor()
    
    # Check US Node (Port 4887)
    c.execute('SELECT protocol, settings, stream_settings, enable FROM inbounds WHERE port=4887')
    row = c.fetchone()
    if row:
        print("--- US NODE 4887 ---")
        print(f"Protocol: {row[0]}")
        print(f"Enabled: {row[3]}")
        print(f"Settings: {row[1]}")
        print(f"Stream Settings: {row[2]}")
    else:
        print("US Node not found on port 4887")
    
    # Check JP Node (Port 666)
    c.execute('SELECT protocol, settings, stream_settings, enable FROM inbounds WHERE port=666')
    row = c.fetchone()
    if row:
        print("\n--- JP NODE 666 ---")
        print(f"Protocol: {row[0]}")
        print(f"Enabled: {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    get_detailed_info()
