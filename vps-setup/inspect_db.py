import sqlite3
import json

def inspect():
    conn = sqlite3.connect('/etc/x-ui/x-ui.db')
    c = conn.cursor()
    
    # Check inbounds schema
    c.execute('PRAGMA table_info(inbounds)')
    cols = c.fetchall()
    print("--- INBOUNDS COLUMNS ---")
    for col in cols: print(col)
    
    # Sample data
    c.execute('SELECT id, remark, port, up, down, total FROM inbounds LIMIT 5')
    rows = c.fetchall()
    print("\n--- INBOUNDS SAMPLE DATA ---")
    for row in rows: print(row)

    # Check for clients (if 3x-ui version supports multiple clients per inbound)
    try:
        c.execute('PRAGMA table_info(clients)')
        client_cols = c.fetchall()
        print("\n--- CLIENTS COLUMNS ---")
        for col in client_cols: print(col)
    except:
        print("\nNo clients table found.")

    conn.close()

if __name__ == "__main__":
    inspect()
