import sqlite3
try:
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute("SELECT json_extract('{\"a\":1}', '$.a')")
    print(cursor.fetchone()[0])
    print("JSON Supported")
except Exception as e:
    print(f"Error: {e}")
