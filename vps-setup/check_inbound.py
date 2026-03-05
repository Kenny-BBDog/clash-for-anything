import sqlite3
import json

def check_inbound():
    conn = sqlite3.connect('/etc/x-ui/x-ui.db')
    c = conn.cursor()
    c.execute('SELECT remark, port, enable, total, up, down FROM inbounds WHERE port=4887')
    row = c.fetchone()
    if row:
        print(f"Remark: {row[0]}")
        print(f"Port: {row[1]}")
        print(f"Enabled: {row[2]}")
        print(f"Total Limit: {row[3]} ({row[3]/(1024**3):.2f} GB)")
        print(f"Used (Up+Down): {row[4]+row[5]} ({(row[4]+row[5])/(1024**3):.2f} GB)")
        if row[3] > 0 and (row[4]+row[5]) >= row[3]:
            print("WARNING: Traffic limit exceeded in 3x-ui!")
    else:
        print("Inbound not found for port 4887")
    conn.close()

if __name__ == "__main__":
    check_inbound()
