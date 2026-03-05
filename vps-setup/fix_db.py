#!/usr/bin/env python3
import sqlite3
import json

def heal_db():
    db_path = '/etc/x-ui/x-ui.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # We check all inbounds that might have clients
    protocols_to_check = ['shadowsocks', 'vmess', 'vless', 'trojan']
    
    cursor.execute("SELECT id, protocol, settings, remark FROM inbounds")
    rows = cursor.fetchall()
    
    repaired_count = 0
    
    for row in rows:
        row_id, protocol, settings_str, remark = row
        
        if protocol.lower() not in protocols_to_check:
            continue
            
        try:
            settings = json.loads(settings_str)
        except Exception as e:
            print(f"Error parsing JSON for ID {row_id} ({remark}): {e}")
            continue
            
        # Check if 'clients' is missing
        if 'clients' not in settings:
            print(f"Repaired ID {row_id} ({remark}): Missing 'clients' field")
            settings['clients'] = []
            
            # Update the database
            new_settings_str = json.dumps(settings)
            cursor.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (new_settings_str, row_id))
            repaired_count += 1
        elif not isinstance(settings['clients'], list):
            print(f"Repaired ID {row_id} ({remark}): 'clients' is not a list")
            settings['clients'] = []
            new_settings_str = json.dumps(settings)
            cursor.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (new_settings_str, row_id))
            repaired_count += 1

    conn.commit()
    conn.close()
    
    print(f"\nScan complete. Repaired {repaired_count} entries.")
    if repaired_count > 0:
        print("Please restart 3x-ui to apply changes: systemctl restart x-ui")

if __name__ == "__main__":
    heal_db()
