import sqlite3
import sys

# Set stdout encoding to utf-8 just in case
sys.stdout.reconfigure(encoding='utf-8')

def verify():
    conn = sqlite3.connect('e:/Project/Calk_KMF/calk_kmf.sqlite')
    cursor = conn.cursor()

    print("Running VACUUM...")
    conn.execute("VACUUM")
    print("VACUUM done.")

    cursor.execute("SELECT COUNT(*) FROM t_bazi_hourly")
    print(f"t_bazi_hourly count: {cursor.fetchone()[0]}")

    try:
        cursor.execute("SELECT COUNT(*) FROM v_bazi_hourly")
        print(f"v_bazi_hourly count: {cursor.fetchone()[0]}")
    except Exception as e:
        print(f"Error querying v_bazi_hourly: {e}")

    cursor.execute("SELECT COUNT(*) FROM t_qumen_chauby_hourly")
    print(f"t_qumen_chauby_hourly count: {cursor.fetchone()[0]}")

    print("Sample Qimen rows:")
    cursor.execute("SELECT * FROM t_qumen_chauby_hourly LIMIT 5")
    for row in cursor.fetchall():
        try:
            print(row)
        except Exception:
            print(repr(row))

    conn.close()

if __name__ == "__main__":
    verify()
