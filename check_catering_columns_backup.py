
from main import get_db_connection

conn = None
cur = None

try:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'catering_bookings'
        ORDER BY ordinal_position;
    """)

    print("Catering bookings table ke columns:")
    for row in cur.fetchall():
        print("-", row[0])

except Exception as e:
    print("Check failed:", e)

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
