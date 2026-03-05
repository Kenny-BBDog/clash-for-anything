import sqlite3
import os

def repair_3x_ui(db_path='/etc/x-ui/x-ui.db'):
    """
    Repairs 3x-ui database by removing malformed or troublesome entries.
    Common causes: Guest pass generation bugs, malformed Shadowsocks settings.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Remove malformed Guest entries
    c.execute("DELETE FROM inbounds WHERE remark LIKE 'Guest-%'")
    deleted_guests = c.rowcount
    
    # 2. Prevent duplication issues (Clean orphans)
    # This is a template for finding nodes with invalid settings JSON
    c.execute("SELECT id, remark, settings FROM inbounds")
    rows = c.fetchall()
    invalid_ids = []
    import json
    for r_id, remark, settings in rows:
        try:
            json.loads(settings)
        except:
            invalid_ids.append(r_id)
    
    for r_id in invalid_ids:
        c.execute("DELETE FROM inbounds WHERE id=?", (r_id,))
    
    conn.commit()
    conn.close()
    
    print(f"Repair Complete:")
    print(f"- Deleted {deleted_guests} guest entries.")
    print(f"- Removed {len(invalid_ids)} nodes with invalid settings JSON.")

if __name__ == "__main__":
    repair_3x_ui()
